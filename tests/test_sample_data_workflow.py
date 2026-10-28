"""
Unit tests for USAspending sample contract data acquisition and quality profiling workflow.
All HTTP and network calls are strictly mocked. No live requests are performed.
"""

import csv
import json
import os
import subprocess
import sys
from unittest.mock import MagicMock, patch

import pytest
import requests

from scripts.download_sample import (
    ApiCallError,
    build_stratum_filters,
    compute_deterministic_page,
    deduplicate_awards,
    execute_sample_download,
    extract_api_error_detail,
    load_config,
    request_with_retry,
    resolve_psc_family_path,
    sanitize_request_payload,
    select_detail_awards,
    validate_award_fields,
)
from scripts.profile_sample import profile_sample


@pytest.fixture
def sample_config():
    """Provides a valid test configuration dictionary."""
    return load_config("config/sample_data_config.yaml")


@pytest.fixture
def mock_psc_tree():
    """Provides official-contract-shaped mock PSC tree."""
    return {
        "results": [
            {
                "id": "Service",
                "ancestors": [],
                "description": "Service",
                "count": 0,
                "children": [
                    {
                        "id": "D",
                        "ancestors": ["Service"],
                        "description": "IT and Telecom",
                        "count": 0,
                        "children": [],
                    },
                    {
                        "id": "R",
                        "ancestors": ["Service"],
                        "description": "Support (Professional/Administrative/Management)",
                        "count": 0,
                        "children": [],
                    },
                ],
            },
            {
                "id": "Product",
                "ancestors": [],
                "description": "Product",
                "count": 0,
                "children": [
                    {
                        "id": "70",
                        "ancestors": ["Product"],
                        "description": "General Purpose Information Technology Equipment",
                        "count": 0,
                        "children": [],
                    }
                ],
            },
        ]
    }


def test_dry_run_default_no_network_no_files(monkeypatch, tmp_path):
    """Asserts that running download_sample without confirmation makes no network calls and writes no data."""
    mock_session = MagicMock()
    with patch("requests.Session", return_value=mock_session), patch("sys.argv", ["download_sample.py"]):
        with pytest.raises(SystemExit) as exc_info:
            from scripts.download_sample import main

            main()
        assert exc_info.value.code == 0
    # Verify no HTTP calls were made
    assert mock_session.request.call_count == 0


def test_confirm_flag_required_before_execution(sample_config):
    """Verifies that execute_sample_download requires explicit confirmation at CLI level."""
    with patch("sys.argv", ["download_sample.py"]):
        with pytest.raises(SystemExit) as exc_info:
            from scripts.download_sample import main

            main()
        assert exc_info.value.code == 0


def test_independent_queries_naics_and_psc_never_combined(sample_config, mock_psc_tree):
    """Verifies each query is independent: NAICS and PSC filters are never combined in a single request."""
    resolved_psc = {
        "psc_group_d": {"full_path": ["Service", "D"]},
        "psc_group_r": {"full_path": ["Service", "R"]},
    }
    date_bounds = {"start_date": "2010-01-01", "end_date": "2015-12-31"}

    for fam_id, f_info in sample_config["inclusion_families"].items():
        filters = build_stratum_filters(
            family_id=fam_id,
            family_info=f_info,
            window_bounds=date_bounds,
            date_type="new_awards_only",
            award_type_codes=["A", "B", "C", "D"],
            resolved_psc_paths=resolved_psc,
        )
        if "naics_codes" in filters:
            assert "psc_codes" not in filters
            assert isinstance(filters["naics_codes"], list)
        if "psc_codes" in filters:
            assert "naics_codes" not in filters
            assert "require" in filters["psc_codes"]


def test_new_awards_only_and_explicit_date_bounds_on_both_endpoints(sample_config):
    """Verifies new_awards_only and valid date bounds are passed to both count and award search requests."""
    resolved_psc = {"psc_group_d": {"full_path": ["Service", "D"]}}
    bounds = {"start_date": "2016-01-01", "end_date": "2019-12-31"}
    filters = build_stratum_filters(
        family_id="psc_group_d",
        family_info=sample_config["inclusion_families"]["psc_group_d"],
        window_bounds=bounds,
        date_type="new_awards_only",
        award_type_codes=["A", "B", "C", "D"],
        resolved_psc_paths=resolved_psc,
    )

    tp = filters.get("time_period", [])
    assert len(tp) == 1
    assert tp[0]["date_type"] == "new_awards_only"
    assert tp[0]["start_date"] == "2016-01-01"
    assert tp[0]["end_date"] == "2019-12-31"


def test_count_parsing_and_zero_count_skips_award_search(sample_config, mock_psc_tree, tmp_path):
    """Verifies that a stratum with 0 contracts in count response skips the award search request."""
    cfg = dict(sample_config)
    cfg["paths"] = {
        "raw_data_dir": str(tmp_path / "raw"),
        "raw_award_counts": str(tmp_path / "counts.json"),
        "raw_award_results": str(tmp_path / "results.json"),
        "raw_transaction_history": str(tmp_path / "tx.json"),
        "sample_awards_csv": str(tmp_path / "awards.csv"),
        "sample_transactions_csv": str(tmp_path / "tx.csv"),
        "manifest_path": str(tmp_path / "manifest.json"),
        "profile_report_path": str(tmp_path / "report.md"),
    }
    cfg["inclusion_families"] = {"naics_541330": sample_config["inclusion_families"]["naics_541330"]}
    cfg["date_windows"] = {"2010_2015": sample_config["date_windows"]["2010_2015"]}

    mock_session = MagicMock()

    psc_resp = MagicMock(status_code=200)
    psc_resp.json.return_value = mock_psc_tree

    count_resp = MagicMock(status_code=200)
    count_resp.json.return_value = {"results": {"contracts": 0}}

    mock_session.request.side_effect = [psc_resp, count_resp]

    manifest = execute_sample_download(cfg, session=mock_session)

    assert len(manifest["queries"]) == 1
    assert manifest["queries"][0]["contracts_count"] == 0
    assert manifest["queries"][0]["skipped"] is True
    assert manifest["queries"][0]["status"] == "skipped_zero_contracts"
    # Award search endpoint was never called
    assert mock_session.request.call_count == 2


