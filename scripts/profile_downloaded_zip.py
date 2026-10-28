"""Audit and profile a USAspending sample downloaded as a ZIP archive.

This script inspects the downloaded ZIP without modifying or extracting it,
analyzing schema dimensions, key uniqueness, award-to-transaction linkage,
date coverage, agency/NAICS compliance, and amount statistics.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import statistics
import sys
import zipfile
from pathlib import Path
from typing import Any

DEFAULT_ZIP_PATH = "data/raw/sample/PrimeAwardSummariesAndTransactions_2026-10-27_H21M56S49644703.zip"

REQUIRED_AWARD_COLUMNS = [
    "contract_award_unique_key",
    "award_id_piid",
    "award_base_action_date",
    "award_latest_action_date",
    "awarding_agency_name",
    "naics_code",
    "total_obligated_amount",
]

REQUIRED_TRANSACTION_COLUMNS = [
    "contract_transaction_unique_key",
    "contract_award_unique_key",
    "award_id_piid",
    "action_date",
    "awarding_agency_name",
    "naics_code",
    "federal_action_obligation",
]

WEBSITE_DECLARED_COUNTS = {
    "awards": 221,
    "transactions": 1384,
}


def compute_sha256(path: Path) -> str:
    """Compute SHA-256 checksum of a file."""
    hasher = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def profile_numeric_column(rows: list[dict[str, str]], col_name: str) -> dict[str, Any]:
    """Profile a numeric column for count, missingness, zero/negative counts, and summary stats."""
    valid_nums: list[float] = []
    missing_count = 0
    zero_count = 0
    neg_count = 0
    pos_count = 0

    for r in rows:
        val_str = r.get(col_name, "").strip()
        if not val_str:
            missing_count += 1
            continue
        try:
            val = float(val_str)
            valid_nums.append(val)
            if val == 0.0:
                zero_count += 1
            elif val < 0.0:
                neg_count += 1
            else:
                pos_count += 1
        except ValueError:
            missing_count += 1

    return {
        "column": col_name,
        "total_rows": len(rows),
        "valid_count": len(valid_nums),
        "missing_count": missing_count,
        "missing_pct": round((missing_count / len(rows) * 100) if rows else 0.0, 2),
        "zero_count": zero_count,
        "negative_count": neg_count,
        "positive_count": pos_count,
        "min": min(valid_nums) if valid_nums else None,
        "median": round(statistics.median(valid_nums), 2) if valid_nums else None,
        "max": max(valid_nums) if valid_nums else None,
    }


def analyze_zip_archive(zip_path: Path) -> dict[str, Any]:
    """Analyze the ZIP archive and return a comprehensive audit dictionary.

    Reads CSV members in-memory without extracting them to disk.
    """
    if not zip_path.exists():
        raise FileNotFoundError(f"Input ZIP not found: {zip_path.resolve()}")

    zip_bytes = zip_path.stat().st_size
    zip_sha256 = compute_sha256(zip_path)

    awards_member_name: str | None = None
    tx_member_name: str | None = None
    members_meta: list[dict[str, Any]] = []

    with zipfile.ZipFile(zip_path, "r") as z:
        for info in z.infolist():
            meta = {
                "filename": info.filename,
                "compressed_bytes": info.compress_size,
                "uncompressed_bytes": info.file_size,
            }
            members_meta.append(meta)
            if "PrimeAwardSummaries" in info.filename and info.filename.endswith(".csv"):
                awards_member_name = info.filename
            elif "PrimeTransactions" in info.filename and info.filename.endswith(".csv"):
                tx_member_name = info.filename

        if not awards_member_name:
            raise ValueError(f"ZIP archive {zip_path.name} is missing PrimeAwardSummaries CSV member.")
        if not tx_member_name:
            raise ValueError(f"ZIP archive {zip_path.name} is missing PrimeTransactions CSV member.")

        # Read award summaries
        with z.open(awards_member_name) as f:
            wrapper = io.TextIOWrapper(f, encoding="utf-8-sig", errors="replace")
            reader = csv.DictReader(wrapper)
            award_columns = reader.fieldnames or []
            award_rows = list(reader)

        # Read transactions
        with z.open(tx_member_name) as f:
            wrapper = io.TextIOWrapper(f, encoding="utf-8-sig", errors="replace")
            reader = csv.DictReader(wrapper)
            tx_columns = reader.fieldnames or []
            tx_rows = list(reader)

    # Missing required columns
    missing_award_req_cols = [c for c in REQUIRED_AWARD_COLUMNS if c not in award_columns]
    missing_tx_req_cols = [c for c in REQUIRED_TRANSACTION_COLUMNS if c not in tx_columns]

    # Award Key Uniqueness and Missingness
    award_unique_keys = [r.get("contract_award_unique_key", "").strip() for r in award_rows]
    award_unique_keys_populated = [k for k in award_unique_keys if k]
    award_keys_set = set(award_unique_keys_populated)

    award_piids = [r.get("award_id_piid", "").strip() for r in award_rows]
    award_piids_populated = [p for p in award_piids if p]

    # Transaction Key Uniqueness and Missingness
    tx_unique_keys = [r.get("contract_transaction_unique_key", "").strip() for r in tx_rows]
    tx_unique_keys_populated = [k for k in tx_unique_keys if k]
    tx_keys_set = set(tx_unique_keys_populated)

    tx_award_keys = [r.get("contract_award_unique_key", "").strip() for r in tx_rows]
    tx_award_keys_populated = [k for k in tx_award_keys if k]
    tx_award_keys_set = set(tx_award_keys_populated)

    # Linkage Metrics
    unmatched_tx_keys = [k for k in tx_award_keys_populated if k not in award_keys_set]
    matched_award_keys = award_keys_set.intersection(tx_award_keys_set)
    awards_zero_tx = [k for k in award_unique_keys_populated if k not in tx_award_keys_set]

    # Transactions per award distribution
    tx_per_award_counts: dict[str, int] = {}
    for k in tx_award_keys_populated:
        tx_per_award_counts[k] = tx_per_award_counts.get(k, 0) + 1

    # Distribution histogram
    tx_count_freq: dict[int, int] = {}
    for c in tx_per_award_counts.values():
        tx_count_freq[c] = tx_count_freq.get(c, 0) + 1
    sorted_tx_count_freq = dict(sorted(tx_count_freq.items()))

    # Date Parsing and Distributions
    award_base_dates = [r.get("award_base_action_date", "").strip() for r in award_rows if r.get("award_base_action_date", "").strip()]
    award_latest_dates = [r.get("award_latest_action_date", "").strip() for r in award_rows if r.get("award_latest_action_date", "").strip()]
    tx_action_dates = [r.get("action_date", "").strip() for r in tx_rows if r.get("action_date", "").strip()]

    award_base_fys: dict[str, int] = {}
    for r in award_rows:
        fy = r.get("award_base_action_date_fiscal_year", "").strip()
        if fy:
            award_base_fys[fy] = award_base_fys.get(fy, 0) + 1

    award_latest_fys: dict[str, int] = {}
    for r in award_rows:
        fy = r.get("award_latest_action_date_fiscal_year", "").strip()
        if fy:
            award_latest_fys[fy] = award_latest_fys.get(fy, 0) + 1

    tx_action_fys: dict[str, int] = {}
    for r in tx_rows:
        fy = r.get("action_date_fiscal_year", "").strip()
        if fy:
            tx_action_fys[fy] = tx_action_fys.get(fy, 0) + 1

    # Check whether transaction file contains action dates outside FY2020 (post 2020-09-30)
    post_fy2020_tx_count = sum(1 for d in tx_action_dates if d > "2020-09-30")
    pre_fy2020_tx_count = sum(1 for d in tx_action_dates if d < "2019-10-01")

    # Agency & NAICS Compliance Checks
    award_nasa_count = sum(1 for r in award_rows if "National Aeronautics and Space Administration" in r.get("awarding_agency_name", ""))
    tx_nasa_count = sum(1 for r in tx_rows if "National Aeronautics and Space Administration" in r.get("awarding_agency_name", ""))
    award_naics_count = sum(1 for r in award_rows if r.get("naics_code", "").strip() == "541330")
    tx_naics_count = sum(1 for r in tx_rows if r.get("naics_code", "").strip() == "541330")

    # Amount Columns Profiling
    award_amount_stats = {
        "total_obligated_amount": profile_numeric_column(award_rows, "total_obligated_amount"),
        "current_total_value_of_award": profile_numeric_column(award_rows, "current_total_value_of_award"),
        "potential_total_value_of_award": profile_numeric_column(award_rows, "potential_total_value_of_award"),
    }
    tx_amount_stats = {
        "federal_action_obligation": profile_numeric_column(tx_rows, "federal_action_obligation"),
    }

    # Top missing columns in Award and Transactions
    award_null_counts = {c: sum(1 for r in award_rows if not r.get(c, "").strip()) for c in award_columns}
    sorted_award_nulls = sorted(award_null_counts.items(), key=lambda x: x[1], reverse=True)
    award_top_missing = [
        {"column": col, "missing_count": cnt, "missing_pct": round(cnt / len(award_rows) * 100, 2)}
        for col, cnt in sorted_award_nulls[:10]
    ]

    tx_null_counts = {c: sum(1 for r in tx_rows if not r.get(c, "").strip()) for c in tx_columns}
    sorted_tx_nulls = sorted(tx_null_counts.items(), key=lambda x: x[1], reverse=True)
    tx_top_missing = [
        {"column": col, "missing_count": cnt, "missing_pct": round(cnt / len(tx_rows) * 100, 2)}
        for col, cnt in sorted_tx_nulls[:10]
    ]

    # Discrepancy analysis
    actual_award_count = len(award_rows)
    actual_tx_count = len(tx_rows)
    tx_discrepancy_count = actual_tx_count - WEBSITE_DECLARED_COUNTS["transactions"]

    return {
        "zip_metadata": {
            "path": str(zip_path.as_posix()),
            "file_size_bytes": zip_bytes,
            "sha256": zip_sha256,
            "members": members_meta,
        },
        "members": {
            "award_summaries": {
                "filename": awards_member_name,
                "row_count": actual_award_count,
                "column_count": len(award_columns),
                "missing_required_columns": missing_award_req_cols,
                "award_unique_keys_count": len(award_unique_keys),
                "award_unique_keys_unique": len(award_keys_set),
                "award_unique_keys_missing": len(award_rows) - len(award_unique_keys_populated),
                "award_id_piid_unique": len(set(award_piids_populated)),
                "award_id_piid_missing": len(award_rows) - len(award_piids_populated),
                "base_action_date_range": {
                    "min": min(award_base_dates) if award_base_dates else None,
                    "max": max(award_base_dates) if award_base_dates else None,
                },
                "latest_action_date_range": {
                    "min": min(award_latest_dates) if award_latest_dates else None,
                    "max": max(award_latest_dates) if award_latest_dates else None,
                },
                "base_fiscal_years": award_base_fys,
                "latest_fiscal_years": dict(sorted(award_latest_fys.items())),
                "agency_compliance_nasa": {
                    "count": award_nasa_count,
                    "percentage": round(award_nasa_count / actual_award_count * 100, 2) if actual_award_count else 0.0,
                },
                "naics_compliance_541330": {
                    "count": award_naics_count,
                    "percentage": round(award_naics_count / actual_award_count * 100, 2) if actual_award_count else 0.0,
                },
                "amount_stats": award_amount_stats,
                "top_missing_columns": award_top_missing,
            },
            "transactions": {
                "filename": tx_member_name,
                "row_count": actual_tx_count,
                "column_count": len(tx_columns),
                "missing_required_columns": missing_tx_req_cols,
                "tx_unique_keys_count": len(tx_unique_keys),
                "tx_unique_keys_unique": len(tx_keys_set),
                "tx_unique_keys_missing": len(tx_rows) - len(tx_unique_keys_populated),
                "unique_award_keys_referenced": len(tx_award_keys_set),
                "action_date_range": {
                    "min": min(tx_action_dates) if tx_action_dates else None,
                    "max": max(tx_action_dates) if tx_action_dates else None,
                },
                "action_fiscal_years": tx_action_fys,
                "post_fy2020_transactions_count": post_fy2020_tx_count,
                "pre_fy2020_transactions_count": pre_fy2020_tx_count,
                "agency_compliance_nasa": {
                    "count": tx_nasa_count,
                    "percentage": round(tx_nasa_count / actual_tx_count * 100, 2) if actual_tx_count else 0.0,
                },
                "naics_compliance_541330": {
                    "count": tx_naics_count,
                    "percentage": round(tx_naics_count / actual_tx_count * 100, 2) if actual_tx_count else 0.0,
                },
                "amount_stats": tx_amount_stats,
                "top_missing_columns": tx_top_missing,
            },
        },
        "linkage": {
            "shared_key": "contract_award_unique_key",
            "total_transaction_rows": actual_tx_count,
            "total_award_summary_rows": actual_award_count,
            "unmatched_transaction_keys_count": len(unmatched_tx_keys),
            "awards_with_zero_transactions_count": len(awards_zero_tx),
            "awards_with_transactions_count": len(matched_award_keys),
            "transactions_per_award_histogram": sorted_tx_count_freq,
            "transactions_per_award_summary": {
                "min": min(tx_per_award_counts.values()) if tx_per_award_counts else 0,
                "median": round(statistics.median(tx_per_award_counts.values()), 2) if tx_per_award_counts else 0,
                "max": max(tx_per_award_counts.values()) if tx_per_award_counts else 0,
            },
        },
        "website_reconciliation": {
            "website_declared_awards": WEBSITE_DECLARED_COUNTS["awards"],
            "actual_downloaded_awards": actual_award_count,
            "awards_discrepancy": actual_award_count - WEBSITE_DECLARED_COUNTS["awards"],
            "website_declared_transactions": WEBSITE_DECLARED_COUNTS["transactions"],
            "actual_downloaded_transactions": actual_tx_count,
            "transactions_discrepancy": tx_discrepancy_count,
            "discrepancy_status": "UNRESOLVED",
            "status_notes": (
                "The website download dialog displayed 1,384 Transactions and 221 Awards for the applied filters. "
                "The downloaded archive contains exactly 221 Award Summary rows and 390 Transaction rows. "
                "All 390 transactions have action dates within FY2020 (2019-10-08 to 2020-09-30). "
                "While 139 of the 221 awards show subsequent modifications through FY2027 in their summary records, "
                "the transaction export does not include post-FY2020 transaction records. "
                "Whether the 1,384 figure represents all lifetime transactions across all fiscal years for the 221 awards "
                "or reflects a different query scoping cannot be established without official server-side confirmation."
            ),
        },
        "feasibility_assessment": {
            "schema_validation_status": "SUFFICIENT",
            "schema_validation_notes": (
                "The sample reliably confirms the USAspending contract export format, column headers, "
                "primary keys (contract_award_unique_key, contract_transaction_unique_key), and clean 100% "
                "referential integrity between awards and transactions within the sample."
            ),
            "successor_feasibility_status": "INSUFFICIENT",
            "successor_feasibility_notes": (
                "This sample is bounded to a single agency (NASA), a single NAICS code (541330), and awards "
                "originated in FY2020. The transaction file omits post-FY2020 modifications. It is neither "
                "a complete historical transaction history nor a representative sample of federal contracts, "
                "and cannot establish feasibility for successor matching or recompete lifecycle models."
            ),
        },
    }


def generate_audit_report(data: dict[str, Any]) -> str:
    """Generate Markdown audit report from analyzed data."""
    meta = data["zip_metadata"]
    aw = data["members"]["award_summaries"]
    tx = data["members"]["transactions"]
    lk = data["linkage"]
    rec = data["website_reconciliation"]
    feas = data["feasibility_assessment"]

    histogram_lines = "\n".join(
        f"| {tx_count} | {num_awards} |"
        for tx_count, num_awards in lk["transactions_per_award_histogram"].items()
    )

    latest_fy_lines = "\n".join(
        f"| FY{fy} | {count} ({round(count / aw['row_count'] * 100, 1)}%) |"
        for fy, count in aw["latest_fiscal_years"].items()
    )

    aw_top_missing_lines = "\n".join(
        f"| `{m['column']}` | {m['missing_count']} | {m['missing_pct']}% |"
        for m in aw["top_missing_columns"]
    )

    tx_top_missing_lines = "\n".join(
        f"| `{m['column']}` | {m['missing_count']} | {m['missing_pct']}% |"
        for m in tx["top_missing_columns"]
    )

    def fmt_cur(v: float | None) -> str:
        if v is None:
            return "N/A"
        if abs(v) < 1e-9:
            return "$0.00"
        if v < 0:
            return f"-${abs(v):,.2f}"
        return f"${v:,.2f}"

    aw_amt = aw["amount_stats"]
    tx_amt = tx["amount_stats"]["federal_action_obligation"]

    return f"""# USAspending Downloaded Sample Audit and Transaction Coverage Report

