#!/usr/bin/env python3
"""
Federal Contract Recompete Intelligence — Sample Contract Data Acquisition (LEGACY / NOT RECOMMENDED)
Project: Sanket

[DEPRECATED / LEGACY DOWNLOADER]
This page-based search downloader (/api/v2/search/spending_by_award/) is preserved only for
historical reference and regression testing. It encountered HTTP 422 errors due to pagination
constraints on deep searches.

For production and controlled cohort acquisition, use the official asynchronous bulk download
client instead:
    scripts/download_via_bulk_api.py
"""

import argparse
import csv
import hashlib
import json
import math
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
import yaml

VERIFIED_AWARD_FIELDS: set[str] = {
    "Award ID",
    "Recipient Name",
    "Recipient UEI",
    "recipient_id",
    "Recipient Location",
    "Awarding Agency",
    "Awarding Agency Code",
    "Awarding Sub Agency",
    "Awarding Sub Agency Code",
    "Funding Agency",
    "Funding Agency Code",
    "Funding Sub Agency",
    "Funding Sub Agency Code",
    "Description",
    "Last Modified Date",
    "Base Obligation Date",
    "generated_internal_id",
    "prime_award_recipient_id",
    "Primary Place of Performance",
    "Place of Performance City Code",
    "Place of Performance State Code",
    "Place of Performance Country Code",
    "Place of Performance Zip5",
    "Start Date",
    "End Date",
    "Award Amount",
    "Total Outlays",
    "Contract Award Type",
    "NAICS",
    "PSC",
}

FORBIDDEN_AWARD_FIELDS: set[str] = {
    "Period of Performance Current End Date",
    "Award Type",
}


def load_config(config_path: str = "config/sample_data_config.yaml") -> dict[str, Any]:
    """Loads and validates the sample data YAML configuration."""
    path = Path(config_path)
    if not path.is_file():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    # Validate award fields allowlist
    configured_fields = cfg.get("award_fields", [])
    validate_award_fields(configured_fields)

    # Validate hard caps and sampling parameters as positive integers
    sampling = cfg.get("sampling_parameters", {})
    target_rows = sampling.get("target_rows_per_stratum", 25)
    if isinstance(target_rows, bool) or not isinstance(target_rows, int) or target_rows < 1 or target_rows > 25:
        raise ValueError("Configured target_rows_per_stratum must be a positive integer <= 25.")

    hard_cap = sampling.get("hard_cap_unique_awards", 400)
    if isinstance(hard_cap, bool) or not isinstance(hard_cap, int) or hard_cap < 1 or hard_cap > 400:
        raise ValueError("Configured hard_cap_unique_awards must be a positive integer <= 400.")

    detail_cap = sampling.get("detail_sample_award_cap", 30)
    if isinstance(detail_cap, bool) or not isinstance(detail_cap, int) or detail_cap < 1 or detail_cap > 30:
        raise ValueError("Configured detail_sample_award_cap must be a positive integer <= 30.")

    tx_limit = sampling.get("transaction_page_limit", 100)
    if isinstance(tx_limit, bool) or not isinstance(tx_limit, int) or tx_limit < 1 or tx_limit > 100:
        raise ValueError("Configured transaction_page_limit must be a positive integer <= 100.")

    families = cfg.get("inclusion_families", {})
    if not isinstance(families, dict) or len(families) == 0 or len(families) > 4:
        raise ValueError("Configured inclusion_families must contain between 1 and 4 families.")

    windows = cfg.get("date_windows", {})
    if not isinstance(windows, dict) or len(windows) == 0 or len(windows) > 4:
        raise ValueError("Configured date_windows must contain between 1 and 4 windows.")

    return cfg


def validate_award_fields(fields: list[str]) -> None:
    """Ensures requested fields strictly adhere to verified documented allowlist."""
    for f in fields:
        if f in FORBIDDEN_AWARD_FIELDS:
            raise ValueError(f"Field '{f}' is forbidden in Spending by Award request.")
        if f not in VERIFIED_AWARD_FIELDS:
            raise ValueError(f"Field '{f}' is not in verified award fields allowlist.")


def resolve_date_windows(
    date_windows_cfg: dict[str, Any],
    run_date_utc: datetime | None = None,
) -> dict[str, dict[str, str]]:
    """Resolves date bounds for configured date windows, including UTC run date for latest."""
    if run_date_utc is None:
        run_date_utc = datetime.now(timezone.utc)
    today_str = run_date_utc.strftime("%Y-%m-%d")

    resolved = {}
    for window_id, bounds in date_windows_cfg.items():
        start_date = bounds["start_date"]
        end_date = bounds.get("end_date")
        if end_date is None and bounds.get("resolve_rule") == "utc_today":
            end_date = today_str
        elif end_date is None:
            raise ValueError(f"Window '{window_id}' has no end_date and no resolution rule.")
        resolved[window_id] = {
            "start_date": start_date,
            "end_date": end_date,
        }
    return resolved