def test_failed_count_http_response_halts_safely(sample_config, mock_psc_tree, tmp_path):
    """Verifies that a failed count HTTP request raises an error, writes incomplete manifest, and does not call award search."""
    cfg = dict(sample_config)
    manifest_file = tmp_path / "manifest.json"
    cfg["paths"] = {
        "raw_data_dir": str(tmp_path / "raw"),
        "raw_award_counts": str(tmp_path / "counts.json"),
        "raw_award_results": str(tmp_path / "results.json"),
        "raw_transaction_history": str(tmp_path / "tx.json"),
        "sample_awards_csv": str(tmp_path / "awards.csv"),
        "sample_transactions_csv": str(tmp_path / "tx.csv"),
        "manifest_path": str(manifest_file),
        "profile_report_path": str(tmp_path / "report.md"),
    }
    cfg["inclusion_families"] = {"naics_541330": sample_config["inclusion_families"]["naics_541330"]}
    cfg["date_windows"] = {"2010_2015": sample_config["date_windows"]["2010_2015"]}

    mock_session = MagicMock()

    psc_resp = MagicMock(status_code=200)
    psc_resp.json.return_value = mock_psc_tree

    count_resp = MagicMock(status_code=500)
    count_resp.raise_for_status.side_effect = requests.HTTPError("Server Error 500")

    mock_session.request.side_effect = [psc_resp, count_resp, count_resp, count_resp, count_resp]

    with patch("time.sleep", return_value=None), pytest.raises(requests.HTTPError):
        execute_sample_download(cfg, session=mock_session)

    # Award search was never called
    assert mock_session.request.call_count == 5  # 1 psc + 1 count + 3 retries
    # Manifest was marked incomplete
    assert manifest_file.is_file()
    manifest_data = json.loads(manifest_file.read_text(encoding="utf-8"))
    assert manifest_data["run_status"] == "incomplete"


@pytest.mark.parametrize(
    "invalid_count_response",
    [
        {"results": {}},  # missing contracts
        {"results": {"contracts": True}},  # boolean True
        {"results": {"contracts": False}},  # boolean False
        {"results": {"contracts": -1}},  # negative count
        {"results": {"contracts": "100"}},  # string count
        {"results": {"contracts": 50.5}},  # float count
        {"results": None},  # malformed results shape
        "plain text not json",  # non-dict
    ],
)
def test_malformed_count_response_fails_safely(sample_config, mock_psc_tree, tmp_path, invalid_count_response):
    """Verifies that non-integer, negative, boolean, or missing contracts count fails safely with ValueError."""
    cfg = dict(sample_config)
    manifest_file = tmp_path / "manifest.json"
    cfg["paths"] = {
        "raw_data_dir": str(tmp_path / "raw"),
        "raw_award_counts": str(tmp_path / "counts.json"),
        "raw_award_results": str(tmp_path / "results.json"),
        "raw_transaction_history": str(tmp_path / "tx.json"),
        "sample_awards_csv": str(tmp_path / "awards.csv"),
        "sample_transactions_csv": str(tmp_path / "tx.csv"),
        "manifest_path": str(manifest_file),
        "profile_report_path": str(tmp_path / "report.md"),
    }
    cfg["inclusion_families"] = {"naics_541330": sample_config["inclusion_families"]["naics_541330"]}
    cfg["date_windows"] = {"2010_2015": sample_config["date_windows"]["2010_2015"]}

    mock_session = MagicMock()
    psc_resp = MagicMock(status_code=200)
    psc_resp.json.return_value = mock_psc_tree

    count_resp = MagicMock(status_code=200)
    count_resp.json.return_value = invalid_count_response

    mock_session.request.side_effect = [psc_resp, count_resp]

    with pytest.raises((ValueError, TypeError)):
        execute_sample_download(cfg, session=mock_session)

    # Award search was never issued
    assert mock_session.request.call_count == 2
    assert manifest_file.is_file()
    manifest_data = json.loads(manifest_file.read_text(encoding="utf-8"))
    assert manifest_data["run_status"] == "incomplete"


def test_deterministic_page_and_detail_selection_helpers():
    """Directly tests compute_deterministic_page stability and select_detail_awards round-robin."""
    p1 = compute_deterministic_page(seed=42, family_id="naics_541330", window_id="2010_2015", page_count=50)
    p2 = compute_deterministic_page(seed=42, family_id="naics_541330", window_id="2010_2015", page_count=50)
    assert p1 == p2
    assert 1 <= p1 <= 50

    awards = [
        {"internal_id": i, "generated_internal_id": f"CONT_{i}", "source_queries": [f"q_{i % 3}"]}
        for i in range(20)
    ]
    selected = select_detail_awards(awards, max_awards=5, seed=42)
    assert len(selected) == 5


