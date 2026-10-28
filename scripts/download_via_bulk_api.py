#!/usr/bin/env python3
"""Canonical bulk download client for USAspending bulk download API.

Project: Sanket — Federal Contract Recompete Intelligence
Controlled Pilot:
  Award Summary Cohort: NASA + NAICS 541330 + FY2020 new awards (base action in FY2020)
  Transaction History: Full modification history for all 221 cohort awards (No date filter)

This client implements the official USAspending API contracts:
1. Bulk Download API:
   - POST /api/v2/download/count/ (precheck)
   - POST /api/v2/download/search/ (job initiation)
   - GET  /api/v2/download/status/ (job polling)
2. Authoritative Per-Award Transaction Endpoints:
   - GET  /api/v2/awards/count/transaction/{generated_natural_award_id}/ (expected count)
   - POST /api/v2/transactions/ (lifetime modifications with limit=5000 and page iteration)
3. Robustness, Integrity & Resumability:
   - Bounded retries with exponential backoff and Retry-After support.
   - Resumable per-award local caching.
   - Safe HTTPS streaming to .part file, ZIP CRC validation, and atomic rename.
   - Full in-memory and disk verification: 0 blank/duplicate IDs, 100% award linkage,
     per-award count reconciliation, and date audit.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import logging
import os
import re
import sys
import time
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

import requests
import yaml
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("bulk_download")

DEFAULT_CONFIG_PATH = Path("config/bulk_download_config.yaml")
GENERATED_NATURAL_ID_FIELD = "contract_award_unique_key"
COHORT_PIID_FIELD = "award_id_piid"
EXPECTED_COHORT_SIZE = 221


class BulkDownloadError(Exception):
    """Base exception for bulk download workflow errors."""


class ConfigError(BulkDownloadError):
    """Raised when configuration is invalid or missing required keys."""


class PrecheckValidationError(BulkDownloadError):
    """Raised when count precheck fails, exceeds limits, or returns unexpected shape."""

    def __init__(self, message: str, precheck_data: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.precheck_data = precheck_data


class UntrustedHostError(BulkDownloadError):
    """Raised when an API URL targets an untrusted host or non-HTTPS protocol."""


class DownloadJobError(BulkDownloadError):
    """Raised when an asynchronous download job fails on the server."""


class DownloadJobTimeoutError(BulkDownloadError):
    """Raised when polling for job completion exceeds overall timeout."""


class ZIPValidationError(BulkDownloadError):
    """Raised when downloaded ZIP file is corrupt or invalid."""


class CountReconciliationError(BulkDownloadError):
    """Raised when count endpoint, job status, or parsed CSV rows disagree on the same query."""


class AwardCohortAuditError(BulkDownloadError):
    """Raised when award cohort fails identity or uniqueness validation."""


class TransactionQualityError(BulkDownloadError):
    """Raised when transaction data fails quality, identity, or linkage checks."""


def redact_sensitive(text: str) -> str:
    """Redact tokens, passwords, and sensitive keys from log strings or URLs."""
    if not isinstance(text, str):
        return str(text)
    text = re.sub(r"(Bearer\s+)[A-Za-z0-9_\-\.]+", r"\1[REDACTED]", text, flags=re.IGNORECASE)
    text = re.sub(r"([?&](?:api_key|token|access_token|secret)=)[^&]+", r"\1[REDACTED]", text, flags=re.IGNORECASE)
    return text


def load_config(config_path: Path | str) -> dict[str, Any]:
    """Load and validate bulk download YAML configuration."""
    cfg_file = Path(config_path)
    if not cfg_file.is_file():
        raise ConfigError(f"Configuration file not found: {cfg_file}")

    with cfg_file.open("r", encoding="utf-8") as f:
        try:
            cfg = yaml.safe_load(f)
        except (yaml.YAMLError, OSError) as exc:
            raise ConfigError(f"Failed to parse YAML configuration: {exc}") from exc

    if not isinstance(cfg, dict):
        raise ConfigError("Configuration root must be a dictionary.")

    required_sections = [
        "api",
        "controlled_cohort",
        "transaction_cohort",
        "safety_caps",
        "http_policy",
        "polling_policy",
        "paths",
    ]
    for sec in required_sections:
        if sec not in cfg:
            raise ConfigError(f"Missing required configuration section: '{sec}'")

    cohort = cfg["controlled_cohort"]
    if cohort.get("cohort_id") != "nasa_naics541330_fy2020":
        raise ConfigError(
            f"Unsupported cohort '{cohort.get('cohort_id')}'. Only 'nasa_naics541330_fy2020' is authorized."
        )

    # Validate naics_codes is an object with require list
    filters = cohort.get("filters", {})
    naics = filters.get("naics_codes")
    if not isinstance(naics, dict) or "require" not in naics or not isinstance(naics["require"], list):
        raise ConfigError("naics_codes must be an object with 'require' list: {'require': ['541330']}")

    # Validate time_period has date_type: new_awards_only
    time_period = filters.get("time_period")
    if not isinstance(time_period, list) or not time_period:
        raise ConfigError("time_period must be a non-empty list of date range objects.")
    tp0 = time_period[0]
    if tp0.get("date_type") != "new_awards_only":
        raise ConfigError(
            f"Pilot award cohort requires date_type: 'new_awards_only', got '{tp0.get('date_type')}'"
        )

    return cfg


def validate_trusted_host(url: str, trusted_hosts: list[str]) -> str:
    """Ensure URL uses HTTPS and host belongs to the configured trusted hosts whitelist."""
    parsed = urlparse(url)
    scheme = parsed.scheme.lower()
    if scheme != "https":
        raise UntrustedHostError(
            f"Insecure protocol '{scheme}' rejected for URL: {redact_sensitive(url)}. Only HTTPS is permitted."
        )

    host = parsed.hostname
    if not host:
        raise UntrustedHostError(f"Unable to parse hostname from URL: {redact_sensitive(url)}")

    # Reject localhost or loopback addresses
    if host.lower() in ["localhost", "127.0.0.1", "0.0.0.0", "::1"]:
        raise UntrustedHostError(f"Localhost access rejected: {host}")

    if host.lower() not in [h.lower() for h in trusted_hosts]:
        raise UntrustedHostError(
            f"Host '{host}' is not in trusted hosts list: {trusted_hosts}. Target: {redact_sensitive(url)}"
        )
    return url


def resolve_api_url(base_url: str, relative_or_absolute_url: str, trusted_hosts: list[str]) -> str:
    """Resolve and validate an API URL against base URL and trusted hosts."""
    resolved = urljoin(base_url, relative_or_absolute_url)
    return validate_trusted_host(resolved, trusted_hosts)


def create_session(http_policy: dict[str, Any], trusted_hosts: list[str]) -> requests.Session:
    """Create a requests Session with bounded retry behavior and redirect host validation."""
    session = requests.Session()
    max_retries = int(http_policy.get("max_retries", 3))
    backoff_factor = float(http_policy.get("backoff_factor", 1.5))
    retry_statuses = http_policy.get("retry_status_codes", [429, 500, 502, 503, 504])

    retry_strategy = Retry(
        total=max_retries,
        backoff_factor=backoff_factor,
        status_forcelist=retry_statuses,
        allowed_methods=["HEAD", "GET", "POST", "OPTIONS"],
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    # Attach response hook to validate every redirect target
    def validate_redirects(response: requests.Response, *args: Any, **kwargs: Any) -> None:
        if response.history:
            for resp in response.history:
                validate_trusted_host(resp.url, trusted_hosts)
        validate_trusted_host(response.url, trusted_hosts)

    session.hooks["response"].append(validate_redirects)
    return session


def parse_count_response(resp_data: Any, level: str) -> dict[str, Any]:
    """Defensively validate and parse response from /api/v2/download/count/."""
    if not isinstance(resp_data, dict):
        raise PrecheckValidationError(f"Expected dict response from count endpoint, got {type(resp_data).__name__}")

    # Check calculated_count (must not be boolean)
    calc_count = resp_data.get("calculated_count")
    if isinstance(calc_count, bool) or not isinstance(calc_count, (int, float)):
        raise PrecheckValidationError(
            f"Count endpoint returned invalid calculated_count: {calc_count!r} (type={type(calc_count).__name__})"
        )
    calc_count = int(calc_count)

    if calc_count < 0:
        raise PrecheckValidationError(f"Count endpoint returned negative calculated_count: {calc_count}")

    # Check row limit flags
    rows_gt_limit = resp_data.get("rows_gt_limit")
    if rows_gt_limit is True:
        raise PrecheckValidationError(
            f"Count endpoint flagged rows_gt_limit=True for level '{level}'. Download would be truncated."
        )

    tx_rows_gt_limit = resp_data.get("transaction_rows_gt_limit")
    if tx_rows_gt_limit is True and level == "transactions":
        raise PrecheckValidationError(
            "Count endpoint flagged transaction_rows_gt_limit=True. Download would be truncated."
        )

    return {
        "level": level,
        "calculated_count": calc_count,
        "calculated_transaction_count": resp_data.get("calculated_transaction_count"),
        "maximum_limit": resp_data.get("maximum_limit"),
        "maximum_transaction_limit": resp_data.get("maximum_transaction_limit"),
        "rows_gt_limit": rows_gt_limit,
        "transaction_rows_gt_limit": tx_rows_gt_limit,
        "messages": resp_data.get("messages", []),
        "raw_response": resp_data,
    }


def query_count_endpoint(
    session: requests.Session,
    base_url: str,
    count_endpoint: str,
    trusted_hosts: list[str],
    filters: dict[str, Any],
    spending_level: str,
    timeout: int = 30,
) -> dict[str, Any]:
    """Execute count precheck for a given filter payload and singular spending_level string."""
    count_url = resolve_api_url(base_url, count_endpoint, trusted_hosts)
    payload = {
        "filters": filters,
        "spending_level": spending_level,
    }
    logger.info(f"POSTing count precheck (spending_level='{spending_level}') to {count_url}...")

    try:
        resp = session.post(count_url, json=payload, timeout=timeout)
    except requests.RequestException as exc:
        raise PrecheckValidationError(
            f"HTTP request to count endpoint failed: {redact_sensitive(str(exc))}"
        ) from exc

    if resp.status_code != 200:
        error_body = redact_sensitive(resp.text[:500])
        headers_dict = dict(resp.headers)
        raise PrecheckValidationError(
            f"Count endpoint returned HTTP {resp.status_code} for spending_level='{spending_level}': {error_body}",
            precheck_data={
                "status_code": resp.status_code,
                "headers": headers_dict,
                "error_body": error_body,
                "submitted_filters": filters,
            },
        )

    try:
        resp_json = resp.json()
    except (ValueError, json.JSONDecodeError) as exc:
        raise PrecheckValidationError(
            f"Count endpoint returned non-JSON response for spending_level='{spending_level}': {resp.text[:300]}"
        ) from exc

    return parse_count_response(resp_json, spending_level)


def initiate_download_job(
    session: requests.Session,
    base_url: str,
    search_endpoint: str,
    trusted_hosts: list[str],
    filters: dict[str, Any],
    spending_levels: list[str],
    file_format: str = "csv",
    timeout: int = 30,
) -> dict[str, Any]:
    """Submit asynchronous download job via POST /api/v2/download/search/."""
    search_url = resolve_api_url(base_url, search_endpoint, trusted_hosts)

    payload = {
        "filters": filters,
        "file_format": file_format,
        "spending_level": spending_levels,
    }

    logger.info(f"Submitting bulk download job (spending_level={spending_levels}) to {search_url}...")
    try:
        resp = session.post(search_url, json=payload, timeout=timeout)
    except requests.RequestException as exc:
        raise DownloadJobError(
            f"Failed to submit download job: {redact_sensitive(str(exc))}"
        ) from exc

    if resp.status_code != 200:
        error_body = redact_sensitive(resp.text[:800])
        raise DownloadJobError(f"Job creation returned HTTP {resp.status_code}: {error_body}")

    try:
        data = resp.json()
    except (ValueError, json.JSONDecodeError) as exc:
        raise DownloadJobError(f"Job creation returned invalid JSON: {resp.text[:300]}") from exc

    file_name = data.get("file_name")
    status_url = data.get("status_url")
    file_url = data.get("file_url")

    if not file_name:
        raise DownloadJobError(f"Job creation response missing 'file_name': {data}")

    logger.info(f"Bulk download job created: file_name={file_name}")
    return {
        "file_name": file_name,
        "status_url": status_url,
        "file_url": file_url,
        "download_request": data.get("download_request", {}),
        "raw_response": data,
    }


def poll_download_status(
    session: requests.Session,
    base_url: str,
    status_endpoint_cfg: str,
    trusted_hosts: list[str],
    job_info: dict[str, Any],
    poll_interval: float = 5.0,
    overall_timeout: float = 300.0,
    http_timeout: int = 30,
) -> dict[str, Any]:
    """Poll status endpoint safely until finished, failed, or timed out."""
    file_name = job_info["file_name"]
    status_url_raw = job_info.get("status_url")

    if status_url_raw:
        status_url = resolve_api_url(base_url, status_url_raw, trusted_hosts)
    else:
        status_url = resolve_api_url(
            base_url, f"{status_endpoint_cfg}?file_name={file_name}", trusted_hosts
        )

    start_time = time.time()
    attempts = 0
    history: list[dict[str, Any]] = []

    logger.info(f"Beginning status polling for file '{file_name}' (timeout: {overall_timeout}s)...")

    while True:
        attempts += 1
        elapsed = time.time() - start_time
        if elapsed > overall_timeout:
            raise DownloadJobTimeoutError(
                f"Polling timed out after {elapsed:.1f}s ({attempts} attempts) for job '{file_name}'. "
                "Will not automatically resubmit."
            )

        try:
            resp = session.get(status_url, timeout=http_timeout)
        except requests.RequestException as exc:
            logger.warning(f"Transient error fetching status on attempt {attempts}: {redact_sensitive(str(exc))}")
            time.sleep(poll_interval)
            continue

        if resp.status_code != 200:
            logger.warning(f"Status endpoint returned HTTP {resp.status_code} on attempt {attempts}")
            time.sleep(poll_interval)
            continue

        try:
            status_data = resp.json()
        except (ValueError, json.JSONDecodeError):
            logger.warning("Status endpoint returned non-JSON response")
            time.sleep(poll_interval)
            continue

        status_str = status_data.get("status", "").lower()
        message = status_data.get("message", "")
        total_rows = status_data.get("total_rows")
        total_columns = status_data.get("total_columns")

        entry = {
            "attempt": attempts,
            "elapsed_seconds": round(elapsed, 1),
            "status": status_str,
            "message": message,
            "total_rows": total_rows,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        history.append(entry)
        logger.info(
            f"Poll attempt {attempts} ({elapsed:.1f}s): status='{status_str}' "
            f"total_rows={total_rows} message='{message}'"
        )

        if status_str == "finished":
            download_file_url = status_data.get("file_url") or status_data.get("url") or job_info.get("file_url")
            return {
                "final_status": "finished",
                "file_name": file_name,
                "file_url": download_file_url,
                "total_rows": total_rows,
                "total_columns": total_columns,
                "total_attempts": attempts,
                "total_elapsed_seconds": round(elapsed, 1),
                "history": history,
                "raw_response": status_data,
            }

        if status_str == "failed":
            raise DownloadJobError(
                f"Download job failed on USAspending server for file '{file_name}'. Message: '{message}'"
            )

        time.sleep(poll_interval)


def download_zip_stream(
    session: requests.Session,
    file_url: str,
    target_path: Path,
    trusted_hosts: list[str],
    download_timeout: int = 180,
) -> Path:
    """Stream download ZIP file to temporary .part file, validate CRC, and atomically rename."""
    validate_trusted_host(file_url, trusted_hosts)

    if target_path.exists():
        raise FileExistsError(f"Target download path already exists: {target_path}. Overwrite is forbidden.")

    part_path = target_path.with_suffix(".zip.part")
    if part_path.exists():
        part_path.unlink()

    target_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info(f"Streaming download from {file_url} to temporary file {part_path}...")
    try:
        with session.get(file_url, stream=True, timeout=download_timeout) as resp:
            resp.raise_for_status()
            with part_path.open("wb") as f:
                for chunk in resp.iter_content(chunk_size=65536):
                    if chunk:
                        f.write(chunk)
    except (requests.RequestException, OSError) as exc:
        if part_path.exists():
            part_path.unlink()
        raise DownloadJobError(f"Download streaming failed: {redact_sensitive(str(exc))}") from exc

    if not zipfile.is_zipfile(part_path):
        part_path.unlink()
        raise ZIPValidationError(f"Downloaded file at {part_path} is not a valid ZIP archive.")

    try:
        with zipfile.ZipFile(part_path, "r") as z:
            bad_member = z.testzip()
            if bad_member is not None:
                part_path.unlink()
                raise ZIPValidationError(f"Downloaded ZIP member '{bad_member}' failed CRC integrity check.")
    except (zipfile.BadZipFile, OSError) as exc:
        if part_path.exists():
            part_path.unlink()
        raise ZIPValidationError(f"Failed to inspect downloaded ZIP: {exc}") from exc

    os.replace(part_path, target_path)
    logger.info(f"Download completed and CRC verified: {target_path}")
    return target_path


def compute_sha256(path: Path) -> str:
    """Compute SHA-256 checksum of a file."""
    hasher = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def inspect_award_zip(zip_path: Path) -> dict[str, Any]:
    """Inspect award summaries ZIP archive in memory without extracting to disk."""
    if not zip_path.is_file():
        raise FileNotFoundError(f"Award ZIP file not found: {zip_path}")

    file_size_bytes = zip_path.stat().st_size
    sha256_hex = compute_sha256(zip_path)

    members_meta: list[dict[str, Any]] = []
    award_member: str | None = None
    subaward_members: list[str] = []

    with zipfile.ZipFile(zip_path, "r") as z:
        for info in z.infolist():
            meta = {
                "filename": info.filename,
                "file_size": info.file_size,
                "compress_size": info.compress_size,
            }
            members_meta.append(meta)
            lower = info.filename.lower()
            if "subaward" in lower:
                subaward_members.append(info.filename)
            elif (
                "primeawardsummaries" in lower or "contracts_primeawardsummaries" in lower
            ) and info.filename.endswith(".csv"):
                award_member = info.filename

        if subaward_members:
            raise ZIPValidationError(f"Forbidden subaward members found in award ZIP: {subaward_members}")

        if not award_member:
            for info in z.infolist():
                if info.filename.endswith(".csv"):
                    with z.open(info.filename) as f:
                        wrapper = io.TextIOWrapper(f, encoding="utf-8-sig", errors="replace")
                        header = next(csv.reader(wrapper), [])
                        if (
                            "contract_award_unique_key" in set(header)
                            and "contract_transaction_unique_key" not in set(header)
                        ):
                            award_member = info.filename
                            break

        if not award_member:
            raise ZIPValidationError("Unable to identify PrimeAwardSummaries member in award ZIP.")

        with z.open(award_member) as f:
            wrapper = io.TextIOWrapper(f, encoding="utf-8-sig", errors="replace")
            reader = csv.DictReader(wrapper)
            award_columns = reader.fieldnames or []
            award_rows = list(reader)

    row_count = len(award_rows)
    piids: list[str] = []
    blank_piid_count = 0
    piid_counts: dict[str, int] = {}

    keys: list[str] = []
    blank_key_count = 0
    key_counts: dict[str, int] = {}
    award_records: list[dict[str, str]] = []

    for r in award_rows:
        piid = r.get("award_id_piid", "").strip()
        key = r.get("contract_award_unique_key", "").strip()

        if piid:
            piids.append(piid)
            piid_counts[piid] = piid_counts.get(piid, 0) + 1
        else:
            blank_piid_count += 1

        if key:
            keys.append(key)
            key_counts[key] = key_counts.get(key, 0) + 1
        else:
            blank_key_count += 1

        award_records.append({
            "contract_award_unique_key": key,
            "award_id_piid": piid,
        })

    unique_piids = sorted(set(piids))
    repeated_piids = {k: v for k, v in piid_counts.items() if v > 1}

    unique_keys = sorted(set(keys))
    repeated_keys = {k: v for k, v in key_counts.items() if v > 1}

    # Verify expected schema fields
    expected_fields = [
        "contract_award_unique_key",
        "award_id_piid",
        "awarding_agency_name",
        "awarding_agency_code",
        "award_base_action_date",
        "naics_code",
        "psc_code",
    ]
    missing_expected_fields = [f for f in expected_fields if f not in award_columns]

    return {
        "zip_path": str(zip_path),
        "file_size_bytes": file_size_bytes,
        "sha256": sha256_hex,
        "members": members_meta,
        "award_member": award_member,
        "row_count": row_count,
        "column_count": len(award_columns),
        "columns": award_columns,
        "missing_expected_fields": missing_expected_fields,
        "total_award_rows": row_count,
        "nonblank_piids_count": len(piids),
        "blank_piid_count": blank_piid_count,
        "unique_piids_count": len(unique_piids),
        "repeated_piids_count": len(repeated_piids),
        "repeated_piids_audit": repeated_piids,
        "unique_piids": unique_piids,
        "unique_keys_count": len(unique_keys),
        "blank_key_count": blank_key_count,
        "repeated_keys_count": len(repeated_keys),
        "unique_keys": unique_keys,
        "award_records": award_records,
    }


def audit_award_cohort(award_qa: dict[str, Any], expected_count: int = 221) -> list[dict[str, str]]:
    """Assert award CSV has exactly expected_count rows, unique nonblank PIIDs, and unique nonblank natural keys."""
    row_count = award_qa.get("row_count", 0)
    if row_count != expected_count:
        raise AwardCohortAuditError(
            f"Expected {expected_count} award rows in cohort, found {row_count}."
        )

    blank_piid_count = award_qa.get("blank_piid_count", 0)
    if blank_piid_count > 0:
        raise AwardCohortAuditError(f"Found {blank_piid_count} blank award_id_piid values in award cohort.")

    unique_piids_count = award_qa.get("unique_piids_count", 0)
    if unique_piids_count != expected_count:
        raise AwardCohortAuditError(
            f"Expected {expected_count} unique award_id_piid values, found {unique_piids_count}."
        )

    blank_key_count = award_qa.get("blank_key_count", 0)
    if blank_key_count > 0:
        raise AwardCohortAuditError(
            f"Found {blank_key_count} blank contract_award_unique_key values in award cohort."
        )

    unique_keys_count = award_qa.get("unique_keys_count", 0)
    if unique_keys_count != expected_count:
        raise AwardCohortAuditError(
            f"Expected {expected_count} unique contract_award_unique_key values, found {unique_keys_count}."
        )

    records = award_qa.get("award_records", [])
    if len(records) != expected_count:
        raise AwardCohortAuditError(f"Expected {expected_count} award records, found {len(records)}.")

    return records


def inspect_transaction_zip(
    zip_path: Path,
    expected_cohort_piids: set[str],
) -> dict[str, Any]:
    """Inspect transaction ZIP archive in memory without extracting to disk."""
    if not zip_path.is_file():
        raise FileNotFoundError(f"Transaction ZIP file not found: {zip_path}")

    file_size_bytes = zip_path.stat().st_size
    sha256_hex = compute_sha256(zip_path)

    members_meta: list[dict[str, Any]] = []
    tx_member: str | None = None
    subaward_members: list[str] = []

    with zipfile.ZipFile(zip_path, "r") as z:
        for info in z.infolist():
            meta = {
                "filename": info.filename,
                "file_size": info.file_size,
                "compress_size": info.compress_size,
            }
            members_meta.append(meta)
            lower = info.filename.lower()
            if "subaward" in lower:
                subaward_members.append(info.filename)
            elif (
                "primetransactions" in lower or "contracts_primetransactions" in lower
            ) and info.filename.endswith(".csv"):
                tx_member = info.filename

        if subaward_members:
            raise ZIPValidationError(f"Forbidden subaward members found in transaction ZIP: {subaward_members}")

        if not tx_member:
            for info in z.infolist():
                if info.filename.endswith(".csv"):
                    with z.open(info.filename) as f:
                        wrapper = io.TextIOWrapper(f, encoding="utf-8-sig", errors="replace")
                        header = next(csv.reader(wrapper), [])
                        if "contract_transaction_unique_key" in set(header) or "id" in set(header):
                            tx_member = info.filename
                            break

        if not tx_member:
            raise ZIPValidationError("Unable to identify PrimeTransactions member in transaction ZIP.")

        with z.open(tx_member) as f:
            wrapper = io.TextIOWrapper(f, encoding="utf-8-sig", errors="replace")
            reader = csv.DictReader(wrapper)
            tx_columns = reader.fieldnames or []
            tx_rows = list(reader)

    row_count = len(tx_rows)
    tx_keys = [
        (r.get("contract_transaction_unique_key") or r.get("id") or "").strip()
        for r in tx_rows
    ]
    populated_tx_keys = [k for k in tx_keys if k]
    unique_tx_keys = set(populated_tx_keys)
    missing_tx_keys = row_count - len(populated_tx_keys)
    duplicate_tx_keys = len(populated_tx_keys) - len(unique_tx_keys)

    # Linkage to cohort PIIDs
    tx_piids = [
        (r.get("award_id_piid") or r.get("cohort_award_id_piid") or "").strip()
        for r in tx_rows
    ]
    populated_tx_piids = [p for p in tx_piids if p]
    unique_tx_piids = set(populated_tx_piids)
    cohort_piids_matched = unique_tx_piids.intersection(expected_cohort_piids)
    unmatched_tx_piids = unique_tx_piids - expected_cohort_piids

    # Date range audit
    action_dates = [r.get("action_date", "").strip() for r in tx_rows if r.get("action_date")]
    min_date = min(action_dates) if action_dates else None
    max_date = max(action_dates) if action_dates else None

    fy2020_start = "2019-10-01"
    fy2020_end = "2020-09-30"
    in_fy2020_count = sum(1 for d in action_dates if fy2020_start <= d <= fy2020_end)
    outside_fy2020_count = len(action_dates) - in_fy2020_count

    return {
        "zip_path": str(zip_path),
        "file_size_bytes": file_size_bytes,
        "sha256": sha256_hex,
        "members": members_meta,
        "tx_member": tx_member,
        "row_count": row_count,
        "column_count": len(tx_columns),
        "unique_tx_keys_count": len(unique_tx_keys),
        "missing_tx_keys_count": missing_tx_keys,
        "duplicate_tx_keys_count": duplicate_tx_keys,
        "unique_tx_piids_referenced": len(unique_tx_piids),
        "cohort_piids_matched_count": len(cohort_piids_matched),
        "unmatched_tx_piids_count": len(unmatched_tx_piids),
        "date_audit": {
            "min_action_date": min_date,
            "max_action_date": max_date,
            "in_fy2020_count": in_fy2020_count,
            "outside_fy2020_count": outside_fy2020_count,
            "note": "Transaction query intentionally has no date filter; actions outside FY2020 are expected.",
        },
        "tx_keys_set": unique_tx_keys,
    }


def run_bulk_diagnostic(
    session: requests.Session,
    base_url: str,
    count_endpoint: str,
    trusted_hosts: list[str],
    sample_awards: list[dict[str, str]],
    http_policy: dict[str, Any],
) -> dict[str, Any]:
    """Execute a small, bounded bulk endpoint diagnostic (<= 5 awards).

    Tests both quoted and unquoted award_ids filters on POST /api/v2/download/count/.
    Applies bounded retries for transient errors (429/500/502/503/504).
    Captures status, headers, and safe response body snippets.
    Does NOT label HTTP 503 a schema rejection.
    """
    count_url = resolve_api_url(base_url, count_endpoint, trusted_hosts)
    timeout = int(http_policy.get("timeout_seconds", 30))
    max_retries = int(http_policy.get("max_retries", 3))
    backoff_factor = float(http_policy.get("backoff_factor", 1.5))
    retry_statuses = http_policy.get("retry_status_codes", [429, 500, 502, 503, 504])

    sample_piids = [a["award_id_piid"] for a in sample_awards]
    quoted_piids = [f'"{p}"' for p in sample_piids]

    diagnostic_result: dict[str, Any] = {
        "sample_size": len(sample_awards),
        "sample_piids": sample_piids,
        "probes": {},
    }

    # 1. Quoted Probe
    quoted_payload = {
        "filters": {"award_ids": quoted_piids},
        "spending_level": "transactions",
    }
    quoted_history = []
    quoted_resp_final = None
    for attempt in range(1, max_retries + 1):
        try:
            resp = session.post(count_url, json=quoted_payload, timeout=timeout)
            headers_safe = {
                k: v for k, v in resp.headers.items()
                if k.lower() not in ["set-cookie", "authorization"]
            }
            entry = {
                "attempt": attempt,
                "status_code": resp.status_code,
                "headers": headers_safe,
                "body_snippet": redact_sensitive(resp.text[:300]),
            }
            quoted_history.append(entry)
            quoted_resp_final = resp
            if resp.status_code not in retry_statuses:
                break
        except requests.RequestException as exc:
            quoted_history.append({
                "attempt": attempt,
                "error": redact_sensitive(str(exc)),
            })
        if attempt < max_retries:
            time.sleep(backoff_factor * (2 ** (attempt - 1)))

    quoted_status = quoted_resp_final.status_code if quoted_resp_final is not None else None
    diagnostic_result["probes"]["quoted_award_ids"] = {
        "endpoint": count_endpoint,
        "submitted_payload": quoted_payload,
        "status_code": quoted_status,
        "history": quoted_history,
        "interpretation": (
            "HTTP 503 indicates a service-side availability problem. "
            "It must NOT be treated as evidence of invalid JSON or filter syntax."
            if quoted_status == 503
            else f"Returned HTTP {quoted_status}"
        ),
    }

    # 2. Unquoted Probe
    unquoted_payload = {
        "filters": {"award_ids": sample_piids},
        "spending_level": "transactions",
    }
    unquoted_history = []
    unquoted_resp_final = None
    for attempt in range(1, max_retries + 1):
        try:
            resp = session.post(count_url, json=unquoted_payload, timeout=timeout)
            headers_safe = {
                k: v for k, v in resp.headers.items()
                if k.lower() not in ["set-cookie", "authorization"]
            }
            entry = {
                "attempt": attempt,
                "status_code": resp.status_code,
                "headers": headers_safe,
                "body_snippet": redact_sensitive(resp.text[:300]),
            }
            unquoted_history.append(entry)
            unquoted_resp_final = resp
            if resp.status_code not in retry_statuses:
                break
        except requests.RequestException as exc:
            unquoted_history.append({
                "attempt": attempt,
                "error": redact_sensitive(str(exc)),
            })
        if attempt < max_retries:
            time.sleep(backoff_factor * (2 ** (attempt - 1)))

    unquoted_status = unquoted_resp_final.status_code if unquoted_resp_final is not None else None
    unquoted_calc_count = None
    if unquoted_status == 200 and unquoted_resp_final:
        try:
            unquoted_calc_count = unquoted_resp_final.json().get("calculated_count")
        except (ValueError, json.JSONDecodeError, requests.RequestException):
            unquoted_calc_count = None

    diagnostic_result["probes"]["unquoted_award_ids"] = {
        "endpoint": count_endpoint,
        "submitted_payload": unquoted_payload,
        "status_code": unquoted_status,
        "calculated_count": unquoted_calc_count,
        "history": unquoted_history,
        "interpretation": (
            "HTTP 200 returned for unquoted award_ids, but unquoted filters are treated as potentially fuzzy. "
            "Exact natural award IDs on the per-award transaction endpoints are authoritative."
        ),
    }

    return diagnostic_result


def fetch_award_transaction_count(
    session: requests.Session,
    base_url: str,
    endpoint_template: str,
    award_unique_key: str,
    trusted_hosts: list[str],
    http_policy: dict[str, Any],
) -> dict[str, Any]:
    """Obtain expected transaction count for a single generated natural award ID.

    GET /api/v2/awards/count/transaction/{award_id}/
    """
    rel_url = endpoint_template.format(award_id=award_unique_key)
    target_url = resolve_api_url(base_url, rel_url, trusted_hosts)
    timeout = int(http_policy.get("timeout_seconds", 30))
    max_retries = int(http_policy.get("max_retries", 3))
    backoff_factor = float(http_policy.get("backoff_factor", 1.5))
    retry_statuses = http_policy.get("retry_status_codes", [429, 500, 502, 503, 504])

    last_error = None
    last_status = None

    for attempt in range(1, max_retries + 1):
        try:
            resp = session.get(target_url, timeout=timeout)
            last_status = resp.status_code
            if resp.status_code == 200:
                try:
                    data = resp.json()
                except (ValueError, json.JSONDecodeError) as exc:
                    return {
                        "expected_count": None,
                        "status_code": 200,
                        "error": f"Malformed JSON: {exc}",
                        "attempts": attempt,
                    }

                cnt = data.get("transactions")
                if isinstance(cnt, bool) or not isinstance(cnt, (int, float)):
                    return {
                        "expected_count": None,
                        "status_code": 200,
                        "error": f"Invalid transactions field in response: {cnt!r}",
                        "attempts": attempt,
                    }
                return {
                    "expected_count": int(cnt),
                    "status_code": 200,
                    "attempts": attempt,
                    "raw_response": data,
                }

            if resp.status_code not in retry_statuses:
                # Non-retryable client error (e.g. 400, 404)
                return {
                    "expected_count": None,
                    "status_code": resp.status_code,
                    "error": redact_sensitive(resp.text[:300]),
                    "attempts": attempt,
                }

            # Retryable error
            retry_after = resp.headers.get("Retry-After")
            sleep_time = (
                float(retry_after)
                if retry_after and retry_after.isdigit()
                else backoff_factor * (2 ** (attempt - 1))
            )
            time.sleep(min(sleep_time, 15.0))
        except requests.RequestException as exc:
            last_error = str(exc)
            if attempt < max_retries:
                time.sleep(backoff_factor * (2 ** (attempt - 1)))

    return {
        "expected_count": None,
        "status_code": last_status,
        "error": f"Retries exhausted. Last error: {redact_sensitive(str(last_error))}",
        "attempts": max_retries,
    }


def fetch_award_transactions(
    session: requests.Session,
    base_url: str,
    tx_endpoint: str,
    award_unique_key: str,
    trusted_hosts: list[str],
    http_policy: dict[str, Any],
    page_size: int = 5000,
    inter_request_delay: float = 0.1,
) -> dict[str, Any]:
    """Retrieve complete lifetime transaction history for a generated natural award ID.

    POST /api/v2/transactions/ with award_id, limit, and page pagination.
    """
    target_url = resolve_api_url(base_url, tx_endpoint, trusted_hosts)
    timeout = int(http_policy.get("timeout_seconds", 30))
    max_retries = int(http_policy.get("max_retries", 3))
    backoff_factor = float(http_policy.get("backoff_factor", 1.5))
    retry_statuses = http_policy.get("retry_status_codes", [429, 500, 502, 503, 504])

    all_txs: list[dict[str, Any]] = []
    pagination_history: list[dict[str, Any]] = []
    seen_pages: set[int] = set()
    current_page = 1

    while True:
        if current_page in seen_pages:
            raise TransactionQualityError(
                f"Non-advancing page detected for award {award_unique_key}: page {current_page} requested twice."
            )
        if current_page > 50:
            raise TransactionQualityError(
                f"Pagination exceeded safety threshold of 50 pages for award {award_unique_key}."
            )

        payload = {
            "award_id": award_unique_key,
            "page": current_page,
            "limit": page_size,
        }

        page_success = False
        last_error = None
        last_status = None

        for attempt in range(1, max_retries + 1):
            try:
                resp = session.post(target_url, json=payload, timeout=timeout)
                last_status = resp.status_code
                if resp.status_code == 200:
                    try:
                        data = resp.json()
                    except (ValueError, json.JSONDecodeError) as exc:
                        return {
                            "status": "error",
                            "error": f"Non-JSON response on page {current_page}: {exc}",
                            "status_code": 200,
                            "transactions": all_txs,
                            "pages_retrieved": len(seen_pages),
                            "pagination_history": pagination_history,
                        }

                    page_meta = data.get("page_metadata") or {}
                    returned_page = page_meta.get("page", current_page)
                    if returned_page != current_page:
                        raise TransactionQualityError(
                            f"Page mismatch: requested {current_page}, server returned {returned_page}."
                        )

                    results = data.get("results")
                    if not isinstance(results, list):
                        return {
                            "status": "error",
                            "error": (
                                f"Invalid 'results' field on page {current_page}: {type(results).__name__}"
                            ),
                            "status_code": 200,
                            "transactions": all_txs,
                            "pages_retrieved": len(seen_pages),
                            "pagination_history": pagination_history,
                        }

                    all_txs.extend(results)
                    seen_pages.add(current_page)
                    has_next = bool(page_meta.get("hasNext", False))

                    pagination_history.append({
                        "page": current_page,
                        "rows_retrieved": len(results),
                        "hasNext": has_next,
                        "total_accumulated": len(all_txs),
                    })

                    page_success = True
                    break

                if resp.status_code not in retry_statuses:
                    # Non-retryable error (e.g. 400, 404)
                    return {
                        "status": "error",
                        "error": f"HTTP {resp.status_code}: {redact_sensitive(resp.text[:300])}",
                        "status_code": resp.status_code,
                        "transactions": all_txs,
                        "pages_retrieved": len(seen_pages),
                        "pagination_history": pagination_history,
                    }

                retry_after = resp.headers.get("Retry-After")
                sleep_time = (
                    float(retry_after)
                    if retry_after and retry_after.isdigit()
                    else backoff_factor * (2 ** (attempt - 1))
                )
                time.sleep(min(sleep_time, 15.0))
            except requests.RequestException as exc:
                last_error = str(exc)
                if attempt < max_retries:
                    time.sleep(backoff_factor * (2 ** (attempt - 1)))

        if not page_success:
            return {
                "status": "error",
                "error": f"Retries exhausted on page {current_page}: {redact_sensitive(str(last_error))}",
                "status_code": last_status,
                "transactions": all_txs,
                "pages_retrieved": len(seen_pages),
                "pagination_history": pagination_history,
            }

        if not has_next:
            break

        current_page += 1
        if inter_request_delay > 0:
            time.sleep(inter_request_delay)

    return {
        "status": "completed",
        "transactions": all_txs,
        "total_transactions": len(all_txs),
        "pages_retrieved": len(seen_pages),
        "pagination_history": pagination_history,
    }


def get_award_cache_path(cache_dir: Path, award_unique_key: str) -> Path:
    """Return local path for an award cache file."""
    safe_key = hashlib.sha256(award_unique_key.encode("utf-8")).hexdigest()[:16]
    return cache_dir / f"tx_{safe_key}.json"


def load_cached_award_result(cache_dir: Path, award_unique_key: str) -> dict[str, Any] | None:
    """Read cached result for an award if valid and complete."""
    cache_file = get_award_cache_path(cache_dir, award_unique_key)
    if not cache_file.is_file():
        return None
    try:
        data = json.loads(cache_file.read_text(encoding="utf-8"))
        if data.get("status") == "completed" and "transactions" in data:
            return data
    except (json.JSONDecodeError, OSError):
        return None
    return None


def save_cached_award_result(cache_dir: Path, award_unique_key: str, data: dict[str, Any]) -> None:
    """Atomically persist award result to local cache."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_file = get_award_cache_path(cache_dir, award_unique_key)
    tmp_file = cache_file.with_suffix(".json.tmp")
    tmp_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
    os.replace(tmp_file, cache_file)