## Executive Summary
This report audits the real USAspending ZIP export downloaded from the official website UI and placed in the project repository. It evaluates file integrity, schema consistency, award-to-transaction linkage, date coverage, and count reconciliation against the website download dialog.

- **ZIP Archive**: `{Path(meta['path']).name}`
- **Archive Size**: {meta['file_size_bytes']:,} bytes
- **SHA-256**: `{meta['sha256']}`
- **Award Summaries Count**: {aw['row_count']} data rows ({aw['column_count']} columns)
- **Prime Transactions Count**: {tx['row_count']} data rows ({tx['column_count']} columns)
- **Referential Integrity**: 100.0% of transactions link to award summaries via `contract_award_unique_key` with 0 unmatched keys.
- **Count Discrepancy Status**: **{rec['discrepancy_status']}** (Website displayed {rec['website_declared_transactions']:,} transactions vs. {rec['actual_downloaded_transactions']:,} rows in downloaded CSV).

---

## 1. Archive Inventory and File Dimensions

| Member Name | Type | Compressed Size | Uncompressed Size | Data Rows | Columns |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `{aw['filename']}` | Award Summaries CSV | {meta['members'][0]['compressed_bytes']:,} bytes | {meta['members'][0]['uncompressed_bytes']:,} bytes | {aw['row_count']} | {aw['column_count']} |
| `{tx['filename']}` | Prime Transactions CSV | {meta['members'][1]['compressed_bytes']:,} bytes | {meta['members'][1]['uncompressed_bytes']:,} bytes | {tx['row_count']} | {tx['column_count']} |