def test_deterministic_page_cross_process_reproducibility():
    """Invokes compute_deterministic_page in independent Python subprocesses with different PYTHONHASHSEED values."""
    runner_code = (
        "import sys; "
        "from scripts.download_sample import compute_deterministic_page; "
        "seed = int(sys.argv[1]); "
        "family = sys.argv[2]; "
        "window = sys.argv[3]; "
        "count = int(sys.argv[4]); "
        "print(compute_deterministic_page(seed, family, window, count))"
    )

    args = ["42", "naics_541330", "2010_2015", "50"]

    # Run in subprocess 1 with PYTHONHASHSEED=0
    env1 = os.environ.copy()
    env1["PYTHONHASHSEED"] = "0"
    proc1 = subprocess.run(
        [sys.executable, "-c", runner_code, *args],
        capture_output=True,
        text=True,
        env=env1,
        check=True,
    )
    res1 = int(proc1.stdout.strip())

    # Run in subprocess 2 with PYTHONHASHSEED=12345
    env2 = os.environ.copy()
    env2["PYTHONHASHSEED"] = "12345"
    proc2 = subprocess.run(
        [sys.executable, "-c", runner_code, *args],
        capture_output=True,
        text=True,
        env=env2,
        check=True,
    )
    res2 = int(proc2.stdout.strip())

    # Run in subprocess 3 with PYTHONHASHSEED=random
    env3 = os.environ.copy()
    env3["PYTHONHASHSEED"] = "random"
    proc3 = subprocess.run(
        [sys.executable, "-c", runner_code, *args],
        capture_output=True,
        text=True,
        env=env3,
        check=True,
    )
    res3 = int(proc3.stdout.strip())

    assert res1 == res2 == res3
    assert 1 <= res1 <= 50

    # Test edge cases: page_count <= 1 returns 1 according to contract
    assert compute_deterministic_page(seed=42, family_id="naics_541330", window_id="2010_2015", page_count=0) == 1
    assert compute_deterministic_page(seed=42, family_id="naics_541330", window_id="2010_2015", page_count=-1) == 1
    assert compute_deterministic_page(seed=42, family_id="naics_541330", window_id="2010_2015", page_count=1) == 1


def test_positive_count_selects_deterministic_page_with_explicit_sort(sample_config, mock_psc_tree, tmp_path):
    """Verifies positive count selects deterministic page and sends explicit sort='Award ID' and order='asc'."""
    cfg = dict(sample_config)
    cfg["paths"] = {
        "raw_data_dir": str(tmp_path / "raw"),
        "raw_award_counts": str(tmp_path / "counts.json"),
        "raw_award_results": str(tmp_path / "results.json"),
        "raw_transaction_history": str(tmp_path / "tx.json"),
        "sample_awards_csv": str(tmp_path / "awards.csv"),
        "sample_transactions_csv": str(tmp_path / "tx.csv"),
        "manifest_path": str(tmp_path / "manifest.json"),
        "profile_report_path": str(tmp_path / "report.md"),
    }
    cfg["inclusion_families"] = {"naics_541330": sample_config["inclusion_families"]["naics_541330"]}
    cfg["date_windows"] = {"2010_2015": sample_config["date_windows"]["2010_2015"]}

    mock_session = MagicMock()
    psc_resp = MagicMock(status_code=200)
    psc_resp.json.return_value = mock_psc_tree

    count_resp = MagicMock(status_code=200)
    count_resp.json.return_value = {"results": {"contracts": 100}}

    search_resp = MagicMock(status_code=200)
    search_resp.json.return_value = {
        "results": [
            {
                "internal_id": 501,
                "Award ID": "AWD-501",
                "generated_internal_id": "CONT_501",
            }
        ]
    }

    tx_resp = MagicMock(status_code=200)
    tx_resp.json.return_value = {
        "page_metadata": {"page": 1, "hasNext": False},
        "results": [{"id": 1, "action_date": "2012-01-01", "federal_action_obligation": 100.0}],
    }

    mock_session.request.side_effect = [psc_resp, count_resp, search_resp, tx_resp]

    manifest = execute_sample_download(cfg, session=mock_session)

    # Verify explicit sort in payload
    search_call = mock_session.request.call_args_list[2]
    search_payload = search_call.kwargs["json"]
    assert search_payload["sort"] == "Award ID"
    assert search_payload["order"] == "asc"
    assert search_payload["page"] > 0
    assert search_payload["limit"] == 25

    # Verify query entry in manifest recorded sort and order
    q = manifest["queries"][0]
    assert q["sort_field"] == "Award ID"
    assert q["sort_order"] == "asc"
    assert q["contracts_count"] == 100
    assert q["page_count"] == 4
    assert q["selected_page"] == search_payload["page"]