class ApiCallError(requests.HTTPError):
    """HTTP error enriched with bounded API error diagnostics and safe request summary."""

    def __init__(
        self,
        message: str,
        response: requests.Response | None = None,
        endpoint: str = "",
        status_code: int | None = None,
        error_detail: str = "",
        request_summary: Any = None,
    ):
        super().__init__(message, response=response)
        self.endpoint = endpoint
        self.status_code = status_code
        self.error_detail = error_detail
        self.request_summary = request_summary


def extract_api_error_detail(resp: Any, max_length: int = 2048) -> str:
    """Extracts a bounded, sanitized error message from an API error response."""
    detail = ""
    try:
        if hasattr(resp, "json"):
            data = resp.json()
            if isinstance(data, dict):
                if "detail" in data:
                    detail = str(data["detail"])
                elif "message" in data:
                    detail = str(data["message"])
                elif "messages" in data and isinstance(data["messages"], list):
                    detail = "; ".join(str(m) for m in data["messages"])
                else:
                    detail = json.dumps(data, ensure_ascii=False)
            elif isinstance(data, list):
                detail = json.dumps(data, ensure_ascii=False)
            elif data is not None:
                detail = str(data)
    except (ValueError, TypeError, AttributeError):
        detail = ""

    if not detail and hasattr(resp, "text") and resp.text:
        detail = str(resp.text).strip()

    if not detail:
        detail = "(no error message provided in response body)"

    if len(detail) > max_length:
        detail = detail[:max_length] + " [truncated]"

    return detail


def sanitize_request_payload(payload: Any) -> Any:
    """Creates a safe, bounded representation of a request payload without credentials."""
    if payload is None:
        return None
    sensitive_keys = {"authorization", "api_key", "password", "token", "secret", "cookie"}
    if isinstance(payload, dict):
        sanitized = {}
        for k, v in payload.items():
            if str(k).lower() in sensitive_keys:
                sanitized[k] = "[REDACTED]"
            else:
                sanitized[k] = sanitize_request_payload(v)
        return sanitized
    elif isinstance(payload, list):
        if len(payload) > 50:
            return [sanitize_request_payload(item) for item in payload[:50]] + [f"... ({len(payload) - 50} more items)"]
        return [sanitize_request_payload(item) for item in payload]
    return payload


def request_with_retry(
    session: requests.Session,
    method: str,
    url: str,
    max_retries: int = 3,
    backoff_factor: float = 1.5,
    timeout: int = 30,
    retry_statuses: set[int] | None = None,
    **kwargs: Any,
) -> requests.Response:
    """Executes HTTP request with bounded retry and exponential backoff on transient errors."""
    if retry_statuses is None:
        retry_statuses = {429, 500, 502, 503, 504}

    attempt = 0
    while True:
        try:
            resp = session.request(method=method, url=url, timeout=timeout, **kwargs)
            if resp.status_code in retry_statuses and attempt < max_retries:
                attempt += 1
                sleep_sec = backoff_factor ** attempt
                time.sleep(sleep_sec)
                continue
            resp.raise_for_status()
            return resp
        except requests.HTTPError as exc:
            error_detail = extract_api_error_detail(resp)
            safe_payload = sanitize_request_payload(
                kwargs.get("json") or kwargs.get("data") or kwargs.get("params")
            )
            reason = getattr(resp, "reason", "Error") or "Error"
            err_msg = (
                f"HTTP {resp.status_code} Error for URL '{url}': {reason}. "
                f"API error detail: {error_detail}. "
                f"Request payload: {json.dumps(safe_payload, ensure_ascii=False) if safe_payload is not None else 'None'}"
            )
            raise ApiCallError(
                message=err_msg,
                response=resp,
                endpoint=url,
                status_code=resp.status_code,
                error_detail=error_detail,
                request_summary=safe_payload if isinstance(safe_payload, dict) else {"payload": safe_payload},
            ) from exc
        except (requests.Timeout, requests.ConnectionError):
            if attempt < max_retries:
                attempt += 1
                sleep_sec = backoff_factor ** attempt
                time.sleep(sleep_sec)
                continue
            raise


