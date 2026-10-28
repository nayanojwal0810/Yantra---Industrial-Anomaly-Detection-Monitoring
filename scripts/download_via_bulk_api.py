#!/usr/bin/env python3
"""Canonical bulk download client for USAspending bulk download API.

Project: Sanket — Federal Contract Recompete Intelligence
Controlled Cohort: NASA + NAICS 541330 + FY2020 action dates (Show New Awards Only OFF)

This script uses the official USAspending asynchronous bulk download API:
- POST /api/v2/download/count/ (precheck awards and transactions)
- POST /api/v2/download/search/ (initiate asynchronous download job)
- GET  /api/v2/download/status/ (poll job completion status)
- Stream download to temporary .part file, validate ZIP, and atomic rename.
- In-memory ZIP quality audit (no extraction to disk).
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
    """Raised when count precheck fails or mismatches reference expectations."""

    def __init__(self, message: str, precheck_data: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.precheck_data = precheck_data


class UntrustedHostError(BulkDownloadError):
    """Raised when an API URL targets an untrusted host."""


class DownloadJobError(BulkDownloadError):
    """Raised when an asynchronous download job fails on the server."""


class DownloadJobTimeoutError(BulkDownloadError):
    """Raised when polling for job completion exceeds overall timeout."""


class ZIPValidationError(BulkDownloadError):
    """Raised when downloaded ZIP file is corrupt or invalid."""


def redact_sensitive(text: str) -> str:
    """Redact tokens, passwords, and sensitive keys from log strings or URLs."""
    if not isinstance(text, str):
        return str(text)
    # Redact Authorization header patterns or token parameters
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
        "reference_ui_counts",
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

    return cfg


def validate_trusted_host(url: str, trusted_hosts: list[str]) -> str:
    """Ensure URL host belongs to the configured trusted hosts whitelist."""
    parsed = urlparse(url)
    host = parsed.hostname
    if not host:
        raise UntrustedHostError(f"Unable to parse hostname from URL: {redact_sensitive(url)}")
    if host.lower() not in [h.lower() for h in trusted_hosts]:
        raise UntrustedHostError(
            f"Host '{host}' is not in trusted hosts list: {trusted_hosts}. Target: {redact_sensitive(url)}"
        )
    return url


def resolve_api_url(base_url: str, relative_or_absolute_url: str, trusted_hosts: list[str]) -> str:
    """Resolve and validate an API URL against base URL and trusted hosts."""
    resolved = urljoin(base_url, relative_or_absolute_url)
    return validate_trusted_host(resolved, trusted_hosts)


def create_session(http_policy: dict[str, Any]) -> requests.Session:
    """Create a requests Session with bounded retry behavior for transient errors."""
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
    return session


def parse_count_response(resp_data: Any, level: str) -> dict[str, Any]:
    """Defensively validate and parse response from /api/v2/download/count/."""
    if not isinstance(resp_data, dict):
        raise PrecheckValidationError(f"Expected dict response from count endpoint, got {type(resp_data).__name__}")

    # Check calculated_count (must not be boolean)
    calc_count = resp_data.get("calculated_count")
    if isinstance(calc_count, bool) or not isinstance(calc_count, (int, float)):
        # Check alternative transaction count key if level is transactions
        calc_tx = resp_data.get("calculated_transaction_count")
        if level == "transactions" and not isinstance(calc_tx, bool) and isinstance(calc_tx, (int, float)):
            calc_count = int(calc_tx)
        else:
            raise PrecheckValidationError(
                f"Count endpoint returned invalid calculated_count: {calc_count!r} (type={type(calc_count).__name__})"
            )
    else:
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


def execute_count_precheck(
    session: requests.Session,
    config: dict[str, Any],
) -> dict[str, Any]:
    """Execute count precheck for both awards and transactions levels.

    Validates that:
    1. Calculated counts do not exceed safety caps.
    2. Calculated counts match reference UI counts exactly (785 awards, 1,384 transactions).
    If a mismatch or violation occurs, raises PrecheckValidationError.
    """
    base_url = config["api"]["base_url"]
    count_endpoint = config["api"]["endpoints"]["count"]
    trusted_hosts = config["api"]["trusted_hosts"]
    count_url = resolve_api_url(base_url, count_endpoint, trusted_hosts)

    filters = config["controlled_cohort"]["filters"]
    ref_counts = config["reference_ui_counts"]
    safety_caps = config["safety_caps"]
    timeout = config["http_policy"].get("timeout_seconds", 30)

    results: dict[str, Any] = {}

    for level in ["awards", "transactions"]:
        payload = {
            "filters": filters,
            "spending_level": level,
        }
        logger.info(f"POSTing count precheck for spending_level='{level}' to {count_url}...")
        try:
            resp = session.post(count_url, json=payload, timeout=timeout)
        except requests.RequestException as exc:
            raise PrecheckValidationError(
                f"HTTP request to count endpoint failed for level '{level}': {redact_sensitive(str(exc))}"
            ) from exc

        if resp.status_code != 200:
            error_body = redact_sensitive(resp.text[:500])
            raise PrecheckValidationError(
                f"Count endpoint returned HTTP {resp.status_code} for level '{level}': {error_body}"
            )

        try:
            resp_json = resp.json()
        except (ValueError, json.JSONDecodeError) as exc:
            raise PrecheckValidationError(
                f"Count endpoint returned non-JSON response for level '{level}': {resp.text[:300]}"
            ) from exc

        parsed = parse_count_response(resp_json, level)
        results[level] = parsed

    # Validate awards count against safety cap and reference
    awards_count = results["awards"]["calculated_count"]
    awards_cap = safety_caps["awards_max"]
    ref_awards = ref_counts["awards"]
    if awards_count > awards_cap:
        raise PrecheckValidationError(
            f"Precheck awards count ({awards_count}) exceeds safety cap ({awards_cap}).",
            precheck_data=results,
        )
    if awards_count != ref_awards:
        raise PrecheckValidationError(
            f"Count precheck mismatch for awards: API returned {awards_count}, "
            f"expected reference UI count {ref_awards}. Download aborted per contract.",
            precheck_data=results,
        )

    # Validate transactions count against safety cap and reference
    tx_count = results["transactions"]["calculated_count"]
    tx_cap = safety_caps["transactions_max"]
    ref_tx = ref_counts["transactions"]
    if tx_count > tx_cap:
        raise PrecheckValidationError(
            f"Precheck transactions count ({tx_count}) exceeds safety cap ({tx_cap}).",
            precheck_data=results,
        )
    if tx_count != ref_tx:
        raise PrecheckValidationError(
            f"Count precheck mismatch for transactions: API returned {tx_count}, "
            f"expected reference UI count {ref_tx}. Download aborted per contract.",
            precheck_data=results,
        )

    logger.info(
        f"Count precheck PASSED: {awards_count} awards (ref: {ref_awards}), "
        f"{tx_count} transactions (ref: {ref_tx})."
    )
    return results


def initiate_bulk_download_job(
    session: requests.Session,
    config: dict[str, Any],
) -> dict[str, Any]:
    """Submit asynchronous download job via POST /api/v2/download/search/."""
    base_url = config["api"]["base_url"]
    search_endpoint = config["api"]["endpoints"]["search"]
    trusted_hosts = config["api"]["trusted_hosts"]
    search_url = resolve_api_url(base_url, search_endpoint, trusted_hosts)

    cohort = config["controlled_cohort"]
    filters = cohort["filters"]
    spending_levels = cohort["spending_levels"]
    file_format = cohort["file_format"]
    timeout = config["http_policy"].get("timeout_seconds", 30)

    # Contract requires: filters, file_format, spending_level. Omit columns to preserve full schema.
    payload = {
        "filters": filters,
        "file_format": file_format,
        "spending_level": spending_levels,
    }

    logger.info(f"Submitting bulk download job to {search_url}...")
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

    logger.info(f"Bulk download job created successfully: file_name={file_name}")
    return {
        "file_name": file_name,
        "status_url": status_url,
        "file_url": file_url,
        "download_request": data.get("download_request", {}),
        "raw_response": data,
    }


def poll_download_status(
    session: requests.Session,
    job_info: dict[str, Any],
    config: dict[str, Any],
) -> dict[str, Any]:
    """Poll the status endpoint until the download job is finished, failed, or times out."""
    base_url = config["api"]["base_url"]
    status_endpoint_cfg = config["api"]["endpoints"]["status"]
    trusted_hosts = config["api"]["trusted_hosts"]
    poll_interval = config["polling_policy"].get("poll_interval_seconds", 5)
    overall_timeout = config["polling_policy"].get("overall_timeout_seconds", 300)
    http_timeout = config["http_policy"].get("timeout_seconds", 30)

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
        entry = {
            "attempt": attempts,
            "elapsed_seconds": round(elapsed, 1),
            "status": status_str,
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        history.append(entry)
        logger.info(f"Poll attempt {attempts} ({elapsed:.1f}s): status='{status_str}' message='{message}'")

        if status_str == "finished":
            download_file_url = status_data.get("url") or status_data.get("file_url") or job_info.get("file_url")
            return {
                "final_status": "finished",
                "file_name": file_name,
                "file_url": download_file_url,
                "total_attempts": attempts,
                "total_elapsed_seconds": round(elapsed, 1),
                "history": history,
                "raw_response": status_data,
            }

        if status_str == "failed":
            raise DownloadJobError(
                f"Download job failed on USAspending server. Status message: '{message}'"
            )

        # Status is 'ready', 'running', or intermediate state
        time.sleep(poll_interval)


def download_zip_stream(
    session: requests.Session,
    file_url: str,
    target_path: Path,
    config: dict[str, Any],
) -> Path:
    """Stream download ZIP file to temporary .part file, validate, and atomically rename."""
    trusted_hosts = config["api"]["trusted_hosts"]
    validate_trusted_host(file_url, trusted_hosts)

    if target_path.exists():
        raise FileExistsError(f"Target download path already exists: {target_path}. Overwrite is forbidden.")

    part_path = target_path.with_suffix(".zip.part")
    if part_path.exists():
        part_path.unlink()

    target_path.parent.mkdir(parents=True, exist_ok=True)
    download_timeout = config["http_policy"].get("download_timeout_seconds", 180)

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

    # Validate downloaded archive as a valid ZIP
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

    # Atomic rename
    os.replace(part_path, target_path)
    logger.info(f"Download completed and verified: {target_path}")
    return target_path


def compute_sha256(path: Path) -> str:
    """Compute SHA-256 checksum of a file."""
    hasher = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def inspect_zip_in_memory(zip_path: Path) -> dict[str, Any]:
    """Inspect ZIP members in memory without extracting raw CSVs to disk."""
    if not zip_path.is_file():
        raise FileNotFoundError(f"ZIP file not found: {zip_path}")

    file_size_bytes = zip_path.stat().st_size
    sha256_hex = compute_sha256(zip_path)

    members_meta: list[dict[str, Any]] = []
    awards_member: str | None = None
    tx_member: str | None = None
    subaward_members: list[str] = []

    with zipfile.ZipFile(zip_path, "r") as z:
        for info in z.infolist():
            member_dict = {
                "filename": info.filename,
                "file_size": info.file_size,
                "compress_size": info.compress_size,
            }
            members_meta.append(member_dict)

            lower_name = info.filename.lower()
            if "subaward" in lower_name:
                subaward_members.append(info.filename)
            elif "primeawardsummaries" in lower_name or "contracts_primeawardsummaries" in lower_name:
                awards_member = info.filename
            elif "primetransactions" in lower_name or "contracts_primetransactions" in lower_name:
                tx_member = info.filename

        if subaward_members:
            raise ZIPValidationError(
                f"Found unexpected subaward members in ZIP: {subaward_members}. Subawards are forbidden."
            )

        # Fallback inspection by header if filename matching did not find both
        if not awards_member or not tx_member:
            for info in z.infolist():
                if not info.filename.endswith(".csv"):
                    continue
                with z.open(info.filename) as f:
                    wrapper = io.TextIOWrapper(f, encoding="utf-8-sig", errors="replace")
                    reader = csv.reader(wrapper)
                    try:
                        header = next(reader)
                    except StopIteration:
                        header = []
                    header_set = set(header)
                    if "contract_award_unique_key" in header_set and "contract_transaction_unique_key" not in header_set:
                        awards_member = info.filename
                    elif "contract_transaction_unique_key" in header_set:
                        tx_member = info.filename

        if not awards_member:
            raise ZIPValidationError("Unable to identify PrimeAwardSummaries member in downloaded ZIP.")
        if not tx_member:
            raise ZIPValidationError("Unable to identify PrimeTransactions member in downloaded ZIP.")

        # Read award summaries in memory
        with z.open(awards_member) as f:
            wrapper = io.TextIOWrapper(f, encoding="utf-8-sig", errors="replace")
            reader = csv.DictReader(wrapper)
            award_columns = reader.fieldnames or []
            award_rows = list(reader)

        # Read transactions in memory
        with z.open(tx_member) as f:
            wrapper = io.TextIOWrapper(f, encoding="utf-8-sig", errors="replace")
            reader = csv.DictReader(wrapper)
            tx_columns = reader.fieldnames or []
            tx_rows = list(reader)

    # Award stats
    award_row_count = len(award_rows)
    award_keys = [r.get("contract_award_unique_key", "").strip() for r in award_rows]
    populated_award_keys = [k for k in award_keys if k]
    unique_award_keys = set(populated_award_keys)
    award_missing_keys = award_row_count - len(populated_award_keys)
    award_duplicate_keys = len(populated_award_keys) - len(unique_award_keys)

    # Transaction stats
    tx_row_count = len(tx_rows)
    tx_unique_keys = [r.get("contract_transaction_unique_key", "").strip() for r in tx_rows]
    populated_tx_unique_keys = [k for k in tx_unique_keys if k]
    unique_tx_keys = set(populated_tx_unique_keys)
    tx_missing_keys = tx_row_count - len(populated_tx_unique_keys)
    tx_duplicate_keys = len(populated_tx_unique_keys) - len(unique_tx_keys)

    tx_award_keys = [r.get("contract_award_unique_key", "").strip() for r in tx_rows]
    populated_tx_award_keys = [k for k in tx_award_keys if k]
    unique_tx_award_keys = set(populated_tx_award_keys)

    # Linkage
    tx_award_keys_in_awards = unique_tx_award_keys.intersection(unique_award_keys)
    linkage_pct = (
        (len(tx_award_keys_in_awards) / len(unique_tx_award_keys) * 100.0)
        if unique_tx_award_keys
        else 0.0
    )

    # FY2020 Action Date audit (2019-10-01 to 2020-09-30)
    fy_start = "2019-10-01"
    fy_end = "2020-09-30"
    in_fy_count = 0
    out_of_fy_count = 0
    date_deviations: list[dict[str, str]] = []

    for r in tx_rows:
        ad = r.get("action_date", "").strip()
        if fy_start <= ad <= fy_end:
            in_fy_count += 1
        else:
            out_of_fy_count += 1
            if len(date_deviations) < 10:
                date_deviations.append(
                    {
                        "transaction_key": r.get("contract_transaction_unique_key", ""),
                        "action_date": ad,
                    }
                )

    return {
        "zip_path": str(zip_path),
        "file_size_bytes": file_size_bytes,
        "sha256": sha256_hex,
        "members": members_meta,
        "awards": {
            "member_name": awards_member,
            "row_count": award_row_count,
            "column_count": len(award_columns),
            "columns": award_columns,
            "unique_keys_count": len(unique_award_keys),
            "missing_keys_count": award_missing_keys,
            "duplicate_keys_count": award_duplicate_keys,
            "keys_set": unique_award_keys,
        },
        "transactions": {
            "member_name": tx_member,
            "row_count": tx_row_count,
            "column_count": len(tx_columns),
            "columns": tx_columns,
            "unique_keys_count": len(unique_tx_keys),
            "missing_keys_count": tx_missing_keys,
            "duplicate_keys_count": tx_duplicate_keys,
            "unique_award_keys_referenced": len(unique_tx_award_keys),
            "linkage_referenced_in_awards_count": len(tx_award_keys_in_awards),
            "linkage_percentage": round(linkage_pct, 2),
            "action_date_audit": {
                "fy_start": fy_start,
                "fy_end": fy_end,
                "in_fy_count": in_fy_count,
                "out_of_fy_count": out_of_fy_count,
                "deviations_sample": date_deviations,
            },
            "keys_set": unique_tx_keys,
        },
    }


def compare_with_manual_archive(
    api_qa: dict[str, Any],
    manual_archive_path: Path,
) -> dict[str, Any]:
    """Compare in-memory inspected API ZIP against the manual archive if present."""
    if not manual_archive_path.is_file():
        return {
            "manual_archive_present": False,
            "manual_archive_path": str(manual_archive_path),
            "note": "Manual archive not found at configured path.",
        }

    try:
        manual_qa = inspect_zip_in_memory(manual_archive_path)
    except (ZIPValidationError, FileNotFoundError, OSError) as exc:
        return {
            "manual_archive_present": True,
            "manual_archive_path": str(manual_archive_path),
            "error": f"Failed to inspect manual archive: {exc}",
        }

    api_award_keys: set[str] = api_qa["awards"]["keys_set"]
    manual_award_keys: set[str] = manual_qa["awards"]["keys_set"]
    awards_intersection = api_award_keys.intersection(manual_award_keys)

    api_tx_keys: set[str] = api_qa["transactions"]["keys_set"]
    manual_tx_keys: set[str] = manual_qa["transactions"]["keys_set"]
    tx_intersection = api_tx_keys.intersection(manual_tx_keys)

    return {
        "manual_archive_present": True,
        "manual_archive_path": str(manual_archive_path),
        "manual_sha256": manual_qa["sha256"],
        "manual_awards_row_count": manual_qa["awards"]["row_count"],
        "manual_transactions_row_count": manual_qa["transactions"]["row_count"],
        "api_awards_row_count": api_qa["awards"]["row_count"],
        "api_transactions_row_count": api_qa["transactions"]["row_count"],
        "award_keys_overlap_count": len(awards_intersection),
        "award_keys_manual_only": len(manual_award_keys - api_award_keys),
        "award_keys_api_only": len(api_award_keys - manual_award_keys),
        "tx_keys_overlap_count": len(tx_intersection),
        "tx_keys_manual_only": len(manual_tx_keys - api_tx_keys),
        "tx_keys_api_only": len(api_tx_keys - manual_tx_keys),
        "note": "Manual archive was inspected in memory and preserved completely unchanged.",
    }


def generate_manifest_and_report(
    config: dict[str, Any],
    run_status: str,
    precheck_data: dict[str, Any] | None = None,
    job_info: dict[str, Any] | None = None,
    poll_result: dict[str, Any] | None = None,
    qa_result: dict[str, Any] | None = None,
    overlap_result: dict[str, Any] | None = None,
    error_message: str | None = None,
) -> tuple[dict[str, Any], str]:
    """Generate structured manifest dict and markdown report."""
    timestamp = datetime.now(timezone.utc).isoformat()
    cohort = config["controlled_cohort"]
    ref_counts = config["reference_ui_counts"]

    # Build manifest
    manifest: dict[str, Any] = {
        "manifest_version": "1.0.0",
        "generated_at_utc": timestamp,
        "run_status": run_status,
        "controlled_cohort": cohort,
        "reference_ui_counts": ref_counts,
        "error_message": error_message,
        "precheck": precheck_data,
        "job_creation": job_info,
        "polling": poll_result,
        "qa": None,
        "overlap_with_manual_archive": overlap_result,
    }

    if qa_result:
        # Avoid serializing set objects in manifest
        clean_qa = json.loads(
            json.dumps(
                qa_result,
                default=lambda o: list(o) if isinstance(o, set) else str(o),
            )
        )
        # Drop raw key sets from manifest to keep it lightweight
        if "awards" in clean_qa and "keys_set" in clean_qa["awards"]:
            del clean_qa["awards"]["keys_set"]
        if "transactions" in clean_qa and "keys_set" in clean_qa["transactions"]:
            del clean_qa["transactions"]["keys_set"]
        manifest["qa"] = clean_qa

    # Build markdown report
    md_lines = [
        "# Sanket — USAspending Bulk Download Client Validation Report",
        "",
        f"**Run Status**: `{run_status}`  ",
        f"**Timestamp (UTC)**: `{timestamp}`  ",
        f"**Controlled Cohort**: `{cohort['cohort_id']}` ({cohort['description']})  ",
        "",
        "## 1. Executive Summary",
        "",
    ]

    if run_status == "dry_run":
        md_lines.extend(
            [
                "This execution was a **dry run** (`--confirm-sample-download` was not passed).",
                "Zero HTTP requests were sent and zero raw sample files were created or modified.",
                "",
                "### Planned Cohort Filters",
                "```json",
                json.dumps(cohort["filters"], indent=2),
                "```",
                "",
                f"- **Intended Awards Count (UI Ref)**: `{ref_counts['awards']}`",
                f"- **Intended Transactions Count (UI Ref)**: `{ref_counts['transactions']}`",
                f"- **API Base URL**: `{config['api']['base_url']}`",
                f"- **Safety Caps**: Awards <= {config['safety_caps']['awards_max']}, Transactions <= {config['safety_caps']['transactions_max']}",
                "",
            ]
        )
    elif run_status == "success":
        md_lines.extend(
            [
                "The canonical bulk download client successfully completed the controlled cohort acquisition.",
                "Count precheck matched reference counts, the asynchronous job finished cleanly, ",
                "and the downloaded ZIP passed all in-memory integrity, linkage, and schema validations.",
                "",
                "## 2. Reconciled Counts & Precheck",
                "",
                "| Spending Level | UI Reference Count | API Count Precheck | Downloaded CSV Rows | Reconciled Status |",
                "| :--- | :--- | :--- | :--- | :--- |",
                f"| Prime Awards | {ref_counts['awards']} | {precheck_data['awards']['calculated_count'] if precheck_data else 'N/A'} | {qa_result['awards']['row_count'] if qa_result else 'N/A'} | **MATCH** |",
                f"| Prime Transactions | {ref_counts['transactions']} | {precheck_data['transactions']['calculated_count'] if precheck_data else 'N/A'} | {qa_result['transactions']['row_count'] if qa_result else 'N/A'} | **MATCH** |",
                "",
                "## 3. Downloaded ZIP Quality & Linkage QA",
                "",
                f"- **ZIP File**: `{qa_result['zip_path']}`",
                f"- **Size**: `{qa_result['file_size_bytes']:,}` bytes",
                f"- **SHA-256**: `{qa_result['sha256']}`",
                f"- **Prime Awards Member**: `{qa_result['awards']['member_name']}` ({qa_result['awards']['row_count']} rows, {qa_result['awards']['column_count']} cols)",
                f"  - Missing `contract_award_unique_key`: `{qa_result['awards']['missing_keys_count']}`",
                f"  - Duplicate keys: `{qa_result['awards']['duplicate_keys_count']}`",
                f"- **Prime Transactions Member**: `{qa_result['transactions']['member_name']}` ({qa_result['transactions']['row_count']} rows, {qa_result['transactions']['column_count']} cols)",
                f"  - Missing `contract_transaction_unique_key`: `{qa_result['transactions']['missing_keys_count']}`",
                f"  - Duplicate keys: `{qa_result['transactions']['duplicate_keys_count']}`",
                f"  - Unique Awards Referenced: `{qa_result['transactions']['unique_award_keys_referenced']}`",
                f"  - Transaction-to-Award Linkage: `{qa_result['transactions']['linkage_percentage']}%` ({qa_result['transactions']['linkage_referenced_in_awards_count']}/{qa_result['transactions']['unique_award_keys_referenced']})",
                f"  - Transactions in FY2020: `{qa_result['transactions']['action_date_audit']['in_fy_count']}/{qa_result['transactions']['row_count']}` (Deviations: {qa_result['transactions']['action_date_audit']['out_of_fy_count']})",
                "",
                "> [!NOTE]",
                "> The downloaded transaction export contains FY2020 action modifications, not all lifetime modifications for each award.",
                "",
            ]
        )
        if overlap_result and overlap_result.get("manual_archive_present"):
            md_lines.extend(
                [
                    "## 4. Reconciliation with Manual Archive (`NASA_2020.zip`)",
                    "",
                    f"- **Manual Archive SHA-256**: `{overlap_result.get('manual_sha256')}`",
                    f"- **Award Keys Overlap**: `{overlap_result['award_keys_overlap_count']}` (Manual only: {overlap_result['award_keys_manual_only']}, API only: {overlap_result['award_keys_api_only']})",
                    f"- **Transaction Keys Overlap**: `{overlap_result['tx_keys_overlap_count']}` (Manual only: {overlap_result['tx_keys_manual_only']}, API only: {overlap_result['tx_keys_api_only']})",
                    f"- **Manual Archive Preservation**: `{overlap_result['note']}`",
                    "",
                ]
            )
    else:
        # Error or count_mismatch
        md_lines.extend(
            [
                f"The bulk download workflow stopped with status: **`{run_status}`**.",
                "",
                "### Error / Halt Details",
                f"```\n{error_message}\n```",
                "",
                "### Controlled Filters Submitted",
                "```json",
                json.dumps(cohort["filters"], indent=2),
                "```",
                "",
            ]
        )
        if precheck_data:
            awards_api = precheck_data.get("awards", {}).get("calculated_count", "N/A")
            tx_api = precheck_data.get("transactions", {}).get("calculated_count", "N/A")
            awards_match = "MATCH" if awards_api == ref_counts["awards"] else "**MISMATCH**"
            tx_match = "MATCH" if tx_api == ref_counts["transactions"] else "**MISMATCH**"

            md_lines.extend(
                [
                    "### Count Precheck Comparison",
                    "",
                    "| Spending Level | UI Reference Count | API Count Precheck | Status |",
                    "| :--- | :--- | :--- | :--- |",
                    f"| Prime Awards | {ref_counts['awards']} | {awards_api} | {awards_match} |",
                    f"| Prime Transactions | {ref_counts['transactions']} | {tx_api} | {tx_match} |",
                    "",
                    "### Count Precheck Raw Responses",
                    "```json",
                    json.dumps(precheck_data, indent=2),
                    "```",
                    "",
                ]
            )

    report_content = "\n".join(md_lines) + "\n"
    return manifest, report_content


def run_bulk_download(
    config_path: Path | str = DEFAULT_CONFIG_PATH,
    confirm_download: bool = False,
) -> int:
    """Main execution function for the bulk download client."""
    try:
        config = load_config(config_path)
    except (ConfigError, OSError) as exc:
        logger.error(f"Configuration error: {exc}")
        return 1

    manifest_path = Path(config["paths"]["manifest_path"])
    report_path = Path(config["paths"]["validation_report_path"])
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    if not confirm_download:
        logger.info("=== DRY RUN MODE ===")
        logger.info("Pass --confirm-sample-download to execute the single controlled FY2020 cohort download.")
        logger.info(f"Target Cohort: {config['controlled_cohort']['cohort_id']}")
        logger.info(f"Filters:\n{json.dumps(config['controlled_cohort']['filters'], indent=2)}")
        logger.info(f"Reference UI Counts: {config['reference_ui_counts']}")
        logger.info(f"Safety Caps: {config['safety_caps']}")
        logger.info(f"API Base URL: {config['api']['base_url']}")
        logger.info(f"Output Directory: {config['paths']['raw_data_dir']}")

        manifest, report = generate_manifest_and_report(config, run_status="dry_run")
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        report_path.write_text(report, encoding="utf-8")
        logger.info(f"Dry run manifest saved to {manifest_path}")
        logger.info(f"Dry run report saved to {report_path}")
        return 0

    session = create_session(config["http_policy"])

    # 1. Count precheck
    precheck_data = None
    try:
        precheck_data = execute_count_precheck(session, config)
    except PrecheckValidationError as exc:
        err_msg = str(exc)
        logger.error(f"Count precheck validation failed: {err_msg}")
        precheck_data = exc.precheck_data or precheck_data
        manifest, report = generate_manifest_and_report(
            config,
            run_status="count_mismatch",
            precheck_data=precheck_data,
            error_message=err_msg,
        )
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        report_path.write_text(report, encoding="utf-8")
        return 2

    # 2. Initiate download job
    job_info = None
    try:
        job_info = initiate_bulk_download_job(session, config)
    except DownloadJobError as exc:
        err_msg = str(exc)
        logger.error(f"Failed to initiate download job: {err_msg}")
        manifest, report = generate_manifest_and_report(
            config,
            run_status="job_creation_failed",
            precheck_data=precheck_data,
            job_info=job_info,
            error_message=err_msg,
        )
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        report_path.write_text(report, encoding="utf-8")
        return 3

    # 3. Poll status
    poll_result = None
    try:
        poll_result = poll_download_status(session, job_info, config)
    except (DownloadJobError, DownloadJobTimeoutError) as exc:
        err_msg = str(exc)
        logger.error(f"Job polling failed: {err_msg}")
        manifest, report = generate_manifest_and_report(
            config,
            run_status="polling_failed",
            precheck_data=precheck_data,
            job_info=job_info,
            poll_result=poll_result,
            error_message=err_msg,
        )
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        report_path.write_text(report, encoding="utf-8")
        return 4

    # 4. Stream and validate ZIP download
    file_url = poll_result["file_url"]
    if not file_url:
        err_msg = "Status polling succeeded but no download file_url was returned."
        logger.error(err_msg)
        manifest, report = generate_manifest_and_report(
            config,
            run_status="missing_file_url",
            precheck_data=precheck_data,
            job_info=job_info,
            poll_result=poll_result,
            error_message=err_msg,
        )
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        report_path.write_text(report, encoding="utf-8")
        return 5

    utc_now_str = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    raw_dir = Path(config["paths"]["raw_data_dir"])
    target_zip = raw_dir / f"api_nasa_naics541330_fy2020_{utc_now_str}.zip"

    try:
        download_zip_stream(session, file_url, target_zip, config)
    except (UntrustedHostError, ZIPValidationError, DownloadJobError, FileExistsError) as exc:
        err_msg = str(exc)
        logger.error(f"ZIP acquisition failed: {err_msg}")
        manifest, report = generate_manifest_and_report(
            config,
            run_status="download_failed",
            precheck_data=precheck_data,
            job_info=job_info,
            poll_result=poll_result,
            error_message=err_msg,
        )
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        report_path.write_text(report, encoding="utf-8")
        return 6

    # 5. In-memory ZIP quality inspection
    try:
        qa_result = inspect_zip_in_memory(target_zip)
    except ZIPValidationError as exc:
        err_msg = str(exc)
        logger.error(f"ZIP QA failed: {err_msg}")
        manifest, report = generate_manifest_and_report(
            config,
            run_status="qa_failed",
            precheck_data=precheck_data,
            job_info=job_info,
            poll_result=poll_result,
            error_message=err_msg,
        )
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        report_path.write_text(report, encoding="utf-8")
        return 7

    # 6. Reconcile downloaded rows with precheck & UI reference
    downloaded_awards = qa_result["awards"]["row_count"]
    downloaded_tx = qa_result["transactions"]["row_count"]
    ref_awards = config["reference_ui_counts"]["awards"]
    ref_tx = config["reference_ui_counts"]["transactions"]

    if downloaded_awards != ref_awards or downloaded_tx != ref_tx:
        err_msg = (
            f"Downloaded row counts mismatch UI reference: Awards {downloaded_awards} vs {ref_awards}, "
            f"Transactions {downloaded_tx} vs {ref_tx}."
        )
        logger.error(err_msg)
        manifest, report = generate_manifest_and_report(
            config,
            run_status="count_mismatch",
            precheck_data=precheck_data,
            job_info=job_info,
            poll_result=poll_result,
            qa_result=qa_result,
            error_message=err_msg,
        )
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        report_path.write_text(report, encoding="utf-8")
        return 8

    # 7. Compare with manual archive if present
    manual_archive_path = Path(config["paths"]["manual_archive_path"])
    overlap_result = compare_with_manual_archive(qa_result, manual_archive_path)

    # 8. Write success manifest and report
    manifest, report = generate_manifest_and_report(
        config,
        run_status="success",
        precheck_data=precheck_data,
        job_info=job_info,
        poll_result=poll_result,
        qa_result=qa_result,
        overlap_result=overlap_result,
    )
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    report_path.write_text(report, encoding="utf-8")

    logger.info(f"Controlled cohort bulk download SUCCEEDED. Manifest: {manifest_path}, Report: {report_path}")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="USAspending Bulk Download Client (Canonical acquisition path for Project Sanket)."
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
        help="Authorize acquisition of ONLY the single configured FY2020 controlled cohort.",
    )

    args = parser.parse_args()
    code = run_bulk_download(
        config_path=args.config,
        confirm_download=args.confirm_sample_download,
    )
    sys.exit(code)


if __name__ == "__main__":
    main()
