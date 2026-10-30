# Urja — Task 1: Dataset Acquisition, Source Verification & Integrity Audit

## 1. Overview & Purpose

This directory contains the code, metadata, reports, and unit tests for **Task 1** of **Project Urja**.

**Project Objective:** Evaluate the effectiveness of non-price household electricity conservation information interventions (neighbour comparison, suburb comparison, and energy conservation advice) using the randomized field experiment dataset from Bangladesh.

**Scope of Task 1:**
- Official source verification against Harvard Dataverse.
- Data acquisition and manifest documentation.
- File integrity and cryptographic checksum comparison.
- In-memory inspection of archive contents without modifying raw data.
- Readability verification and schema extraction with documented variable descriptions.
- Structural data-quality profiling (missingness, row duplication, dimension verification).
- Mandatory licence and portfolio reuse assessment.

> [!NOTE]
> **Strict Non-Analysis Boundary:** Task 1 is strictly diagnostic and read-only. It does NOT include treatment-effect estimation, regressions, baseline balance testing, hypothesis tests, household segmentation, difference-in-differences, machine learning, or exploratory data analysis (EDA).

---

## 2. Research Provenance & Source References

- **Original Research Paper:**
  - *Title:* Non-price energy conservation information and household energy consumption in a developing country: Evidence from an RCT
  - *Authors:* Ahsanuzzaman, Shaikh Eskander, Asad Islam, Liang Choon Wang
  - *Journal:* *Journal of Environmental Economics and Management* (JEEM), Vol. 127, September 2024, 103022
  - *Paper DOI:* [10.1016/j.jeem.2024.103022](https://doi.org/10.1016/j.jeem.2024.103022)
  - *Paper Licence:* Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)

- **Official Harvard Dataverse Record:**
  - *Dataset Title:* Replication Data for: Non-price energy conservation information and household energy consumption in a developing country: Evidence from an RCT
  - *Dataset PID:* `doi:10.7910/DVN/4FLFRE`
  - *Landing Page:* [https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/4FLFRE](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/4FLFRE)
  - *Dataset Version:* 1.0 (Released: 2025-08-13)
  - *Depositor:* Shaikh Eskander (UAB / LSE)
  - *Dataset Licence:* **CC0 1.0 Universal (Public Domain Dedication)**

---

## 3. Directory Layout

```text
validation/urja/task_01/
├── README.md                           # Task overview and execution instructions
├── scripts/
│   └── audit_dataset.py                # Reusable, read-only dataset audit CLI script
├── metadata/
│   ├── source_metadata.json            # Official Harvard Dataverse API metadata
│   └── acquisition_manifest.json       # File-level acquisition and checksum manifest
├── reports/
│   ├── dataset_source_and_licence.md   # Detailed licence & portfolio reuse report
│   ├── file_inventory.csv              # File inventory comparing local vs source
│   ├── schema_inventory.csv            # Field-level schema and variable definitions
│   ├── structural_quality.csv          # Table-level structural data quality summary
│   ├── sha256_manifest.txt             # SHA-256 hashes of original downloaded files
│   ├── task_01_audit_report.md         # Comprehensive Task 1 audit report
│   └── task_01_final_report.md         # Final Task 1 evaluation and PASS decision
└── tests/
    └── test_audit_dataset.py           # Unit tests with synthetic files
```

---

## 4. Execution Instructions

### Prerequisites
- Python 3.10+
- `pandas`, `openpyxl`, `numpy`, `pytest`

### Running the Audit Script
Execute the audit script by specifying the relative or absolute path to the raw data directory:

```bash
python validation/urja/task_01/scripts/audit_dataset.py \
  --raw-dir data/raw \
  --output-dir validation/urja/task_01/reports
```

### Running Unit Tests
All unit tests operate on synthetic in-memory/temporary files and do not touch the raw research data:

```bash
# Using pytest
python -m pytest validation/urja/task_01/tests/test_audit_dataset.py -v

# Or using standard unittest
python -m unittest validation/urja/task_01/tests/test_audit_dataset.py -v
```

---

## 5. Audit Summary Highlights

| Metric | Verified Value | Status |
|---|---|---|
| **Dataverse Record** | `doi:10.7910/DVN/4FLFRE` (v1.0) | Authenticated |
| **Dataset Licence** | CC0 1.0 (SPDX: `CC0-1.0`) | Public Domain / Portfolio Approved |
| **Paper Licence** | CC BY-NC 4.0 | Non-Commercial Attribution |
| **Release Checksum** | MD5: `7d22412f622a0845ac4e78d989ef9999` | 100% Match |
| **Local Checksum** | SHA-256: `8fcedee8296a028142f1b7b747bdf83b38e6296e66e4fe2f90fbb7d32f2fbe9b` | Verified |
| **Primary RCT Data** | `replication_data.dta` (15,882 rows × 20 cols) | Fully Readable |
| **Unique Households** | 2,394 distinct `hid` (Round 0 baseline) | Verified |
| **Survey Rounds** | 7 rounds (`Round 0` to `Round 6`) | Longitudinal Panel Structure |
| **Total Tables Profiled** | 6 data tables across Stata & Excel | 100% Readable |
| **Total Fields Profiled** | 60 distinct fields documented | Fully Catalogued |
| **Task 1 Recommendation** | **PASS** | Meets all acceptance criteria |
