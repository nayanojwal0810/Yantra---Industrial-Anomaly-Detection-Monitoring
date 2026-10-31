# Niramaya — Task 03: HRRP Metric Availability and Numerical Reliability Audit

## Overview

This directory contains the implementation, documentation, and factual execution deliverables for **Task 03: HRRP Metric Availability and Numerical Reliability Audit** of Project **Niramaya**.

The objective of this task is to evaluate whether the metric values in the complete FY 2026 CMS Hospital Readmissions Reduction Program (HRRP) dataset are sufficiently available, interpretable, and numerically consistent to support condition-specific hospital benchmarking.

## Repository & Working Branch

- **Repository:** `https://github.com/nayanojwal0810/Yantra---Industrial-Anomaly-Detection-Monitoring`
- **Branch:** `project1/niramaya-validation`
- **Task Directory:** `validation/niramaya/task_03_metric_reliability_audit/`

All Task 3 code and generated outputs are maintained strictly inside this directory. Pre-existing files and prior task deliverables remain completely untouched. Raw datasets are not committed to version control.

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
python validation/niramaya/task_03_metric_reliability_audit/audit_hrrp_metric_reliability.py --data-file ../data/raw/FY_2026_Hospital_Readmissions_Reduction_Program_Hospital.csv --output-dir validation/niramaya/task_03_metric_reliability_audit/output
```

### CLI Arguments
- `--data-file`: Path to raw HRRP CSV file (default: `../data/raw/FY_2026_Hospital_Readmissions_Reduction_Program_Hospital.csv`).
- `--output-dir`: Path to directory where audit outputs are written (default: `validation/niramaya/task_03_metric_reliability_audit/output`).

## Generated Deliverables

The script writes seven primary artifacts to `output/`:
1. `hrrp_metric_reliability.json`: Structured JSON containing complete metric availability counts, ERR reconciliation metrics, numerical distribution stats, footnote breakdowns, and status patterns.
2. `hrrp_metric_reliability.md`: Human-readable Markdown report detailing factual findings across all 11 required audit areas.
3. `metric_availability_by_measure.csv`: Condition-specific summary table (one row per measure) reporting counts and percentages for all availability indicators.
4. `value_token_frequency.csv`: Exhaustive frequency table of all raw value tokens, normalized classifications, and dataset percentages.
5. `footnote_distribution.csv`: Distribution table of every distinct Footnote code, CMS descriptions, dataset percentages, and measure-level counts.
6. `err_reconciliation_exceptions.csv`: Evidence artifact containing standard headers and 0 data rows (confirming 100% mathematical reconciliation within tolerance).
7. `execution_environment.txt`: Execution environment details (Python version, operating system, platform architecture, and command invocation).

## Summary of Findings

1. **Metric Availability by Condition:**
   - Public numeric ERR availability varies markedly across the six clinical measures:
     - `READM-30-PN-HRRP`: **2,715** numeric ERR (**88.9%**)
     - `READM-30-HF-HRRP`: **2,621** numeric ERR (**85.8%**)
     - `READM-30-COPD-HRRP`: **2,323** numeric ERR (**76.0%**)
     - `READM-30-AMI-HRRP`: **1,736** numeric ERR (**56.8%**)
     - `READM-30-HIP-KNEE-HRRP`: **1,447** numeric ERR (**47.4%**)
     - `READM-30-CABG-HRRP`: **878** numeric ERR (**28.7%**)
   - Across the full dataset, **11,720 of 18,330 rows (63.94%)** publish a numeric ERR.

2. **Record Coverage vs Outcome Availability vs Supporting Count Availability:**
   - **Record Coverage:** 100% (all 3,055 hospitals have rows for all 6 conditions).
   - **Outcome Availability:** 63.94% (11,720 rows publish numeric ERR).
   - **Supporting Count Availability:** 43.85% (8,037 rows publish unmasked discharge and readmission counts).
   - **Privacy-Suppressed Outomes:** Exactly **3,683 rows** have Number of Readmissions masked as `"Too Few to Report"` and Discharges `"N/A"`, yet publish official, risk-standardized numeric ERR, Predicted Rate, and Expected Rate. Volume suppression must not be confused with outcome invalidity.

3. **ERR Mathematical Reconciliation (`Predicted / Expected`):**
   - Formula: `Calculated ERR = Predicted Readmission Rate / Expected Readmission Rate`.
   - All **11,720 eligible rows (100.0%)** reconcile within the **0.0001 absolute tolerance**.
   - Maximum absolute difference observed is **0.000065**, reflecting minor publication rounding of 4-decimal published inputs.
   - Zero reconciliation exceptions (`err_reconciliation_exceptions.csv` has 0 data rows).

4. **Numerical Range & Plausibility:**
   - ERR values range from **0.4698 to 1.6297** (6,070 below 1.0; 7 equal to 1.0; 5,643 above 1.0). Zero negative or zero ERR values.
   - Predicted and Expected Rates range from **1.91% to 28.16%** with uniform 4-decimal precision. Zero rates <= 0% or > 100%.
   - Discharges range from **0 to 3,672**; Readmissions range from **11 to 847**. Readmissions exceeding discharges: **0**.
   - Exactly **205 rows** have Number of Discharges = 0; all 205 carry Footnote 7 ("fewer than 25 eligible discharges") and ERR = N/A.

5. **Footnote Distribution:**
   - Blank (11,343 rows, 61.88%), Footnote 5 (3,255 rows, 17.76%), Footnote 1 (3,150 rows, 17.18%), Footnote 29 (377 rows, 2.06%), Footnote 7 (205 rows, 1.12%).
