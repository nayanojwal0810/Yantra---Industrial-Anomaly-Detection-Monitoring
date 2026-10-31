# Niramaya — Task 03: HRRP Metric Availability and Numerical Reliability Audit

## Overview

This directory contains the implementation, documentation, and factual execution deliverables for **Task 03: HRRP Metric Availability and Numerical Reliability Audit** of Project **Niramaya** (incorporating final authoritative footnote definitions, reconciliation terminology, and standardized statistical methods).

The objective of this task is to evaluate whether metric values across the complete FY 2026 CMS Hospital Readmissions Reduction Program (HRRP) dataset are sufficiently available, interpretable, and numerically consistent to support condition-specific hospital benchmarking.

## Repository & Working Branch

- **Repository:** `nayanojwal0810/Yantra---Industrial-Anomaly-Detection-Monitoring`
- **Branch:** `project1/niramaya-validation`
- **Task Directory:** `validation/niramaya/task_03_metric_reliability_audit/`

All Task 3 code and generated outputs are maintained strictly inside this directory. Pre-existing files and prior task deliverables remain completely untouched. Raw datasets are not committed to version control.

## Input Dataset & Authoritative Sources

| Resource | Source & Reference URL |
| :--- | :--- |
| **Local Raw CSV** | `../data/raw/FY_2026_Hospital_Readmissions_Reduction_Program_Hospital.csv` |
| **CMS HRRP Dataset** | [CMS HRRP Dataset (9n3s-kdb3)](https://data.cms.gov/provider-data/dataset/9n3s-kdb3) |
| **Direct CMS CSV URL** | [CMS Direct Resource Link](https://data.cms.gov/provider-data/sites/default/files/resources/a171bc36c488d3e0dc33ec63abb469a6_1770163617/FY_2026_Hospital_Readmissions_Reduction_Program_Hospital.csv) |
| **CMS Hospitals — About the Data** | [CMS Hospital Data Documentation](https://data.cms.gov/provider-data/topics/hospitals/about-data) |
| **CMS Footnote Crosswalk** | [CMS Hospital Footnote Crosswalk (y9us-9xdf)](https://data.cms.gov/provider-data/dataset/y9us-9xdf) |
| **CMS Hospital Data Dictionary** | [HOSPITAL_Data_Dictionary.pdf](https://data.cms.gov/provider-data/sites/default/files/data_dictionaries/hospital/HOSPITAL_Data_Dictionary.pdf) |

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

The script writes eight primary artifacts to `output/`:
1. `hrrp_metric_reliability.json`: Structured JSON containing complete metric availability counts, ERR reconciliation metrics, numerical distribution stats, footnote breakdowns, and status patterns.
2. `hrrp_metric_reliability.md`: Human-readable Markdown report detailing factual findings across all 11 required audit areas.
3. `metric_availability_by_measure.csv`: Condition-specific summary table (one row per measure) reporting counts and percentages for all availability indicators.
4. `value_token_frequency.csv`: Exhaustive frequency table of all raw value tokens, normalized classifications, and dataset percentages.
5. `footnote_distribution.csv`: Distribution table of every distinct Footnote code, authoritative CMS definitions, documented applications, dataset percentages, and measure-level counts.
6. `footnote_status_crosstab.csv`: Detailed cross-tabulation mapping Footnote codes against ERR status, Discharges status, and Readmissions status across all 18,330 rows.
7. `err_reconciliation_exceptions.csv`: Evidence artifact containing standard headers and 0 data rows (confirming 100% mathematical reconciliation within tolerance).
8. `execution_environment.txt`: Execution environment details (Python version, operating system, platform architecture, percentile method, and command invocation).

## Summary of Findings

1. **Metric Availability by Condition:**
   - Public numeric ERR availability varies widely across the six clinical measures:
     - `READM-30-PN-HRRP` (Pneumonia): **2,715** numeric ERR (**88.87%**)
     - `READM-30-HF-HRRP` (Heart Failure): **2,621** numeric ERR (**85.79%**)
     - `READM-30-COPD-HRRP` (COPD): **2,323** numeric ERR (**76.04%**)
     - `READM-30-AMI-HRRP` (Myocardial Infarction): **1,736** numeric ERR (**56.82%**)
     - `READM-30-HIP-KNEE-HRRP` (Hip/Knee Arthroplasty): **1,447** numeric ERR (**47.36%**)
     - `READM-30-CABG-HRRP` (Coronary Artery Bypass): **878** numeric ERR (**28.74%**)
   - Across the full dataset, **11,720 of 18,330 rows (63.94%)** publish a numeric ERR.

2. **Record Coverage vs Outcome Availability vs Supporting Count Availability:**
   - **Record Coverage:** 100.0% (all 3,055 hospitals have rows for all 6 conditions).
   - **Outcome Availability:** 63.94% (11,720 rows publish numeric ERR).
   - **Supporting Count Availability:** Exactly **8,037 rows (43.85%)** have **both** Number of Discharges and Number of Readmissions as numeric counts.
   - **Withheld Supporting Counts:** Exactly **3,683 rows (20.09%)** have `Number of Discharges = N/A` and `Number of Readmissions = Too Few to Report`, yet publish official numeric values for ERR, Predicted Rate, and Expected Rate. Unavailable supporting counts do not invalidate a published numeric ERR.

3. **ERR Mathematical Reconciliation (`Predicted / Expected`):**
   - Evaluated using strict `Decimal` arithmetic: `Calculated ERR = Predicted Rate / Expected Rate`.
   - All **11,720 eligible rows (100.0%)** reconcile within the **0.0001 audit screening tolerance selected for this validation**.
   - Maximum absolute difference observed is **0.000065**, fully consistent with standard publication rounding of 4-decimal published inputs.
   - Zero reconciliation exceptions (`err_reconciliation_exceptions.csv` has 0 data rows).
   - Median discrepancy (conventional): `0.00002487`; 95th percentile (nearest-rank): `0.00004814`.

4. **Numerical Range & Plausibility:**
   - ERR values range from **0.4698 to 1.6297** (6,070 below 1.0; 7 equal to 1.0; 5,643 above 1.0). Zero negative or zero ERR values. Conventional median: `0.9973`.
   - Predicted rates range from `1.9080%` to `28.1643%` (Median: `15.86015%`); Expected rates range from `3.0876%` to `26.8654%` (Median: `15.85655%`). Uniform 4-decimal precision. Zero rates <= 0% or > 100%.
   - Discharges range from 0 to 3,672; Readmissions range from 11 to 847. Readmissions exceeding discharges: 0.
   - Exactly **205 rows** report `Number of Discharges = 0` with Footnote 7 ("No cases met the criteria for this measure") and ERR = N/A. This is distinct from the statutory HRRP 25-eligible-discharge payment-reduction rule.

5. **Authoritative CMS Footnote Definitions & Documented Applications:**
   - **Blank (`''`):** 11,343 rows (61.88%) — Standard reported metric or unannotated.
   - **Footnote `5`:** 3,255 rows (17.76%) — *"Results are not available for this reporting period."*
   - **Footnote `1`:** 3,150 rows (17.18%) — *"The number of cases/patients is too few to report."* Documented applications include not meeting minimum reporting requirements, too few cases to reliably assess performance, and personal health information protection.
   - **Footnote `29`:** 377 rows (2.06%) — *"This measure was calculated using partial performance period data due to a CMS-approved exception."* Results were based on less than the maximum possible performance period, but not all quarters, due to a CMS-approved Extraordinary Circumstances Exception (ECE) affecting one or more quarters.
   - **Footnote `7`:** 205 rows (1.12%) — *"No cases met the criteria for this measure."*

6. **Footnote 29 Partial-Period Exception Analysis:**
   - Footnote 29 occurs on exactly **377 rows**.
   - All 377 rows publish valid numeric ERR, Predicted Rate, and Expected Rate values (239 with numeric counts, 138 with withheld counts).
   - Footnote 29 identifies a partial-performance-period exception, not an invalid or missing outcome. These records are preserved; future benchmarking analyses should flag them and evaluate sensitivity with and without these records.

7. **Footnote/Status Cross-Tabulation Co-occurrences:**
   - Footnotes 1 and 5 always co-occur with all metrics being N/A (3,150 and 3,255 rows).
   - Footnote 7 always co-occurs with Discharges = 0, ERR = N/A, and Readmissions = N/A (205 rows).
   - Footnote 29 always co-occurs with numeric ERR (239 fully numeric counts, 138 with withheld counts).
   - BLANK footnote always co-occurs with numeric ERR (7,798 fully numeric counts, 3,545 with withheld counts).
   - All categories reconcile to exactly 18,330 source rows (100.0%).