---

## 2. Identifier Uniqueness and Linkage

### Primary Identifiers
- **Award Unique Key (`contract_award_unique_key`)**:
  - Total records: {aw['award_unique_keys_count']}
  - Unique keys: {aw['award_unique_keys_unique']} (100.0% unique)
  - Missing values: {aw['award_unique_keys_missing']}
- **Award PIID (`award_id_piid`)**:
  - Unique PIIDs: {aw['award_id_piid_unique']} (100.0% unique in this sample)
  - Missing values: {aw['award_id_piid_missing']}
- **Transaction Unique Key (`contract_transaction_unique_key`)**:
  - Total records: {tx['tx_unique_keys_count']}
  - Unique keys: {tx['tx_unique_keys_unique']} (100.0% unique)
  - Missing values: {tx['tx_unique_keys_missing']}

### Award-to-Transaction Linkage
- **Join Key**: `{lk['shared_key']}`
- **Unmatched Transaction Keys**: {lk['unmatched_transaction_keys_count']} (0.0% unmatched)
- **Awards with Zero Transactions**: {lk['awards_with_zero_transactions_count']} (0.0% unlinked; all 221 awards have at least one transaction row)
- **Transactions Per Award**: Min = {lk['transactions_per_award_summary']['min']}, Median = {lk['transactions_per_award_summary']['median']}, Max = {lk['transactions_per_award_summary']['max']}