def resolve_psc_family_path(
    tree_data: Any,
    group_id: str,
    expected_category: str = "Service",
) -> dict[str, Any]:
    """
    Recursively inspects PSC filter tree nodes to find the unambiguous service family
    matching group_id ('D' or 'R') under the Service category branch.
    Rejects Group 7 product codes or any nodes outside the Service category.
    """
    nodes = tree_data.get("results", []) if isinstance(tree_data, dict) else tree_data
    if not isinstance(nodes, list):
        raise TypeError(
            f"Unexpected PSC tree format: expected list of root nodes in 'results', "
            f"got {type(nodes).__name__}"
        )

    # Locate Service category root node
    service_root = None
    for node in nodes:
        node_id = str(node.get("id", "")).strip()
        if node_id.lower() == expected_category.lower():
            service_root = node
            break

    if not service_root:
        raise ValueError(f"Could not locate expected '{expected_category}' root node in PSC tree.")

    # Search for group_id inside Service subtree
    matches: list[tuple[dict[str, Any], list[str]]] = []

    def _search(curr_node: dict[str, Any], current_path: list[str]) -> None:
        c_id = str(curr_node.get("id", "")).strip()
        path = current_path + [c_id]
        if c_id.upper() == group_id.upper() and len(current_path) >= 1:
            matches.append((curr_node, path))
        for child in curr_node.get("children", []) or []:
            _search(child, path)

    _search(service_root, [])

    if not matches:
        raise ValueError(
            f"PSC Category '{group_id}' was not found under the '{expected_category}' branch. "
            f"Cannot resolve valid ancestry path for psc_codes.require."
        )

    if len(matches) > 1:
        raise ValueError(
            f"Ambiguous PSC Category '{group_id}': found {len(matches)} matching nodes under '{expected_category}'."
        )

    target_node, full_path = matches[0]
    description = target_node.get("description", "")
    desc_lower = description.lower()

    # Validate node description against April 2025 PSC Manual service scope
    if group_id.upper() == "D":
        if (
            "it and telecom" not in desc_lower
            and "information technology" not in desc_lower
            and "telecommunications" not in desc_lower
        ):
            raise ValueError(
                f"Resolved node 'D' description '{description}' does not match official "
                f"April 2025 PSC Manual designation for IT and Telecom service codes."
            )
    elif group_id.upper() == "R" and (
        "support" not in desc_lower
        and "professional" not in desc_lower
        and "administrative" not in desc_lower
        and "management" not in desc_lower
    ):
        raise ValueError(
            f"Resolved node 'R' description '{description}' does not match official "
            f"April 2025 PSC Manual designation for Category R Support services."
        )

    return {
        "node_id": target_node.get("id"),
        "description": description,
        "full_path": full_path,
        "manual_url": "https://www.acquisition.gov/sites/default/files/manual/PSC%20Manual%20April%202025.pdf",
        "manual_version": "April 2025",
    }