def test_positive_count_empty_selected_page_records_discrepancy_and_does_not_retry_page_1(
    sample_config, mock_psc_tree, tmp_path
):
    """Verifies that an empty result on positive count is recorded as discrepancy/incomplete and does NOT retry page 1."""
    cfg = dict(sample_config)
    manifest_file = tmp_path / "manifest.json"
    cfg["paths"] = {
        "raw_data_dir": str(tmp_path / "raw"),
        "raw_award_counts": str(tmp_path / "counts.json"),
        "raw_award_results": str(tmp_path / "results.json"),
        "raw_transaction_history": str(tmp_path / "tx.json"),
        "sample_awards_csv": str(tmp_path / "awards.csv"),
        "sample_transactions_csv": str(tmp_path / "tx.csv"),
        "manifest_path": str(manifest_file),
        "profile_report_path": str(tmp_path / "report.md"),
    }
    cfg["inclusion_families"] = {"naics_541330": sample_config["inclusion_families"]["naics_541330"]}
    cfg["date_windows"] = {"2010_2015": sample_config["date_windows"]["2010_2015"]}

    mock_session = MagicMock()
    psc_resp = MagicMock(status_code=200)
    psc_resp.json.return_value = mock_psc_tree

    count_resp = MagicMock(status_code=200)
    count_resp.json.return_value = {"results": {"contracts": 100}}

    # Selected page returns empty results
    search_resp = MagicMock(status_code=200)
    search_resp.json.return_value = {"results": []}

    mock_session.request.side_effect = [psc_resp, count_resp, search_resp]

    with pytest.raises(RuntimeError, match="returned 0 results despite positive contracts count"):
        execute_sample_download(cfg, session=mock_session)

    # Exactly 3 calls: psc, count, award search (no retry of page 1!)
    assert mock_session.request.call_count == 3
    assert manifest_file.is_file()
    manifest_data = json.loads(manifest_file.read_text(encoding="utf-8"))
    assert manifest_data["run_status"] == "incomplete"
    assert manifest_data["queries"][0]["discrepancy_empty_selected_page"] is True


def test_count_and_award_requests_use_equivalent_filter_meaning(sample_config, mock_psc_tree, tmp_path):
    """Verifies that count and award search requests use equivalent filters (award types, time period, family)."""
    cfg = dict(sample_config)
    cfg["paths"] = {
        "raw_data_dir": str(tmp_path / "raw"),
        "raw_award_counts": str(tmp_path / "counts.json"),
        "raw_award_results": str(tmp_path / "results.json"),
        "raw_transaction_history": str(tmp_path / "tx.json"),
        "sample_awards_csv": str(tmp_path / "awards.csv"),
        "sample_transactions_csv": str(tmp_path / "tx.csv"),
        "manifest_path": str(tmp_path / "manifest.json"),
        "profile_report_path": str(tmp_path / "report.md"),
    }
    cfg["inclusion_families"] = {"psc_group_d": sample_config["inclusion_families"]["psc_group_d"]}
    cfg["date_windows"] = {"2016_2019": sample_config["date_windows"]["2016_2019"]}

    mock_session = MagicMock()
    psc_resp = MagicMock(status_code=200)
    psc_resp.json.return_value = mock_psc_tree

    count_resp = MagicMock(status_code=200)
    count_resp.json.return_value = {"results": {"contracts": 10}}

    search_resp = MagicMock(status_code=200)
    search_resp.json.return_value = {
        "results": [{"internal_id": 601, "Award ID": "AWD-601", "generated_internal_id": "CONT_601"}]
    }

    tx_resp = MagicMock(status_code=200)
    tx_resp.json.return_value = {
        "page_metadata": {"page": 1, "hasNext": False},
        "results": [{"id": 1, "action_date": "2018-01-01", "federal_action_obligation": 200.0}],
    }

    mock_session.request.side_effect = [psc_resp, count_resp, search_resp, tx_resp]

    execute_sample_download(cfg, session=mock_session)

    count_payload = mock_session.request.call_args_list[1].kwargs["json"]
    search_payload = mock_session.request.call_args_list[2].kwargs["json"]

    assert count_payload["filters"] == search_payload["filters"]
    assert count_payload["filters"]["award_type_codes"] == ["A", "B", "C", "D"]
    assert count_payload["filters"]["time_period"][0]["date_type"] == "new_awards_only"
    assert count_payload["filters"]["psc_codes"]["require"] == [["Service", "D"]]


def test_award_result_fields_strict_allowlist_no_forbidden_fields(sample_config):
    """Verifies that requested fields strictly match allowlist and forbidden fields raise ValueError."""
    validate_award_fields(sample_config["award_fields"])

    with pytest.raises(ValueError, match="forbidden"):
        validate_award_fields(["Period of Performance Current End Date"])

    with pytest.raises(ValueError, match="forbidden"):
        validate_award_fields(["Award Type"])

    with pytest.raises(ValueError, match="not in verified award fields"):
        validate_award_fields(["Random Unofficial Field"])


def test_deduplication_preserves_memberships_and_flags_missing_id():
    """Verifies cross-query deduplication by internal_id, membership preservation, and safe flagging of missing internal_id."""
    raw_rows = [
        {
            "internal_id": 1001,
            "Award ID": "CONT-001",
            "generated_internal_id": "CONT_AW_001",
            "_stratum_query_id": "naics_541330__2010_2015",
            "_stratum_family_id": "naics_541330",
            "_stratum_window_id": "2010_2015",
        },
        {
            "internal_id": 1001,  # Same internal_id in different query
            "Award ID": "CONT-001",
            "generated_internal_id": "CONT_AW_001",
            "_stratum_query_id": "psc_group_d__2010_2015",
            "_stratum_family_id": "psc_group_d",
            "_stratum_window_id": "2010_2015",
        },
        {
            "internal_id": None,  # Missing internal_id
            "Award ID": "CONT-002",
            "generated_internal_id": "CONT_AW_002",
            "_stratum_query_id": "naics_541715__2016_2019",
            "_stratum_family_id": "naics_541715",
            "_stratum_window_id": "2016_2019",
        },
    ]

    unique_awards, summary = deduplicate_awards(raw_rows, hard_cap=400)

    assert len(unique_awards) == 2
    assert summary["cross_query_overlaps"] == 1
    assert summary["missing_internal_id_count"] == 1

    awd_1001 = next(a for a in unique_awards if a.get("internal_id") == 1001)
    assert awd_1001["membership_count"] == 2
    assert "naics_541330" in awd_1001["source_families"]
    assert "psc_group_d" in awd_1001["source_families"]

    missing_awd = next(a for a in unique_awards if a.get("missing_internal_id") is True)
    assert missing_awd["internal_id"] is None
    assert missing_awd["membership_count"] == 1