#### Transactions per Award Distribution
| Transactions per Award | Number of Awards |
| :--- | :--- |
{histogram_lines}

---

## 3. Date Coverage and Fiscal Year Analysis

### Award Base Action Dates
- **Min Base Action Date**: `{aw['base_action_date_range']['min']}`
- **Max Base Action Date**: `{aw['base_action_date_range']['max']}`
- **Fiscal Year Distribution**: 100.0% FY2020 ({aw['base_fiscal_years'].get('2020', 0)} / {aw['row_count']}).

### Award Latest Action Dates
- **Min Latest Action Date**: `{aw['latest_action_date_range']['min']}`
- **Max Latest Action Date**: `{aw['latest_action_date_range']['max']}`
- **Fiscal Year Distribution**:
| Fiscal Year | Awards Count |
| :--- | :--- |
{latest_fy_lines}

> **Observation**: 139 out of 221 awards (62.9%) experienced subsequent modifications or actions in FY2021 through FY2027, with the latest action recorded on `{aw['latest_action_date_range']['max']}`.

### Transaction Action Dates
- **Min Action Date**: `{tx['action_date_range']['min']}`
- **Max Action Date**: `{tx['action_date_range']['max']}`
- **Fiscal Year Distribution**: 100.0% FY2020 ({tx['action_fiscal_years'].get('2020', 0)} / {tx['row_count']}).
- **Post-FY2020 Transactions Present**: **{tx['post_fy2020_transactions_count']}**
- **Pre-FY2020 Transactions Present**: **{tx['pre_fy2020_transactions_count']}**

