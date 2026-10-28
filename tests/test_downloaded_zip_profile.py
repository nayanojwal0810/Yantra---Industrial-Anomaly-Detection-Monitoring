"""Unit tests for scripts/profile_downloaded_zip.py.

Tests cover:
- Valid ZIP analysis with both Award Summaries and Prime Transactions.
- Missing member error handling.
- Missing required columns detection.
- Join metrics (unmatched keys, zero-tx awards).
- Date-range and FY distribution calculations.
- Displayed-vs-actual discrepancy reconciliation.
- Missing file error handling and CLI execution.
"""

from __future__ import annotations

import csv
import io
import zipfile
from pathlib import Path

import pytest

from scripts.profile_downloaded_zip import (
    REQUIRED_AWARD_COLUMNS,
    REQUIRED_TRANSACTION_COLUMNS,
    analyze_zip_archive,
    generate_audit_report,
    profile_numeric_column,
)


def create_synthetic_zip(
    tmp_path: Path,
    awards_rows: list[dict[str, str]] | None = None,
    tx_rows: list[dict[str, str]] | None = None,
    include_awards: bool = True,
    include_tx: bool = True,
    awards_filename: str = "Contracts_PrimeAwardSummaries_test.csv",
    tx_filename: str = "Contracts_PrimeTransactions_test.csv",
) -> Path:
    """Helper to build an in-memory/temp ZIP with synthetic USAspending CSV files."""
    zip_path = tmp_path / "test_usaspending_export.zip"

    default_award_cols = list(REQUIRED_AWARD_COLUMNS) + ["award_base_action_date_fiscal_year", "award_latest_action_date_fiscal_year"]
    default_tx_cols = list(REQUIRED_TRANSACTION_COLUMNS) + ["action_date_fiscal_year"]

    with zipfile.ZipFile(zip_path, "w") as z:
        if include_awards:
            awards_data = awards_rows if awards_rows is not None else [
                {
                    "contract_award_unique_key": "CONT_AWD_001",
                    "award_id_piid": "PIID001",
                    "award_base_action_date": "2019-10-15",
                    "award_base_action_date_fiscal_year": "2020",
                    "award_latest_action_date": "2021-03-20",
                    "award_latest_action_date_fiscal_year": "2021",
                    "awarding_agency_name": "National Aeronautics and Space Administration",
                    "naics_code": "541330",
                    "total_obligated_amount": "500000.00",
                },
                {
                    "contract_award_unique_key": "CONT_AWD_002",
                    "award_id_piid": "PIID002",
                    "award_base_action_date": "2020-01-10",
                    "award_base_action_date_fiscal_year": "2020",
                    "award_latest_action_date": "2020-01-10",
                    "award_latest_action_date_fiscal_year": "2020",
                    "awarding_agency_name": "National Aeronautics and Space Administration",
                    "naics_code": "541330",
                    "total_obligated_amount": "120000.00",
                },
            ]
            buf = io.StringIO()
            writer = csv.DictWriter(buf, fieldnames=default_award_cols)
            writer.writeheader()
            for r in awards_data:
                writer.writerow(r)
            z.writestr(awards_filename, buf.getvalue())

        if include_tx:
            tx_data = tx_rows if tx_rows is not None else [
                {
                    "contract_transaction_unique_key": "TX_001",
                    "contract_award_unique_key": "CONT_AWD_001",
                    "award_id_piid": "PIID001",
                    "action_date": "2019-10-15",
                    "action_date_fiscal_year": "2020",
                    "awarding_agency_name": "National Aeronautics and Space Administration",
                    "naics_code": "541330",
                    "federal_action_obligation": "300000.00",
                },
                {
                    "contract_transaction_unique_key": "TX_002",
                    "contract_award_unique_key": "CONT_AWD_001",
                    "award_id_piid": "PIID001",
                    "action_date": "2020-05-12",
                    "action_date_fiscal_year": "2020",
                    "awarding_agency_name": "National Aeronautics and Space Administration",
                    "naics_code": "541330",
                    "federal_action_obligation": "200000.00",
                },
                {
                    "contract_transaction_unique_key": "TX_003",
                    "contract_award_unique_key": "CONT_AWD_002",
                    "award_id_piid": "PIID002",
                    "action_date": "2020-01-10",
                    "action_date_fiscal_year": "2020",
                    "awarding_agency_name": "National Aeronautics and Space Administration",
                    "naics_code": "541330",
                    "federal_action_obligation": "120000.00",
                },
            ]
            buf = io.StringIO()
            writer = csv.DictWriter(buf, fieldnames=default_tx_cols)
            writer.writeheader()
            for r in tx_data:
                writer.writerow(r)
            z.writestr(tx_filename, buf.getvalue())

    return zip_path


