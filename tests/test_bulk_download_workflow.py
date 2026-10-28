"""Unit tests for the official USAspending bulk download workflow.

Project: Sanket — Federal Contract Recompete Intelligence
All tests execute strictly offline with mocked HTTP sessions/responses.
"""

from __future__ import annotations

import csv
import io
import json
import zipfile
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
import requests
import yaml

from scripts.download_via_bulk_api import (
    AwardCohortAuditError,
    ConfigError,
    DownloadJobError,
    DownloadJobTimeoutError,
    PrecheckValidationError,
    TransactionQualityError,
    UntrustedHostError,
    ZIPValidationError,
    aggregate_and_package_transactions,
    audit_award_cohort,
    compare_with_manual_archives,
    create_session,
    download_zip_stream,
    fetch_award_transaction_count,
    fetch_award_transactions,
    initiate_download_job,
    inspect_award_zip,
    inspect_transaction_zip,
    load_cached_award_result,
    load_config,
    parse_count_response,
    poll_download_status,
    process_all_cohort_transactions,
    query_count_endpoint,
    redact_sensitive,
    resolve_api_url,
    run_bulk_diagnostic,
    run_bulk_download,
    save_cached_award_result,
    validate_trusted_host,
    verify_transaction_archive_from_disk,
)


@pytest.fixture
def sample_config(tmp_path: Path) -> dict[str, Any]:
    """Provide a validated sample configuration pointing to temporary paths."""
    manifest_file = tmp_path / "reports" / "test_manifest.json"
    report_file = tmp_path / "reports" / "test_report.md"
    bulk_dir = tmp_path / "data" / "raw" / "sample" / "bulk_api"
    manual_on = tmp_path / "data" / "raw" / "sample" / "manual_on.zip"
    manual_off = tmp_path / "data" / "raw" / "sample" / "manual_off.zip"

    return {
        "version": "1.1.0",
        "api": {
            "base_url": "https://api.usaspending.gov",
            "endpoints": {
                "count": "/api/v2/download/count/",
                "search": "/api/v2/download/search/",
                "status": "/api/v2/download/status/",
            },
            "trusted_hosts": [
                "api.usaspending.gov",
                "files.usaspending.gov",
                "files-nonprod.usaspending.gov",
            ],
        },
        "controlled_cohort": {
            "cohort_id": "nasa_naics541330_fy2020",
            "description": "NASA Awarding Agency, NAICS 541330, FY2020 new awards",
            "filters": {
                "award_type_codes": ["A", "B", "C", "D"],
                "agencies": [
                    {
                        "type": "awarding",
                        "tier": "toptier",
                        "name": "National Aeronautics and Space Administration",
                    }
                ],
                "naics_codes": {"require": ["541330"]},
                "time_period": [
                    {
                        "start_date": "2019-10-01",
                        "end_date": "2020-09-30",
                        "date_type": "new_awards_only",
                    }
                ],
            },
            "spending_level_count": "awards",
            "spending_level_download": ["awards"],
            "file_format": "csv",
        },
        "transaction_cohort": {
            "batch_size": 2,
            "exact_match_quoting": True,
            "spending_level_count": "transactions",
            "spending_level_download": ["transactions"],
            "max_transactions_per_batch: 25000": 25000,
        },
        "reference_observations": {
            "manual_on_download": {"awards": 221, "transactions": 390},
            "manual_off_download": {"awards": 785, "transactions": 1384},
        },
        "safety_caps": {
            "awards_max": 5000,
            "transactions_max_per_batch": 25000,
        },
        "http_policy": {
            "timeout_seconds": 10,
            "download_timeout_seconds": 30,
            "max_retries": 2,
            "backoff_factor": 0.1,
            "retry_status_codes": [429, 500, 502, 503, 504],
        },
        "polling_policy": {
            "poll_interval_seconds": 0.01,
            "overall_timeout_seconds": 0.5,
        },
        "paths": {
            "bulk_api_dir": str(bulk_dir),
            "raw_data_dir": str(tmp_path / "data" / "raw" / "sample"),
            "manual_archive_on": str(manual_on),
            "manual_archive_off": str(manual_off),
            "manifest_path": str(manifest_file),
            "validation_report_path": str(report_file),
        },
    }