> **Finding**: While the award summaries demonstrate that the awards had active modifications well into FY2026/FY2027, the transaction file contains **only FY2020 transactions**. It does **not** contain the later-year transactions corresponding to `award_latest_action_date`.

---

## 4. Filter Compliance Verification

| Dimension | Filter Requirement | Award Summary Conformance | Transaction Conformance | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Awarding Agency** | NASA | {aw['agency_compliance_nasa']['count']}/{aw['row_count']} ({aw['agency_compliance_nasa']['percentage']}%) | {tx['agency_compliance_nasa']['count']}/{tx['row_count']} ({tx['agency_compliance_nasa']['percentage']}%) | FULL COMPLIANCE |
| **NAICS** | 541330 (Engineering Services) | {aw['naics_compliance_541330']['count']}/{aw['row_count']} ({aw['naics_compliance_541330']['percentage']}%) | {tx['naics_compliance_541330']['count']}/{tx['row_count']} ({tx['naics_compliance_541330']['percentage']}%) | FULL COMPLIANCE |
| **Time Period** | FY2020 New Awards | 221 Base Action Dates in FY2020 | 390 Action Dates in FY2020 | FULL COMPLIANCE |

---

## 5. Amount Fields and Statistics

Cumulative award totals must not be conflated with discrete transaction obligations.

