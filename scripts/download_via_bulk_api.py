#!/usr/bin/env python3
"""Canonical bulk download client for USAspending bulk download API.

Project: Sanket — Federal Contract Recompete Intelligence
Controlled Pilot:
  Stage 1: FY2020 New Awards Cohort (NASA + NAICS 541330 + base transaction date in FY2020)
  Stage 2: Transaction History Retrieval for Cohort Award IDs (No transaction date filter)

This client implements the official USAspending asynchronous bulk download API:
- POST /api/v2/download/count/ (count precheck with singular spending_level string)
- POST /api/v2/download/search/ (job initiation with array spending_level)
- GET  /api/v2/download/status/ (job polling with relative URL / file_name resolution)
- Safe HTTPS streaming to .part file, ZIP CRC validation, and atomic rename.
- In-memory CSV quality audit without disk extraction.
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
            elif ("primeawardsummaries" in lower or "contracts_primeawardsummaries" in lower) and info.filename.endswith(".csv"):
                award_member = info.filename

        if subaward_members:
            raise ZIPValidationError(f"Forbidden subaward members found in award ZIP: {subaward_members}")

        if not award_member:
            for info in z.infolist():
                if info.filename.endswith(".csv"):
                    with z.open(info.filename) as f:
                        wrapper = io.TextIOWrapper(f, encoding="utf-8-sig", errors="replace")
                        header = next(csv.reader(wrapper), [])
                        if "contract_award_unique_key" in set(header) and "contract_transaction_unique_key" not in set(header):
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

    for r in award_rows:
        piid = r.get("award_id_piid", "").strip()
        if piid:
            piids.append(piid)
            piid_counts[piid] = piid_counts.get(piid, 0) + 1
        else:
            blank_piid_count += 1

    unique_piids = sorted(set(piids))
    repeated_piids = {k: v for k, v in piid_counts.items() if v > 1}

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
    }


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
            elif ("primetransactions" in lower or "contracts_primetransactions" in lower) and info.filename.endswith(".csv"):
                tx_member = info.filename

        if subaward_members:
            raise ZIPValidationError(f"Forbidden subaward members found in transaction ZIP: {subaward_members}")

        if not tx_member:
            for info in z.infolist():
                if info.filename.endswith(".csv"):
                    with z.open(info.filename) as f:
                        wrapper = io.TextIOWrapper(f, encoding="utf-8-sig", errors="replace")
                        header = next(csv.reader(wrapper), [])
                        if "contract_transaction_unique_key" in set(header):
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
    tx_keys = [r.get("contract_transaction_unique_key", "").strip() for r in tx_rows]
    populated_tx_keys = [k for k in tx_keys if k]
    unique_tx_keys = set(populated_tx_keys)
    missing_tx_keys = row_count - len(populated_tx_keys)
    duplicate_tx_keys = len(populated_tx_keys) - len(unique_tx_keys)

    # Linkage to cohort PIIDs
    tx_piids = [r.get("award_id_piid", "").strip() for r in tx_rows]
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
    award_stage_data: dict[str, Any] | None = None,
    tx_stage_data: dict[str, Any] | None = None,
    manual_comparison: dict[str, Any] | None = None,
    error_message: str | None = None,
) -> tuple[dict[str, Any], str]:
    """Generate structured JSON manifest and comprehensive markdown validation report."""
    timestamp = datetime.now(timezone.utc).isoformat()
    cohort = config["controlled_cohort"]
    tx_cfg = config["transaction_cohort"]
    ref_obs = config.get("reference_observations", {})

    manifest: dict[str, Any] = {
        "manifest_version": "2.0.0",
        "generated_at_utc": timestamp,
        "run_status": run_status,
        "controlled_cohort": cohort,
        "transaction_cohort_config": tx_cfg,
        "reference_observations": ref_obs,
        "error_message": error_message,
        "stage_1_award_cohort": award_stage_data,
        "stage_2_transaction_history": tx_stage_data,
        "manual_archives_audit": manual_comparison,
    }

    # Clean keys_set if present in QA dicts to keep manifest lightweight
    clean_manifest = json.loads(
        json.dumps(
            manifest,
            default=lambda o: list(o) if isinstance(o, set) else str(o),
        )
    )

    # Build markdown report
    md = [
        "# Sanket — USAspending Controlled FY2020 Pilot Validation Report",
        "",
        f"**Run Status**: `{run_status}`  ",
        f"**Timestamp (UTC)**: `{timestamp}`  ",
        f"**Cohort ID**: `{cohort['cohort_id']}` ({cohort['description']})  ",
        "",
        "## 1. Executive Summary & Query Architecture",
        "",
        "This controlled pilot implements a two-stage asynchronous bulk download architecture:",
        "1. **Stage 1 (Award Cohort)**: NASA + NAICS 541330 (`require: ['541330']`) + FY2020 new awards (`date_type: 'new_awards_only'`).",
        "2. **Stage 2 (Transaction History)**: Full modification history queried by cohort `award_ids` with **NO date filter**.",
        "",
    ]

    if run_status == "dry_run":
        md.extend(
            [
                "### Mode: Dry Run",
                "Zero HTTP requests were sent and zero raw data files were written.",
                "",
                "#### Planned Stage 1 (Awards) Filters:",
                "```json",
                json.dumps(cohort["filters"], indent=2),
                "```",
                "",
                "#### Planned Stage 2 (Transactions) Query Strategy:",
                f"- **Batch Size**: {tx_cfg.get('batch_size', 100)} PIIDs per job",
                f"- **Exact Match Quoting**: `{tx_cfg.get('exact_match_quoting', True)}`",
                "- **Spending Level**: `transactions` (count: string, download: array)",
                "- **Date Filter**: None (deliberately omitted to fetch complete lifetime actions)",
                "",
            ]
        )
    else:
        # Live run report
        md.append("## 2. Stage 1: Award Cohort Reconciliation")
        if award_stage_data:
            pre_calc = award_stage_data.get("precheck_count")
            st_rows = award_stage_data.get("status_total_rows")
            csv_rows = award_stage_data.get("csv_row_count")
            reconciled = "MATCH" if pre_calc == csv_rows == (st_rows or csv_rows) else "**MISMATCH**"

            md.extend(
                [
                    "",
                    "| Stage 1 Metric | Count / Value |",
                    "| :--- | :--- |",
                    f"| Count API Precheck (`calculated_count`) | `{pre_calc}` |",
                    f"| Job Status Metadata (`total_rows`) | `{st_rows}` |",
                    f"| Downloaded CSV Data Rows | `{csv_rows}` |",
                    f"| Same-Query Reconciliation Status | **{reconciled}** |",
                    f"| Total Columns in Award CSV | `{award_stage_data.get('csv_column_count')}` |",
                    f"| Unique PIIDs Extracted | `{award_stage_data.get('unique_piids_count')}` |",
                    f"| Blank PIID Count | `{award_stage_data.get('blank_piid_count')}` |",
                    f"| Repeated PIID Count | `{award_stage_data.get('repeated_piids_count')}` |",
                    "",
                    f"- **ZIP File Path**: `{award_stage_data.get('zip_path')}`",
                    f"- **SHA-256**: `{award_stage_data.get('sha256')}`",
                    f"- **File Size**: `{award_stage_data.get('file_size_bytes'):,}` bytes",
                    "",
                ]
            )
        else:
            md.append("Stage 1 did not execute or failed before completion.")

        md.append("## 3. Stage 2: Transaction History Retrieval")
        if tx_stage_data:
            tx_status = tx_stage_data.get("status")
            md.extend(
                [
                    "",
                    f"**Transaction Stage Status**: `{tx_status}`  ",
                    f"**Batches Planned**: `{tx_stage_data.get('total_batches')}`  ",
                    f"**Exact Match Quoting Used**: `{tx_stage_data.get('exact_match_quoting')}`  ",
                    "",
                ]
            )
            if tx_status == "rejected_by_server":
                md.extend(
                    [
                        "### Server Rejection of Documented Form",
                        f"**Endpoint**: `{tx_stage_data.get('rejected_endpoint')}`  ",
                        f"**HTTP Status**: `{tx_stage_data.get('http_status')}`  ",
                        f"**Reason / Message**: `{tx_stage_data.get('error_message')}`  ",
                        "",
                        "> [!IMPORTANT]",
                        "> Per specification: 'If the endpoint rejects the documented form, preserve the server response",
                        "> and stop rather than trying arbitrary payload variants.' The client recorded the server rejection",
                        "> and halted honestly without silently inventing workarounds.",
                        "",
                        "#### Rejected Request Sample Payload:",
                        "```json",
                        json.dumps(tx_stage_data.get("sample_rejected_payload", {}), indent=2),
                        "```",
                        "",
                    ]
                )
            elif tx_status == "completed":
                md.extend(
                    [
                        "### Transaction Batch Execution Summary",
                        f"- Total Transaction Batches Downloaded: `{len(tx_stage_data.get('batches', []))}`",
                        f"- Total Transaction Rows: `{tx_stage_data.get('total_tx_rows')}`",
                        f"- Date Range: `{tx_stage_data.get('min_action_date')}` to `{tx_stage_data.get('max_action_date')}`",
                        f"- Transactions Outside FY2020: `{tx_stage_data.get('outside_fy2020_count')}`",
                        "",
                    ]
                )
        else:
            md.append("Stage 2 was not initiated.")

        if error_message:
            md.extend(
                [
                    "## 4. Error / Halt Diagnostics",
                    "```",
                    error_message,
                    "```",
                    "",
                ]
            )

        md.append("## 5. Context: Comparison with Prior Manual Downloads")
        md.extend(
            [
                "",
                "| Archive | Filter Semantics | Awards | Transactions | Role in Sanket |",
                "| :--- | :--- | :--- | :--- | :--- |",
                "| Manual ON (`...H21M56S49644703.zip`) | FY2020, Show New Awards ON | 221 | 390 | Prior reference observation |",
                "| Manual OFF (`NASA_2020.zip`) | FY2020, Show New Awards OFF | 785 | 1,384 | Prior reference observation |",
                f"| Current Pilot Stage 1 | FY2020, `new_awards_only` | {award_stage_data.get('csv_row_count') if award_stage_data else 'N/A'} | N/A (separate) | Official bulk API award cohort |",
                "",
                "> [!NOTE]",
                "> 'Show New Awards Only' ON filters by initial award obligation date (`new_awards_only`), yielding 221 awards.",
                "> 'Show New Awards Only' OFF filters by transaction action dates (`action_date`), yielding 785 awards.",
                "> The transaction export in the combined manual download was date-truncated to FY2020; querying transaction history",
                "> separately without date filters is required to capture full lifetime modifications.",
                "",
            ]
        )

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

    quoting_enabled = config["transaction_cohort"].get("exact_match_quoting", True)

    if not confirm_download:
        logger.info("=== DRY RUN MODE ===")
        logger.info("Pass --confirm-sample-download to execute the controlled FY2020 pilot.")
        logger.info(f"Target Cohort: {config['controlled_cohort']['cohort_id']}")
        logger.info(f"Stage 1 Award Filters:\n{json.dumps(config['controlled_cohort']['filters'], indent=2)}")
        logger.info(f"Stage 2 Quoting Enabled: {quoting_enabled}")
        logger.info(f"Safety Caps: {config['safety_caps']}")
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
    trusted_hosts = config["api"]["trusted_hosts"]

    session = create_session(config["http_policy"], trusted_hosts)
    bulk_api_dir = Path(config["paths"]["bulk_api_dir"])
    bulk_api_dir.mkdir(parents=True, exist_ok=True)

    timestamp_str = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    # =========================================================================
    # STAGE 1: Controlled Award Summary Cohort Acquisition
    # =========================================================================
    logger.info("--- STARTING STAGE 1: Award Summary Cohort ---")
    award_filters = config["controlled_cohort"]["filters"]
    award_count_level = config["controlled_cohort"].get("spending_level_count", "awards")
    award_download_levels = config["controlled_cohort"].get("spending_level_download", ["awards"])
    file_format = config["controlled_cohort"].get("file_format", "csv")
    awards_cap = config["safety_caps"]["awards_max"]

    # 1.1 Count precheck
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
        err_msg = f"Stage 1 award count precheck failed: {exc}"
        logger.error(err_msg)
        manifest, report = generate_manifest_and_report(
            config,
            run_status="award_precheck_failed",
            error_message=err_msg,
        )
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        report_path.write_text(report, encoding="utf-8")
        return 2

    award_calc_count = award_count_resp["calculated_count"]
    logger.info(f"Stage 1 Count Precheck PASSED: calculated_count = {award_calc_count}")

    if award_calc_count > awards_cap:
        err_msg = f"Award count ({award_calc_count}) exceeds safety cap ({awards_cap})."
        logger.error(err_msg)
        manifest, report = generate_manifest_and_report(
            config,
            run_status="award_cap_exceeded",
            error_message=err_msg,
        )
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        report_path.write_text(report, encoding="utf-8")
        return 3

    # 1.2 Submit award download job
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
    except DownloadJobError as exc:
        err_msg = f"Stage 1 award job initiation failed: {exc}"
        logger.error(err_msg)
        manifest, report = generate_manifest_and_report(
            config,
            run_status="award_job_init_failed",
            error_message=err_msg,
        )
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        report_path.write_text(report, encoding="utf-8")
        return 4

    # 1.3 Poll award job status
    try:
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
    except (DownloadJobError, DownloadJobTimeoutError) as exc:
        err_msg = f"Stage 1 award job polling failed: {exc}"
        logger.error(err_msg)
        manifest, report = generate_manifest_and_report(
            config,
            run_status="award_polling_failed",
            error_message=err_msg,
        )
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        report_path.write_text(report, encoding="utf-8")
        return 5

    # 1.4 Download award ZIP
    target_award_zip = bulk_api_dir / f"PrimeAwardSummaries_nasa_naics541330_fy2020_{timestamp_str}.zip"
    try:
        download_zip_stream(
            session=session,
            file_url=award_poll["file_url"],
            target_path=target_award_zip,
            trusted_hosts=trusted_hosts,
            download_timeout=config["http_policy"]["download_timeout_seconds"],
        )
    except (UntrustedHostError, ZIPValidationError, DownloadJobError, FileExistsError) as exc:
        err_msg = f"Stage 1 award ZIP acquisition failed: {exc}"
        logger.error(err_msg)
        manifest, report = generate_manifest_and_report(
            config,
            run_status="award_download_failed",
            error_message=err_msg,
        )
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        report_path.write_text(report, encoding="utf-8")
        return 6

    # 1.5 Inspect award ZIP in memory
    try:
        award_qa = inspect_award_zip(target_award_zip)
    except ZIPValidationError as exc:
        err_msg = f"Stage 1 award ZIP quality inspection failed: {exc}"
        logger.error(err_msg)
        manifest, report = generate_manifest_and_report(
            config,
            run_status="award_qa_failed",
            error_message=err_msg,
        )
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        report_path.write_text(report, encoding="utf-8")
        return 7

    # 1.6 Same-query reconciliation for Stage 1
    status_total_rows = award_poll.get("total_rows")
    csv_row_count = award_qa["row_count"]
    if award_calc_count != csv_row_count:
        err_msg = (
            f"Stage 1 count mismatch on same exact query: Count API returned {award_calc_count}, "
            f"but downloaded CSV contained {csv_row_count} rows."
        )
        logger.error(err_msg)
        manifest, report = generate_manifest_and_report(
            config,
            run_status="award_count_mismatch",
            error_message=err_msg,
        )
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        report_path.write_text(report, encoding="utf-8")
        return 8

    award_stage_data = {
        "precheck_count": award_calc_count,
        "status_total_rows": status_total_rows,
        "csv_row_count": csv_row_count,
        "csv_column_count": award_qa["column_count"],
        "zip_path": str(target_award_zip),
        "sha256": award_qa["sha256"],
        "file_size_bytes": award_qa["file_size_bytes"],
        "unique_piids_count": award_qa["unique_piids_count"],
        "blank_piid_count": award_qa["blank_piid_count"],
        "repeated_piids_count": award_qa["repeated_piids_count"],
        "repeated_piids_audit": award_qa["repeated_piids_audit"],
    }
    logger.info(
        f"Stage 1 Reconciliation PASSED: {csv_row_count} awards (Unique PIIDs: {award_qa['unique_piids_count']})"
    )

    # Compare with manual archives
    manual_on_path = Path(config["paths"]["manual_archive_on"])
    manual_off_path = Path(config["paths"]["manual_archive_off"])
    manual_comparison = compare_with_manual_archives(manual_on_path, manual_off_path)

    # =========================================================================
    # STAGE 2: Transaction History Retrieval for Cohort PIIDs
    # =========================================================================
    logger.info("--- STARTING STAGE 2: Transaction History for Cohort PIIDs ---")
    cohort_piids = award_qa["unique_piids"]
    if not cohort_piids:
        err_msg = "Stage 1 returned zero cohort PIIDs. Cannot proceed with transaction history acquisition."
        logger.error(err_msg)
        manifest, report = generate_manifest_and_report(
            config,
            run_status="no_cohort_piids",
            award_stage_data=award_stage_data,
            error_message=err_msg,
        )
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        report_path.write_text(report, encoding="utf-8")
        return 9

    batch_size = config["transaction_cohort"].get("batch_size", 100)
    batches = [cohort_piids[i : i + batch_size] for i in range(0, len(cohort_piids), batch_size)]
    logger.info(f"Split {len(cohort_piids)} cohort PIIDs into {len(batches)} batch(es) of max size {batch_size}")

    tx_count_level = config["transaction_cohort"].get("spending_level_count", "transactions")
    tx_download_levels = config["transaction_cohort"].get("spending_level_download", ["transactions"])
    tx_cap_per_batch = config["safety_caps"]["transactions_max_per_batch"]

    tx_stage_data: dict[str, Any] = {
        "status": "in_progress",
        "total_batches": len(batches),
        "exact_match_quoting": quoting_enabled,
        "batches": [],
    }

    # Execute transactions batches
    for b_idx, batch in enumerate(batches, start=1):
        logger.info(f"Processing Transaction Batch {b_idx}/{len(batches)} ({len(batch)} PIIDs)...")

        # Format award_ids: if quoting_enabled, surround in double quotes per contract
        if quoting_enabled:
            formatted_piids = [f'"{p}"' for p in batch]
        else:
            formatted_piids = list(batch)

        # Strictly award_ids only, no date filters!
        tx_filters = {"award_ids": formatted_piids}

        # 2.1 Count precheck for transaction batch
        try:
            tx_count_resp = query_count_endpoint(
                session=session,
                base_url=base_url,
                count_endpoint=count_endpoint,
                trusted_hosts=trusted_hosts,
                filters=tx_filters,
                spending_level=tx_count_level,
                timeout=config["http_policy"]["timeout_seconds"],
            )
        except PrecheckValidationError as exc:
            err_msg = str(exc)
            logger.error(f"Transaction batch {b_idx} count precheck failed: {err_msg}")
            # If server rejected documented quoted form, capture exact evidence and halt
            tx_stage_data["status"] = "rejected_by_server"
            tx_stage_data["rejected_endpoint"] = count_endpoint
            tx_stage_data["http_status"] = getattr(exc, "precheck_data", {}).get("status_code", "N/A")
            tx_stage_data["error_message"] = err_msg
            tx_stage_data["sample_rejected_payload"] = {
                "filters": tx_filters,
                "spending_level": tx_count_level,
            }

            manifest, report = generate_manifest_and_report(
                config,
                run_status="transaction_precheck_rejected",
                award_stage_data=award_stage_data,
                tx_stage_data=tx_stage_data,
                manual_comparison=manual_comparison,
                error_message=(
                    f"Transaction precheck rejected by server on batch {b_idx}: {err_msg}. "
                    "Halting per specification rule: 'If the endpoint rejects the documented form, "
                    "preserve the server response and stop rather than trying arbitrary payload variants.'"
                ),
            )
            manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
            report_path.write_text(report, encoding="utf-8")
            return 10

        tx_calc_count = tx_count_resp["calculated_count"]
        logger.info(f"Transaction Batch {b_idx} Count Precheck: {tx_calc_count} transactions")

        if tx_calc_count > tx_cap_per_batch:
            err_msg = (
                f"Transaction batch {b_idx} count ({tx_calc_count}) exceeds cap ({tx_cap_per_batch})."
            )
            logger.error(err_msg)
            tx_stage_data["status"] = "batch_cap_exceeded"
            manifest, report = generate_manifest_and_report(
                config,
                run_status="batch_cap_exceeded",
                award_stage_data=award_stage_data,
                tx_stage_data=tx_stage_data,
                error_message=err_msg,
            )
            manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
            report_path.write_text(report, encoding="utf-8")
            return 11

        # 2.2 Submit transaction download job
        try:
            tx_job = initiate_download_job(
                session=session,
                base_url=base_url,
                search_endpoint=search_endpoint,
                trusted_hosts=trusted_hosts,
                filters=tx_filters,
                spending_levels=tx_download_levels,
                file_format=file_format,
                timeout=config["http_policy"]["timeout_seconds"],
            )
        except DownloadJobError as exc:
            err_msg = f"Transaction batch {b_idx} job initiation failed: {exc}"
            logger.error(err_msg)
            tx_stage_data["status"] = "job_init_failed"
            manifest, report = generate_manifest_and_report(
                config,
                run_status="tx_job_init_failed",
                award_stage_data=award_stage_data,
                tx_stage_data=tx_stage_data,
                error_message=err_msg,
            )
            manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
            report_path.write_text(report, encoding="utf-8")
            return 12

        # 2.3 Poll transaction job status
        try:
            tx_poll = poll_download_status(
                session=session,
                base_url=base_url,
                status_endpoint_cfg=status_endpoint,
                trusted_hosts=trusted_hosts,
                job_info=tx_job,
                poll_interval=config["polling_policy"]["poll_interval_seconds"],
                overall_timeout=config["polling_policy"]["overall_timeout_seconds"],
                http_timeout=config["http_policy"]["timeout_seconds"],
            )
        except (DownloadJobError, DownloadJobTimeoutError) as exc:
            err_msg = f"Transaction batch {b_idx} polling failed: {exc}"
            logger.error(err_msg)
            tx_stage_data["status"] = "polling_failed"
            manifest, report = generate_manifest_and_report(
                config,
                run_status="tx_polling_failed",
                award_stage_data=award_stage_data,
                tx_stage_data=tx_stage_data,
                error_message=err_msg,
            )
            manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
            report_path.write_text(report, encoding="utf-8")
            return 13

        # 2.4 Stream transaction ZIP
        target_tx_zip = bulk_api_dir / f"PrimeTransactions_batch{b_idx}_{timestamp_str}.zip"
        try:
            download_zip_stream(
                session=session,
                file_url=tx_poll["file_url"],
                target_path=target_tx_zip,
                trusted_hosts=trusted_hosts,
                download_timeout=config["http_policy"]["download_timeout_seconds"],
            )
        except (UntrustedHostError, ZIPValidationError, DownloadJobError, FileExistsError) as exc:
            err_msg = f"Transaction batch {b_idx} download failed: {exc}"
            logger.error(err_msg)
            tx_stage_data["status"] = "download_failed"
            manifest, report = generate_manifest_and_report(
                config,
                run_status="tx_download_failed",
                award_stage_data=award_stage_data,
                tx_stage_data=tx_stage_data,
                error_message=err_msg,
            )
            manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
            report_path.write_text(report, encoding="utf-8")
            return 14

        # 2.5 In-memory QA of transaction ZIP
        try:
            tx_qa = inspect_transaction_zip(target_tx_zip, expected_cohort_piids=set(cohort_piids))
        except ZIPValidationError as exc:
            err_msg = f"Transaction batch {b_idx} ZIP QA failed: {exc}"
            logger.error(err_msg)
            tx_stage_data["status"] = "qa_failed"
            manifest, report = generate_manifest_and_report(
                config,
                run_status="tx_qa_failed",
                award_stage_data=award_stage_data,
                tx_stage_data=tx_stage_data,
                error_message=err_msg,
            )
            manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
            report_path.write_text(report, encoding="utf-8")
            return 15

        # 2.6 Same-query reconciliation for transaction batch
        tx_csv_rows = tx_qa["row_count"]
        if tx_calc_count != tx_csv_rows:
            err_msg = (
                f"Transaction batch {b_idx} count mismatch: Count API reported {tx_calc_count}, "
                f"CSV rows {tx_csv_rows}."
            )
            logger.error(err_msg)
            tx_stage_data["status"] = "count_mismatch"
            manifest, report = generate_manifest_and_report(
                config,
                run_status="tx_count_mismatch",
                award_stage_data=award_stage_data,
                tx_stage_data=tx_stage_data,
                error_message=err_msg,
            )
            manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
            report_path.write_text(report, encoding="utf-8")
            return 16

        batch_result = {
            "batch_index": b_idx,
            "piids_queried_count": len(batch),
            "precheck_count": tx_calc_count,
            "status_total_rows": tx_poll.get("total_rows"),
            "csv_row_count": tx_csv_rows,
            "zip_path": str(target_tx_zip),
            "sha256": tx_qa["sha256"],
            "file_size_bytes": tx_qa["file_size_bytes"],
            "unique_tx_keys_count": tx_qa["unique_tx_keys_count"],
            "missing_tx_keys_count": tx_qa["missing_tx_keys_count"],
            "duplicate_tx_keys_count": tx_qa["duplicate_tx_keys_count"],
            "cohort_piids_matched_count": tx_qa["cohort_piids_matched_count"],
            "unmatched_tx_piids_count": tx_qa["unmatched_tx_piids_count"],
            "date_audit": tx_qa["date_audit"],
        }
        tx_stage_data["batches"].append(batch_result)
        logger.info(f"Transaction Batch {b_idx} completed: {tx_csv_rows} rows reconciled.")

    tx_stage_data["status"] = "completed"
    tx_stage_data["total_tx_rows"] = sum(b["csv_row_count"] for b in tx_stage_data["batches"])

    # Collect min/max dates across all batches
    all_mins = [b["date_audit"]["min_action_date"] for b in tx_stage_data["batches"] if b["date_audit"]["min_action_date"]]
    all_maxs = [b["date_audit"]["max_action_date"] for b in tx_stage_data["batches"] if b["date_audit"]["max_action_date"]]
    tx_stage_data["min_action_date"] = min(all_mins) if all_mins else None
    tx_stage_data["max_action_date"] = max(all_maxs) if all_maxs else None
    tx_stage_data["outside_fy2020_count"] = sum(b["date_audit"]["outside_fy2020_count"] for b in tx_stage_data["batches"])

    # Compare with manual archives
    manual_on_path = Path(config["paths"]["manual_archive_on"])
    manual_off_path = Path(config["paths"]["manual_archive_off"])
    manual_comparison = compare_with_manual_archives(manual_on_path, manual_off_path)

    # Success manifest and report
    manifest, report = generate_manifest_and_report(
        config,
        run_status="success",
        award_stage_data=award_stage_data,
        tx_stage_data=tx_stage_data,
        manual_comparison=manual_comparison,
    )
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    report_path.write_text(report, encoding="utf-8")
    logger.info(f"Controlled FY2020 Pilot SUCCEEDED. Manifest: {manifest_path}, Report: {report_path}")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="USAspending Canonical Bulk Download Client (Two-Stage FY2020 Controlled Pilot)."
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
        help="Send unquoted PIIDs if the server rejects double quotes.",
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
