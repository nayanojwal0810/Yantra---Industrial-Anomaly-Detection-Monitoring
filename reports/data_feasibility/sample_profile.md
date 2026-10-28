# Sample Contract Data Profile (NOT RUN — no sample has been downloaded)

## Status Notice
> [!IMPORTANT]
> **NOT RUN — no sample has been downloaded.**
> The download and profiling scripts have been implemented and validated against mocked endpoints only. In accordance with task constraints, no live API requests have been made and no data has been written to `data/raw/sample/`.

---

## Planned Workflow & Commands

To download the limited contract award sample and profile the acquired data, run the following commands in sequence:

1. **Dry Run (Inspect planned queries and filters without network calls):**
   ```bash
   python scripts/download_sample.py
   ```

2. **Execute Limited Sample Download (After manual review):**
   ```bash
   python scripts/download_sample.py --confirm-sample-download
   ```

3. **Profile the Downloaded Sample Data:**
   ```bash
   python scripts/profile_sample.py
   ```

4. **Execute Workflow Unit Tests:**
   ```bash
   python -m pytest tests/test_sample_data_workflow.py -q
   ```

---

## Official Documentation Contract References
1. **API Endpoint Index:** https://api.usaspending.gov/docs/endpoints
2. **Spending by Award Contract:** https://github.com/fedspendingtransparency/usaspending-api/blob/master/usaspending_api/api_contracts/contracts/v2/search/spending_by_award.md
3. **Spending by Award Count Contract:** https://github.com/fedspendingtransparency/usaspending-api/blob/master/usaspending_api/api_contracts/contracts/v2/search/spending_by_award_count.md
4. **Search Filters Contract:** https://github.com/fedspendingtransparency/usaspending-api/blob/master/usaspending_api/api_contracts/search_filters.md
5. **Transaction History Contract:** https://github.com/fedspendingtransparency/usaspending-api/blob/master/usaspending_api/api_contracts/contracts/v2/transactions.md
6. **PSC Tree Contract:** https://github.com/fedspendingtransparency/usaspending-api/blob/master/usaspending_api/api_contracts/contracts/v2/references/filter_tree/psc.md
7. **Official PSC Manual:** https://www.acquisition.gov/psc-manual
8. **PSC Manual April 2025 PDF:** https://www.acquisition.gov/sites/default/files/manual/PSC%20Manual%20April%202025.pdf
9. **Census NAICS Manual PDF:** https://www.census.gov/naics/reference_files_tools/2022_NAICS_Manual.pdf

---

## Pre-Download Readiness Checklist

| Evaluation Criterion | Status | Notes |
| :--- | :--- | :--- |
| Inclusion Query Execution | NOT MEASURED | Awaiting user execution of download command |
| Cross-Query Deduplication & Overlap | NOT MEASURED | Awaiting sample acquisition |
| Key Identifier Disambiguation (`internal_id`, `generated_internal_id`, `Award ID`) | NOT MEASURED | Awaiting sample acquisition |
| Core Field Missingness vs Zero Differentiation | NOT MEASURED | Awaiting sample acquisition |
| Date Parsing & Chronology Consistency (`Start Date <= End Date`) | NOT MEASURED | Awaiting sample acquisition |
| Award Amount & Outlays Distribution (incl. $5M boundary) | NOT MEASURED | Awaiting sample acquisition |
| Transaction History Linkage & Detail Capping | NOT MEASURED | Awaiting sample acquisition |
| Full Extraction Feasibility Assessment | NOT MEASURED | Awaiting measured data profiling |

---

*This document will be automatically replaced with verified empirical profiling metrics and evidence-based analysis when `scripts/profile_sample.py` is executed after running `scripts/download_sample.py --confirm-sample-download`.*