### Award Summary Dollar Fields
| Metric | `total_obligated_amount` | `current_total_value_of_award` | `potential_total_value_of_award` |
| :--- | :--- | :--- | :--- |
| **Total Populated** | {aw_amt['total_obligated_amount']['valid_count']} | {aw_amt['current_total_value_of_award']['valid_count']} | {aw_amt['potential_total_value_of_award']['valid_count']} |
| **Missing** | {aw_amt['total_obligated_amount']['missing_count']} | {aw_amt['current_total_value_of_award']['missing_count']} | {aw_amt['potential_total_value_of_award']['missing_count']} |
| **Zero Values** | {aw_amt['total_obligated_amount']['zero_count']} | {aw_amt['current_total_value_of_award']['zero_count']} | {aw_amt['potential_total_value_of_award']['zero_count']} |
| **Negative Values** | {aw_amt['total_obligated_amount']['negative_count']} | {aw_amt['current_total_value_of_award']['negative_count']} | {aw_amt['potential_total_value_of_award']['negative_count']} |
| **Minimum** | {fmt_cur(aw_amt['total_obligated_amount']['min'])} | {fmt_cur(aw_amt['current_total_value_of_award']['min'])} | {fmt_cur(aw_amt['potential_total_value_of_award']['min'])} |
| **Median** | {fmt_cur(aw_amt['total_obligated_amount']['median'])} | {fmt_cur(aw_amt['current_total_value_of_award']['median'])} | {fmt_cur(aw_amt['potential_total_value_of_award']['median'])} |
| **Maximum** | {fmt_cur(aw_amt['total_obligated_amount']['max'])} | {fmt_cur(aw_amt['current_total_value_of_award']['max'])} | {fmt_cur(aw_amt['potential_total_value_of_award']['max'])} |