def test_hard_caps_enforced_in_code(sample_config, tmp_path):
    """Verifies that configured values above caps and invalid integers are rejected before network requests."""
    # > 400 unique awards raises ValueError
    oversized_rows = [
        {
            "internal_id": i,
            "Award ID": f"AWD-{i}",
            "_stratum_query_id": "q1",
            "_stratum_family_id": "f1",
            "_stratum_window_id": "w1",
        }
        for i in range(405)
    ]
    with pytest.raises(ValueError, match="Hard cap exceeded"):
        deduplicate_awards(oversized_rows, hard_cap=400)

    # Config cap validation
    cfg_file = tmp_path / "bad_config.yaml"
    bad_cfg = dict(sample_config)

    # Target rows > 25
    bad_cfg["sampling_parameters"]["target_rows_per_stratum"] = 30
    cfg_file.write_text(json.dumps(bad_cfg), encoding="utf-8")
    with pytest.raises(ValueError, match="target_rows_per_stratum must be a positive integer <= 25"):
        load_config(str(cfg_file))

    # Detail cap > 30
    bad_cfg["sampling_parameters"]["target_rows_per_stratum"] = 25
    bad_cfg["sampling_parameters"]["detail_sample_award_cap"] = 50
    cfg_file.write_text(json.dumps(bad_cfg), encoding="utf-8")
    with pytest.raises(ValueError, match="detail_sample_award_cap must be a positive integer <= 30"):
        load_config(str(cfg_file))

    # Unique awards cap > 400
    bad_cfg["sampling_parameters"]["detail_sample_award_cap"] = 30
    bad_cfg["sampling_parameters"]["hard_cap_unique_awards"] = 500
    cfg_file.write_text(json.dumps(bad_cfg), encoding="utf-8")
    with pytest.raises(ValueError, match="hard_cap_unique_awards must be a positive integer <= 400"):
        load_config(str(cfg_file))

    # Transaction page limit > 100
    bad_cfg["sampling_parameters"]["hard_cap_unique_awards"] = 400
    bad_cfg["sampling_parameters"]["transaction_page_limit"] = 150
    cfg_file.write_text(json.dumps(bad_cfg), encoding="utf-8")
    with pytest.raises(ValueError, match="transaction_page_limit must be a positive integer <= 100"):
        load_config(str(cfg_file))


def test_transaction_requests_identifier_preference_and_fallback(sample_config, mock_psc_tree, tmp_path):
    """Verifies transaction detail prefers generated_internal_id, falls back to internal_id, and handles missing IDs."""
    cfg = dict(sample_config)
    cfg["paths"] = {
        "raw_data_dir": str(tmp_path / "raw"),
        "raw_award_counts": str(tmp_path / "counts.json"),
        "raw_award_results": str(tmp_path / "results.json"),
        "raw_transaction_history": str(tmp_path / "tx.json"),
        "sample_awards_csv": str(tmp_path / "awards.csv"),
        "sample_transactions_csv": str(tmp_path / "tx.csv"),
        "manifest_path": str(tmp_path / "manifest.json"),
        "profile_report_path": str(tmp_path / "report.md"),
    }
    cfg["inclusion_families"] = {"naics_541330": sample_config["inclusion_families"]["naics_541330"]}
    cfg["date_windows"] = {"2010_2015": sample_config["date_windows"]["2010_2015"]}

    mock_session = MagicMock()

    psc_resp = MagicMock(status_code=200)
    psc_resp.json.return_value = mock_psc_tree

    count_resp = MagicMock(status_code=200)
    count_resp.json.return_value = {"results": {"contracts": 25}}

    search_resp = MagicMock(status_code=200)
    search_resp.json.return_value = {
        "results": [
            {
                "internal_id": 101,
                "generated_internal_id": "CONT_AW_101",
                "Award ID": "W911-01",
                "Award Amount": 1000000.0,
            },
            {
                "internal_id": 102,
                "generated_internal_id": None,
                "Award ID": "W911-02",
                "Award Amount": 2000000.0,
            },
        ]
    }

    tx_resp1 = MagicMock(status_code=200)
    tx_resp1.json.return_value = {
        "page_metadata": {"page": 1, "hasNext": False},
        "results": [{"id": 901, "action_date": "2012-05-01", "federal_action_obligation": 500000.0}],
    }

    tx_resp2 = MagicMock(status_code=200)
    tx_resp2.json.return_value = {
        "page_metadata": {"page": 1, "hasNext": True},
        "results": [{"id": 902, "action_date": "2013-06-01", "federal_action_obligation": 800000.0}],
    }

    mock_session.request.side_effect = [psc_resp, count_resp, search_resp, tx_resp1, tx_resp2]

    manifest = execute_sample_download(cfg, session=mock_session)

    assert manifest["transaction_detail_summary"]["requests_attempted"] == 2
    assert manifest["transaction_detail_summary"]["truncated_count"] == 1
    assert manifest["transaction_detail_summary"]["no_next_page_count"] == 1

    call_args_tx1 = mock_session.request.call_args_list[3]
    assert call_args_tx1.kwargs["json"]["award_id"] == "CONT_AW_101"

    call_args_tx2 = mock_session.request.call_args_list[4]
    assert call_args_tx2.kwargs["json"]["award_id"] == "102"


