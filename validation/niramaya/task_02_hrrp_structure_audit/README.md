# Niramaya — Task 02: HRRP Structure and Data-Grain Audit

## Overview

This directory contains the implementation, documentation, and factual execution deliverables for **Task 02: HRRP Structure and Data-Grain Audit** of Project **Niramaya**.

The objective of this task is to establish whether the complete CMS Hospital Readmissions Reduction Program (HRRP) dataset possesses a consistent, reliable hospital-condition-period structure, whether its proposed natural business key is strictly unique, and whether facility coverage and reporting periods are uniform across the entire dataset.

## Repository & Working Branch

- **Repository:** `https://github.com/nayanojwal0810/Yantra---Industrial-Anomaly-Detection-Monitoring`
- **Branch:** `project1/niramaya-validation`
- **Task Directory:** `validation/niramaya/task_02_hrrp_structure_audit/`

All Task 2 code and generated outputs are maintained strictly inside this directory. Pre-existing files and prior task deliverables remain completely untouched. Raw datasets are not committed to version control.

## Input Dataset

| Property | Value |
| :--- | :--- |
| **Local File Name** | `FY_2026_Hospital_Readmissions_Reduction_Program_Hospital.csv` |
| **Relative Path** | `../data/raw/FY_2026_Hospital_Readmissions_Reduction_Program_Hospital.csv` |
| **CMS Catalogue Source** | [CMS HRRP Dataset (9n3s-kdb3)](https://data.cms.gov/provider-data/dataset/9n3s-kdb3) |
| **Direct CMS CSV URL** | [CMS Direct Resource Link](https://data.cms.gov/provider-data/sites/default/files/resources/a171bc36c488d3e0dc33ec63abb469a6_1770163617/FY_2026_Hospital_Readmissions_Reduction_Program_Hospital.csv) |

## Audit Script Execution

The validation script uses standard library Python modules only. It accepts configurable CLI arguments for both input data file and output directory:

```bash
# Execute from the repository root (validation-repo)
python validation/niramaya/task_02_hrrp_structure_audit/audit_hrrp_structure.py --data-file ../data/raw/FY_2026_Hospital_Readmissions_Reduction_Program_Hospital.csv --output-dir validation/niramaya/task_02_hrrp_structure_audit/output
```

### CLI Arguments
- `--data-file`: Path to the raw HRRP CSV file (default: `../data/raw/FY_2026_Hospital_Readmissions_Reduction_Program_Hospital.csv`).
- `--output-dir`: Path to the directory where audit outputs will be written (default: `validation/niramaya/task_02_hrrp_structure_audit/output`).

## Generated Deliverables

The script writes five primary artifacts to `output/`:
1. `hrrp_structure_audit.json`: Complete machine-readable audit results including record counts, measure breakdowns, business key uniqueness, facility coverage stats, and date validation.
2. `hrrp_structure_audit.md`: Human-readable markdown audit report detailing findings and factual assessments.
3. `facility_measure_coverage.csv`: Full facility-by-measure coverage matrix covering all 3,055 unique hospitals and their status across the 6 HRRP clinical measures.
4. `duplicate_business_keys.csv`: Evidence artifact containing standard key headers and 0 data rows (confirming candidate key uniqueness).
5. `execution_environment.txt`: Execution environment details (Python version, operating system, platform architecture, and command invocation).

## Summary of Findings

1. **Dataset Completeness & Dimensions:**
   - 18,330 total data records and 12 columns parsed strictly as strings.
   - 0 malformed rows, 0 exact duplicate rows, and 0 blank values in key fields (`Facility ID`, `Measure Name`, `Start Date`, `End Date`, `Facility Name`, `State`).

2. **Required Measure Identifiers:**
   - All 6 expected CMS clinical measures are present with exact naming:
     - `READM-30-AMI-HRRP`: 3,055 records, 3,055 unique hospitals
     - `READM-30-COPD-HRRP`: 3,055 records, 3,055 unique hospitals
     - `READM-30-CABG-HRRP`: 3,055 records, 3,055 unique hospitals
     - `READM-30-HF-HRRP`: 3,055 records, 3,055 unique hospitals
     - `READM-30-HIP-KNEE-HRRP`: 3,055 records, 3,055 unique hospitals
     - `READM-30-PN-HRRP`: 3,055 records, 3,055 unique hospitals
   - 0 missing expected measures; 0 unexpected measure codes.

3. **Candidate Business Key & Data Grain:**
   - Proposed candidate key: `Facility ID + Measure Name + Start Date + End Date`
   - Total rows: 18,330 | Distinct candidate keys: 18,330.
   - Duplicated candidate-key groups: **0**.
   - Confirmed: The candidate key is **strictly unique** across the complete dataset and accurately models the data grain.

4. **Facility-Level Measure Coverage:**
   - 3,055 total unique hospitals.
   - Hospitals with all 6 expected measures: **3,055 (100.0%)**.
   - Hospitals with fewer than 6 measures: **0**.
   - Hospitals with unexpected or duplicate measures: **0**.
   - Coverage status breakdown: **3,055 Complete**, 0 Incomplete, 0 Exception.

5. **Reporting Period Consistency:**
   - Expected CMS 3-year performance window: `07/01/2021` to `06/30/2024`.
   - Records matching expected window: **18,330 (100.0%)**.
   - Records with other periods: **0**.
   - All 3,055 hospitals and all 6 measures share this single, uniform reporting window.

6. **Facility Identity Consistency:**
   - Each `Facility ID` maps to exactly **1** unique `Facility Name` and **1** unique `State` across all 6 records (0 raw or normalized discrepancies).
   - 51 distinct geographic jurisdictions represented (all 50 US states + District of Columbia), all using standard 2-letter uppercase postal codes.
   - `Facility ID` is verified as a completely reliable entity identifier within this dataset.
