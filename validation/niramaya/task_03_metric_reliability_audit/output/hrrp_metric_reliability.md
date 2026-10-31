# NIRAMAYA — HRRP METRIC AVAILABILITY AND NUMERICAL RELIABILITY AUDIT REPORT

> **Project:** Niramaya  
> **Task:** Task 03 — HRRP Metric Availability and Numerical Reliability Audit  
> **Audit Date & Time (UTC):** 2026-10-31T14:10:39Z  
> **Audit Date & Time (Local):** 2026-10-31 19:40:39 +0530  
> **Execution Command:** `python validation/niramaya/task_03_metric_reliability_audit/audit_hrrp_metric_reliability.py --data-file ../data/raw/FY_2026_Hospital_Readmissions_Reduction_Program_Hospital.csv --output-dir validation/niramaya/task_03_metric_reliability_audit/output`  

---

## 1. Executive Summary

This audit evaluates the numerical availability, suppression mechanics, and mathematical consistency of the six HRRP metric fields across the complete FY 2026 CMS dataset (18,330 rows).

| Evaluation Area | Key Factual Finding | Status / Assessment |
| :--- | :--- | :--- |
| **Total Processed Records** | 18,330 rows across 3,055 hospitals | 100% complete dataset parsed |
| **Published ERR Availability** | 11,720 rows (63.94%) | High variation by clinical condition |
| **Supporting Count Availability** | 8,037 rows (43.85%) | Discharges & readmissions unmasked |
| **Volume Suppression with Valid ERR** | 3,683 rows (20.1%) | Masked for privacy, valid ERR published |
| **ERR Mathematical Reconciliation** | 11,720 eligible rows tested (`Pred / Exp`) | **100.0% within 0.0001 tolerance** (0 exceptions) |
| **Maximum ERR Discrepancy** | 0.000064675598759313145524894 | Negligible (rounding artifact < 0.000065) |
| **Numerical Range Integrity** | ERR: 0.4698 to 1.6297; Rates: 1.91% to 28.16% | Zero negative values; zero extreme outliers |
| **Discharges < 25 Exploration** | Exactly 205 rows with Discharges = 0 | All 205 carry Footnote 7 and ERR = N/A |
| **Readmissions > Discharges** | 0 occurrences | Zero logical count contradictions |

---

## 2. Dataset Overview & Source