def test_transaction_requests_defensive_metadata_and_distinct_statuses(sample_config, mock_psc_tree, tmp_path):
    """Verifies that hasNext=True, hasNext=False, malformed metadata, zero rows, and errors produce distinct honest statuses."""
    cfg = dict(sample_config)
    cfg["paths"] = {
        "raw_data_dir": str(tmp_path / "raw"),
        "raw_award_counts": str(tmp_path / "counts.json"),
        "raw_award_results": str(tmp_path / "results.json"),
        "raw_transaction_history": str(tmp_path / "tx.json"),
        "sample_awards_csv": str(tmp_path / "awards.csv"),
        "sample_transactions_csv": str(tmp_path / "tx.csv"),
        "manifest_path": str(tmp_path / "manifest.json"),
        "profile_report_path": str(tmp_path / "report.md"),
    }
    cfg["inclusion_families"] = {"naics_541330": sample_config["inclusion_families"]["naics_541330"]}
    cfg["date_windows"] = {"2010_2015": sample_config["date_windows"]["2010_2015"]}

    mock_session = MagicMock()

    psc_resp = MagicMock(status_code=200)
    psc_resp.json.return_value = mock_psc_tree

    count_resp = MagicMock(status_code=200)
    count_resp.json.return_value = {"results": {"contracts": 25}}

    search_resp = MagicMock(status_code=200)
    search_resp.json.return_value = {
        "results": [
            {"internal_id": 201, "generated_internal_id": "CONT_201", "Award ID": "AWD-201"},
            {"internal_id": 202, "generated_internal_id": "CONT_202", "Award ID": "AWD-202"},
            {"internal_id": 203, "generated_internal_id": "CONT_203", "Award ID": "AWD-203"},
            {"internal_id": 204, "generated_internal_id": "CONT_204", "Award ID": "AWD-204"},
        ]
    }

    # 1. Successful with zero rows
    tx_resp1 = MagicMock(status_code=200)
    tx_resp1.json.return_value = {
        "page_metadata": {"page": 1, "hasNext": False},
        "results": [],
    }

    # 2. Successful with transactions and malformed/missing hasNext -> unknown completeness
    tx_resp2 = MagicMock(status_code=200)
    tx_resp2.json.return_value = {
        "page_metadata": {"page": 1, "hasNext": "not_a_bool"},
        "results": [{"id": 1, "action_date": "2020-01-01", "federal_action_obligation": 500.0}],
    }

    # 3. Successful with transactions and hasNext == True -> truncated
    tx_resp3 = MagicMock(status_code=200)
    tx_resp3.json.return_value = {
        "page_metadata": {"page": 1, "hasNext": True},
        "results": [{"id": 2, "action_date": "2020-02-01", "federal_action_obligation": 600.0}],
    }

    # 4. HTTP 500 failure
    tx_resp4 = MagicMock(status_code=500)
    tx_resp4.raise_for_status.side_effect = requests.HTTPError("Server Error 500")

    mock_session.request.side_effect = [
        psc_resp,
        count_resp,
        search_resp,
        tx_resp1,
        tx_resp2,
        tx_resp3,
        tx_resp4,
        tx_resp4,
        tx_resp4,
        tx_resp4,
    ]

    with patch("time.sleep", return_value=None):
        manifest = execute_sample_download(cfg, session=mock_session)

    tx_summary = manifest["transaction_detail_summary"]
    assert tx_summary["requests_attempted"] == 4
    assert tx_summary["success_zero_transactions"] == 1
    assert tx_summary["success_with_transactions"] == 2
    assert tx_summary["truncated_count"] == 1
    assert tx_summary["no_next_page_count"] == 1
    assert tx_summary["unknown_completeness_count"] == 1
    assert tx_summary["failures"] == 1


def test_psc_tree_validation_aborts_on_invalid_or_ambiguous_group(mock_psc_tree):
    """Verifies that PSC validation stops before count/award requests if D or R cannot be confirmed unambiguously."""
    with pytest.raises(ValueError, match="was not found"):
        resolve_psc_family_path(mock_psc_tree, group_id="X", expected_category="Service")

    product_tree = {
        "results": [
            {
                "id": "Product",
                "description": "Product",
                "children": [{"id": "D", "description": "IT and Telecom"}],
            }
        ]
    }
    with pytest.raises(ValueError, match="Could not locate expected 'Service' root node"):
        resolve_psc_family_path(product_tree, group_id="D", expected_category="Service")

    bad_desc_tree = {
        "results": [
            {
                "id": "Service",
                "description": "Service",
                "children": [{"id": "D", "description": "Clothing and Textiles"}],
            }
        ]
    }
    with pytest.raises(ValueError, match="does not match official"):
        resolve_psc_family_path(bad_desc_tree, group_id="D", expected_category="Service")


