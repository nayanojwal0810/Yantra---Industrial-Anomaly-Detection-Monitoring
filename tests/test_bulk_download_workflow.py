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

from scripts.download_via_bulk_api import (
    ConfigError,
    DownloadJobError,
    DownloadJobTimeoutError,
    PrecheckValidationError,
    UntrustedHostError,
    ZIPValidationError,
    compare_with_manual_archive,
    download_zip_stream,
    execute_count_precheck,
    generate_manifest_and_report,
    initiate_bulk_download_job,
    inspect_zip_in_memory,
    load_config,
    parse_count_response,
    poll_download_status,
    redact_sensitive,
    resolve_api_url,
    run_bulk_download,
    validate_trusted_host,
)


@pytest.fixture
def sample_config(tmp_path: Path) -> dict[str, Any]:
    """Provide a validated sample configuration pointing to temporary paths."""
    manifest_file = tmp_path / "reports" / "test_manifest.json"
    report_file = tmp_path / "reports" / "test_report.md"
    raw_dir = tmp_path / "data" / "raw" / "sample"
    manual_zip = raw_dir / "NASA_2020.zip"

    return {
        "version": "1.0.0",
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
            "description": "NASA Awarding Agency, NAICS 541330, FY2020 action dates",
            "filters": {
                "award_type_codes": ["A", "B", "C", "D"],
                "agencies": [
                    {
                        "type": "awarding",
                        "tier": "toptier",
                        "name": "National Aeronautics and Space Administration",
                    }
                ],
                "naics_codes": ["541330"],
                "time_period": [
                    {
                        "start_date": "2019-10-01",
                        "end_date": "2020-09-30",
                        "date_type": "action_date",
                    }
                ],
            },
            "spending_levels": ["awards", "transactions"],
            "file_format": "csv",
        },
        "reference_ui_counts": {
            "awards": 785,
            "transactions": 1384,
        },
        "safety_caps": {
            "awards_max": 5000,
            "transactions_max": 25000,
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
            "raw_data_dir": str(raw_dir),
            "manual_archive_path": str(manual_zip),
            "manifest_path": str(manifest_file),
            "validation_report_path": str(report_file),
        },
    }