def test_valid_synthetic_zip_analysis(tmp_path: Path) -> None:
    """Test analyzing a fully valid synthetic ZIP with summaries and transactions."""
    zip_path = create_synthetic_zip(tmp_path)
    res = analyze_zip_archive(zip_path)

    assert res["zip_metadata"]["file_size_bytes"] > 0
    assert len(res["zip_metadata"]["sha256"]) == 64

    aw = res["members"]["award_summaries"]
    assert aw["row_count"] == 2
    assert aw["award_unique_keys_unique"] == 2
    assert aw["award_unique_keys_missing"] == 0
    assert aw["base_action_date_range"] == {"min": "2019-10-15", "max": "2020-01-10"}
    assert aw["latest_action_date_range"] == {"min": "2020-01-10", "max": "2021-03-20"}
    assert aw["agency_compliance_nasa"]["percentage"] == 100.0
    assert aw["naics_compliance_541330"]["percentage"] == 100.0

    tx = res["members"]["transactions"]
    assert tx["row_count"] == 3
    assert tx["tx_unique_keys_unique"] == 3
    assert tx["post_fy2020_transactions_count"] == 0

    lk = res["linkage"]
    assert lk["unmatched_transaction_keys_count"] == 0
    assert lk["awards_with_zero_transactions_count"] == 0
    assert lk["transactions_per_award_histogram"] == {1: 1, 2: 1}

    # Verify report generation works on valid output
    report_md = generate_audit_report(res)
    assert "# USAspending Downloaded Sample Audit" in report_md
    assert "UNRESOLVED" in report_md


def test_missing_awards_member_raises_value_error(tmp_path: Path) -> None:
    """Test error when Award Summaries member is absent."""
    zip_path = create_synthetic_zip(tmp_path, include_awards=False)
    with pytest.raises(ValueError, match="missing PrimeAwardSummaries CSV member"):
        analyze_zip_archive(zip_path)


def test_missing_transactions_member_raises_value_error(tmp_path: Path) -> None:
    """Test error when Prime Transactions member is absent."""
    zip_path = create_synthetic_zip(tmp_path, include_tx=False)
    with pytest.raises(ValueError, match="missing PrimeTransactions CSV member"):
        analyze_zip_archive(zip_path)


def test_missing_required_columns_detection(tmp_path: Path) -> None:
    """Test that missing required columns are properly reported."""
    zip_path = tmp_path / "missing_cols.zip"
    with zipfile.ZipFile(zip_path, "w") as z:
        # Create awards CSV without awarding_agency_name and naics_code
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=["contract_award_unique_key", "award_id_piid"])
        writer.writeheader()
        writer.writerow({"contract_award_unique_key": "K1", "award_id_piid": "P1"})
        z.writestr("Contracts_PrimeAwardSummaries_test.csv", buf.getvalue())

        # Create tx CSV with all required
        buf2 = io.StringIO()
        writer2 = csv.DictWriter(buf2, fieldnames=REQUIRED_TRANSACTION_COLUMNS)
        writer2.writeheader()
        writer2.writerow({
            "contract_transaction_unique_key": "T1",
            "contract_award_unique_key": "K1",
            "award_id_piid": "P1",
            "action_date": "2020-01-01",
            "awarding_agency_name": "NASA",
            "naics_code": "541330",
            "federal_action_obligation": "100.0",
        })
        z.writestr("Contracts_PrimeTransactions_test.csv", buf2.getvalue())

    res = analyze_zip_archive(zip_path)
    missing = res["members"]["award_summaries"]["missing_required_columns"]
    assert "awarding_agency_name" in missing
    assert "naics_code" in missing
    assert "total_obligated_amount" in missing