- **Input File:** `FY_2026_Hospital_Readmissions_Reduction_Program_Hospital.csv`
- **Resolved Local Path:** `D:\Niramaya\data\raw\FY_2026_Hospital_Readmissions_Reduction_Program_Hospital.csv`
- **CMS Provider Data Catalogue URL:** [https://data.cms.gov/provider-data/dataset/9n3s-kdb3](https://data.cms.gov/provider-data/dataset/9n3s-kdb3)
- **Direct CMS Resource URL:** [https://data.cms.gov/provider-data/sites/default/files/resources/a171bc36c488d3e0dc33ec63abb469a6_1770163617/FY_2026_Hospital_Readmissions_Reduction_Program_Hospital.csv](https://data.cms.gov/provider-data/sites/default/files/resources/a171bc36c488d3e0dc33ec63abb469a6_1770163617/FY_2026_Hospital_Readmissions_Reduction_Program_Hospital.csv)
- **Total Records Processed:** 18,330
- **Total Columns:** 12

---

## 3. Metric Field Value Classifications

Every value across the six metric fields was classified using strict type and token inspection:

| Metric Field | Total Rows | Blank | Numeric Integer | Numeric Decimal | N/A | Too Few to Report | Other Non-numeric | Distinct Tokens |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `Number of Discharges` | 18,330 | 0 | 8,242 | 0 | 10,088 | 0 | 0 | 1,045 |
| `Footnote` | 18,330 | 11,343 | 6,987 | 0 | 0 | 0 | 0 | 5 |
| `Excess Readmission Ratio` | 18,330 | 0 | 0 | 11,720 | 6,610 | 0 | 0 | 3,253 |
| `Predicted Readmission Rate` | 18,330 | 0 | 0 | 11,720 | 6,610 | 0 | 0 | 11,261 |
| `Expected Readmission Rate` | 18,330 | 0 | 0 | 11,720 | 6,610 | 0 | 0 | 11,230 |
| `Number of Readmissions` | 18,330 | 0 | 8,037 | 0 | 6,610 | 3,683 | 0 | 291 |

---

## 4. Nonnumeric Token Frequencies

Distinct nonnumeric string tokens observed across the five metric fields (excluding Footnote):

| Metric Field | Raw Token | Normalized Classification | Frequency | Percentage of Dataset |
| :--- | :--- | :--- | :--- | :--- |
| `Number of Discharges` | `N/A` | `N_A` | 10,088 | 55.04% |
| `Excess Readmission Ratio` | `N/A` | `N_A` | 6,610 | 36.06% |
| `Predicted Readmission Rate` | `N/A` | `N_A` | 6,610 | 36.06% |
| `Expected Readmission Rate` | `N/A` | `N_A` | 6,610 | 36.06% |
| `Number of Readmissions` | `Too Few to Report` | `TOO_FEW_TO_REPORT` | 3,683 | 20.09% |
| `Number of Readmissions` | `N/A` | `N_A` | 6,610 | 36.06% |

---

## 5. Metric Availability by Clinical Condition

The six CMS conditions exhibit distinct clinical prevalence and surgical centralization, leading to marked differences in public ERR availability:

| Measure Code | Clinical Description | Total Rows | Numeric ERR | ERR Avail % | All 3 Rates Numeric | Numeric Discharges | Numeric Readmissions | Both Counts Masked, ERR Numeric |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `READM-30-AMI-HRRP` | Acute Myocardial Infarction 30-Day Readmission | 3,055 | 1,736 | **56.8%** | 1,736 | 1,307 | 1,240 | 496 |
| `READM-30-CABG-HRRP` | Coronary Artery Bypass Graft 30-Day Readmission | 3,055 | 878 | **28.7%** | 878 | 381 | 363 | 515 |
| `READM-30-COPD-HRRP` | Chronic Obstructive Pulmonary Disease 30-Day Readmission | 3,055 | 2,323 | **76.0%** | 2,323 | 1,552 | 1,545 | 778 |
| `READM-30-HF-HRRP` | Heart Failure 30-Day Readmission | 3,055 | 2,621 | **85.8%** | 2,621 | 2,324 | 2,316 | 305 |
| `READM-30-HIP-KNEE-HRRP` | Elective Primary Total Hip/Knee Arthroplasty Readmission | 3,055 | 1,447 | **47.4%** | 1,447 | 350 | 253 | 1,194 |
| `READM-30-PN-HRRP` | Pneumonia 30-Day Readmission | 3,055 | 2,715 | **88.9%** | 2,715 | 2,328 | 2,320 | 395 |

> [!NOTE]
> When ERR is numeric, Predicted Readmission Rate and Expected Readmission Rate are **always** numeric (100% concordance across all 11,720 numeric records).

---

## 6. Record Coverage vs Outcome Availability vs Count Availability

A critical distinction must be maintained between three distinct tiers of data availability:

1. **Record Coverage (18,330 rows, 100.0%):** Every one of the 3,055 hospitals has exactly one record for all six conditions.
2. **Published Outcome Availability (11,720 rows, 63.94%):** The subset of hospital-condition pairs with a published numeric Excess Readmission Ratio.
3. **Supporting Count Availability (8,037 rows, 43.85%):** The subset of rows with unmasked numeric discharge and readmission volumes.
4. **Volume-Suppressed Outcome Availability (3,683 rows, 20.1%):** Rows where Number of Discharges is `N/A` and Readmissions is `Too Few to Report`, but CMS published an official risk-standardized numeric ERR.

> [!IMPORTANT]
> Suppressed volume counts must **not** be treated as proof of outcome invalidity. Public ERR availability reflects CMS risk-standardized calculations, which CMS publishes even when raw numerator counts are suppressed for privacy.

---

## 7. ERR Mathematical Reconciliation (`Predicted / Expected`)

CMS defines the Excess Readmission Ratio as:
> `ERR = Predicted Readmission Rate / Expected Readmission Rate`

Using strict `Decimal` arithmetic, all 11,720 rows with numeric ERR, Predicted Rate, and Expected Rate were evaluated against the official 0.0001 screening tolerance:

- **Total Rows Eligible for Reconciliation:** 11,720
- **Rows Reconciled Within 0.0001 Tolerance:** 11,720 (**100.0%**)
- **Rows Beyond 0.0001 Tolerance (Exceptions):** **0**
- **Maximum Absolute Discrepancy:** `0.000064675598759313145524894`
- **Median Absolute Discrepancy:** `0.000024873382104670793472144`
- **95th Percentile Discrepancy:** `0.0000481387788676608954820244`

### Condition-Level Reconciliation Breakdown

| Measure Code | Eligible Rows | Within Tolerance | % Within Tolerance | Max Difference | Median Difference | 95th Percentile Diff |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `READM-30-AMI-HRRP` | 1,736 | 1,736 | 100.0% | `0.00005639` | `0.00002432` | `0.00004771` |
| `READM-30-CABG-HRRP` | 878 | 878 | 100.0% | `0.00005538` | `0.00002425` | `0.00004829` |
| `READM-30-COPD-HRRP` | 2,323 | 2,323 | 100.0% | `0.00005395` | `0.00002563` | `0.00004798` |
| `READM-30-HF-HRRP` | 2,621 | 2,621 | 100.0% | `0.00005408` | `0.00002468` | `0.00004807` |
| `READM-30-HIP-KNEE-HRRP` | 1,447 | 1,447 | 100.0% | `0.00006467` | `0.00002484` | `0.00005113` |
| `READM-30-PN-HRRP` | 2,715 | 2,715 | 100.0% | `0.00005554` | `0.00002494` | `0.00004783` |

### Top Discrepancies (Largest Deviations Observed)
The largest deviations are well below the 0.0001 threshold and result from standard rounding of 4-decimal published values:

| Facility ID | State | Measure | Published ERR | Predicted Rate | Expected Rate | Calculated Ratio | Abs Difference |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `050485` | CA | `READM-30-HIP-KNEE-HRRP` | `1.3162` | `8.2319` | `6.2546` | `1.316135` | `0.00006467` |
| `110161` | GA | `READM-30-HIP-KNEE-HRRP` | `0.9816` | `4.3430` | `4.4247` | `0.981535` | `0.00006452` |
| `140161` | IL | `READM-30-HIP-KNEE-HRRP` | `1.0426` | `4.2525` | `4.0785` | `1.042662` | `0.00006274` |
| `140046` | IL | `READM-30-HIP-KNEE-HRRP` | `0.9495` | `4.7537` | `5.0062` | `0.949562` | `0.00006254` |
| `100126` | FL | `READM-30-HIP-KNEE-HRRP` | `1.4314` | `8.4104` | `5.8759` | `1.431338` | `0.00006182` |

---

## 8. Numerical Range and Plausibility Checks

### Excess Readmission Ratio Distribution
- **Total Numeric Observations:** 11,720
- **Zero Values:** 0
- **Negative Values:** 0
- **Values < 1.0 (Favorable):** 6,070 (51.8%)
- **Values == 1.0 (Neutral):** 7 (0.06%)
- **Values > 1.0 (Excess Readmissions):** 5,643 (48.1%)
- **Range:** Min `0.4698` to Max `1.6297`
- **Percentiles:** p10=`0.9142`, p25=`0.9582`, p50=`0.9973`, p75=`1.0423`, p90=`1.0923`, p95=`1.1318`, p99=`1.2476`

### Predicted & Expected Readmission Rates
- **Predicted Rate Range:** `1.9080%` to `28.1643%` (p50: `15.8602%`)
- **Expected Rate Range:** `3.0876%` to `26.8654%` (p50: `15.8570%`)
- **Decimal Precision:** Uniformly 4 decimal places across 100% of numeric rate records.
- **Anomalies (> 100% or <= 0%):** 0 occurrences.

### Volume Counts (Discharges & Readmissions)
- **Discharges Range:** 0 to 3,672
- **Discharges < 25:** Exactly 205 records (all 205 have Discharges = 0, Footnote 7, and ERR = N/A).
- **Readmissions Range:** 11 to 847
- **Readmissions > Discharges:** 0 occurrences (0 logical contradictions).

---

## 9. Footnote Distribution

| Footnote Code | CMS Definition / Interpretation | Frequency | % Dataset |
| :--- | :--- | :--- | :--- |
| `BLANK` | Blank (No footnote; standard reported metric or unannotated) | 11,343 | 61.88% |
| `5` | The number of cases/patients is too small to tell how well the hospital is performing | 3,255 | 17.76% |
| `1` | The number of cases/patients is too small to reliably tell how well the hospital is performing | 3,150 | 17.18% |
| `29` | Data is currently not available / results are not available for this reporting period | 377 | 2.06% |
| `7` | The number of cases/patients is too small to reliably tell how well the hospital is performing (or fewer than 25 eligible discharges) | 205 | 1.12% |

---

## 10. Status-Pattern Analysis (Field Co-occurrences)

Across all 18,330 rows, the metric fields resolve into exactly six distinct reporting patterns:

| # | Discharges | Readmissions | ERR | Predicted | Expected | Footnote | Frequency | Percentage |
| :-: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | `NUMERIC_INTEGER` | `NUMERIC_INTEGER` | `NUMERIC_DECIMAL` | `NUMERIC_DECIMAL` | `NUMERIC_DECIMAL` | `BLANK` | 7,798 | 42.54% |
| 2 | `N_A` | `N_A` | `N_A` | `N_A` | `N_A` | `NONBLANK` | 6,405 | 34.94% |
| 3 | `N_A` | `TOO_FEW_TO_REPORT` | `NUMERIC_DECIMAL` | `NUMERIC_DECIMAL` | `NUMERIC_DECIMAL` | `BLANK` | 3,545 | 19.34% |
| 4 | `NUMERIC_INTEGER` | `NUMERIC_INTEGER` | `NUMERIC_DECIMAL` | `NUMERIC_DECIMAL` | `NUMERIC_DECIMAL` | `NONBLANK` | 239 | 1.30% |
| 5 | `NUMERIC_INTEGER` | `N_A` | `N_A` | `N_A` | `N_A` | `NONBLANK` | 205 | 1.12% |
| 6 | `N_A` | `TOO_FEW_TO_REPORT` | `NUMERIC_DECIMAL` | `NUMERIC_DECIMAL` | `NUMERIC_DECIMAL` | `NONBLANK` | 138 | 0.75% |

---

## 11. Important Caveats and Unresolved Questions

- Record coverage (100% of 18,330 hospital-condition rows) differs substantially from outcome availability (63.94% numeric ERR).
- Public outcome availability varies dramatically across clinical conditions: Pneumonia (88.9%) and Heart Failure (85.8%) have high coverage, while CABG (28.7%) has low coverage due to surgical volume concentration.
- Suppression of readmission volume ('Too Few to Report', 3,683 rows) co-occurs with fully reported numeric ERR, Predicted Rate, and Expected Rate; volume suppression must not be treated as outcome invalidity.
- Discharge count is 'N/A' in 3,683 rows where readmission count is 'Too Few to Report' but ERR is numeric, confirming that CMS risk-standardized ratios are published even when raw counts are masked for patient privacy.
- Exactly 205 records report Number of Discharges = 0 with Footnote 7 ('fewer than 25 eligible discharges') and ERR = N/A.
- 100.0% of the 11,720 numeric ERR records mathematically reconcile with Predicted Rate / Expected Rate within the 0.0001 screening tolerance (maximum absolute discrepancy is 0.000065, reflecting standard publication rounding).
- Zero numeric records exhibit negative values, zero rates, or readmissions exceeding discharges.
- Numeric ERR availability is a measure of public data publication, not an indicator of official HRRP payment-reduction penalty eligibility.