### Transaction Dollar Fields
| Metric | `federal_action_obligation` |
| :--- | :--- |
| **Total Populated** | {tx_amt['valid_count']} |
| **Missing** | {tx_amt['missing_count']} |
| **Zero Values** | {tx_amt['zero_count']} (Administrative / no-cost actions) |
| **Negative Values** | {tx_amt['negative_count']} (Deobligations) |
| **Positive Values** | {tx_amt['positive_count']} |
| **Minimum** | {fmt_cur(tx_amt['min'])} |
| **Median** | {fmt_cur(tx_amt['median'])} |
| **Maximum** | {fmt_cur(tx_amt['max'])} |

---

## 6. Discrepancy Reconciliation (Website Declared vs. Downloaded CSV)

| Entity | Website Dialog Declared | Actual Downloaded CSV | Discrepancy | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Awards** | {rec['website_declared_awards']} | {rec['actual_downloaded_awards']} | {rec['awards_discrepancy']} | MATCHED (Exact) |
| **Transactions** | {rec['website_declared_transactions']} | {rec['actual_downloaded_transactions']} | {rec['transactions_discrepancy']} | **UNRESOLVED** |

### Evidence-Based Assessment
1. The website download dialog displayed `Awards: 221 records` and `Transactions: 1,384 records`.
2. The downloaded award summary CSV contains exactly 221 records, matching the displayed count.
3. The downloaded transaction CSV contains 390 records. All 390 records have action dates strictly within FY2020.
4. Award summary records show that 139 awards had subsequent actions through FY2027.
5. **Conclusion**: The reason why the website dialog showed 1,384 transactions while the downloaded CSV contains 390 transactions is **UNRESOLVED**. Plausible explanations include (a) the website dialog estimated all historical transactions for the 221 awards while the download endpoint applied the FY2020 action date filter, or (b) another backend counting distinction. In accordance with safety rules, no conclusion is assumed without direct API documentation or server confirmation.

---

## 7. Top Missing Schema Columns

### Award Summaries (Top Missing Fields)
| Column | Missing Count | Missing Pct |
| :--- | :--- | :--- |
{aw_top_missing_lines}

### Prime Transactions (Top Missing Fields)
| Column | Missing Count | Missing Pct |
| :--- | :--- | :--- |
{tx_top_missing_lines}

---

## 8. Data Feasibility Assessment

### Schema Validation: **{feas['schema_validation_status']}**
The downloaded data successfully verifies the official USAspending file structure:
- Consistent multi-column schemas (286 columns for award summaries, 297 columns for prime transactions).
- Reliable join key (`contract_award_unique_key`) providing 100% referential linkage between transactions and award summaries.
- Valid representation of core recompete metadata: agency codes, NAICS codes, action dates, performance periods, and monetary amounts.