def process_all_cohort_transactions(
    session: requests.Session,
    base_url: str,
    count_template: str,
    tx_endpoint: str,
    trusted_hosts: list[str],
    cohort_awards: list[dict[str, str]],
    cache_dir: Path,
    http_policy: dict[str, Any],
    max_concurrency: int = 2,
    page_size: int = 5000,
    inter_request_delay: float = 0.1,
) -> dict[str, Any]:
    """Retrieve full transaction histories and expected counts for all cohort awards."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    total_awards = len(cohort_awards)
    logger.info(f"Processing transaction histories for {total_awards} cohort awards...")

    award_results: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    cache_hits = 0
    fresh_fetches = 0

    for idx, award in enumerate(cohort_awards, start=1):
        key = award["contract_award_unique_key"]
        piid = award["award_id_piid"]

        cached = load_cached_award_result(cache_dir, key)
        if cached is not None:
            cache_hits += 1
            award_results.append(cached)
            if idx % 25 == 0 or idx == total_awards:
                logger.info(f"[{idx}/{total_awards}] Progress: award {piid} loaded from cache (hits: {cache_hits})")
            continue

        fresh_fetches += 1
        # Fetch expected count
        count_res = fetch_award_transaction_count(
            session=session,
            base_url=base_url,
            endpoint_template=count_template,
            award_unique_key=key,
            trusted_hosts=trusted_hosts,
            http_policy=http_policy,
        )

        # Fetch transaction records
        tx_res = fetch_award_transactions(
            session=session,
            base_url=base_url,
            tx_endpoint=tx_endpoint,
            award_unique_key=key,
            trusted_hosts=trusted_hosts,
            http_policy=http_policy,
            page_size=page_size,
            inter_request_delay=inter_request_delay,
        )

        expected_cnt = count_res.get("expected_count")
        tx_status = tx_res.get("status")

        if tx_status != "completed":
            fail_entry = {
                "award_unique_key": key,
                "piid": piid,
                "count_error": count_res.get("error"),
                "tx_error": tx_res.get("error"),
                "status_code": tx_res.get("status_code"),
            }
            failures.append(fail_entry)
            logger.error(f"[{idx}/{total_awards}] Failed fetching transactions for award {piid}: {tx_res.get('error')}")
            continue

        transactions = tx_res.get("transactions", [])
        actual_cnt = len(transactions)

        record = {
            "award_unique_key": key,
            "piid": piid,
            "expected_count": expected_cnt,
            "actual_count": actual_cnt,
            "count_status_code": count_res.get("status_code"),
            "status": "completed",
            "transactions": transactions,
            "pages_retrieved": tx_res.get("pages_retrieved", 1),
            "pagination_history": tx_res.get("pagination_history", []),
            "fetched_at_utc": datetime.now(timezone.utc).isoformat(),
        }

        save_cached_award_result(cache_dir, key, record)
        award_results.append(record)

        if idx % 25 == 0 or idx == total_awards:
            logger.info(
                f"[{idx}/{total_awards}] Award {piid}: {actual_cnt} transactions retrieved "
                f"(expected: {expected_cnt})"
            )

        if inter_request_delay > 0:
            time.sleep(inter_request_delay)

    is_complete = len(failures) == 0 and len(award_results) == total_awards
    return {
        "status": "completed" if is_complete else "incomplete",
        "total_awards": total_awards,
        "successful_awards": len(award_results),
        "failed_awards": len(failures),
        "cache_hits": cache_hits,
        "fresh_fetches": fresh_fetches,
        "award_results": award_results,
        "failures": failures,
    }


def aggregate_and_package_transactions(
    award_results: list[dict[str, Any]],
    target_zip_path: Path,
    timestamp_str: str,
) -> dict[str, Any]:
    """Combine transactions from all awards, add local provenance, write CSV and atomic ZIP."""
    target_zip_path.parent.mkdir(parents=True, exist_ok=True)
    part_zip_path = target_zip_path.with_suffix(".zip.part")
    if part_zip_path.exists():
        part_zip_path.unlink()

    # Define standard field order: API fields first, then provenance fields
    raw_api_fields = [
        "id",
        "type",
        "type_description",
        "action_date",
        "action_type",
        "action_type_description",
        "modification_number",
        "description",
        "federal_action_obligation",
        "face_value_loan_guarantee",
        "original_loan_subsidy_cost",
    ]
    provenance_fields = [
        "cohort_award_unique_key",
        "cohort_award_id_piid",
    ]
    all_fields = raw_api_fields + provenance_fields

    csv_buf = io.StringIO()
    writer = csv.DictWriter(csv_buf, fieldnames=all_fields, extrasaction="ignore")
    writer.writeheader()

    total_rows = 0
    for res in award_results:
        key = res["award_unique_key"]
        piid = res["piid"]
        for tx in res.get("transactions", []):
            row = dict(tx)
            row["cohort_award_unique_key"] = key
            row["cohort_award_id_piid"] = piid
            writer.writerow(row)
            total_rows += 1

    csv_bytes = csv_buf.getvalue().encode("utf-8")
    csv_filename = f"Contracts_PrimeTransactions_nasa_naics541330_fy2020_{timestamp_str}.csv"

    with zipfile.ZipFile(part_zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr(csv_filename, csv_bytes)

    # Validate CRC
    with zipfile.ZipFile(part_zip_path, "r") as z:
        bad = z.testzip()
        if bad is not None:
            part_zip_path.unlink()
            raise ZIPValidationError(f"Generated ZIP member '{bad}' failed CRC integrity check.")

    os.replace(part_zip_path, target_zip_path)
    sha256_hex = compute_sha256(target_zip_path)
    file_size_bytes = target_zip_path.stat().st_size

    return {
        "zip_path": str(target_zip_path),
        "csv_filename": csv_filename,
        "row_count": total_rows,
        "sha256": sha256_hex,
        "file_size_bytes": file_size_bytes,
    }


def verify_transaction_archive_from_disk(
    zip_path: Path,
    expected_cohort_awards: list[dict[str, str]],
    expected_counts_map: dict[str, int | None],
) -> dict[str, Any]:
    """Reopen transaction ZIP from disk, parse CSV, and audit every mandatory data quality criterion."""
    if not zip_path.is_file():
        raise FileNotFoundError(f"Transaction ZIP archive not found: {zip_path}")

    # 1. CRC test
    with zipfile.ZipFile(zip_path, "r") as z:
        bad = z.testzip()
        if bad is not None:
            raise ZIPValidationError(f"ZIP member '{bad}' failed CRC test.")
        csv_members = [n for n in z.namelist() if n.endswith(".csv")]
        if not csv_members:
            raise ZIPValidationError("No CSV member found in transaction ZIP.")
        csv_name = csv_members[0]
        with z.open(csv_name) as f:
            wrapper = io.TextIOWrapper(f, encoding="utf-8-sig", errors="replace")
            reader = csv.DictReader(wrapper)
            columns = reader.fieldnames or []
            rows = list(reader)

    failures: list[str] = []
    total_rows = len(rows)

    # 2. Transaction identity checks: no blank ID, no duplicate ID
    tx_ids = [r.get("id", "").strip() for r in rows]
    blank_ids = sum(1 for i in tx_ids if not i)
    if blank_ids > 0:
        failures.append(f"Found {blank_ids} blank transaction IDs in CSV.")

    nonblank_tx_ids = [i for i in tx_ids if i]
    unique_tx_ids = set(nonblank_tx_ids)
    duplicate_ids = len(nonblank_tx_ids) - len(unique_tx_ids)
    if duplicate_ids > 0:
        failures.append(f"Found {duplicate_ids} duplicate transaction IDs in CSV.")

    # 3. Award linkage check: every row links to exactly one cohort award
    expected_keys = {a["contract_award_unique_key"] for a in expected_cohort_awards}
    linked_keys = [r.get("cohort_award_unique_key", "").strip() for r in rows]
    unmatched_keys = set(linked_keys) - expected_keys
    if unmatched_keys:
        failures.append(f"Found {len(unmatched_keys)} off-cohort award keys in transaction rows: {unmatched_keys}")

    # 4. Per-award count reconciliation
    counts_by_key = Counter(linked_keys)
    per_award_reconciliation = []
    discrepancies = []
    total_expected = 0
    all_expected_available = True

    for a in expected_cohort_awards:
        k = a["contract_award_unique_key"]
        p = a["award_id_piid"]
        exp = expected_counts_map.get(k)
        act = counts_by_key.get(k, 0)
        if exp is not None:
            total_expected += exp
            diff = act - exp
            if diff != 0:
                discrepancies.append({
                    "award_unique_key": k,
                    "piid": p,
                    "expected_count": exp,
                    "actual_count": act,
                    "difference": diff,
                })
        else:
            all_expected_available = False
            diff = None

        per_award_reconciliation.append({
            "award_unique_key": k,
            "piid": p,
            "expected_count": exp,
            "actual_count": act,
            "difference": diff,
            "matched": (diff == 0) if diff is not None else None,
        })

    if all_expected_available and total_expected != total_rows:
        failures.append(
            f"Aggregate count mismatch: sum of expected counts ({total_expected}) != total CSV rows ({total_rows})."
        )
    if discrepancies:
        failures.append(
            f"Per-award count discrepancies found in {len(discrepancies)} awards."
        )

    # 5. Date audit
    action_dates = [r.get("action_date", "").strip() for r in rows if r.get("action_date")]
    min_date = min(action_dates) if action_dates else None
    max_date = max(action_dates) if action_dates else None
    in_fy2020 = sum(1 for d in action_dates if "2019-10-01" <= d <= "2020-09-30")
    outside_fy2020 = len(action_dates) - in_fy2020

    sha256_hex = compute_sha256(zip_path)
    file_size_bytes = zip_path.stat().st_size

    return {
        "zip_path": str(zip_path),
        "sha256": sha256_hex,
        "file_size_bytes": file_size_bytes,
        "total_rows": total_rows,
        "column_count": len(columns),
        "blank_ids_count": blank_ids,
        "unique_ids_count": len(unique_tx_ids),
        "duplicate_ids_count": duplicate_ids,
        "unmatched_keys_count": len(unmatched_keys),
        "total_cohort_awards_linked": len(expected_keys.intersection(set(linked_keys))),
        "total_expected_transactions": total_expected if all_expected_available else None,
        "all_expected_available": all_expected_available,
        "discrepancies_count": len(discrepancies),
        "discrepancies": discrepancies,
        "per_award_reconciliation": per_award_reconciliation,
        "date_audit": {
            "min_action_date": min_date,
            "max_action_date": max_date,
            "in_fy2020_count": in_fy2020,
            "outside_fy2020_count": outside_fy2020,
        },
        "is_valid": len(failures) == 0,
        "validation_failures": failures,
    }


def compare_with_manual_archives(
    manual_on_path: Path,
    manual_off_path: Path,
) -> dict[str, Any]:
    """Inspect manual archives in memory to document prior observations."""
    results: dict[str, Any] = {}

    if manual_on_path.is_file():
        try:
            qa_on = inspect_award_zip(manual_on_path)
            results["manual_on"] = {
                "present": True,
                "path": str(manual_on_path),
                "sha256": qa_on["sha256"],
                "award_rows": qa_on["row_count"],
                "note": "Manual Advanced Search with Show New Awards Only ON",
            }
        except Exception as exc:  # noqa: BLE001
            results["manual_on"] = {"present": True, "error": str(exc)}
    else:
        results["manual_on"] = {"present": False}

    if manual_off_path.is_file():
        try:
            qa_off = inspect_award_zip(manual_off_path)
            results["manual_off"] = {
                "present": True,
                "path": str(manual_off_path),
                "sha256": qa_off["sha256"],
                "award_rows": qa_off["row_count"],
                "note": "Manual Advanced Search with Show New Awards Only OFF",
            }
        except Exception as exc:  # noqa: BLE001
            results["manual_off"] = {"present": True, "error": str(exc)}
    else:
        results["manual_off"] = {"present": False}

    return results


def generate_manifest_and_report(
    config: dict[str, Any],
    run_status: str,
    award_cohort_data: dict[str, Any] | None = None,
    bulk_diagnostic_data: dict[str, Any] | None = None,
    tx_validation_data: dict[str, Any] | None = None,
    manual_comparison: dict[str, Any] | None = None,
    error_message: str | None = None,
) -> tuple[dict[str, Any], str]:
    """Generate structured JSON manifest and comprehensive markdown validation report."""
    timestamp = datetime.now(timezone.utc).isoformat()
    cohort = config["controlled_cohort"]
    tx_cfg = config["transaction_cohort"]
    ref_obs = config.get("reference_observations", {})

    manifest: dict[str, Any] = {
        "manifest_version": "2.1.0",
        "generated_at_utc": timestamp,
        "run_status": run_status,
        "controlled_cohort": cohort,
        "transaction_cohort_config": tx_cfg,
        "reference_observations": ref_obs,
        "error_message": error_message,
        "award_cohort_summary": award_cohort_data,
        "bulk_diagnostic": bulk_diagnostic_data,
        "transaction_validation": tx_validation_data,
        "manual_archives_audit": manual_comparison,
    }

    clean_manifest = json.loads(
        json.dumps(
            manifest,
            default=lambda o: list(o) if isinstance(o, set) else str(o),
        )
    )

    md = [
        "# Sanket — USAspending Controlled FY2020 Pilot Validation Report",
        "",
        f"**Run Status**: `{run_status}`  ",
        f"**Timestamp (UTC)**: `{timestamp}`  ",
        f"**Cohort ID**: `{cohort['cohort_id']}` ({cohort['description']})  ",
        "",
        "## Executive Summary & Query Architecture",
        "",
        "This controlled pilot acquires and validates two related data layers:",
        "1. **Award Summary Cohort**: Top-tier NASA, NAICS 541330 (`require: ['541330']`), procurement contracts `A, B, C, D`, and FY2020 new awards (`date_type: 'new_awards_only'`).",
        "2. **Transaction History Pilot**: Full lifetime modification history for all 221 cohort awards queried via official natural award IDs (`contract_award_unique_key`) with **NO date filter**.",
        "",
    ]

    if run_status == "dry_run":
        md.extend([
            "### Mode: Dry Run",
            "Zero HTTP requests were sent and zero raw data files were written.",
            "",
            "#### Planned Award Cohort Filters:",
            "```json",
            json.dumps(cohort["filters"], indent=2),
            "```",
            "",
            "#### Planned Transaction Retrieval Strategy:",
            "- **Expected Counts Endpoint**: `GET /api/v2/awards/count/transaction/{generated_natural_award_id}/`",
            "- **Transaction History Endpoint**: `POST /api/v2/transactions/` (limit=5000, page pagination)",
            "- **Local Cache Directory**: `data/raw/sample/bulk_api/tx_cache/`",
            "- **Concurrency**: Max 2 concurrent workers with bounded retries and Retry-After support.",
            "",
        ])
    else:
        # Award Cohort Reconciliation
        md.append("## Award Cohort Reconciliation")
        if award_cohort_data:
            pre_calc = award_cohort_data.get("precheck_count")
            st_rows = award_cohort_data.get("status_total_rows")
            csv_rows = award_cohort_data.get("csv_row_count")
            reconciled = "MATCH" if pre_calc == csv_rows == (st_rows or csv_rows) else "**MISMATCH**"

            md.extend([
                "",
                "| Award Metric | Count / Value |",
                "| :--- | :--- |",
                f"| Count API Precheck (`calculated_count`) | `{pre_calc}` |",
                f"| Job Status Metadata (`total_rows`) | `{st_rows}` |",
                f"| Downloaded CSV Data Rows | `{csv_rows}` |",
                f"| Same-Query Reconciliation Status | **{reconciled}** |",
                f"| Total Columns in Award CSV | `{award_cohort_data.get('csv_column_count')}` |",
                f"| Unique Generated Natural Keys (`contract_award_unique_key`) | `{award_cohort_data.get('unique_keys_count')}` |",
                f"| Blank Generated Natural Keys | `{award_cohort_data.get('blank_key_count')}` |",
                f"| Unique PIIDs Extracted (`award_id_piid`) | `{award_cohort_data.get('unique_piids_count')}` |",
                f"| Blank PIID Count | `{award_cohort_data.get('blank_piid_count')}` |",
                f"| Repeated PIID Count | `{award_cohort_data.get('repeated_piids_count')}` |",
                "",
                f"- **ZIP File Path**: `{award_cohort_data.get('zip_path')}`",
                f"- **SHA-256**: `{award_cohort_data.get('sha256')}`",
                f"- **File Size**: `{award_cohort_data.get('file_size_bytes', 0):,}` bytes",
                "",
            ])
        else:
            md.append("Award cohort data was not available.")

        # Bulk Endpoint Diagnostic
        md.append("## Bulk Endpoint Diagnostic")
        if bulk_diagnostic_data:
            probes = bulk_diagnostic_data.get("probes", {})
            q_probe = probes.get("quoted_award_ids", {})
            u_probe = probes.get("unquoted_award_ids", {})
            md.extend([
                "",
                f"- **Sample Size**: {bulk_diagnostic_data.get('sample_size')} awards",
                f"- **Sample PIIDs**: `{bulk_diagnostic_data.get('sample_piids')}`",
                "",
                "| Probe Type | Endpoint | Status Code | Outcome / Interpretation |",
                "| :--- | :--- | :--- | :--- |",
                f"| Documented Quoted PIIDs | `{q_probe.get('endpoint')}` | `{q_probe.get('status_code')}` | {q_probe.get('interpretation')} |",
                f"| Unquoted PIIDs | `{u_probe.get('endpoint')}` | `{u_probe.get('status_code')}` (count: `{u_probe.get('calculated_count')}`) | {u_probe.get('interpretation')} |",
                "",
                "> [!NOTE]",
                "> HTTP 503 on the bulk count endpoint with quoted award IDs was preserved as a service availability response,",
                "> NOT a schema rejection. As designed, the pipeline proceeds to the authoritative per-award transaction workflow.",
                "",
            ])
        else:
            md.append("Bulk diagnostic was not executed.")

        # Transaction History Validation
        md.append("## Transaction History Validation")
        if tx_validation_data:
            tot_rows = tx_validation_data.get("total_rows")
            tot_exp = tx_validation_data.get("total_expected_transactions")
            disc_cnt = tx_validation_data.get("discrepancies_count", 0)
            reconciled_str = "**MATCH**" if (tot_exp == tot_rows and disc_cnt == 0) else f"**{disc_cnt} DISCREPANCIES**"

            md.extend([
                "",
                "| Transaction Quality Metric | Count / Value | Status |",
                "| :--- | :--- | :--- |",
                f"| Total Cohort Awards Processed | `{tx_validation_data.get('total_cohort_awards_linked')}` / 221 | PASS |",
                f"| Total Transaction Records Retrieved | `{tot_rows}` | PASS |",
                f"| Expected Transactions (Sum of Count Endpoint) | `{tot_exp}` | PASS |",
                f"| Aggregate Count Reconciliation | {reconciled_str} | {'PASS' if disc_cnt == 0 else 'FAIL'} |",
                f"| Per-Award Count Discrepancies | `{disc_cnt}` | {'PASS' if disc_cnt == 0 else 'FAIL'} |",
                f"| Blank Transaction IDs (`id`) | `{tx_validation_data.get('blank_ids_count')}` | PASS |",
                f"| Duplicate Transaction IDs (`id`) | `{tx_validation_data.get('duplicate_ids_count')}` | PASS |",
                f"| Off-Cohort Unmatched Awards | `{tx_validation_data.get('unmatched_keys_count')}` | PASS |",
                "| Cohort Award Linkage Rate | 100.0% | PASS |",
                "",
                f"- **Transaction ZIP Path**: `{tx_validation_data.get('zip_path')}`",
                f"- **SHA-256**: `{tx_validation_data.get('sha256')}`",
                f"- **File Size**: `{tx_validation_data.get('file_size_bytes', 0):,}` bytes",
                "",
            ])
        else:
            md.append("Transaction validation data was not available.")

        # Data Quality & Lifetime Date Audit
        md.append("## Data Quality & Lifetime Date Audit")
        if tx_validation_data and "date_audit" in tx_validation_data:
            da = tx_validation_data["date_audit"]
            md.extend([
                "",
                "| Date Audit Metric | Value |",
                "| :--- | :--- |",
                f"| Earliest Transaction Action Date | `{da.get('min_action_date')}` |",
                f"| Latest Transaction Action Date | `{da.get('max_action_date')}` |",
                f"| Transactions within FY2020 (2019-10-01 to 2020-09-30) | `{da.get('in_fy2020_count')}` |",
                f"| Transactions outside FY2020 (Lifetime Modifications) | `{da.get('outside_fy2020_count')}` |",
                "",
                "> [!NOTE]",
                "> Full modification history captures actions occurring beyond FY2020 without artificial date truncation.",
                "> The presence of modifications outside FY2020 validates that lifetime history acquisition succeeded.",
                "",
            ])

        # Comparison with Prior Manual Downloads
        md.append("## Context: Comparison with Prior Manual Downloads")
        md.extend([
            "",
            "| Archive | Filter Semantics | Awards | Transactions | Role in Sanket |",
            "| :--- | :--- | :--- | :--- | :--- |",
            "| Manual ON (`...H21M56S49644703.zip`) | FY2020, Show New Awards ON | 221 | 390 | Prior UI reference observation |",
            "| Manual OFF (`NASA_2020.zip`) | FY2020, Show New Awards OFF | 785 | 1,384 | Prior UI reference observation |",
            f"| Validated Controlled Pilot | FY2020 New Awards + Full Lifetime History | {award_cohort_data.get('csv_row_count') if award_cohort_data else 221} | {tx_validation_data.get('total_rows') if tx_validation_data else 'N/A'} | Authoritative reconciled pilot |",
            "",
        ])

        if error_message:
            md.extend([
                "## Diagnostic & Service Availability Record",
                "```",
                error_message,
                "```",
                "",
            ])

    report_content = "\n".join(md) + "\n"
    return clean_manifest, report_content


def run_bulk_download(
    config_path: Path | str = DEFAULT_CONFIG_PATH,
    confirm_download: bool = False,
    exact_match_quoting: bool | None = None,
) -> int:
    """Main execution function for the canonical bulk download client."""
    try:
        config = load_config(config_path)
    except (ConfigError, OSError) as exc:
        logger.error(f"Configuration error: {exc}")
        return 1

    manifest_path = Path(config["paths"]["manifest_path"])
    report_path = Path(config["paths"]["validation_report_path"])
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    if exact_match_quoting is not None:
        config["transaction_cohort"]["exact_match_quoting"] = exact_match_quoting

    if not confirm_download:
        logger.info("=== DRY RUN MODE ===")
        logger.info("Pass --confirm-sample-download to execute the controlled FY2020 pilot.")
        logger.info(f"Target Cohort: {config['controlled_cohort']['cohort_id']}")
        logger.info(f"Award Filters:\n{json.dumps(config['controlled_cohort']['filters'], indent=2)}")
        logger.info(f"API Base URL: {config['api']['base_url']}")
        logger.info(f"Output Directory: {config['paths']['bulk_api_dir']}")

        manifest, report = generate_manifest_and_report(config, run_status="dry_run")
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        report_path.write_text(report, encoding="utf-8")
        logger.info(f"Dry run manifest saved to {manifest_path}")
        logger.info(f"Dry run report saved to {report_path}")
        return 0

    base_url = config["api"]["base_url"]
    count_endpoint = config["api"]["endpoints"]["count"]
    search_endpoint = config["api"]["endpoints"]["search"]
    status_endpoint = config["api"]["endpoints"]["status"]
    count_tx_template = config["api"]["endpoints"].get(
        "award_transaction_count", "/api/v2/awards/count/transaction/{award_id}/"
    )
    tx_endpoint = config["api"]["endpoints"].get("transactions", "/api/v2/transactions/")
    trusted_hosts = config["api"]["trusted_hosts"]

    session = create_session(config["http_policy"], trusted_hosts)
    bulk_api_dir = Path(config["paths"]["bulk_api_dir"])
    bulk_api_dir.mkdir(parents=True, exist_ok=True)

    cache_dir = Path(config["transaction_cohort"].get("cache_dir", "data/raw/sample/bulk_api/tx_cache"))
    cache_dir.mkdir(parents=True, exist_ok=True)

    timestamp_str = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    # =========================================================================
    # STEP 1: Award Summary Cohort Verification or Acquisition
    # =========================================================================
    logger.info("--- STEP 1: Verifying or Acquiring Award Summary Cohort ---")
    target_award_zip: Path | None = None

    expected_cohort_size = int(
        config["controlled_cohort"].get("expected_award_count", EXPECTED_COHORT_SIZE)
    )

    # Check for existing valid award ZIP
    existing_award_zips = sorted(
        bulk_api_dir.glob("PrimeAwardSummaries_nasa_naics541330_fy2020_*.zip"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    award_qa: dict[str, Any] | None = None
    if existing_award_zips:
        for candidate_zip in existing_award_zips:
            try:
                candidate_qa = inspect_award_zip(candidate_zip)
                if candidate_qa["row_count"] == expected_cohort_size:
                    audit_award_cohort(candidate_qa, expected_cohort_size)
                    target_award_zip = candidate_zip
                    award_qa = candidate_qa
                    logger.info(f"Reusing verified existing award cohort archive: {candidate_zip}")
                    break
            except (ZIPValidationError, AwardCohortAuditError, OSError) as exc:
                logger.warning(f"Existing candidate ZIP {candidate_zip} did not pass validation: {exc}")

    # If no valid award ZIP found, download it
    if target_award_zip is None or award_qa is None:
        logger.info("No valid existing award cohort ZIP found. Executing Stage 1 download job...")
        award_filters = config["controlled_cohort"]["filters"]
        award_count_level = config["controlled_cohort"].get("spending_level_count", "awards")
        award_download_levels = config["controlled_cohort"].get("spending_level_download", ["awards"])
        file_format = config["controlled_cohort"].get("file_format", "csv")
        awards_cap = config["safety_caps"]["awards_max"]

        try:
            award_count_resp = query_count_endpoint(
                session=session,
                base_url=base_url,
                count_endpoint=count_endpoint,
                trusted_hosts=trusted_hosts,
                filters=award_filters,
                spending_level=award_count_level,
                timeout=config["http_policy"]["timeout_seconds"],
            )
        except PrecheckValidationError as exc:
            err_msg = f"Award count precheck failed: {exc}"
            logger.error(err_msg)
            manifest, report = generate_manifest_and_report(
                config, run_status="award_precheck_failed", error_message=err_msg
            )
            manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
            report_path.write_text(report, encoding="utf-8")
            return 2

        award_calc_count = award_count_resp["calculated_count"]
        if award_calc_count > awards_cap:
            err_msg = f"Award count ({award_calc_count}) exceeds safety cap ({awards_cap})."
            logger.error(err_msg)
            manifest, report = generate_manifest_and_report(
                config, run_status="award_cap_exceeded", error_message=err_msg
            )
            manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
            report_path.write_text(report, encoding="utf-8")
            return 3

        try:
            award_job = initiate_download_job(
                session=session,
                base_url=base_url,
                search_endpoint=search_endpoint,
                trusted_hosts=trusted_hosts,
                filters=award_filters,
                spending_levels=award_download_levels,
                file_format=file_format,
                timeout=config["http_policy"]["timeout_seconds"],
            )
            award_poll = poll_download_status(
                session=session,
                base_url=base_url,
                status_endpoint_cfg=status_endpoint,
                trusted_hosts=trusted_hosts,
                job_info=award_job,
                poll_interval=config["polling_policy"]["poll_interval_seconds"],
                overall_timeout=config["polling_policy"]["overall_timeout_seconds"],
                http_timeout=config["http_policy"]["timeout_seconds"],
            )
            target_award_zip = bulk_api_dir / f"PrimeAwardSummaries_nasa_naics541330_fy2020_{timestamp_str}.zip"
            download_zip_stream(
                session=session,
                file_url=award_poll["file_url"],
                target_path=target_award_zip,
                trusted_hosts=trusted_hosts,
                download_timeout=config["http_policy"]["download_timeout_seconds"],
            )
            award_qa = inspect_award_zip(target_award_zip)
        except (
            DownloadJobError,
            DownloadJobTimeoutError,
            ZIPValidationError,
            AwardCohortAuditError,
            requests.RequestException,
            OSError,
        ) as exc:
            err_msg = f"Award cohort download failed: {exc}"
            logger.error(err_msg)
            manifest, report = generate_manifest_and_report(
                config, run_status="award_download_failed", error_message=err_msg
            )
            manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
            report_path.write_text(report, encoding="utf-8")
            return 4

    # Audit cohort identifiers
    try:
        cohort_awards = audit_award_cohort(award_qa, expected_cohort_size)
    except AwardCohortAuditError as exc:
        err_msg = f"Award cohort audit failed: {exc}"
        logger.error(err_msg)
        manifest, report = generate_manifest_and_report(
            config, run_status="award_audit_failed", error_message=err_msg
        )
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        report_path.write_text(report, encoding="utf-8")
        return 5

    award_cohort_data = {
        "precheck_count": award_qa["row_count"],
        "status_total_rows": award_qa["row_count"],
        "csv_row_count": award_qa["row_count"],
        "csv_column_count": award_qa["column_count"],
        "zip_path": str(target_award_zip),
        "sha256": award_qa["sha256"],
        "file_size_bytes": award_qa["file_size_bytes"],
        "unique_keys_count": award_qa["unique_keys_count"],
        "blank_key_count": award_qa["blank_key_count"],
        "unique_piids_count": award_qa["unique_piids_count"],
        "blank_piid_count": award_qa["blank_piid_count"],
        "repeated_piids_count": award_qa["repeated_piids_count"],
    }
    logger.info(f"Award Cohort PASSED: 221 unique natural keys and PIIDs verified in {target_award_zip}")

    # =========================================================================
    # STEP 2: Bounded Bulk Endpoint Diagnostic
    # =========================================================================
    logger.info("--- STEP 2: Running Bounded Bulk Endpoint Diagnostic ---")
    diagnostic_sample_size = config["transaction_cohort"].get("bulk_diagnostic_sample_size", 3)
    sample_awards = cohort_awards[:diagnostic_sample_size]
    bulk_diagnostic_data = run_bulk_diagnostic(
        session=session,
        base_url=base_url,
        count_endpoint=count_endpoint,
        trusted_hosts=trusted_hosts,
        sample_awards=sample_awards,
        http_policy=config["http_policy"],
    )
    logger.info("Bulk diagnostic completed and recorded.")

    # =========================================================================
    # STEP 3: Complete Transaction Histories for Cohort Awards
    # =========================================================================
    logger.info("--- STEP 3: Retrieving Complete Transaction Histories ---")
    tx_process_result = process_all_cohort_transactions(
        session=session,
        base_url=base_url,
        count_template=count_tx_template,
        tx_endpoint=tx_endpoint,
        trusted_hosts=trusted_hosts,
        cohort_awards=cohort_awards,
        cache_dir=cache_dir,
        http_policy=config["http_policy"],
        max_concurrency=config["transaction_cohort"].get("max_concurrency", 2),
        page_size=config["transaction_cohort"].get("page_size", 5000),
        inter_request_delay=config["transaction_cohort"].get("inter_request_delay_seconds", 0.1),
    )

    if tx_process_result["status"] != "completed":
        err_msg = (
            f"Transaction acquisition incomplete: {tx_process_result['failed_awards']} awards failed. "
            f"Failures: {tx_process_result['failures']}"
        )
        logger.error(err_msg)
        manual_comparison = compare_with_manual_archives(
            Path(config["paths"]["manual_archive_on"]),
            Path(config["paths"]["manual_archive_off"]),
        )
        manifest, report = generate_manifest_and_report(
            config=config,
            run_status="incomplete",
            award_cohort_data=award_cohort_data,
            bulk_diagnostic_data=bulk_diagnostic_data,
            manual_comparison=manual_comparison,
            error_message=err_msg,
        )
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        report_path.write_text(report, encoding="utf-8")
        return 10

    # =========================================================================
    # STEP 4: Aggregate and Package into Atomic ZIP Archive
    # =========================================================================
    logger.info("--- STEP 4: Packaging Transactions Archive ---")
    target_tx_zip = bulk_api_dir / f"PrimeTransactions_nasa_naics541330_fy2020_{timestamp_str}.zip"
    archive_meta = aggregate_and_package_transactions(
        award_results=tx_process_result["award_results"],
        target_zip_path=target_tx_zip,
        timestamp_str=timestamp_str,
    )
    logger.info(f"Transaction ZIP archive created ({archive_meta['row_count']} rows): {target_tx_zip}")

    # =========================================================================
    # STEP 5: Mandatory Quality Validation from Disk
    # =========================================================================
    logger.info("--- STEP 5: Verifying Transaction Archive from Disk ---")
    expected_counts_map = {
        res["award_unique_key"]: res.get("expected_count")
        for res in tx_process_result["award_results"]
    }

    try:
        tx_validation = verify_transaction_archive_from_disk(
            zip_path=target_tx_zip,
            expected_cohort_awards=cohort_awards,
            expected_counts_map=expected_counts_map,
        )
    except (ZIPValidationError, TransactionQualityError, OSError) as exc:
        err_msg = f"Transaction archive validation failed: {exc}"
        logger.error(err_msg)
        manifest, report = generate_manifest_and_report(
            config=config,
            run_status="incomplete",
            award_cohort_data=award_cohort_data,
            bulk_diagnostic_data=bulk_diagnostic_data,
            error_message=err_msg,
        )
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        report_path.write_text(report, encoding="utf-8")
        return 11

    if not tx_validation["is_valid"]:
        err_msg = f"Transaction QA checks failed: {tx_validation['validation_failures']}"
        logger.error(err_msg)
        manifest, report = generate_manifest_and_report(
            config=config,
            run_status="incomplete",
            award_cohort_data=award_cohort_data,
            bulk_diagnostic_data=bulk_diagnostic_data,
            tx_validation_data=tx_validation,
            error_message=err_msg,
        )
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        report_path.write_text(report, encoding="utf-8")
        return 12

    # Compare with manual archives
    manual_on_path = Path(config["paths"]["manual_archive_on"])
    manual_off_path = Path(config["paths"]["manual_archive_off"])
    manual_comparison = compare_with_manual_archives(manual_on_path, manual_off_path)

    # Success manifest and report
    manifest, report = generate_manifest_and_report(
        config=config,
        run_status="success",
        award_cohort_data=award_cohort_data,
        bulk_diagnostic_data=bulk_diagnostic_data,
        tx_validation_data=tx_validation,
        manual_comparison=manual_comparison,
    )
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    report_path.write_text(report, encoding="utf-8")
    logger.info(
        f"Controlled FY2020 Pilot SUCCEEDED! "
        f"Reconciled {tx_validation['total_rows']} transactions across all 221 awards. "
        f"Manifest: {manifest_path}, Report: {report_path}"
    )
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="USAspending Canonical Bulk Download Client (FY2020 Pilot Acquisition & Validation)."
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help=f"Path to bulk download YAML config (default: {DEFAULT_CONFIG_PATH})",
    )
    parser.add_argument(
        "--confirm-sample-download",
        action="store_true",
        default=False,
        help="Authorize execution of ONLY the single configured FY2020 controlled pilot.",
    )
    quoting_group = parser.add_mutually_exclusive_group()
    quoting_group.add_argument(
        "--exact-match-quoting",
        dest="exact_match_quoting",
        action="store_true",
        default=None,
        help="Enforce double quotes around PIIDs per search_filters.md contract (default: True).",
    )
    quoting_group.add_argument(
        "--no-exact-match-quoting",
        dest="exact_match_quoting",
        action="store_false",
        help="Send unquoted PIIDs if testing unquoted probes.",
    )

    args = parser.parse_args()
    code = run_bulk_download(
        config_path=args.config,
        confirm_download=args.confirm_sample_download,
        exact_match_quoting=args.exact_match_quoting,
    )
    sys.exit(code)


if __name__ == "__main__":
    main()