def create_test_zip(
    awards: list[dict[str, str]],
    transactions: list[dict[str, str]],
    include_subawards: bool = False,
) -> bytes:
    """Helper to create an in-memory ZIP bytes buffer containing CSV members."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        # Awards member
        if awards:
            out = io.StringIO()
            writer = csv.DictWriter(out, fieldnames=list(awards[0].keys()))
            writer.writeheader()
            writer.writerows(awards)
            z.writestr("Contracts_PrimeAwardSummaries_test.csv", out.getvalue())

        # Transactions member
        if transactions:
            out = io.StringIO()
            writer = csv.DictWriter(out, fieldnames=list(transactions[0].keys()))
            writer.writeheader()
            writer.writerows(transactions)
            z.writestr("Contracts_PrimeTransactions_test.csv", out.getvalue())

        # Subawards member (forbidden in workflow)
        if include_subawards:
            z.writestr("Contracts_Subawards_test.csv", "subaward_key,parent_award_key\nS1,A1\n")

    return buf.getvalue()


# -----------------------------------------------------------------------------
# 1. Configuration & Dry-run Tests
# -----------------------------------------------------------------------------


def test_dry_run_sends_zero_requests_and_writes_zero_raw_files(
    sample_config: dict[str, Any], tmp_path: Path
) -> None:
    """Dry run mode must not make network requests and must not create raw sample files."""
    cfg_path = tmp_path / "test_config.yaml"
    import yaml

    with cfg_path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(sample_config, f)

    with patch("requests.Session.post") as mock_post, patch("requests.Session.get") as mock_get:
        exit_code = run_bulk_download(config_path=cfg_path, confirm_download=False)

        assert exit_code == 0
        mock_post.assert_not_called()
        mock_get.assert_not_called()

        raw_dir = Path(sample_config["paths"]["raw_data_dir"])
        assert not raw_dir.exists() or len(list(raw_dir.glob("*.zip"))) == 0

        manifest_path = Path(sample_config["paths"]["manifest_path"])
        assert manifest_path.exists()
        manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
        assert manifest_data["run_status"] == "dry_run"


def test_load_config_rejects_unauthorized_cohort(sample_config: dict[str, Any], tmp_path: Path) -> None:
    """Config loader must refuse cohorts other than nasa_naics541330_fy2020."""
    sample_config["controlled_cohort"]["cohort_id"] = "dod_naics541715_fy2021"
    cfg_path = tmp_path / "bad_cohort_config.yaml"
    import yaml

    with cfg_path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(sample_config, f)

    with pytest.raises(ConfigError, match="Unsupported cohort"):
        load_config(cfg_path)


# -----------------------------------------------------------------------------
# 2. Host and URL Resolution Tests
# -----------------------------------------------------------------------------


def test_trusted_host_validation() -> None:
    """Trusted host validator must accept whitelisted hosts and reject others."""
    trusted = ["api.usaspending.gov", "files.usaspending.gov"]
    assert validate_trusted_host("https://api.usaspending.gov/endpoint", trusted)
    assert validate_trusted_host("https://files.usaspending.gov/download.zip", trusted)

    with pytest.raises(UntrustedHostError, match="not in trusted hosts list"):
        validate_trusted_host("https://attacker.com/download.zip", trusted)

    with pytest.raises(UntrustedHostError, match="not in trusted hosts list"):
        validate_trusted_host("https://subdomain.api.usaspending.gov.attacker.com/endpoint", trusted)


def test_resolve_api_url_relative_and_absolute() -> None:
    """resolve_api_url must handle both relative paths and absolute URLs safely."""
    base = "https://api.usaspending.gov"
    trusted = ["api.usaspending.gov", "files.usaspending.gov"]

    rel = resolve_api_url(base, "/api/v2/download/count/", trusted)
    assert rel == "https://api.usaspending.gov/api/v2/download/count/"

    abs_url = resolve_api_url(base, "https://files.usaspending.gov/bulk/sample.zip", trusted)
    assert abs_url == "https://files.usaspending.gov/bulk/sample.zip"


# -----------------------------------------------------------------------------
# 3. Count Precheck Parsing and Validation Tests
# -----------------------------------------------------------------------------


def test_parse_count_response_valid() -> None:
    """parse_count_response parses valid count endpoint payload."""
    payload = {
        "calculated_count": 785,
        "maximum_limit": 500000,
        "rows_gt_limit": False,
        "messages": [],
    }
    parsed = parse_count_response(payload, "awards")
    assert parsed["calculated_count"] == 785
    assert parsed["rows_gt_limit"] is False


def test_parse_count_response_rejects_booleans_and_malformed() -> None:
    """parse_count_response defensively rejects boolean or malformed counts."""
    # Boolean masquerading as number
    with pytest.raises(PrecheckValidationError, match="invalid calculated_count"):
        parse_count_response({"calculated_count": True}, "awards")

    # String masquerading as number
    with pytest.raises(PrecheckValidationError, match="invalid calculated_count"):
        parse_count_response({"calculated_count": "785"}, "awards")

    # Negative count
    with pytest.raises(PrecheckValidationError, match="negative calculated_count"):
        parse_count_response({"calculated_count": -5}, "awards")

    # rows_gt_limit = True
    with pytest.raises(PrecheckValidationError, match="rows_gt_limit=True"):
        parse_count_response({"calculated_count": 500000, "rows_gt_limit": True}, "awards")

    # transaction_rows_gt_limit = True
    with pytest.raises(PrecheckValidationError, match="transaction_rows_gt_limit=True"):
        parse_count_response(
            {"calculated_count": 500000, "transaction_rows_gt_limit": True}, "transactions"
        )


def test_execute_count_precheck_ui_count_mismatch_stops(sample_config: dict[str, Any]) -> None:
    """Precheck must raise PrecheckValidationError if count differs from reference UI count."""
    session = requests.Session()

    mock_resp_awards = MagicMock()
    mock_resp_awards.status_code = 200
    mock_resp_awards.json.return_value = {
        "calculated_count": 800,  # Expected 785!
        "rows_gt_limit": False,
    }

    with (
        patch.object(session, "post", return_value=mock_resp_awards),
        pytest.raises(PrecheckValidationError, match="Count precheck mismatch for awards"),
    ):
        execute_count_precheck(session, sample_config)


def test_execute_count_precheck_exceeding_safety_cap_stops(sample_config: dict[str, Any]) -> None:
    """Precheck must stop if calculated count exceeds configured safety cap."""
    session = requests.Session()

    sample_config["safety_caps"]["awards_max"] = 500
    sample_config["reference_ui_counts"]["awards"] = 785

    mock_resp_awards = MagicMock()
    mock_resp_awards.status_code = 200
    mock_resp_awards.json.return_value = {
        "calculated_count": 785,
        "rows_gt_limit": False,
    }

    with (
        patch.object(session, "post", return_value=mock_resp_awards),
        pytest.raises(PrecheckValidationError, match="exceeds safety cap"),
    ):
        execute_count_precheck(session, sample_config)


def test_execute_count_precheck_success(sample_config: dict[str, Any]) -> None:
    """Precheck succeeds when awards=785 and transactions=1384."""
    session = requests.Session()

    resp_awards = MagicMock()
    resp_awards.status_code = 200
    resp_awards.json.return_value = {
        "calculated_count": 785,
        "rows_gt_limit": False,
    }

    resp_tx = MagicMock()
    resp_tx.status_code = 200
    resp_tx.json.return_value = {
        "calculated_count": 1384,
        "rows_gt_limit": False,
    }

    with patch.object(session, "post", side_effect=[resp_awards, resp_tx]):
        result = execute_count_precheck(session, sample_config)
        assert result["awards"]["calculated_count"] == 785
        assert result["transactions"]["calculated_count"] == 1384


# -----------------------------------------------------------------------------
# 4. Asynchronous Bulk Download Job Creation & Polling Tests
# -----------------------------------------------------------------------------


def test_initiate_bulk_download_job_payload_shape(sample_config: dict[str, Any]) -> None:
    """Job creation must send exact filters, csv format, and awards+transactions spending level."""
    session = requests.Session()

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "file_name": "PrimeAwardSummariesAndTransactions_test.zip",
        "status_url": "/api/v2/download/status/?file_name=test.zip",
        "file_url": "https://files.usaspending.gov/test.zip",
        "download_request": {"spending_level": ["awards", "transactions"]},
    }

    with patch.object(session, "post", return_value=mock_resp) as mock_post:
        job = initiate_bulk_download_job(session, sample_config)

        assert job["file_name"] == "PrimeAwardSummariesAndTransactions_test.zip"
        assert "file_url" in job

        # Check call arguments
        call_kwargs = mock_post.call_args[1]
        payload = call_kwargs["json"]
        assert payload["file_format"] == "csv"
        assert payload["spending_level"] == ["awards", "transactions"]
        assert "columns" not in payload  # Must preserve full schema
        assert payload["filters"]["award_type_codes"] == ["A", "B", "C", "D"]
        assert payload["filters"]["time_period"][0]["date_type"] == "action_date"


def test_poll_download_status_transitions_running_to_finished(sample_config: dict[str, Any]) -> None:
    """Polling transitions through running -> finished correctly."""
    session = requests.Session()
    job_info = {
        "file_name": "test.zip",
        "status_url": "/api/v2/download/status/?file_name=test.zip",
        "file_url": "https://files.usaspending.gov/test.zip",
    }

    resp1 = MagicMock()
    resp1.status_code = 200
    resp1.json.return_value = {"status": "running", "message": "In progress"}

    resp2 = MagicMock()
    resp2.status_code = 200
    resp2.json.return_value = {
        "status": "finished",
        "url": "https://files.usaspending.gov/test.zip",
        "message": "Complete",
    }

    with patch.object(session, "get", side_effect=[resp1, resp2]):
        result = poll_download_status(session, job_info, sample_config)
        assert result["final_status"] == "finished"
        assert result["file_url"] == "https://files.usaspending.gov/test.zip"
        assert len(result["history"]) == 2


def test_poll_download_status_failed_raises_error(sample_config: dict[str, Any]) -> None:
    """Polling server failure raises DownloadJobError with server message."""
    session = requests.Session()
    job_info = {
        "file_name": "test.zip",
        "status_url": "/api/v2/download/status/?file_name=test.zip",
    }

    resp_failed = MagicMock()
    resp_failed.status_code = 200
    resp_failed.json.return_value = {
        "status": "failed",
        "message": "Out of memory processing transaction records",
    }

    with (
        patch.object(session, "get", return_value=resp_failed),
        pytest.raises(DownloadJobError, match="Out of memory processing"),
    ):
        poll_download_status(session, job_info, sample_config)


def test_poll_download_status_timeout_stops_without_resubmit(sample_config: dict[str, Any]) -> None:
    """Polling exceeding timeout raises DownloadJobTimeoutError."""
    session = requests.Session()
    job_info = {
        "file_name": "test.zip",
        "status_url": "/api/v2/download/status/?file_name=test.zip",
    }
    sample_config["polling_policy"]["overall_timeout_seconds"] = 0.05
    sample_config["polling_policy"]["poll_interval_seconds"] = 0.02

    resp_running = MagicMock()
    resp_running.status_code = 200
    resp_running.json.return_value = {"status": "running", "message": "Still running"}

    with patch.object(session, "get", return_value=resp_running), patch.object(session, "post") as mock_post:
        with pytest.raises(DownloadJobTimeoutError, match="Polling timed out"):
            poll_download_status(session, job_info, sample_config)

        # Must not resubmit job
        mock_post.assert_not_called()


# -----------------------------------------------------------------------------
# 5. Streaming Download and Atomic Save Tests
# -----------------------------------------------------------------------------


def test_download_zip_stream_atomic_rename(sample_config: dict[str, Any], tmp_path: Path) -> None:
    """Download streams to .part file and atomically renames on success."""
    session = requests.Session()
    target_zip = tmp_path / "downloads" / "final.zip"

    zip_bytes = create_test_zip(
        awards=[{"contract_award_unique_key": "AW1", "award_id_piid": "PIID1"}],
        transactions=[{
            "contract_transaction_unique_key": "TX1",
            "contract_award_unique_key": "AW1",
            "action_date": "2020-05-01",
        }],
    )

    mock_resp = MagicMock()
    mock_resp.__enter__.return_value = mock_resp
    mock_resp.status_code = 200
    mock_resp.iter_content.return_value = [zip_bytes]

    with patch.object(session, "get", return_value=mock_resp):
        res = download_zip_stream(
            session,
            "https://files.usaspending.gov/test.zip",
            target_zip,
            sample_config,
        )

        assert res.is_file()
        assert not target_zip.with_suffix(".zip.part").exists()
        assert zipfile.is_zipfile(target_zip)


def test_download_zip_stream_refuses_to_overwrite_existing(
    sample_config: dict[str, Any], tmp_path: Path
) -> None:
    """download_zip_stream must raise FileExistsError if target already exists."""
    session = requests.Session()
    target_zip = tmp_path / "already_exists.zip"
    target_zip.write_text("existing data", encoding="utf-8")

    with pytest.raises(FileExistsError, match="Target download path already exists"):
        download_zip_stream(
            session,
            "https://files.usaspending.gov/test.zip",
            target_zip,
            sample_config,
        )


def test_download_zip_stream_corrupt_zip_fails_safely(
    sample_config: dict[str, Any], tmp_path: Path
) -> None:
    """Corrupt streamed content cleans up temporary .part and raises ZIPValidationError."""
    session = requests.Session()
    target_zip = tmp_path / "bad.zip"

    mock_resp = MagicMock()
    mock_resp.__enter__.return_value = mock_resp
    mock_resp.status_code = 200
    mock_resp.iter_content.return_value = [b"NOT A VALID ZIP ARCHIVE CONTENT"]

    with patch.object(session, "get", return_value=mock_resp):
        with pytest.raises(ZIPValidationError, match="not a valid ZIP archive"):
            download_zip_stream(
                session,
                "https://files.usaspending.gov/bad.zip",
                target_zip,
                sample_config,
            )

        assert not target_zip.exists()
        assert not target_zip.with_suffix(".zip.part").exists()


# -----------------------------------------------------------------------------
# 6. In-Memory ZIP Quality Inspection and Linkage Tests
# -----------------------------------------------------------------------------


def test_inspect_zip_in_memory_metrics(tmp_path: Path) -> None:
    """In-memory QA correctly calculates row counts, keys, linkage, and date coverage."""
    awards = [
        {"contract_award_unique_key": "A1", "award_id_piid": "P1"},
        {"contract_award_unique_key": "A2", "award_id_piid": "P2"},
    ]
    transactions = [
        {
            "contract_transaction_unique_key": "T1",
            "contract_award_unique_key": "A1",
            "action_date": "2019-11-15",  # In FY2020
        },
        {
            "contract_transaction_unique_key": "T2",
            "contract_award_unique_key": "A1",
            "action_date": "2020-03-20",  # In FY2020
        },
        {
            "contract_transaction_unique_key": "T3",
            "contract_award_unique_key": "A2",
            "action_date": "2020-08-10",  # In FY2020
        },
        {
            "contract_transaction_unique_key": "T4",
            "contract_award_unique_key": "A999",  # Unlinked!
            "action_date": "2021-02-01",  # Out of FY2020!
        },
    ]

    zip_bytes = create_test_zip(awards, transactions)
    zip_path = tmp_path / "sample_qa.zip"
    zip_path.write_bytes(zip_bytes)

    qa = inspect_zip_in_memory(zip_path)

    # Awards QA
    assert qa["awards"]["row_count"] == 2
    assert qa["awards"]["unique_keys_count"] == 2
    assert qa["awards"]["missing_keys_count"] == 0
    assert qa["awards"]["duplicate_keys_count"] == 0

    # Transactions QA
    assert qa["transactions"]["row_count"] == 4
    assert qa["transactions"]["unique_keys_count"] == 4
    assert qa["transactions"]["unique_award_keys_referenced"] == 3  # A1, A2, A999
    assert qa["transactions"]["linkage_referenced_in_awards_count"] == 2  # A1, A2
    # 2 out of 3 awards linked = 66.67%
    assert qa["transactions"]["linkage_percentage"] == 66.67

    # Date audit
    date_audit = qa["transactions"]["action_date_audit"]
    assert date_audit["in_fy_count"] == 3
    assert date_audit["out_of_fy_count"] == 1
    assert len(date_audit["deviations_sample"]) == 1
    assert date_audit["deviations_sample"][0]["transaction_key"] == "T4"


def test_inspect_zip_in_memory_rejects_subawards(tmp_path: Path) -> None:
    """inspect_zip_in_memory must reject any ZIP containing subaward members."""
    zip_bytes = create_test_zip(
        awards=[{"contract_award_unique_key": "A1"}],
        transactions=[{"contract_transaction_unique_key": "T1", "contract_award_unique_key": "A1", "action_date": "2020-01-01"}],
        include_subawards=True,
    )
    zip_path = tmp_path / "has_subawards.zip"
    zip_path.write_bytes(zip_bytes)

    with pytest.raises(ZIPValidationError, match="unexpected subaward members"):
        inspect_zip_in_memory(zip_path)


def test_compare_with_manual_archive(tmp_path: Path) -> None:
    """compare_with_manual_archive correctly calculates key overlap without altering files."""
    awards_api = [
        {"contract_award_unique_key": "A1"},
        {"contract_award_unique_key": "A2"},
    ]
    tx_api = [
        {"contract_transaction_unique_key": "T1", "contract_award_unique_key": "A1", "action_date": "2020-01-01"},
        {"contract_transaction_unique_key": "T2", "contract_award_unique_key": "A2", "action_date": "2020-01-01"},
    ]
    api_zip = tmp_path / "api.zip"
    api_zip.write_bytes(create_test_zip(awards_api, tx_api))
    api_qa = inspect_zip_in_memory(api_zip)

    awards_manual = [
        {"contract_award_unique_key": "A1"},
        {"contract_award_unique_key": "A3"},
    ]
    tx_manual = [
        {"contract_transaction_unique_key": "T1", "contract_award_unique_key": "A1", "action_date": "2020-01-01"},
        {"contract_transaction_unique_key": "T3", "contract_award_unique_key": "A3", "action_date": "2020-01-01"},
    ]
    manual_zip = tmp_path / "NASA_2020.zip"
    manual_zip.write_bytes(create_test_zip(awards_manual, tx_manual))

    overlap = compare_with_manual_archive(api_qa, manual_zip)

    assert overlap["manual_archive_present"] is True
    assert overlap["award_keys_overlap_count"] == 1  # A1
    assert overlap["award_keys_manual_only"] == 1  # A3
    assert overlap["award_keys_api_only"] == 1  # A2
    assert overlap["tx_keys_overlap_count"] == 1  # T1


# -----------------------------------------------------------------------------
# 7. Redaction and Manifest Formatting Tests
# -----------------------------------------------------------------------------


def test_redact_sensitive() -> None:
    """redact_sensitive masks bearer tokens and query parameter secrets."""
    auth_header = "Authorization: Bearer secret_token_xyz_12345"
    redacted = redact_sensitive(auth_header)
    assert "[REDACTED]" in redacted
    assert "secret_token_xyz_12345" not in redacted

    url = "https://api.usaspending.gov/endpoint?api_key=my_super_secret_key&other=param"
    redacted_url = redact_sensitive(url)
    assert "[REDACTED]" in redacted_url
    assert "my_super_secret_key" not in redacted_url


def test_generate_manifest_and_report_mismatch(sample_config: dict[str, Any]) -> None:
    """generate_manifest_and_report records count_mismatch status properly."""
    manifest, report = generate_manifest_and_report(
        sample_config,
        run_status="count_mismatch",
        error_message="API returned 800 awards instead of 785",
    )
    assert manifest["run_status"] == "count_mismatch"
    assert "800 awards" in manifest["error_message"]
    assert "count_mismatch" in report