def create_test_zip(
    filename_in_zip: str,
    rows: list[dict[str, str]],
    extra_members: dict[str, str] | None = None,
) -> bytes:
    """Helper to create an in-memory ZIP buffer with CSV members."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        if rows:
            out = io.StringIO()
            writer = csv.DictWriter(out, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
            z.writestr(filename_in_zip, out.getvalue())

        if extra_members:
            for fname, content in extra_members.items():
                z.writestr(fname, content)

    return buf.getvalue()


# -----------------------------------------------------------------------------
# 1. Configuration & Dry-Run Tests
# -----------------------------------------------------------------------------


def test_dry_run_sends_zero_requests_and_writes_zero_raw_files(
    sample_config: dict[str, Any], tmp_path: Path
) -> None:
    """Dry run mode must not make network calls and must not write raw data."""
    cfg_path = tmp_path / "test_config.yaml"
    with cfg_path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(sample_config, f)

    with patch("requests.Session.post") as mock_post, patch("requests.Session.get") as mock_get:
        exit_code = run_bulk_download(config_path=cfg_path, confirm_download=False)

        assert exit_code == 0
        mock_post.assert_not_called()
        mock_get.assert_not_called()

        bulk_dir = Path(sample_config["paths"]["bulk_api_dir"])
        assert not bulk_dir.exists() or len(list(bulk_dir.glob("*.zip"))) == 0

        manifest_path = Path(sample_config["paths"]["manifest_path"])
        assert manifest_path.exists()
        manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
        assert manifest_data["run_status"] == "dry_run"


def test_load_config_validates_naics_object_and_new_awards_only(
    sample_config: dict[str, Any], tmp_path: Path
) -> None:
    """load_config must reject list naics_codes or missing new_awards_only date_type."""
    # Test 1: naics_codes as list instead of dict
    bad_cfg = dict(sample_config)
    bad_cfg["controlled_cohort"] = dict(sample_config["controlled_cohort"])
    bad_cfg["controlled_cohort"]["filters"] = dict(sample_config["controlled_cohort"]["filters"])
    bad_cfg["controlled_cohort"]["filters"]["naics_codes"] = ["541330"]

    cfg_file = tmp_path / "bad_naics.yaml"
    cfg_file.write_text(yaml.safe_dump(bad_cfg), encoding="utf-8")
    with pytest.raises(ConfigError, match="naics_codes must be an object with 'require' list"):
        load_config(cfg_file)

    # Test 2: date_type not new_awards_only
    bad_cfg2 = dict(sample_config)
    bad_cfg2["controlled_cohort"] = dict(sample_config["controlled_cohort"])
    bad_cfg2["controlled_cohort"]["filters"] = dict(sample_config["controlled_cohort"]["filters"])
    bad_cfg2["controlled_cohort"]["filters"]["time_period"] = [
        {"start_date": "2019-10-01", "end_date": "2020-09-30", "date_type": "action_date"}
    ]
    cfg_file2 = tmp_path / "bad_date.yaml"
    cfg_file2.write_text(yaml.safe_dump(bad_cfg2), encoding="utf-8")
    with pytest.raises(ConfigError, match="date_type: 'new_awards_only'"):
        load_config(cfg_file2)


def test_load_config_rejects_unauthorized_cohort(
    sample_config: dict[str, Any], tmp_path: Path
) -> None:
    """load_config must reject cohorts other than nasa_naics541330_fy2020."""
    sample_config["controlled_cohort"]["cohort_id"] = "dod_other_cohort"
    cfg_file = tmp_path / "unauthorized.yaml"
    cfg_file.write_text(yaml.safe_dump(sample_config), encoding="utf-8")
    with pytest.raises(ConfigError, match="Unsupported cohort"):
        load_config(cfg_file)


# -----------------------------------------------------------------------------
# 2. Host, Protocol, and URL Resolution Tests
# -----------------------------------------------------------------------------


def test_validate_trusted_host_enforces_https_and_rejects_untrusted() -> None:
    """validate_trusted_host must reject HTTP, localhost, and non-whitelisted domains."""
    trusted = ["api.usaspending.gov", "files.usaspending.gov"]

    # Valid HTTPS
    assert validate_trusted_host("https://api.usaspending.gov/endpoint", trusted)
    assert validate_trusted_host("https://files.usaspending.gov/test.zip", trusted)

    # Non-HTTPS
    with pytest.raises(UntrustedHostError, match="Only HTTPS is permitted"):
        validate_trusted_host("http://api.usaspending.gov/endpoint", trusted)

    # Localhost
    with pytest.raises(UntrustedHostError, match="Localhost access rejected"):
        validate_trusted_host("https://localhost/endpoint", trusted)
    with pytest.raises(UntrustedHostError, match="Localhost access rejected"):
        validate_trusted_host("https://127.0.0.1/endpoint", trusted)

    # Untrusted domain
    with pytest.raises(UntrustedHostError, match="not in trusted hosts list"):
        validate_trusted_host("https://malicious.com/test.zip", trusted)


def test_resolve_api_url_relative_and_absolute() -> None:
    """resolve_api_url safely joins relative paths and validates absolute URLs."""
    base = "https://api.usaspending.gov"
    trusted = ["api.usaspending.gov", "files.usaspending.gov"]

    rel = resolve_api_url(base, "/api/v2/download/count/", trusted)
    assert rel == "https://api.usaspending.gov/api/v2/download/count/"

    abs_url = resolve_api_url(base, "https://files.usaspending.gov/bulk/sample.zip", trusted)
    assert abs_url == "https://files.usaspending.gov/bulk/sample.zip"


def test_redirect_to_untrusted_host_rejected(sample_config: dict[str, Any]) -> None:
    """HTTP session hook must abort if a redirect target is an untrusted host."""
    session = create_session(sample_config["http_policy"], sample_config["api"]["trusted_hosts"])

    # Simulate response history with untrusted redirect
    mock_resp = MagicMock()
    mock_resp.url = "https://untrusted.com/download.zip"
    mock_resp.history = []

    with pytest.raises(UntrustedHostError, match="not in trusted hosts list"):
        for hook in session.hooks["response"]:
            hook(mock_resp)


# -----------------------------------------------------------------------------
# 3. Payload Shape, Quoting, and Spending Level Tests
# -----------------------------------------------------------------------------


def test_award_cohort_payload_shape_and_spending_level(sample_config: dict[str, Any]) -> None:
    """Award cohort job must use string 'awards' for count and ['awards'] for search."""
    session = requests.Session()
    base_url = sample_config["api"]["base_url"]
    trusted = sample_config["api"]["trusted_hosts"]

    # 1. Count query
    mock_count_resp = MagicMock()
    mock_count_resp.status_code = 200
    mock_count_resp.json.return_value = {
        "calculated_count": 221,
        "rows_gt_limit": False,
    }

    with patch.object(session, "post", return_value=mock_count_resp) as mock_post:
        res = query_count_endpoint(
            session=session,
            base_url=base_url,
            count_endpoint="/api/v2/download/count/",
            trusted_hosts=trusted,
            filters=sample_config["controlled_cohort"]["filters"],
            spending_level="awards",
        )
        assert res["calculated_count"] == 221

        count_call_payload = mock_post.call_args[1]["json"]
        assert count_call_payload["spending_level"] == "awards"  # Singular string!
        assert count_call_payload["filters"]["naics_codes"] == {"require": ["541330"]}
        assert count_call_payload["filters"]["time_period"][0]["date_type"] == "new_awards_only"

    # 2. Search job
    mock_search_resp = MagicMock()
    mock_search_resp.status_code = 200
    mock_search_resp.json.return_value = {
        "file_name": "test_awards.zip",
        "status_url": "/api/v2/download/status/?file_name=test_awards.zip",
        "file_url": "https://files.usaspending.gov/test_awards.zip",
        "download_request": {},
    }

    with patch.object(session, "post", return_value=mock_search_resp) as mock_post2:
        job = initiate_download_job(
            session=session,
            base_url=base_url,
            search_endpoint="/api/v2/download/search/",
            trusted_hosts=trusted,
            filters=sample_config["controlled_cohort"]["filters"],
            spending_levels=["awards"],
            file_format="csv",
        )
        assert job["file_name"] == "test_awards.zip"
        search_call_payload = mock_post2.call_args[1]["json"]
        assert search_call_payload["spending_level"] == ["awards"]  # Array of string!
        assert "columns" not in search_call_payload  # Full schema preserved


def test_transaction_cohort_payload_shape_no_date_filters_and_exact_quoting(
    sample_config: dict[str, Any],
) -> None:
    """Transaction query must have ONLY award_ids, NO time_period, and exact quoting."""
    session = requests.Session()
    base_url = sample_config["api"]["base_url"]
    trusted = sample_config["api"]["trusted_hosts"]

    batch_piids = ["80AFRC20C0012", "80AFRC20C0019"]
    quoted_piids = [f'"{p}"' for p in batch_piids]
    tx_filters = {"award_ids": quoted_piids}

    # Verify no date or NAICS filters
    assert "time_period" not in tx_filters
    assert "naics_codes" not in tx_filters
    assert "agencies" not in tx_filters

    # 1. Count query
    mock_count_resp = MagicMock()
    mock_count_resp.status_code = 200
    mock_count_resp.json.return_value = {
        "calculated_count": 15,
        "rows_gt_limit": False,
    }

    with patch.object(session, "post", return_value=mock_count_resp) as mock_post:
        res = query_count_endpoint(
            session=session,
            base_url=base_url,
            count_endpoint="/api/v2/download/count/",
            trusted_hosts=trusted,
            filters=tx_filters,
            spending_level="transactions",
        )
        assert res["calculated_count"] == 15

        payload = mock_post.call_args[1]["json"]
        assert payload["spending_level"] == "transactions"  # Singular string!
        assert payload["filters"]["award_ids"] == ['"80AFRC20C0012"', '"80AFRC20C0019"']


# -----------------------------------------------------------------------------
# 4. Count Precheck Parsing & Defensiveness Tests
# -----------------------------------------------------------------------------


def test_parse_count_response_rejects_booleans_and_malformed() -> None:
    """parse_count_response defensively rejects boolean, string, or negative counts."""
    with pytest.raises(PrecheckValidationError, match="invalid calculated_count"):
        parse_count_response({"calculated_count": True}, "awards")

    with pytest.raises(PrecheckValidationError, match="invalid calculated_count"):
        parse_count_response({"calculated_count": "221"}, "awards")

    with pytest.raises(PrecheckValidationError, match="negative calculated_count"):
        parse_count_response({"calculated_count": -1}, "awards")

    with pytest.raises(PrecheckValidationError, match="rows_gt_limit=True"):
        parse_count_response({"calculated_count": 500000, "rows_gt_limit": True}, "awards")


def test_no_gate_on_unrelated_reference_ui_counts(sample_config: dict[str, Any]) -> None:
    """Precheck does not hard-gate against manual 785/1384 counts when running new_awards_only."""
    # When API returns 221 awards (or any non-capped number), it does not fail
    # simply because reference_observations mentions 785 or 221.
    payload = {"calculated_count": 221, "rows_gt_limit": False}
    parsed = parse_count_response(payload, "awards")
    assert parsed["calculated_count"] == 221


# -----------------------------------------------------------------------------
# 5. Polling, Timeout, and Status Failure Tests
# -----------------------------------------------------------------------------


def test_poll_download_status_transitions_running_to_finished(
    sample_config: dict[str, Any],
) -> None:
    """Polling transitions through running -> finished correctly and captures total_rows."""
    session = requests.Session()
    base_url = sample_config["api"]["base_url"]
    trusted = sample_config["api"]["trusted_hosts"]
    job_info = {
        "file_name": "test.zip",
        "status_url": "/api/v2/download/status/?file_name=test.zip",
    }

    resp1 = MagicMock()
    resp1.status_code = 200
    resp1.json.return_value = {"status": "running", "message": "In progress"}

    resp2 = MagicMock()
    resp2.status_code = 200
    resp2.json.return_value = {
        "status": "finished",
        "url": "https://files.usaspending.gov/test.zip",
        "total_rows": 221,
        "message": None,
    }

    with patch.object(session, "get", side_effect=[resp1, resp2]):
        result = poll_download_status(
            session=session,
            base_url=base_url,
            status_endpoint_cfg="/api/v2/download/status/",
            trusted_hosts=trusted,
            job_info=job_info,
            poll_interval=0.01,
            overall_timeout=1.0,
        )
        assert result["final_status"] == "finished"
        assert result["total_rows"] == 221


def test_poll_download_status_failed_raises_error(sample_config: dict[str, Any]) -> None:
    """Polling server failure raises DownloadJobError with message."""
    session = requests.Session()
    base_url = sample_config["api"]["base_url"]
    trusted = sample_config["api"]["trusted_hosts"]
    job_info = {"file_name": "test.zip"}

    resp_failed = MagicMock()
    resp_failed.status_code = 200
    resp_failed.json.return_value = {"status": "failed", "message": "Backend query timeout"}

    with (
        patch.object(session, "get", return_value=resp_failed),
        pytest.raises(DownloadJobError, match="Backend query timeout"),
    ):
        poll_download_status(
            session=session,
            base_url=base_url,
            status_endpoint_cfg="/api/v2/download/status/",
            trusted_hosts=trusted,
            job_info=job_info,
        )


def test_poll_download_status_timeout_stops_without_resubmit(
    sample_config: dict[str, Any],
) -> None:
    """Polling timeout raises DownloadJobTimeoutError and sends zero new job submissions."""
    session = requests.Session()
    base_url = sample_config["api"]["base_url"]
    trusted = sample_config["api"]["trusted_hosts"]
    job_info = {"file_name": "test.zip"}

    resp_running = MagicMock()
    resp_running.status_code = 200
    resp_running.json.return_value = {"status": "running"}

    with (
        patch.object(session, "get", return_value=resp_running),
        patch.object(session, "post") as mock_post,
        pytest.raises(DownloadJobTimeoutError, match="Polling timed out"),
    ):
        poll_download_status(
            session=session,
            base_url=base_url,
            status_endpoint_cfg="/api/v2/download/status/",
            trusted_hosts=trusted,
            job_info=job_info,
            poll_interval=0.01,
            overall_timeout=0.03,
        )
    mock_post.assert_not_called()


# -----------------------------------------------------------------------------
# 6. Streaming Download, CRC Validation & Atomic Rename Tests
# -----------------------------------------------------------------------------


def test_download_zip_stream_atomic_rename_and_no_overwrite(
    sample_config: dict[str, Any], tmp_path: Path
) -> None:
    """download_zip_stream streams to .part, CRC checks, and atomically renames."""
    session = requests.Session()
    target_zip = tmp_path / "downloads" / "final.zip"
    trusted = sample_config["api"]["trusted_hosts"]

    zip_bytes = create_test_zip(
        "Contracts_PrimeAwardSummaries.csv",
        [{"contract_award_unique_key": "AW1", "award_id_piid": "PIID1"}],
    )

    mock_resp = MagicMock()
    mock_resp.__enter__.return_value = mock_resp
    mock_resp.status_code = 200
    mock_resp.iter_content.return_value = [zip_bytes]

    with patch.object(session, "get", return_value=mock_resp):
        res = download_zip_stream(
            session=session,
            file_url="https://files.usaspending.gov/test.zip",
            target_path=target_zip,
            trusted_hosts=trusted,
        )
        assert res.is_file()
        assert not target_zip.with_suffix(".zip.part").exists()
        assert zipfile.is_zipfile(target_zip)

    # Overwrite refusal
    with pytest.raises(FileExistsError, match="already exists"):
        download_zip_stream(
            session=session,
            file_url="https://files.usaspending.gov/test.zip",
            target_path=target_zip,
            trusted_hosts=trusted,
        )


def test_download_zip_stream_corrupt_zip_fails_safely(
    sample_config: dict[str, Any], tmp_path: Path
) -> None:
    """Corrupt streamed content cleans up temporary .part and raises ZIPValidationError."""
    session = requests.Session()
    target_zip = tmp_path / "bad.zip"
    trusted = sample_config["api"]["trusted_hosts"]

    mock_resp = MagicMock()
    mock_resp.__enter__.return_value = mock_resp
    mock_resp.status_code = 200
    mock_resp.iter_content.return_value = [b"NOT A VALID ZIP ARCHIVE CONTENT"]

    with (
        patch.object(session, "get", return_value=mock_resp),
        pytest.raises(ZIPValidationError, match="not a valid ZIP archive"),
    ):
        download_zip_stream(
            session=session,
            file_url="https://files.usaspending.gov/bad.zip",
            target_path=target_zip,
            trusted_hosts=trusted,
        )
    assert not target_zip.exists()
    assert not target_zip.with_suffix(".zip.part").exists()


# -----------------------------------------------------------------------------
# 7. In-Memory QA, Deduplication, and Linkage Tests
# -----------------------------------------------------------------------------


def test_inspect_award_zip_in_memory_metrics_and_subaward_rejection(tmp_path: Path) -> None:
    """inspect_award_zip calculates row counts, PIIDs, repeated PIIDs, and rejects subawards."""
    awards = [
        {"contract_award_unique_key": "A1", "award_id_piid": "P1", "awarding_agency_name": "NASA"},
        {"contract_award_unique_key": "A2", "award_id_piid": "P2", "awarding_agency_name": "NASA"},
        {"contract_award_unique_key": "A3", "award_id_piid": "P1", "awarding_agency_name": "NASA"},  # Repeated P1!
        {"contract_award_unique_key": "A4", "award_id_piid": "", "awarding_agency_name": "NASA"},    # Blank PIID!
    ]
    zip_bytes = create_test_zip("Contracts_PrimeAwardSummaries_test.csv", awards)
    zip_path = tmp_path / "award_test.zip"
    zip_path.write_bytes(zip_bytes)

    qa = inspect_award_zip(zip_path)
    assert qa["row_count"] == 4
    assert qa["blank_piid_count"] == 1
    assert qa["unique_piids_count"] == 2  # P1, P2
    assert qa["repeated_piids_count"] == 1  # P1 appeared twice
    assert qa["unique_piids"] == ["P1", "P2"]

    # Reject subawards
    bad_zip_bytes = create_test_zip(
        "Contracts_PrimeAwardSummaries.csv",
        awards,
        extra_members={"Contracts_Subawards.csv": "subaward_key\nS1\n"},
    )
    bad_zip_path = tmp_path / "has_subawards.zip"
    bad_zip_path.write_bytes(bad_zip_bytes)
    with pytest.raises(ZIPValidationError, match="Forbidden subaward members"):
        inspect_award_zip(bad_zip_path)


def test_inspect_transaction_zip_accepts_outside_fy2020_and_audits_keys(tmp_path: Path) -> None:
    """inspect_transaction_zip accepts transactions outside FY2020 and audits keys."""
    txs = [
        {
            "contract_transaction_unique_key": "T1",
            "contract_award_unique_key": "A1",
            "award_id_piid": "P1",
            "action_date": "2020-03-15",  # In FY2020
        },
        {
            "contract_transaction_unique_key": "T2",
            "contract_award_unique_key": "A1",
            "award_id_piid": "P1",
            "action_date": "2021-06-20",  # Outside FY2020 (expected!)
        },
        {
            "contract_transaction_unique_key": "T3",
            "contract_award_unique_key": "A2",
            "award_id_piid": "P2",
            "action_date": "2018-01-10",  # Outside FY2020 (expected!)
        },
    ]
    zip_bytes = create_test_zip("Contracts_PrimeTransactions_test.csv", txs)
    zip_path = tmp_path / "tx_test.zip"
    zip_path.write_bytes(zip_bytes)

    qa = inspect_transaction_zip(zip_path, expected_cohort_piids={"P1", "P2"})
    assert qa["row_count"] == 3
    assert qa["unique_tx_keys_count"] == 3
    assert qa["missing_tx_keys_count"] == 0
    assert qa["duplicate_tx_keys_count"] == 0
    assert qa["cohort_piids_matched_count"] == 2
    assert qa["unmatched_tx_piids_count"] == 0

    # Date audit
    date_audit = qa["date_audit"]
    assert date_audit["in_fy2020_count"] == 1
    assert date_audit["outside_fy2020_count"] == 2
    assert date_audit["min_action_date"] == "2018-01-10"
    assert date_audit["max_action_date"] == "2021-06-20"


# -----------------------------------------------------------------------------
# 8. Transaction Pilot & Diagnostics Tests
# -----------------------------------------------------------------------------


def test_bulk_diagnostic_quoted_503_preserved_as_service_issue() -> None:
    """run_bulk_diagnostic captures 503 on quoted probe without labeling it schema failure."""
    session = requests.Session()
    resp_503 = MagicMock()
    resp_503.status_code = 503
    resp_503.text = ""
    resp_503.headers = {"X-Server": "BIG-IP"}

    resp_200 = MagicMock()
    resp_200.status_code = 200
    resp_200.json.return_value = {"calculated_count": 11}
    resp_200.headers = {}

    sample_awards = [
        {"contract_award_unique_key": "A1", "award_id_piid": "P1"},
        {"contract_award_unique_key": "A2", "award_id_piid": "P2"},
    ]
    http_policy = {"timeout_seconds": 5, "max_retries": 1, "backoff_factor": 0.01, "retry_status_codes": [503]}

    with patch.object(session, "post", side_effect=[resp_503, resp_200]):
        diag = run_bulk_diagnostic(
            session=session,
            base_url="https://api.usaspending.gov",
            count_endpoint="/api/v2/download/count/",
            trusted_hosts=["api.usaspending.gov"],
            sample_awards=sample_awards,
            http_policy=http_policy,
        )

        assert diag["sample_size"] == 2
        quoted_probe = diag["probes"]["quoted_award_ids"]
        assert quoted_probe["status_code"] == 503
        assert "NOT be treated as evidence of invalid JSON" in quoted_probe["interpretation"]

        unquoted_probe = diag["probes"]["unquoted_award_ids"]
        assert unquoted_probe["status_code"] == 200
        assert unquoted_probe["calculated_count"] == 11


def test_audit_award_cohort_validates_generated_natural_ids() -> None:
    """audit_award_cohort asserts row count, nonblank unique keys, and nonblank unique PIIDs."""
    # Valid cohort
    valid_qa = {
        "row_count": 2,
        "unique_keys_count": 2,
        "blank_key_count": 0,
        "unique_piids_count": 2,
        "blank_piid_count": 0,
        "award_records": [
            {"contract_award_unique_key": "K1", "award_id_piid": "P1"},
            {"contract_award_unique_key": "K2", "award_id_piid": "P2"},
        ],
    }
    records = audit_award_cohort(valid_qa, expected_count=2)
    assert len(records) == 2

    # Blank natural key
    bad_key_qa = dict(valid_qa)
    bad_key_qa["blank_key_count"] = 1
    with pytest.raises(AwardCohortAuditError, match="blank contract_award_unique_key"):
        audit_award_cohort(bad_key_qa, expected_count=2)

    # Duplicate natural key
    dup_key_qa = dict(valid_qa)
    dup_key_qa["unique_keys_count"] = 1
    with pytest.raises(AwardCohortAuditError, match="Expected 2 unique contract_award_unique_key"):
        audit_award_cohort(dup_key_qa, expected_count=2)

    # Blank PIID
    bad_piid_qa = dict(valid_qa)
    bad_piid_qa["blank_piid_count"] = 1
    with pytest.raises(AwardCohortAuditError, match="blank award_id_piid"):
        audit_award_cohort(bad_piid_qa, expected_count=2)

    # Row count mismatch
    wrong_count_qa = dict(valid_qa)
    wrong_count_qa["row_count"] = 3
    with pytest.raises(AwardCohortAuditError, match="Expected 2 award rows"):
        audit_award_cohort(wrong_count_qa, expected_count=2)


def test_fetch_award_transactions_pagination_across_pages() -> None:
    """fetch_award_transactions iterates pages until hasNext is False."""
    session = requests.Session()
    http_policy = {"timeout_seconds": 5, "max_retries": 1, "backoff_factor": 0.01, "retry_status_codes": [503]}

    resp_p1 = MagicMock()
    resp_p1.status_code = 200
    resp_p1.json.return_value = {
        "page_metadata": {"page": 1, "hasNext": True},
        "results": [{"id": "TX_1", "action_date": "2020-01-15"}],
    }

    resp_p2 = MagicMock()
    resp_p2.status_code = 200
    resp_p2.json.return_value = {
        "page_metadata": {"page": 2, "hasNext": False},
        "results": [{"id": "TX_2", "action_date": "2021-02-10"}],
    }

    with patch.object(session, "post", side_effect=[resp_p1, resp_p2]):
        res = fetch_award_transactions(
            session=session,
            base_url="https://api.usaspending.gov",
            tx_endpoint="/api/v2/transactions/",
            award_unique_key="CONT_AWD_TEST",
            trusted_hosts=["api.usaspending.gov"],
            http_policy=http_policy,
            inter_request_delay=0.001,
        )

        assert res["status"] == "completed"
        assert res["total_transactions"] == 2
        assert res["pages_retrieved"] == 2
        assert [t["id"] for t in res["transactions"]] == ["TX_1", "TX_2"]


def test_fetch_award_transactions_detects_non_advancing_loop() -> None:
    """Non-advancing page number raises TransactionQualityError to prevent infinite loop."""
    session = requests.Session()
    http_policy = {"timeout_seconds": 5, "max_retries": 1, "backoff_factor": 0.01, "retry_status_codes": [503]}

    resp_bad = MagicMock()
    resp_bad.status_code = 200
    # Returns page 1 when page 1 was requested, but with hasNext=True, and then returns page 1 again
    resp_bad.json.return_value = {
        "page_metadata": {"page": 99, "hasNext": True},  # Mismatched page!
        "results": [{"id": "TX_1"}],
    }

    with (
        patch.object(session, "post", return_value=resp_bad),
        pytest.raises(TransactionQualityError, match="Page mismatch"),
    ):
        fetch_award_transactions(
            session=session,
            base_url="https://api.usaspending.gov",
            tx_endpoint="/api/v2/transactions/",
            award_unique_key="CONT_AWD_TEST",
            trusted_hosts=["api.usaspending.gov"],
            http_policy=http_policy,
        )


def test_transient_503_retry_behavior_with_retry_after() -> None:
    """fetch_award_transaction_count retries on 503 and honors Retry-After."""
    session = requests.Session()
    http_policy = {"timeout_seconds": 5, "max_retries": 3, "backoff_factor": 0.01, "retry_status_codes": [503]}

    resp_503 = MagicMock()
    resp_503.status_code = 503
    resp_503.headers = {"Retry-After": "0.01"}

    resp_200 = MagicMock()
    resp_200.status_code = 200
    resp_200.json.return_value = {"transactions": 6}

    with patch.object(session, "get", side_effect=[resp_503, resp_200]):
        res = fetch_award_transaction_count(
            session=session,
            base_url="https://api.usaspending.gov",
            endpoint_template="/api/v2/awards/count/transaction/{award_id}/",
            award_unique_key="CONT_AWD_TEST",
            trusted_hosts=["api.usaspending.gov"],
            http_policy=http_policy,
        )

        assert res["status_code"] == 200
        assert res["expected_count"] == 6
        assert res["attempts"] == 2


def test_non_retryable_client_errors_return_immediately() -> None:
    """Client errors (e.g. 404) return without exhausting max_retries."""
    session = requests.Session()
    http_policy = {"timeout_seconds": 5, "max_retries": 3, "backoff_factor": 0.01, "retry_status_codes": [503]}

    resp_404 = MagicMock()
    resp_404.status_code = 404
    resp_404.text = "Award Not Found"

    with patch.object(session, "get", return_value=resp_404):
        res = fetch_award_transaction_count(
            session=session,
            base_url="https://api.usaspending.gov",
            endpoint_template="/api/v2/awards/count/transaction/{award_id}/",
            award_unique_key="CONT_AWD_NONEXISTENT",
            trusted_hosts=["api.usaspending.gov"],
            http_policy=http_policy,
        )

        assert res["status_code"] == 404
        assert res["expected_count"] is None
        assert res["attempts"] == 1  # Exactly 1 attempt, no useless retries!


def test_malformed_and_empty_responses_handled_safely() -> None:
    """Non-JSON or malformed responses do not cause unhandled crashes."""
    session = requests.Session()
    http_policy = {"timeout_seconds": 5, "max_retries": 1, "backoff_factor": 0.01, "retry_status_codes": [503]}

    resp_bad_json = MagicMock()
    resp_bad_json.status_code = 200
    resp_bad_json.json.side_effect = ValueError("Invalid JSON")

    with patch.object(session, "get", return_value=resp_bad_json):
        res = fetch_award_transaction_count(
            session=session,
            base_url="https://api.usaspending.gov",
            endpoint_template="/api/v2/awards/count/transaction/{award_id}/",
            award_unique_key="CONT_AWD_TEST",
            trusted_hosts=["api.usaspending.gov"],
            http_policy=http_policy,
        )
        assert res["expected_count"] is None
        assert "Malformed JSON" in res["error"]


def test_duplicate_and_blank_transaction_ids_flagged(tmp_path: Path) -> None:
    """verify_transaction_archive_from_disk flags duplicate and blank transaction IDs."""
    tx_rows = [
        {"id": "T1", "cohort_award_unique_key": "A1", "action_date": "2020-05-01"},
        {"id": "T1", "cohort_award_unique_key": "A1", "action_date": "2020-06-01"},  # Duplicate T1
        {"id": "", "cohort_award_unique_key": "A1", "action_date": "2020-07-01"},    # Blank ID
    ]
    zip_bytes = create_test_zip("Contracts_PrimeTransactions.csv", tx_rows)
    tx_zip = tmp_path / "bad_tx.zip"
    tx_zip.write_bytes(zip_bytes)

    cohort = [{"contract_award_unique_key": "A1", "award_id_piid": "P1"}]
    expected_counts = {"A1": 3}

    res = verify_transaction_archive_from_disk(tx_zip, cohort, expected_counts)
    assert res["is_valid"] is False
    assert res["blank_ids_count"] == 1
    assert res["duplicate_ids_count"] == 1


def test_unexpected_off_cohort_awards_flagged(tmp_path: Path) -> None:
    """verify_transaction_archive_from_disk flags transactions linking to off-cohort awards."""
    tx_rows = [
        {"id": "T1", "cohort_award_unique_key": "A1", "action_date": "2020-05-01"},
        {"id": "T2", "cohort_award_unique_key": "OFF_COHORT_AWARD", "action_date": "2020-06-01"},
    ]
    zip_bytes = create_test_zip("Contracts_PrimeTransactions.csv", tx_rows)
    tx_zip = tmp_path / "off_cohort.zip"
    tx_zip.write_bytes(zip_bytes)

    cohort = [{"contract_award_unique_key": "A1", "award_id_piid": "P1"}]
    expected_counts = {"A1": 1}

    res = verify_transaction_archive_from_disk(tx_zip, cohort, expected_counts)
    assert res["is_valid"] is False
    assert res["unmatched_keys_count"] == 1


def test_resumability_cache_save_and_load(tmp_path: Path) -> None:
    """save_cached_award_result writes atomically and load_cached_award_result reads it back."""
    cache_dir = tmp_path / "tx_cache"
    data = {
        "award_unique_key": "CONT_AWD_TEST",
        "piid": "PIID_TEST",
        "status": "completed",
        "transactions": [{"id": "T1"}],
        "expected_count": 1,
    }

    save_cached_award_result(cache_dir, "CONT_AWD_TEST", data)
    assert not (cache_dir / "tx_CONT_AWD_TEST.json.tmp").exists()

    loaded = load_cached_award_result(cache_dir, "CONT_AWD_TEST")
    assert loaded is not None
    assert loaded["piid"] == "PIID_TEST"
    assert loaded["transactions"] == [{"id": "T1"}]


def test_honest_incomplete_status_when_retries_exhausted(tmp_path: Path) -> None:
    """process_all_cohort_transactions marks status incomplete when an award fails repeatedly."""
    session = requests.Session()
    cache_dir = tmp_path / "cache"
    http_policy = {"timeout_seconds": 5, "max_retries": 1, "backoff_factor": 0.01, "retry_status_codes": [500]}

    cohort = [{"contract_award_unique_key": "A1", "award_id_piid": "P1"}]

    resp_500 = MagicMock()
    resp_500.status_code = 500
    resp_500.text = "Internal Server Error"

    with patch.object(session, "get", return_value=resp_500), patch.object(session, "post", return_value=resp_500):
        res = process_all_cohort_transactions(
            session=session,
            base_url="https://api.usaspending.gov",
            count_template="/count/{award_id}/",
            tx_endpoint="/transactions/",
            trusted_hosts=["api.usaspending.gov"],
            cohort_awards=cohort,
            cache_dir=cache_dir,
            http_policy=http_policy,
        )

        assert res["status"] == "incomplete"
        assert res["failed_awards"] == 1
        assert len(res["failures"]) == 1
        assert res["failures"][0]["piid"] == "P1"


# -----------------------------------------------------------------------------
# 8. Redaction and Manual Archive Audit Tests
# -----------------------------------------------------------------------------


def test_redact_sensitive() -> None:
    """redact_sensitive masks bearer tokens and API keys."""
    text = "Authorization: Bearer secret_token_xyz"
    assert "[REDACTED]" in redact_sensitive(text)
    assert "secret_token_xyz" not in redact_sensitive(text)

    url = "https://api.usaspending.gov/download?api_key=secret123"
    assert "[REDACTED]" in redact_sensitive(url)
    assert "secret123" not in redact_sensitive(url)


def test_compare_with_manual_archives(tmp_path: Path) -> None:
    """compare_with_manual_archives inspects ON and OFF manual archives."""
    on_zip = tmp_path / "on.zip"
    on_zip.write_bytes(
        create_test_zip("Contracts_PrimeAwardSummaries.csv", [{"contract_award_unique_key": "A1"}])
    )
    off_zip = tmp_path / "off.zip"
    off_zip.write_bytes(
        create_test_zip("Contracts_PrimeAwardSummaries.csv", [{"contract_award_unique_key": "A2"}])
    )

    res = compare_with_manual_archives(on_zip, off_zip)
    assert res["manual_on"]["present"] is True
    assert res["manual_on"]["award_rows"] == 1
    assert res["manual_off"]["present"] is True
    assert res["manual_off"]["award_rows"] == 1


def test_aggregate_and_package_transactions(tmp_path: Path) -> None:
    """aggregate_and_package_transactions creates atomic ZIP with provenance fields and CRC check."""
    award_results = [
        {
            "award_unique_key": "CONT_AWD_1",
            "piid": "PIID_1",
            "transactions": [
                {"id": "T1", "action_date": "2020-01-01", "federal_action_obligation": 1000.0},
            ],
        },
        {
            "award_unique_key": "CONT_AWD_2",
            "piid": "PIID_2",
            "transactions": [
                {"id": "T2", "action_date": "2021-02-01", "federal_action_obligation": 2000.0},
            ],
        },
    ]
    target_zip = tmp_path / "test_tx.zip"
    meta = aggregate_and_package_transactions(award_results, target_zip, "20261028T000000Z")

    assert target_zip.is_file()
    assert meta["row_count"] == 2
    assert zipfile.is_zipfile(target_zip)

    with zipfile.ZipFile(target_zip, "r") as z:
        assert z.testzip() is None
        csv_name = next(n for n in z.namelist() if n.endswith(".csv"))
        with z.open(csv_name) as f:
            reader = csv.DictReader(io.TextIOWrapper(f, encoding="utf-8"))
            rows = list(reader)
            assert len(rows) == 2
            assert rows[0]["cohort_award_unique_key"] == "CONT_AWD_1"
            assert rows[0]["cohort_award_id_piid"] == "PIID_1"
            assert rows[1]["cohort_award_unique_key"] == "CONT_AWD_2"
            assert rows[1]["cohort_award_id_piid"] == "PIID_2"