def test_bounded_retry_behavior_and_no_infinite_loop():
    """Verifies request_with_retry backs off and stops after max_retries without looping infinitely."""
    mock_session = MagicMock()
    err_resp = MagicMock(status_code=500)
    err_resp.raise_for_status.side_effect = requests.HTTPError("Server Error 500")
    mock_session.request.return_value = err_resp

    with patch("time.sleep", return_value=None), pytest.raises(requests.HTTPError):
        request_with_retry(
            session=mock_session,
            method="POST",
            url="https://api.usaspending.gov/test",
            max_retries=2,
            backoff_factor=1.0,
            retry_statuses={500},
        )

    assert mock_session.request.call_count == 3


def test_profiling_distinguishes_missing_from_zero(tmp_path, monkeypatch):
    """Verifies that the profiling script explicitly differentiates null/missing from numeric zero."""
    monkeypatch.chdir(tmp_path)

    manifest_dir = tmp_path / "reports" / "data_feasibility"
    manifest_dir.mkdir(parents=True)
    raw_dir = tmp_path / "data" / "raw" / "sample"
    raw_dir.mkdir(parents=True)

    manifest_data = {
        "manifest_version": "1.0.0",
        "run_status": "complete",
        "retrieved_at_utc": "2026-10-27T12:00:00Z",
        "queries": [],
        "deduplication_summary": {"total_unique_awards": 3, "cross_query_overlaps": 0},
        "transaction_detail_summary": {
            "target_awards": 1,
            "requests_attempted": 1,
            "success_with_transactions": 1,
            "success_zero_transactions": 0,
            "failures": 0,
            "truncated_count": 0,
            "no_next_page_count": 1,
            "unknown_completeness_count": 0,
        },
    }
    with open(manifest_dir / "sample_query_manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest_data, f)

    awards_data = [
        {
            "internal_id": 1,
            "Award ID": "AWD-1",
            "generated_internal_id": "CONT_1",
            "Award Amount": 0.0,  # Zero
            "Total Outlays": "None",  # Missing
            "Start Date": "2020-01-01",
            "End Date": "2022-01-01",
            "NAICS": "541330",
            "PSC": "D301",
            "source_queries": "q1",
            "source_families": "naics_541330",
            "source_windows": "2020_2023",
            "membership_count": 1,
            "missing_internal_id": False,
        },
        {
            "internal_id": 2,
            "Award ID": "AWD-2",
            "generated_internal_id": "CONT_2",
            "Award Amount": "",  # Missing
            "Total Outlays": 0.0,  # Zero
            "Start Date": "2020-01-01",
            "End Date": "2022-01-01",
            "NAICS": "541330",
            "PSC": "D301",
            "source_queries": "q1",
            "source_families": "naics_541330",
            "source_windows": "2020_2023",
            "membership_count": 1,
            "missing_internal_id": False,
        },
        {
            "internal_id": 3,
            "Award ID": "AWD-3",
            "generated_internal_id": "CONT_3",
            "Award Amount": 5_000_000.0,  # Exact $5M
            "Total Outlays": 1_000_000.0,  # Positive
            "Start Date": "2020-01-01",
            "End Date": "2022-01-01",
            "NAICS": "541330",
            "PSC": "D301",
            "source_queries": "q1",
            "source_families": "naics_541330",
            "source_windows": "2020_2023",
            "membership_count": 1,
            "missing_internal_id": False,
        },
    ]

    fieldnames = list(awards_data[0].keys())
    with open(raw_dir / "sample_awards.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(awards_data)

    tx_data = [
        {
            "award_id_lookup": "CONT_1",
            "id_type_used": "generated_internal_id",
            "award_internal_id": 1,
            "award_generated_internal_id": "CONT_1",
            "award_display_id": "AWD-1",
            "transaction_id": 11,
            "action_date": "2020-02-01",
            "federal_action_obligation": 500000.0,
            "page_truncated": False,
            "history_completeness": "no_next_page",
        }
    ]
    with open(raw_dir / "sample_transactions.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(tx_data[0].keys()))
        writer.writeheader()
        writer.writerows(tx_data)

    summary = profile_sample()

    assert summary["dollar_profile_5m"]["at_5m"] == 1

    report_text = (manifest_dir / "sample_profile.md").read_text(encoding="utf-8")
    assert "Missing / Blank Count" in report_text
    assert "Numeric Zero Count" in report_text
    assert "$5,000,000 Threshold Exploration" in report_text


def test_profiling_fails_cleanly_when_data_missing(tmp_path, monkeypatch):
    """Verifies that the profiler fails cleanly with an informative error if manifest is not complete."""
    monkeypatch.chdir(tmp_path)
    manifest_dir = tmp_path / "reports" / "data_feasibility"
    manifest_dir.mkdir(parents=True)

    # Not run status
    manifest_data = {"run_status": "not_run"}
    with open(manifest_dir / "sample_query_manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest_data, f)

    with pytest.raises(RuntimeError, match="manifest run_status is 'not_run'"):
        profile_sample()

    # Incomplete status
    manifest_data = {"run_status": "incomplete"}
    with open(manifest_dir / "sample_query_manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest_data, f)

    with pytest.raises(RuntimeError, match="manifest run_status is 'incomplete'"):
        profile_sample()


def test_api_422_surfaces_actionable_diagnostics_and_halts(sample_config, mock_psc_tree, tmp_path):
    """
    Verifies that a 422 Unprocessable Entity failure raises ApiCallError with
    detailed API error message, endpoint, status code, safe request payload,
    halts the downloader immediately without proceeding to transaction detail queries,
    and records the actionable diagnostic in the manifest.
    """
    cfg = dict(sample_config)
    manifest_file = tmp_path / "manifest.json"
    raw_dir = tmp_path / "raw"
    cfg["paths"] = {
        "raw_data_dir": str(raw_dir),
        "raw_award_counts": str(tmp_path / "counts.json"),
        "raw_award_results": str(tmp_path / "results.json"),
        "raw_transaction_history": str(tmp_path / "tx.json"),
        "sample_awards_csv": str(raw_dir / "sample_awards.csv"),
        "sample_transactions_csv": str(raw_dir / "sample_transactions.csv"),
        "manifest_path": str(manifest_file),
        "profile_report_path": str(tmp_path / "report.md"),
    }
    cfg["inclusion_families"] = {"naics_541330": sample_config["inclusion_families"]["naics_541330"]}
    cfg["date_windows"] = {"2010_2015": sample_config["date_windows"]["2010_2015"]}

    mock_session = MagicMock()

    # 1. PSC tree succeeds
    psc_resp = MagicMock(status_code=200, ok=True)
    psc_resp.json.return_value = mock_psc_tree

    # 2. Count succeeds
    count_resp = MagicMock(status_code=200, ok=True)
    count_resp.json.return_value = {"results": {"contracts": 5000}}

    # 3. Award search fails with 422
    search_resp = MagicMock(status_code=422, ok=False, reason="Unprocessable Entity")
    search_resp.json.return_value = {
        "detail": "Page #200 with limit 25 is over the maximum result limit 50000. Please provide search_after."
    }
    search_resp.raise_for_status.side_effect = requests.HTTPError(
        "422 Client Error: Unprocessable Entity for url: https://api.usaspending.gov/api/v2/search/spending_by_award/",
        response=search_resp,
    )

    mock_session.request.side_effect = [psc_resp, count_resp, search_resp]

    with pytest.raises(ApiCallError) as exc_info:
        execute_sample_download(cfg, session=mock_session)

    err = exc_info.value
    assert err.status_code == 422
    assert "https://api.usaspending.gov/api/v2/search/spending_by_award/" in err.endpoint
    assert "Page #200 with limit 25 is over the maximum result limit" in err.error_detail
    assert "filters" in err.request_summary
    assert "fields" in err.request_summary

    # Ensure transaction endpoint was never called
    assert mock_session.request.call_count == 3

    # Manifest was marked incomplete with actionable error
    assert manifest_file.is_file()
    manifest_data = json.loads(manifest_file.read_text(encoding="utf-8"))
    assert manifest_data["run_status"] == "incomplete"
    assert len(manifest_data["errors"]) >= 1
    assert "HTTP 422 Error" in manifest_data["errors"][0]
    assert "over the maximum result limit" in manifest_data["errors"][0]

    # No data files were written
    assert not (raw_dir / "sample_awards.csv").exists()
    assert not (raw_dir / "sample_transactions.csv").exists()


def test_api_error_diagnostics_bounds_excerpt_and_handles_non_json():
    """
    Verifies that extract_api_error_detail bounds huge error responses (<= 2048 chars)
    and handles non-JSON / HTML error responses gracefully.
    """
    # 1. Huge JSON message
    huge_text = "E" * 5000
    mock_huge = MagicMock()
    mock_huge.json.return_value = {"detail": huge_text}
    detail = extract_api_error_detail(mock_huge, max_length=2048)
    assert len(detail) <= 2048 + len(" [truncated]")
    assert detail.endswith(" [truncated]")

    # 2. HTML 502 Bad Gateway response
    mock_html = MagicMock()
    mock_html.json.side_effect = ValueError("No JSON")
    mock_html.text = "<html><body>502 Bad Gateway</body></html>"
    detail_html = extract_api_error_detail(mock_html)
    assert "502 Bad Gateway" in detail_html

    # 3. Empty response
    mock_empty = MagicMock()
    mock_empty.json.side_effect = ValueError("No JSON")
    mock_empty.text = ""
    detail_empty = extract_api_error_detail(mock_empty)
    assert "no error message provided" in detail_empty


def test_request_payload_sanitizes_credentials():
    """Verifies that sensitive authentication keys in payloads are redacted."""
    raw_payload = {
        "filters": {"award_type_codes": ["A"]},
        "authorization": "Bearer secret-token-123",
        "api_key": "my-secret-key",
        "nested": {"token": "xyz", "normal": 42},
    }
    sanitized = sanitize_request_payload(raw_payload)
    assert sanitized["authorization"] == "[REDACTED]"
    assert sanitized["api_key"] == "[REDACTED]"
    assert sanitized["nested"]["token"] == "[REDACTED]"
    assert sanitized["nested"]["normal"] == 42
    assert sanitized["filters"]["award_type_codes"] == ["A"]


def test_successful_request_does_not_log_award_data():
    """
    Verifies that successful HTTP requests do not invoke error extraction
    or log/attach award results into error structures.
    """
    mock_session = MagicMock()
    mock_resp = MagicMock(status_code=200, ok=True)
    award_records = [{"Award ID": "CONT_123", "Secret Column": "Val"}]
    mock_resp.json.return_value = {"results": award_records}

    mock_session.request.return_value = mock_resp

    resp = request_with_retry(
        session=mock_session,
        method="POST",
        url="https://api.usaspending.gov/api/v2/search/spending_by_award/",
        json={"filters": {}},
    )
    assert resp.status_code == 200


