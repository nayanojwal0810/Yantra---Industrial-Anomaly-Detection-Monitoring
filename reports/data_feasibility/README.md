# Sanket — Federal Contract Recompete Intelligence
## Official Bulk Download Workflow and Controlled FY2020 Pilot

This directory documents the canonical bulk data acquisition architecture and validation reports for Project Sanket.

### Acquisition Architecture

USAspending provides two primary data extraction paths:
1. **Canonical Acquisition Path (Recommended)**: Asynchronous Bulk Download API (`/api/v2/download/count/`, `/api/v2/download/search/`, `/api/v2/download/status/`). This path generates official zipped CSV archives with full schema fidelity for prime award summaries and transaction histories. Implemented in:
   ```
   scripts/download_via_bulk_api.py
   ```
2. **Legacy Extraction Path (Deprecated)**: Page-based search downloader (`/api/v2/search/spending_by_award/`). Preserved solely for regression history. Deep pagination on large cohorts triggers HTTP 422 errors. Documented in:
   ```
   scripts/download_sample.py (DEPRECATED)
   ```

---

### Two-Stage Acquisition Architecture

To ensure full modification fidelity, the download of award summaries and transaction histories is strictly separated:
- **Stage 1 (Award Summary Cohort)**:
  - Filters: Top-tier NASA, NAICS `541330` (`naics_codes: {"require": ["541330"]}`), procurement contract types `A, B, C, D`, and FY2020 new awards (`time_period: [{"start_date": "2019-10-01", "end_date": "2020-09-30", "date_type": "new_awards_only"}]`).
  - Precheck: `POST /api/v2/download/count/` with singular string `spending_level: "awards"`.
  - Search Job: `POST /api/v2/download/search/` with array `spending_level: ["awards"]`.
  - Reconciliation: Validates count API `calculated_count` == status `total_rows` == downloaded CSV rows (221 rows).
  - Cohort List: Extracts and deduplicates all nonblank `award_id_piid` values.
- **Stage 2 (Transaction History Retrieval)**:
  - Filters: Queried strictly by `award_ids` corresponding to the cohort PIIDs.
  - **No Date Filter**: Intentionally omits `time_period`, NAICS, and agency filters so that all lifetime modifications for the cohort awards are retrieved rather than being truncated to FY2020.
  - Precheck: `POST /api/v2/download/count/` with singular string `spending_level: "transactions"`.
  - Search Job: `POST /api/v2/download/search/` with array `spending_level: ["transactions"]`.
  - Batching: Deterministic batches of 100 PIIDs.

---

### Canonical CLI Usage (`scripts/download_via_bulk_api.py`)

All commands must be executed from the repository root:

#### 1. Dry Run (Default)
Inspect planned filters, intended counts, output paths, and endpoint URLs without making HTTP requests or writing sample data:
```bash
python scripts/download_via_bulk_api.py
```

#### 2. Execute Controlled FY2020 Pilot
Authorizes execution of ONLY the single configured FY2020 controlled pilot:
```bash
python scripts/download_via_bulk_api.py --confirm-sample-download
```

Optional Quoting Flags:
- `--exact-match-quoting` (Default): Enforces surrounding each PIID in double quotes per `search_filters.md` documentation. If the server rejects this form (e.g. HTTP 503), the client halts honestly and logs the exact server response.
- `--no-exact-match-quoting`: Sends raw unquoted PIIDs if the server rejects double quotes.

---

### Configuration (`config/bulk_download_config.yaml`)

The bulk download configuration defines:
- **API Base URL & Endpoints**: `/api/v2/download/count/`, `/api/v2/download/search/`, `/api/v2/download/status/`
- **Trusted Hosts Whitelist**: `api.usaspending.gov`, `files.usaspending.gov`, `files-nonprod.usaspending.gov` (HTTPS strictly enforced)
- **Controlled Award Cohort Filters**:
  - `award_type_codes`: `["A", "B", "C", "D"]`
  - `agencies`: `[{"type": "awarding", "tier": "toptier", "name": "National Aeronautics and Space Administration"}]`
  - `naics_codes`: `{"require": ["541330"]}` (Object form)
  - `time_period`: `[{"start_date": "2019-10-01", "end_date": "2020-09-30", "date_type": "new_awards_only"}]`
- **Transaction Cohort Settings**: Batch size 100, `exact_match_quoting: true`
- **Safety Caps**: 5,000 awards, 25,000 transactions per batch
- **HTTP & Polling Policies**: Exponential backoff on 429/5xx, 300s overall polling timeout

---

### Testing & Validation

Run the full offline test suite (mocked HTTP sessions, zero network calls):
```bash
python -m pytest tests/ -q
python -m ruff check scripts tests
python -m compileall -q scripts tests
```

---

### Generated Reports

- **Manifest**: `reports/data_feasibility/bulk_download_manifest.json` (Structured JSON containing UTC run timestamps, exact filter parameters, precheck count responses, job statuses, and error diagnostics).
- **Validation Report**: `reports/data_feasibility/bulk_download_validation.md` (Human-readable reconciliation report, Stage 1 metrics, Stage 2 server response diagnostics, and comparison with manual archives).
- **Manual Archive Audit**: `reports/data_feasibility/downloaded_sample_audit.md` (Audit of manually acquired `NASA_2020.zip` and UI sample archives).