def test_linkage_with_unmatched_and_zero_transactions(tmp_path: Path) -> None:
    """Test linkage metrics when there is an unmatched tx and an award with zero transactions."""
    awards = [
        {"contract_award_unique_key": "AWD_A", "award_id_piid": "P_A"},
        {"contract_award_unique_key": "AWD_B", "award_id_piid": "P_B"},
    ]
    txs = [
        {"contract_transaction_unique_key": "T1", "contract_award_unique_key": "AWD_A"},
        {"contract_transaction_unique_key": "T2", "contract_award_unique_key": "AWD_UNMATCHED"},
    ]
    zip_path = tmp_path / "partial_linkage.zip"
    with zipfile.ZipFile(zip_path, "w") as z:
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=REQUIRED_AWARD_COLUMNS)
        writer.writeheader()
        for a in awards:
            writer.writerow({**{c: "" for c in REQUIRED_AWARD_COLUMNS}, **a})
        z.writestr("Contracts_PrimeAwardSummaries_test.csv", buf.getvalue())

        buf2 = io.StringIO()
        writer2 = csv.DictWriter(buf2, fieldnames=REQUIRED_TRANSACTION_COLUMNS)
        writer2.writeheader()
        for t in txs:
            writer2.writerow({**{c: "" for c in REQUIRED_TRANSACTION_COLUMNS}, **t})
        z.writestr("Contracts_PrimeTransactions_test.csv", buf2.getvalue())

    res = analyze_zip_archive(zip_path)
    lk = res["linkage"]
    assert lk["unmatched_transaction_keys_count"] == 1
    assert lk["awards_with_zero_transactions_count"] == 1
    assert lk["awards_with_transactions_count"] == 1


def test_date_range_and_post_fy2020_detection(tmp_path: Path) -> None:
    """Test date parsing and detection of transactions outside FY2020."""
    txs = [
        {"contract_transaction_unique_key": "T1", "contract_award_unique_key": "K1", "action_date": "2020-02-15"},
        {"contract_transaction_unique_key": "T2", "contract_award_unique_key": "K1", "action_date": "2021-04-10"},
        {"contract_transaction_unique_key": "T3", "contract_award_unique_key": "K1", "action_date": "2018-08-01"},
    ]
    zip_path = tmp_path / "dates.zip"
    with zipfile.ZipFile(zip_path, "w") as z:
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=REQUIRED_AWARD_COLUMNS)
        writer.writeheader()
        writer.writerow({**{c: "" for c in REQUIRED_AWARD_COLUMNS}, "contract_award_unique_key": "K1"})
        z.writestr("Contracts_PrimeAwardSummaries_test.csv", buf.getvalue())

        buf2 = io.StringIO()
        writer2 = csv.DictWriter(buf2, fieldnames=REQUIRED_TRANSACTION_COLUMNS)
        writer2.writeheader()
        for t in txs:
            writer2.writerow({**{c: "" for c in REQUIRED_TRANSACTION_COLUMNS}, **t})
        z.writestr("Contracts_PrimeTransactions_test.csv", buf2.getvalue())

    res = analyze_zip_archive(zip_path)
    tx = res["members"]["transactions"]
    assert tx["action_date_range"]["min"] == "2018-08-01"
    assert tx["action_date_range"]["max"] == "2021-04-10"
    assert tx["post_fy2020_transactions_count"] == 1
    assert tx["pre_fy2020_transactions_count"] == 1


def test_discrepancy_reconciliation_marked_unresolved(tmp_path: Path) -> None:
    """Verify website-declared vs downloaded count handling."""
    zip_path = create_synthetic_zip(tmp_path)
    res = analyze_zip_archive(zip_path)
    rec = res["website_reconciliation"]

    assert rec["website_declared_awards"] == 221
    assert rec["website_declared_transactions"] == 1384
    assert rec["actual_downloaded_awards"] == 2
    assert rec["actual_downloaded_transactions"] == 3
    assert rec["discrepancy_status"] == "UNRESOLVED"
    assert "cannot be established without official server-side confirmation" in rec["status_notes"]


def test_file_not_found_handling(tmp_path: Path) -> None:
    """Test that FileNotFoundError is raised when target ZIP does not exist."""
    non_existent = tmp_path / "does_not_exist.zip"
    with pytest.raises(FileNotFoundError, match="Input ZIP not found"):
        analyze_zip_archive(non_existent)


def test_profile_numeric_column_statistics() -> None:
    """Test numeric column statistical calculations."""
    rows = [
        {"val": "100.0"},
        {"val": "-50.0"},
        {"val": "0.0"},
        {"val": "200.0"},
        {"val": ""},
        {"val": "invalid"},
    ]
    stats = profile_numeric_column(rows, "val")
    assert stats["total_rows"] == 6
    assert stats["valid_count"] == 4
    assert stats["missing_count"] == 2
    assert stats["zero_count"] == 1
    assert stats["negative_count"] == 1
    assert stats["positive_count"] == 2
    assert stats["min"] == -50.0
    assert stats["median"] == 50.0
    assert stats["max"] == 200.0