def build_stratum_filters(
    family_id: str,
    family_info: dict[str, Any],
    window_bounds: dict[str, str],
    date_type: str,
    award_type_codes: list[str],
    resolved_psc_paths: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Constructs request filter object for a single stratum query."""
    filters: dict[str, Any] = {
        "award_type_codes": list(award_type_codes),
        "time_period": [
            {
                "start_date": window_bounds["start_date"],
                "end_date": window_bounds["end_date"],
                "date_type": date_type,
            }
        ],
    }

    fam_type = family_info.get("type")
    if fam_type == "naics":
        code = str(family_info["code"]).strip()
        filters["naics_codes"] = [code]
    elif fam_type == "psc":
        if family_id not in resolved_psc_paths:
            raise KeyError(f"Resolved PSC path missing for family '{family_id}'")
        resolved = resolved_psc_paths[family_id]
        filters["psc_codes"] = {"require": [resolved["full_path"]]}
    else:
        raise ValueError(f"Unknown family type '{fam_type}' for family '{family_id}'")

    return filters


def compute_deterministic_page(
    seed: int, family_id: str, window_id: str, page_count: int
) -> int:
    """Computes a deterministic, stable page number within 1..page_count."""
    if page_count <= 1:
        return 1
    key = f"{seed}:{family_id}:{window_id}".encode()
    digest = hashlib.sha256(key).hexdigest()
    return (int(digest, 16) % page_count) + 1


def deduplicate_awards(
    raw_rows: list[dict[str, Any]], hard_cap: int = 400
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """
    Deduplicates award rows across queries using internal_id when present.
    If internal_id is missing, flags and preserves record without merging on weak match.
    Enforces the hard cap on unique records.
    """
    dedup_map: dict[str, dict[str, Any]] = {}
    missing_id_records: list[dict[str, Any]] = []
    total_raw_rows = len(raw_rows)
    overlaps = 0

    for row in raw_rows:
        stratum_query = row.get("_stratum_query_id", "unknown")
        stratum_fam = row.get("_stratum_family_id", "unknown")
        stratum_win = row.get("_stratum_window_id", "unknown")

        internal_id = row.get("internal_id")
        has_internal_id = internal_id is not None and str(internal_id).strip() != ""

        if not has_internal_id:
            rec = {k: v for k, v in row.items() if not k.startswith("_")}
            rec["source_queries"] = [stratum_query]
            rec["source_families"] = [stratum_fam]
            rec["source_windows"] = [stratum_win]
            rec["membership_count"] = 1
            rec["missing_internal_id"] = True
            missing_id_records.append(rec)
        else:
            key = str(internal_id)
            if key not in dedup_map:
                rec = {k: v for k, v in row.items() if not k.startswith("_")}
                rec["source_queries"] = [stratum_query]
                rec["source_families"] = [stratum_fam]
                rec["source_windows"] = [stratum_win]
                rec["membership_count"] = 1
                rec["missing_internal_id"] = False
                dedup_map[key] = rec
            else:
                overlaps += 1
                existing = dedup_map[key]
                if stratum_query not in existing["source_queries"]:
                    existing["source_queries"].append(stratum_query)
                if stratum_fam not in existing["source_families"]:
                    existing["source_families"].append(stratum_fam)
                if stratum_win not in existing["source_windows"]:
                    existing["source_windows"].append(stratum_win)
                existing["membership_count"] = len(existing["source_queries"])

    unique_awards = list(dedup_map.values()) + missing_id_records

    if len(unique_awards) > hard_cap:
        raise ValueError(
            f"Hard cap exceeded: {len(unique_awards)} unique awards exceeds cap of {hard_cap}."
        )

    summary = {
        "total_raw_rows": total_raw_rows,
        "total_unique_awards": len(unique_awards),
        "cross_query_overlaps": overlaps,
        "missing_internal_id_count": len(missing_id_records),
    }
    return unique_awards, summary


def select_detail_awards(
    unique_awards: list[dict[str, Any]],
    max_awards: int = 30,
    seed: int = 42,
) -> list[dict[str, Any]]:
    """
    Deterministically selects up to max_awards across inclusion families and windows.
    Uses ONLY record identifiers and stratum memberships — NOT supplier/recipient identity.
    """
    if not unique_awards or max_awards <= 0:
        return []

    # Sort awards deterministically by stable record identifiers
    def sort_key(a: dict[str, Any]) -> str:
        gen_id = str(a.get("generated_internal_id") or "")
        int_id = str(a.get("internal_id") or "")
        awd_id = str(a.get("Award ID") or "")
        return f"{gen_id}|{int_id}|{awd_id}"

    sorted_awards = sorted(unique_awards, key=sort_key)

    # Group awards by their primary stratum query
    grouped_by_query: dict[str, list[dict[str, Any]]] = {}
    for awd in sorted_awards:
        primary_query = awd.get("source_queries", ["default"])[0]
        grouped_by_query.setdefault(primary_query, []).append(awd)

    # Round-robin selection across query strata to balance families and windows
    selected: list[dict[str, Any]] = []
    selected_internal_ids: set[str] = set()
    query_keys = sorted(grouped_by_query.keys())

    # Deterministic rotation based on seed
    shift = seed % len(query_keys) if query_keys else 0
    ordered_keys = query_keys[shift:] + query_keys[:shift]

    round_idx = 0
    while len(selected) < min(max_awards, len(sorted_awards)):
        progress = False
        for qk in ordered_keys:
            stratum_list = grouped_by_query[qk]
            if round_idx < len(stratum_list):
                candidate = stratum_list[round_idx]
                cid = str(candidate.get("internal_id") or candidate.get("generated_internal_id"))
                if cid not in selected_internal_ids:
                    selected.append(candidate)
                    selected_internal_ids.add(cid)
                    progress = True
                    if len(selected) >= max_awards:
                        break
        if not progress:
            break
        round_idx += 1

    return selected[:max_awards]


def atomic_write_json(file_path: Path, data: Any) -> None:
    """Writes JSON payload atomically using a temporary file."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = file_path.with_suffix(file_path.suffix + ".tmp")
    with open(temp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    temp_path.replace(file_path)


def atomic_write_csv(file_path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    """Writes CSV rows atomically using a temporary file."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = file_path.with_suffix(file_path.suffix + ".tmp")
    with open(temp_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    temp_path.replace(file_path)


def print_dry_run_plan(
    config: dict[str, Any],
    run_date_utc: datetime | None = None,
) -> None:
    """Prints the comprehensive dry-run sample query plan without making network requests."""
    resolved_windows = resolve_date_windows(config["date_windows"], run_date_utc)
    families = config["inclusion_families"]
    sampling = config["sampling_parameters"]
    paths = config["paths"]
    date_type = config.get("date_semantics", {}).get("date_type", "new_awards_only")

    print("=" * 80)
    print("USAspending Sample Contract Data Acquisition -- DRY RUN PLAN")
    print("=" * 80)
    print("Notice: Dry run mode active. No network requests will be executed.")
    print("To execute download, run with: --confirm-sample-download\n")

    print("OFFICIAL SOURCE CONTRACTS:")
    for name, url in config.get("official_sources", {}).items():
        print(f"  - {name}: {url}")
    print()

    print("DATE SEMANTICS & WINDOWS:")
    print(f"  Date Filter Type: {date_type} (selects awards with base transaction date in window)")
    for win_id, bounds in resolved_windows.items():
        print(f"  - {win_id}: {bounds['start_date']} to {bounds['end_date']}")
    print()

    print("INCLUSION FAMILIES (4 independent inclusion families):")
    for fam_id, f_info in families.items():
        print(f"  - {fam_id}: {f_info.get('label')}")
        if f_info.get("type") == "psc":
            print(f"    Target category: {f_info.get('expected_category')} | Manual: {f_info.get('manual_version')}")
    print()

    print("PLANNED STRATA MATRIX (16 queries max = 4 families x 4 windows):")
    stratum_count = 0
    for fam_id, f_info in families.items():
        for win_id, bounds in resolved_windows.items():
            stratum_count += 1
            fam_desc = f_info.get("code") or f"Group {f_info.get('group_id')}"
            print(
                f"  [{stratum_count:02d}] Stratum: {fam_id}__{win_id} | "
                f"Family: {fam_desc} | Bounds: {bounds['start_date']}..{bounds['end_date']}"
            )
    print()

    print("SAMPLING STRATEGY & BOUNDS:")
    print(f"  Seed: {sampling.get('seed')}")
    print(f"  Stratum target rows: up to {sampling.get('target_rows_per_stratum')}")
    print(f"  Hard cap unique awards: {sampling.get('hard_cap_unique_awards')}")
    print(f"  Detail sample award cap: {sampling.get('detail_sample_award_cap')}")
    print(f"  Transaction page 1 limit: {sampling.get('transaction_page_limit')} rows")
    print(f"  Sort field / order: {sampling.get('award_sort_field')} ({sampling.get('award_sort_order')})")
    print("  Page selection strategy:")
    print("    1. Call spending_by_award_count with stratum filters.")
    print("    2. If contracts == 0: skip stratum.")
    print("    3. If contracts > 0: page_count = ceil(contracts / target_rows_per_stratum).")
    print("    4. Deterministic page = (hash(seed:family:window) % page_count) + 1.")
    print("    5. If selected page returns 0 rows: mark discrepancy/incomplete and fail safely without fallback.")
    print("  Note: This is a bounded exploratory sample, not a statistically representative sample.\n")

    print("PLANNED OUTPUT PATHS:")
    print(f"  Raw data directory: {paths.get('raw_data_dir')}")
    print(f"  Sample awards CSV: {paths.get('sample_awards_csv')}")
    print(f"  Sample transactions CSV: {paths.get('sample_transactions_csv')}")
    print(f"  Query manifest: {paths.get('manifest_path')}")
    print(f"  Profile report: {paths.get('profile_report_path')}")
    print("=" * 80)


def execute_sample_download(
    config: dict[str, Any],
    session: requests.Session | None = None,
    run_date_utc: datetime | None = None,
) -> dict[str, Any]:
    """
    Executes the confirmed sample data download from USAspending API.
    Enforces validation, hard caps, bounded retries, and atomic writes.
    """
    if run_date_utc is None:
        run_date_utc = datetime.now(timezone.utc)
    retrieved_at_utc = run_date_utc.strftime("%Y-%m-%dT%H:%M:%SZ")

    if session is None:
        session = requests.Session()

    endpoints = config["api_endpoints"]
    families = config["inclusion_families"]
    date_windows_cfg = config["date_windows"]
    date_type = config.get("date_semantics", {}).get("date_type", "new_awards_only")
    award_types = config["award_type_codes"]
    award_fields = config["award_fields"]
    sampling = config["sampling_parameters"]
    http_cfg = config.get("http_policy", {})
    paths = config["paths"]

    timeout = http_cfg.get("timeout_seconds", 30)
    max_retries = http_cfg.get("max_retries", 3)
    backoff = http_cfg.get("backoff_factor", 1.5)
    retry_statuses = set(http_cfg.get("retry_status_codes", [429, 500, 502, 503, 504]))

    manifest_path = Path(paths["manifest_path"])

    # Base manifest initialization
    manifest: dict[str, Any] = {
        "manifest_version": "1.0.0",
        "run_status": "in_progress",
        "retrieved_at_utc": retrieved_at_utc,
        "config_version": config.get("version", "1.0.0"),
        "official_sources": config.get("official_sources", {}),
        "date_semantics": {
            "date_type": date_type,
            "definition": "Selects awards whose base transaction date falls within the requested bounds",
        },
        "sampling_limits": {
            "strata_count_max": len(families) * len(date_windows_cfg),
            "target_rows_per_stratum": sampling.get("target_rows_per_stratum", 25),
            "hard_cap_unique_awards": sampling.get("hard_cap_unique_awards", 400),
            "detail_sample_award_cap": sampling.get("detail_sample_award_cap", 30),
            "transaction_page_limit": sampling.get("transaction_page_limit", 100),
        },
        "psc_resolution": {},
        "queries": [],
        "deduplication_summary": {},
        "transaction_detail_summary": {},
        "api_warnings": [],
        "errors": [],
    }

    try:
        # Step 1: Resolve UTC date bounds
        resolved_windows = resolve_date_windows(date_windows_cfg, run_date_utc)

        # Step 2: Fetch and validate PSC filter tree
        psc_tree_url = endpoints["psc_tree"]
        psc_resp = request_with_retry(
            session=session,
            method="GET",
            url=psc_tree_url,
            max_retries=max_retries,
            backoff_factor=backoff,
            timeout=timeout,
            retry_statuses=retry_statuses,
        )
        tree_json = psc_resp.json()

        resolved_psc_paths: dict[str, dict[str, Any]] = {}
        for fam_id, f_info in families.items():
            if f_info.get("type") == "psc":
                group_id = f_info["group_id"]
                res = resolve_psc_family_path(
                    tree_data=tree_json,
                    group_id=group_id,
                    expected_category=f_info.get("expected_category", "Service"),
                )
                resolved_psc_paths[fam_id] = res
                manifest["psc_resolution"][fam_id] = res

        # Step 3: Run stratum queries
        raw_counts_payloads: list[dict[str, Any]] = []
        raw_results_payloads: list[dict[str, Any]] = []
        collected_award_rows: list[dict[str, Any]] = []

        target_stratum_rows = sampling.get("target_rows_per_stratum", 25)
        seed = sampling.get("seed", 42)
        sort_field = sampling.get("award_sort_field", "Award Amount")
        sort_order = sampling.get("award_sort_order", "desc")

        for fam_id, f_info in families.items():
            for win_id, bounds in resolved_windows.items():
                query_id = f"{fam_id}__{win_id}"
                stratum_filters = build_stratum_filters(
                    family_id=fam_id,
                    family_info=f_info,
                    window_bounds=bounds,
                    date_type=date_type,
                    award_type_codes=award_types,
                    resolved_psc_paths=resolved_psc_paths,
                )

                # 3a. Call Spending by Award Count endpoint
                count_url = endpoints["spending_by_award_count"]
                count_resp = request_with_retry(
                    session=session,
                    method="POST",
                    url=count_url,
                    json={"filters": stratum_filters},
                    max_retries=max_retries,
                    backoff_factor=backoff,
                    timeout=timeout,
                    retry_statuses=retry_statuses,
                )
                try:
                    count_json = count_resp.json()
                except Exception as e:
                    raise ValueError(
                        f"Count endpoint for stratum '{query_id}' returned invalid JSON: {e}"
                    ) from e

                raw_counts_payloads.append({"query_id": query_id, "response": count_json})

                if not isinstance(count_json, dict) or not isinstance(count_json.get("results"), dict):
                    raise TypeError(
                        f"Malformed count response shape for stratum '{query_id}': expected JSON object with 'results' dict, "
                        f"got {type(count_json).__name__}"
                    )

                contracts_count = count_json["results"].get("contracts")
                if isinstance(contracts_count, bool) or not isinstance(contracts_count, int) or contracts_count < 0:
                    raise ValueError(
                        f"Malformed count response for stratum '{query_id}': expected non-negative integer "
                        f"for 'contracts', got {contracts_count!r}"
                    )

                query_entry: dict[str, Any] = {
                    "query_id": query_id,
                    "family_id": fam_id,
                    "window_id": win_id,
                    "start_date": bounds["start_date"],
                    "end_date": bounds["end_date"],
                    "date_type": date_type,
                    "filters": stratum_filters,
                    "contracts_count": contracts_count,
                    "page_count": 0,
                    "selected_page": None,
                    "seed": seed,
                    "sort_field": sort_field,
                    "sort_order": sort_order,
                    "returned_rows": 0,
                    "skipped": False,
                    "discrepancy_empty_selected_page": False,
                    "status": "pending",
                }

                if contracts_count == 0:
                    query_entry["skipped"] = True
                    query_entry["status"] = "skipped_zero_contracts"
                    manifest["queries"].append(query_entry)
                    continue

                page_count = math.ceil(contracts_count / target_stratum_rows)
                selected_page = compute_deterministic_page(
                    seed=seed, family_id=fam_id, window_id=win_id, page_count=page_count
                )
                query_entry["page_count"] = page_count
                query_entry["selected_page"] = selected_page

                # 3b. Call Spending by Award endpoint
                award_search_url = endpoints["spending_by_award"]
                award_req_body = {
                    "filters": stratum_filters,
                    "fields": award_fields,
                    "page": selected_page,
                    "limit": target_stratum_rows,
                    "sort": sort_field,
                    "order": sort_order,
                }

                search_resp = request_with_retry(
                    session=session,
                    method="POST",
                    url=award_search_url,
                    json=award_req_body,
                    max_retries=max_retries,
                    backoff_factor=backoff,
                    timeout=timeout,
                    retry_statuses=retry_statuses,
                )
                try:
                    search_json = search_resp.json()
                except Exception as e:
                    raise ValueError(
                        f"Award search endpoint for stratum '{query_id}' returned invalid JSON: {e}"
                    ) from e

                if not isinstance(search_json, dict) or not isinstance(search_json.get("results"), list):
                    raise TypeError(
                        f"Malformed award search response shape for stratum '{query_id}': expected JSON object with 'results' list, "
                        f"got {type(search_json).__name__}"
                    )

                res_rows = search_json["results"]

                raw_results_payloads.append(
                    {
                        "query_id": query_id,
                        "request": award_req_body,
                        "response": search_json,
                    }
                )

                # Halt safely on empty results without fallback per sampling integrity policy
                if len(res_rows) == 0:
                    query_entry["discrepancy_empty_selected_page"] = True
                    query_entry["status"] = "discrepancy_empty_selected_page"
                    query_entry["returned_rows"] = 0
                    manifest["queries"].append(query_entry)
                    raise RuntimeError(
                        f"Selected page {selected_page} returned 0 results despite positive contracts count "
                        f"({contracts_count}) in stratum '{query_id}'. Failing safely without fallback per sampling integrity policy."
                    )

                query_entry["status"] = "success"
                query_entry["returned_rows"] = len(res_rows)
                manifest["queries"].append(query_entry)

                for r in res_rows:
                    annotated = dict(r)
                    annotated["_stratum_query_id"] = query_id
                    annotated["_stratum_family_id"] = fam_id
                    annotated["_stratum_window_id"] = win_id
                    collected_award_rows.append(annotated)

        # Step 4: Union, deduplicate, and enforce hard cap
        unique_awards, dedup_summary = deduplicate_awards(
            raw_rows=collected_award_rows,
            hard_cap=sampling.get("hard_cap_unique_awards", 400),
        )
        manifest["deduplication_summary"] = dedup_summary

        # Step 5: Detail transaction sampling (max 30 awards)
        detail_cap = sampling.get("detail_sample_award_cap", 30)
        selected_detail_awards = select_detail_awards(
            unique_awards=unique_awards,
            max_awards=detail_cap,
            seed=seed,
        )

        tx_history_payloads: list[dict[str, Any]] = []
        flattened_tx_rows: list[dict[str, Any]] = []

        tx_summary = {
            "target_awards": len(selected_detail_awards),
            "requests_attempted": 0,
            "success_with_transactions": 0,
            "success_zero_transactions": 0,
            "failures": 0,
            "missing_unusable_id_count": 0,
            "truncated_count": 0,
            "no_next_page_count": 0,
            "unknown_completeness_count": 0,
        }

        tx_url = endpoints["transactions"]
        tx_page_limit = sampling.get("transaction_page_limit", 100)
        tx_sort_field = sampling.get("transaction_sort_field", "action_date")
        tx_sort_order = sampling.get("transaction_sort_order", "asc")

        for awd in selected_detail_awards:
            gen_id = awd.get("generated_internal_id")
            int_id = awd.get("internal_id")
            disp_id = awd.get("Award ID")

            # Prefer generated_internal_id per API contract, fallback to internal_id
            if gen_id and str(gen_id).strip():
                lookup_id = str(gen_id).strip()
                id_type = "generated_internal_id"
            elif int_id is not None and str(int_id).strip():
                lookup_id = str(int_id).strip()
                id_type = "internal_id"
            else:
                lookup_id = None
                id_type = "none"

            if lookup_id is None:
                tx_summary["missing_unusable_id_count"] += 1
                tx_history_payloads.append(
                    {
                        "award_display_id": disp_id,
                        "status": "missing_unusable_id",
                        "has_next": None,
                        "history_completeness": "unknown",
                        "error": "Award lacks both generated_internal_id and internal_id",
                    }
                )
                continue

            tx_summary["requests_attempted"] += 1
            tx_req_body = {
                "award_id": lookup_id,
                "page": 1,
                "limit": tx_page_limit,
                "sort": tx_sort_field,
                "order": tx_sort_order,
            }

            try:
                tx_resp = request_with_retry(
                    session=session,
                    method="POST",
                    url=tx_url,
                    json=tx_req_body,
                    max_retries=max_retries,
                    backoff_factor=backoff,
                    timeout=timeout,
                    retry_statuses=retry_statuses,
                )
                try:
                    tx_json = tx_resp.json()
                except Exception as e:
                    raise ValueError(f"Transaction endpoint returned invalid JSON: {e}") from e

                if not isinstance(tx_json, dict) or not isinstance(tx_json.get("results"), list):
                    raise TypeError("Malformed transaction response: expected JSON object with 'results' list.")

                tx_results = tx_json["results"]
                page_meta = tx_json.get("page_metadata")

                # Defensive page_metadata inspection
                if isinstance(page_meta, dict) and "hasNext" in page_meta and isinstance(page_meta["hasNext"], bool):
                    if page_meta["hasNext"] is True:
                        has_next = True
                        completeness = "truncated"
                        tx_summary["truncated_count"] += 1
                    else:
                        has_next = False
                        completeness = "no_next_page"
                        tx_summary["no_next_page_count"] += 1
                else:
                    has_next = None
                    completeness = "unknown"
                    tx_summary["unknown_completeness_count"] += 1

                if len(tx_results) > 0:
                    tx_summary["success_with_transactions"] += 1
                    if completeness == "truncated":
                        status = "success_with_transactions_truncated"
                    elif completeness == "no_next_page":
                        status = "success_with_transactions_no_next_page"
                    else:
                        status = "success_with_transactions_unknown_completeness"
                else:
                    tx_summary["success_zero_transactions"] += 1
                    status = "success_zero_transactions"

                tx_history_payloads.append(
                    {
                        "award_id_lookup": lookup_id,
                        "id_type_used": id_type,
                        "award_display_id": disp_id,
                        "status": status,
                        "has_next": has_next,
                        "history_completeness": completeness,
                        "returned_transactions": len(tx_results),
                        "response": tx_json,
                    }
                )

                for tx in tx_results:
                    tx_row = {
                        "award_id_lookup": lookup_id,
                        "id_type_used": id_type,
                        "award_internal_id": int_id,
                        "award_generated_internal_id": gen_id,
                        "award_display_id": disp_id,
                        "transaction_id": tx.get("id") or tx.get("transaction_id"),
                        "action_date": tx.get("action_date"),
                        "action_type": tx.get("action_type"),
                        "action_type_description": tx.get("action_type_description"),
                        "modification_number": tx.get("modification_number"),
                        "description": tx.get("description"),
                        "federal_action_obligation": tx.get("federal_action_obligation"),
                        "face_value_loan_guarantee": tx.get("face_value_loan_guarantee"),
                        "original_loan_subsidy_cost": tx.get("original_loan_subsidy_cost"),
                        "page_truncated": has_next if has_next is not None else "unknown",
                        "history_completeness": completeness,
                    }
                    flattened_tx_rows.append(tx_row)

            except (requests.RequestException, ValueError, KeyError) as e:
                tx_summary["failures"] += 1
                tx_history_payloads.append(
                    {
                        "award_id_lookup": lookup_id,
                        "id_type_used": id_type,
                        "award_display_id": disp_id,
                        "status": "request_failure",
                        "has_next": None,
                        "history_completeness": "unknown",
                        "error": str(e),
                    }
                )

        manifest["transaction_detail_summary"] = tx_summary

        # Step 6: Atomic file writing
        atomic_write_json(Path(paths["raw_award_counts"]), raw_counts_payloads)
        atomic_write_json(Path(paths["raw_award_results"]), raw_results_payloads)
        atomic_write_json(Path(paths["raw_transaction_history"]), tx_history_payloads)

        # Flatten award records for CSV
        csv_award_rows: list[dict[str, Any]] = []
        for awd in unique_awards:
            row_dict = dict(awd)
            row_dict["source_queries"] = ";".join(sorted(row_dict.get("source_queries", [])))
            row_dict["source_families"] = ";".join(sorted(row_dict.get("source_families", [])))
            row_dict["source_windows"] = ";".join(sorted(row_dict.get("source_windows", [])))
            csv_award_rows.append(row_dict)

        award_csv_fieldnames = (
            ["internal_id"]
            + [f for f in award_fields if f != "internal_id"]
            + [
                "source_queries",
                "source_families",
                "source_windows",
                "membership_count",
                "missing_internal_id",
            ]
        )
        atomic_write_csv(Path(paths["sample_awards_csv"]), award_csv_fieldnames, csv_award_rows)

        tx_csv_fieldnames = [
            "award_id_lookup",
            "id_type_used",
            "award_internal_id",
            "award_generated_internal_id",
            "award_display_id",
            "transaction_id",
            "action_date",
            "action_type",
            "action_type_description",
            "modification_number",
            "description",
            "federal_action_obligation",
            "face_value_loan_guarantee",
            "original_loan_subsidy_cost",
            "page_truncated",
            "history_completeness",
        ]
        atomic_write_csv(Path(paths["sample_transactions_csv"]), tx_csv_fieldnames, flattened_tx_rows)

        # Mark run as complete
        manifest["run_status"] = "complete"
        atomic_write_json(manifest_path, manifest)

        print("\nDownload execution completed successfully.")
        print(f"Unique awards acquired: {len(unique_awards)}")
        print(f"Detail transaction histories fetched: {tx_summary['requests_attempted']}")
        print(f"Output files saved under: {paths['raw_data_dir']}")
        print(f"Manifest updated at: {manifest_path}")

        return manifest

    except Exception as e:
        manifest["run_status"] = "incomplete"
        manifest["errors"].append(str(e))
        try:
            atomic_write_json(manifest_path, manifest)
        except OSError:
            pass
        raise


def main() -> None:
    parser = argparse.ArgumentParser(
        description="USAspending Sample Contract Data Acquisition Script"
    )
    parser.add_argument(
        "--config",
        default="config/sample_data_config.yaml",
        help="Path to YAML configuration file",
    )
    parser.add_argument(
        "--confirm-sample-download",
        action="store_true",
        help="Explicit confirmation required to execute API requests and data writes",
    )
    args = parser.parse_args()

    config = load_config(args.config)

    if not args.confirm_sample_download:
        print_dry_run_plan(config)
        sys.exit(0)

    execute_sample_download(config)


if __name__ == "__main__":
    main()
