# Niramaya — Task 01: Raw Data File Integrity Audit

## Overview

This directory contains the implementation, documentation, and factual execution evidence for **Task 01: Raw Data File Integrity Audit** of Project **Niramaya**.

The objective of this task is to perform an independent, read-only file integrity audit on the two primary local raw CMS datasets before any downstream joins, transformations, or modelling are undertaken.

## Working Branch & Scope

- **Repository:** `https://github.com/nayanojwal0810/Yantra---Industrial-Anomaly-Detection-Monitoring`
- **Branch:** `project1/niramaya-validation`
- **Task Directory:** `validation/niramaya/task_01_raw_file_audit/`

All code and generated artifacts for Task 01 are strictly isolated within this directory. Unrelated repository content was not modified, deleted, or relied upon. Raw CSV files are never committed to version control.

## Input Datasets

| File | Dataset Description | Expected CMS Source | Catalogue Reference |
| :--- | :--- | :--- | :--- |
| **File A** | `FY_2026_Hospital_Readmissions_Reduction_Program_Hospital.csv` | [CMS HRRP Dataset (9n3s-kdb3)](https://data.cms.gov/provider-data/dataset/9n3s-kdb3) | 18,330 rows, 12 cols |
| **File B** | `Hospital_General_Information.csv` | [CMS Hospital General Info (xubh-q36u)](https://data.cms.gov/provider-data/dataset/xubh-q36u) | 5,419 rows, 38 cols |

## Workspace Directory Layout

```text
Niramaya/
    data/
        raw/
            FY_2026_Hospital_Readmissions_Reduction_Program_Hospital.csv
            Hospital_General_Information.csv
    validation-repo/
        validation/
            niramaya/
                task_01_raw_file_audit/
                    audit_raw_files.py
                    README.md
                    output/
                        raw_file_audit.json
                        raw_file_audit.md
                        execution_environment.txt
```

## Audit Script Execution

The validation script uses standard library Python modules only. It accepts configurable paths via CLI flags:

```bash
# Execute from the repository root (validation-repo)
python validation/niramaya/task_01_raw_file_audit/audit_raw_files.py --data-dir ../data/raw --output-dir validation/niramaya/task_01_raw_file_audit/output
```

### CLI Arguments
- `--data-dir`: Path to the directory holding raw CSV files (default: `../data/raw`).
- `--output-dir`: Path where audit reports are written (default: `validation/niramaya/task_01_raw_file_audit/output`).

## Output Deliverables

The script writes three primary artifacts to `output/`:
1. `raw_file_audit.json`: Complete machine-readable audit results with SHA-256 hashes, column names, structural checks, and Facility ID distributions.
2. `raw_file_audit.md`: Human-readable markdown audit report detailing findings, catalogue comparisons, and factual issue assessments.
3. `execution_environment.txt`: Execution environment details including Python version, operating system, platform architecture, and command invocation.

## Summary of Audit Findings

1. **Existence & Integrity:**
   - Both input CSV files exist as regular readable files and have valid non-zero sizes:
     - `FY_2026_Hospital_Readmissions_Reduction_Program_Hospital.csv`: 2,068,464 bytes (~1.9726 MB), SHA-256: `7e7915dd2751a1e59ac46dbc9194fb781e820962a04d47c31344ea2bb30c91f6`
     - `Hospital_General_Information.csv`: 1,450,767 bytes (~1.3836 MB), SHA-256: `f874f09fef895a1ccf5bb7392dcbb2be05c9860339261b093fe00f0c1b013480`
   - Both files are encoded in standard UTF-8 without BOM corruption.

2. **Dimensions & Catalogue Reference Alignment:**
   - HRRP: Actual rows: **18,330** (Reference: 18,330, diff: 0), Actual columns: **12** (Reference: 12, diff: 0). Exact match.
   - Hospital General Info: Actual rows: **5,419** (Reference: 5,419, diff: 0), Actual columns: **38** (Reference: 38, diff: 0). Exact match.

3. **Required Columns:**
   - All 12 required fields for the HRRP file are confirmed present.
   - All 5 required fields for the Hospital General Information file are confirmed present.
   - Zero empty column headers and zero duplicate column headers.

4. **Facility ID Preservation:**
   - `Facility ID` exists in both datasets and is preserved as text.
   - Zero blank/empty identifiers.
   - String length is uniformly 6 characters (100% of rows in both files).
   - Identifiers with leading zeroes (e.g., `010001`) preserve the leading `'0'`:
     - HRRP: 3,354 row occurrences starting with `'0'`.
     - Hospital General Info: 854 row occurrences starting with `'0'`.

5. **Data Row Integrity & Duplicates:**
   - Zero malformed rows (no rows with mismatched column widths).
   - Zero exact duplicate data rows in either dataset.
   - Zero issues requiring attention.