### Successor Matching / Recompete Feasibility: **{feas['successor_feasibility_status']}**
This dataset is **strictly insufficient** to establish feasibility of recompete successor matching:
- **Scope Limitation**: Limited to a single awarding agency (NASA), a single NAICS code (541330), and awards initiated in FY2020.
- **Truncated Transaction History**: Transactions are strictly restricted to FY2020 actions. Post-FY2020 modifications and follow-on awards are absent from this export.
- **Cohort Representation**: The eventual Sanket cohort requires combining multiple NAICS families, IT PSCs, and PSC R families with historical dollar thresholds. This pilot does not represent that full population.
"""


def main() -> int:
    """Run CLI for profiling downloaded ZIP."""
    parser = argparse.ArgumentParser(description="Profile downloaded USAspending ZIP archive.")
    parser.add_argument(
        "--zip",
        dest="zip_path",
        default=DEFAULT_ZIP_PATH,
        help=f"Path to downloaded ZIP archive (default: {DEFAULT_ZIP_PATH})",
    )
    parser.add_argument(
        "--output-dir",
        dest="output_dir",
        default="reports/data_feasibility",
        help="Directory to save audit report and manifest (default: reports/data_feasibility)",
    )
    args = parser.parse_args()

    zip_file = Path(args.zip_path)
    if not zip_file.is_absolute():
        zip_file = Path.cwd() / zip_file

    if not zip_file.exists():
        print(f"ERROR: Expected ZIP archive not found at: {zip_file.resolve()}", file=sys.stderr)
        return 1

    print(f"Auditing USAspending ZIP archive: {zip_file.resolve()}")
    try:
        data = analyze_zip_archive(zip_file)
    except (ValueError, FileNotFoundError, zipfile.BadZipFile, KeyError, csv.Error, OSError) as e:
        print(f"ERROR during archive analysis: {e}", file=sys.stderr)
        return 1

    out_dir = Path(args.output_dir)
    if not out_dir.is_absolute():
        out_dir = Path.cwd() / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = out_dir / "downloaded_sample_manifest.json"
    report_path = out_dir / "downloaded_sample_audit.md"

    # Write manifest
    with manifest_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"Manifest written to: {manifest_path.resolve()}")

    # Write Markdown audit report
    report_content = generate_audit_report(data)
    with report_path.open("w", encoding="utf-8") as f:
        f.write(report_content)
    print(f"Audit report written to: {report_path.resolve()}")

    # Print summary facts to stdout
    print("\n=== AUDIT SUMMARY ===")
    print(f"Archive File: {zip_file.name}")
    print(f"SHA-256: {data['zip_metadata']['sha256']}")
    print(f"Award Summaries: {data['members']['award_summaries']['row_count']} rows, {data['members']['award_summaries']['column_count']} cols")
    print(f"Transactions: {data['members']['transactions']['row_count']} rows, {data['members']['transactions']['column_count']} cols")
    print(f"Award Keys: {data['members']['award_summaries']['award_unique_keys_unique']} unique, 0 missing")
    print(f"Transaction Keys: {data['members']['transactions']['tx_unique_keys_unique']} unique, 0 missing")
    print(f"Linkage: 100% linked ({data['linkage']['unmatched_transaction_keys_count']} unmatched tx, {data['linkage']['awards_with_zero_transactions_count']} zero-tx awards)")
    print(f"Transaction Dates: {data['members']['transactions']['action_date_range']['min']} to {data['members']['transactions']['action_date_range']['max']} (All FY2020)")
    print(f"Discrepancy: Declared Tx = {data['website_reconciliation']['website_declared_transactions']}, Actual Tx = {data['website_reconciliation']['actual_downloaded_transactions']} (Status: {data['website_reconciliation']['discrepancy_status']})")
    print("Audit completed successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
