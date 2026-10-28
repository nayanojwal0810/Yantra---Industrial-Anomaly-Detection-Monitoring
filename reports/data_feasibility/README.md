# Sanket — Federal Contract Recompete Intelligence
## Official Bulk Download Workflow and Quality Profiling

This directory documents the data acquisition architecture and validation reports for Project Sanket.

### Acquisition Architecture

USAspending provides two primary data extraction APIs:
1. **Canonical Acquisition Path (Recommended)**: Asynchronous Bulk Download API (`/api/v2/download/count/`, `/api/v2/download/search/`, `/api/v2/download/status/`). This path generates official zipped CSV archives with full schema fidelity for prime award summaries and transaction histories. Implemented in:
   ```
   scripts/download_via_bulk_api.py
   ```
2. **Legacy Extraction Path (Deprecated)**: Page-based search downloader (`/api/v2/search/spending_by_award/`). Preserved solely for regression history. Deep pagination on large cohorts triggers HTTP 422 errors. Documented in:
   ```
   scripts/download_sample.py (DEPRECATED)
   ```

---

### Canonical CLI Usage (`scripts/download_via_bulk_api.py`)

All commands must be executed from the repository root:

#### 1. Dry Run (Default)
Inspect planned filters, intended counts, output paths, and endpoint URLs without making HTTP requests or writing sample data:
```bash
python scripts/download_via_bulk_api.py
```

#### 2. Controlled FY2020 Cohort Download
Explicitly authorizes only the configured controlled cohort (NASA + NAICS 541330 + FY2020 action dates):
```bash
python scripts/download_via_bulk_api.py --confirm-sample-download
```

**Workflow Safety Protocol**:
- Performs count precheck at `/api/v2/download/count/` for `awards` and `transactions` spending levels.
- Verifies counts against safety caps and user reference UI counts (785 awards, 1,384 transactions).
- If API counts differ from reference UI counts, the client **halts before job creation** and records the mismatch in `reports/data_feasibility/bulk_download_manifest.json` and `reports/data_feasibility/bulk_download_validation.md`.
- Streams archive to `.part` file, verifies ZIP integrity, and atomically renames.
- Performs in-memory schema, key uniqueness, linkage, and date coverage QA without extracting raw CSVs to disk.

---

### Configuration (`config/bulk_download_config.yaml`)

The bulk download configuration defines:
- **API Base URL & Endpoints**: `/api/v2/download/count/`, `/api/v2/download/search/`, `/api/v2/download/status/`
- **Trusted Hosts Whitelist**: `api.usaspending.gov`, `files.usaspending.gov`, `files-nonprod.usaspending.gov`
- **Controlled Cohort Filters**:
  - Award types: Procurement contracts only (`A`, `B`, `C`, `D`)
  - Agency: Top-tier awarding agency `National Aeronautics and Space Administration`
  - NAICS: `541330` (Engineering Services)
  - Time period: `2019-10-01` to `2020-09-30` with `date_type: "action_date"` (equivalent to Advanced Search UI with "Show New Awards Only" OFF)
- **Reference UI Counts**: 785 awards, 1,384 transactions
- **Safety Caps**: 5,000 awards, 25,000 transactions
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
- **Validation Report**: `reports/data_feasibility/bulk_download_validation.md` (Human-readable reconciliation report and precheck comparison table).
- **Manual Archive Audit**: `reports/data_feasibility/downloaded_sample_audit.md` (Audit of manually acquired `NASA_2020.zip` and UI sample archives).
