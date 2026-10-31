# NIRAMAYA — HRRP METRIC AVAILABILITY AND NUMERICAL RELIABILITY AUDIT REPORT

> **Project:** Niramaya  
> **Task:** Task 03 — HRRP Metric Availability and Numerical Reliability Audit (Targeted Correction)  
> **Audit Date & Time (UTC):** 2026-10-31T14:39:23Z  
> **Audit Date & Time (Local):** 2026-10-31 20:09:23 +0530  
> **Execution Command:** `python validation/niramaya/task_03_metric_reliability_audit/audit_hrrp_metric_reliability.py --data-file ../data/raw/FY_2026_Hospital_Readmissions_Reduction_Program_Hospital.csv --output-dir validation/niramaya/task_03_metric_reliability_audit/output`  

---

## 1. Executive Summary

This audit evaluates the numerical availability, suppression mechanics, and mathematical consistency of the six HRRP metric fields across the complete FY 2026 CMS dataset (18,330 rows).

| Evaluation Area | Key Factual Finding | Status / Assessment |
| :--- | :--- | :--- |
| **Total Processed Records** | 18,330 rows across 3,055 hospitals | 100% complete dataset parsed |
| **Published ERR Availability** | 11,720 rows (63.94%) | High variation by clinical condition |
| **Supporting Count Availability** | 8,037 rows (43.85%) | Both Discharges & Readmissions numeric |
| **Withheld Supporting Counts with Valid ERR** | 3,683 rows (20.1%) | Counts withheld, valid ERR published |
| **ERR Mathematical Reconciliation** | 11,720 eligible rows tested (`Pred / Exp`) | **100.0% within 0.0001 audit tolerance** (0 exceptions) |
| **Maximum ERR Discrepancy** | 0.000064675598759313145524894 | Negligible (rounding artifact < 0.000065) |
| **Numerical Range** | ERR: 0.4698 to 1.6297; Rates: 1.91% to 28.16% | Zero negative values; zero zero-rates |
| **Discharges = 0 Records** | Exactly 205 rows with Discharges = 0 | All 205 carry Footnote 7 and ERR = N/A |
| **Partial-Period Exceptions (Footnote 29)** | Exactly 377 rows carry Footnote 29 | CMS ECE exception; valid numeric ERR |
| **Readmissions > Discharges** | 0 occurrences | Zero logical count contradictions |

---

## 2. Dataset Overview & Source

- **Input File:** `FY_2026_Hospital_Readmissions_Reduction_Program_Hospital.csv`
- **Resolved Local Path:** `D:\Niramaya\data\raw\FY_2026_Hospital_Readmissions_Reduction_Program_Hospital.csv`
- **CMS Provider Data Catalogue URL:** [https://data.cms.gov/provider-data/dataset/9n3s-kdb3](https://data.cms.gov/provider-data/dataset/9n3s-kdb3)
- **Direct CMS Resource URL:** [https://data.cms.gov/provider-data/sites/default/files/resources/a171bc36c488d3e0dc33ec63abb469a6_1770163617/FY_2026_Hospital_Readmissions_Reduction_Program_Hospital.csv](https://data.cms.gov/provider-data/sites/default/files/resources/a171bc36c488d3e0dc33ec63abb469a6_1770163617/FY_2026_Hospital_Readmissions_Reduction_Program_Hospital.csv)
- **CMS Hospitals — About the Data:** [https://data.cms.gov/provider-data/topics/hospitals/about-data](https://data.cms.gov/provider-data/topics/hospitals/about-data)
- **CMS Footnote Crosswalk Source:** [https://data.cms.gov/provider-data/dataset/y9us-9xdf](https://data.cms.gov/provider-data/dataset/y9us-9xdf)
- **Total Records Processed:** 18,330
- **Total Columns:** 12
- **Statistical Percentile Method:** Nearest-rank method: index = ceil(p * n / 100) - 1 (with index = 0 for p = 0); conventional median: average of two middle elements for even sample size

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

The six CMS conditions exhibit marked differences in public ERR availability:

| Measure Code | Clinical Description | Total Rows | Numeric ERR | ERR Avail % | All 3 Rates Numeric | Numeric Discharges | Numeric Readmissions | Both Counts Numeric | Both Counts Withheld, ERR Numeric |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `READM-30-AMI-HRRP` | Acute Myocardial Infarction 30-Day Readmission | 3,055 | 1,736 | **56.8%** | 1,736 | 1,307 | 1,240 | 1,240 | 496 |
| `READM-30-CABG-HRRP` | Coronary Artery Bypass Graft 30-Day Readmission | 3,055 | 878 | **28.7%** | 878 | 381 | 363 | 363 | 515 |
| `READM-30-COPD-HRRP` | Chronic Obstructive Pulmonary Disease 30-Day Readmission | 3,055 | 2,323 | **76.0%** | 2,323 | 1,552 | 1,545 | 1,545 | 778 |
| `READM-30-HF-HRRP` | Heart Failure 30-Day Readmission | 3,055 | 2,621 | **85.8%** | 2,621 | 2,324 | 2,316 | 2,316 | 305 |
| `READM-30-HIP-KNEE-HRRP` | Elective Primary Total Hip/Knee Arthroplasty Readmission | 3,055 | 1,447 | **47.4%** | 1,447 | 350 | 253 | 253 | 1,194 |
| `READM-30-PN-HRRP` | Pneumonia 30-Day Readmission | 3,055 | 2,715 | **88.9%** | 2,715 | 2,328 | 2,320 | 2,320 | 395 |

> [!NOTE]
> When ERR is numeric, Predicted Readmission Rate and Expected Readmission Rate are **always** numeric (100% concordance across all 11,720 numeric records).

---

## 6. Record Coverage vs Outcome Availability vs Count Availability

A clear distinction must be maintained between three distinct tiers of data availability:

1. **Record Coverage (18,330 rows, 100.0%):** Every one of the 3,055 hospitals has exactly one record for all six conditions.
2. **Published Outcome Availability (11,720 rows, 63.94%):** The subset of hospital-condition pairs with a published numeric Excess Readmission Ratio.
3. **Supporting Count Availability (8,037 rows, 43.85%):** The subset of records where **both** Number of Discharges and Number of Readmissions are numeric.
4. **Withheld Supporting Counts with Published Outcome (3,683 rows, 20.1%):** Records where Number of Discharges is `N/A` and Readmissions is `Too Few to Report`, but CMS published an official risk-standardized numeric ERR.

> [!IMPORTANT]
> Unavailable or withheld supporting counts must **not** be treated as proof of outcome invalidity. Public ERR availability reflects CMS risk-standardized calculations, which are published even when raw counts are withheld.

---

## 7. ERR Mathematical Reconciliation (`Predicted / Expected`)

CMS defines the Excess Readmission Ratio as:
> `ERR = Predicted Readmission Rate / Expected Readmission Rate`

Using strict `Decimal` arithmetic, all 11,720 rows with numeric ERR, Predicted Rate, and Expected Rate were evaluated against the 0.0001 audit screening tolerance selected for this validation:

- **Total Rows Eligible for Reconciliation:** 11,720
- **Rows Reconciled Within 0.0001 Tolerance:** 11,720 (**100.0%**)
- **Rows Beyond 0.0001 Tolerance (Exceptions):** **0**
- **Maximum Absolute Discrepancy:** `0.000064675598759313145524894`
- **Median Absolute Discrepancy (Conventional):** `0.0000248724697990757485307335`
- **95th Percentile Discrepancy (Nearest-Rank):** `0.0000481366903669426643962929`

### Condition-Level Reconciliation Breakdown

| Measure Code | Eligible Rows | Within Tolerance | % Within Tolerance | Max Difference | Median Difference | 95th Percentile Diff |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `READM-30-AMI-HRRP` | 1,736 | 1,736 | 100.0% | `0.00005639` | `0.00002431` | `0.00004771` |
| `READM-30-CABG-HRRP` | 878 | 878 | 100.0% | `0.00005538` | `0.00002424` | `0.00004829` |
| `READM-30-COPD-HRRP` | 2,323 | 2,323 | 100.0% | `0.00005395` | `0.00002563` | `0.00004798` |
| `READM-30-HF-HRRP` | 2,621 | 2,621 | 100.0% | `0.00005408` | `0.00002468` | `0.00004807` |
| `READM-30-HIP-KNEE-HRRP` | 1,447 | 1,447 | 100.0% | `0.00006467` | `0.00002484` | `0.00005113` |
| `READM-30-PN-HRRP` | 2,715 | 2,715 | 100.0% | `0.00005554` | `0.00002494` | `0.00004783` |

### Top Discrepancies (Largest Deviations Observed)
The largest deviations are well below the 0.0001 screening threshold and result from standard rounding of 4-decimal published values:

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
- **Conventional Median:** `0.9973`
- **Nearest-Rank Percentiles:** p10=`0.9141`, p25=`0.9582`, p50=`0.9973`, p75=`1.0423`, p90=`1.0923`, p95=`1.1318`, p99=`1.2476`

### Predicted & Expected Readmission Rates
- **Predicted Rate Range:** `1.9080%` to `28.1643%` (Median: `15.86015%`)
- **Expected Rate Range:** `3.0876%` to `26.8654%` (Median: `15.85655%`)
- **Decimal Precision:** Uniformly 4 decimal places across 100% of numeric rate records.
- **Zero or Negative Rates:** 0 occurrences.
- **Rates > 100%:** 0 occurrences.

### Volume Counts (Discharges & Readmissions)
- **Discharges Range:** 0 to 3,672
- **Discharges < 25:** Exactly 205 records (all 205 have Discharges = 0, Footnote 7 ['No cases met the criteria for this measure'], and ERR = N/A).
- **Readmissions Range:** 11 to 847
- **Readmissions > Discharges:** 0 occurrences (0 logical contradictions).

---

## 9. Footnote Distribution & Cross-Tabulation

The Footnote field was audited using authoritative definitions from CMS Hospitals — About the data and the CMS Hospital Footnote Crosswalk (dataset y9us-9xdf):

| Footnote Code | CMS Definition | Documented Application / Context | Frequency | % Dataset |
| :--- | :--- | :--- | :--- | :--- |
| `BLANK` | Blank (No footnote; standard reported metric or unannotated) | Standard public data publication without exception or suppression annotation. | 11,343 | 61.88% |
| `5` | Results are not available for this reporting period. | Results were not available from CMS for the specified reporting period. | 3,255 | 17.76% |
| `1` | The number of cases/patients is too few to report. | The hospital did not meet the minimum case threshold for public reporting, had too few cases to reliably assess performance, or data was suppressed to protect personal health information. | 3,150 | 17.18% |
| `29` | This measure was calculated using partial performance period data due to a CMS-approved exception. | Results were based on less than the maximum possible performance period, but not all quarters, due to a CMS-approved Extraordinary Circumstances Exception affecting one or more quarters. | 377 | 2.06% |
| `7` | No cases met the criteria for this measure. | No cases treated at the hospital met the inclusion criteria for the specific condition measure during the performance window. | 205 | 1.12% |

### Footnote Code vs Metric Status Cross-Tabulation

This cross-tabulation establishes the exact co-occurrence of footnote codes with metric availability dimensions across all 18,330 source rows (reconciling to 100.0% of the dataset):

| Footnote Code | Footnote Meaning | ERR Status | Discharges Status | Readmissions Status | Records | % Dataset |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `1` | The number of cases/patients is too few to report. | `Non-numeric (N/A)` | `Non-numeric (N/A)` | `Non-numeric (N/A)` | 3,150 | 17.18% |
| `29` | This measure was calculated using partial performance period data due to a CMS-approved exception. | `Numeric` | `Numeric` | `Numeric` | 239 | 1.30% |
| `29` | This measure was calculated using partial performance period data due to a CMS-approved exception. | `Numeric` | `Non-numeric (N/A)` | `Non-numeric (Too Few to Report)` | 138 | 0.75% |
| `5` | Results are not available for this reporting period. | `Non-numeric (N/A)` | `Non-numeric (N/A)` | `Non-numeric (N/A)` | 3,255 | 17.76% |
| `7` | No cases met the criteria for this measure. | `Non-numeric (N/A)` | `Numeric` | `Non-numeric (N/A)` | 205 | 1.12% |
| `BLANK` | Blank (No footnote; standard reported metric or unannotated) | `Numeric` | `Numeric` | `Numeric` | 7,798 | 42.54% |
| `BLANK` | Blank (No footnote; standard reported metric or unannotated) | `Numeric` | `Non-numeric (N/A)` | `Non-numeric (Too Few to Report)` | 3,545 | 19.34% |

---

## 10. Status-Pattern Analysis (Field Co-occurrences)

Across all 18,330 rows, the metric fields resolve into exactly six distinct reporting patterns:

| # | Discharges | Readmissions | ERR | Predicted | Expected | Footnote | Frequency | Percentage |
| :-: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | `NUMERIC_INTEGER` | `NUMERIC_INTEGER` | `NUMERIC_DECIMAL` | `NUMERIC_DECIMAL` | `NUMERIC_DECIMAL` | `BLANK` | 7,798 | 42.54% |
| 2 | `N_A` | `N_A` | `N_A` | `N_A` | `N_A` | `NONBLANK` | 6,405 | 34.94% |
| 3 | `N_A` | `TOO_FEW_TO_REPORT` | `NUMERIC_DECIMAL` | `NUMERIC_DECIMAL` | `NUMERIC_DECIMAL` | `BLANK` | 3,545 | 19.34% |
| 4 | `NUMERIC_INTEGER` | `NUMERIC_INTEGER` | `NUMERIC_DECIMAL` | `NUMERIC_DECIMAL` | `NUMERIC_DECIMAL` | `NONBLANK` | 239 | 1.30% |
| 5 | `NUMERIC_INTEGER` | `N_A` | `N_A` | `N_A` | `N_A` | `NONBLANK` | 205 | 1.12% |
| 6 | `N_A` | `TOO_FEW_TO_REPORT` | `NUMERIC_DECIMAL` | `NUMERIC_DECIMAL` | `NUMERIC_DECIMAL` | `NONBLANK` | 138 | 0.75% |

---

## 11. Important Caveats and Unresolved Questions

- Record coverage (100% of 18,330 hospital-condition rows) differs substantially from outcome availability (63.94% numeric ERR).
- Public ERR availability varies widely across clinical conditions: Pneumonia (88.87%) and Heart Failure (85.79%) have high availability, whereas CABG has the lowest proportion of published numeric ERR at 28.74%.
- Supporting-count availability (where both Number of Discharges and Number of Readmissions are numeric) is 8,037 records (43.85% of dataset).
- Exactly 3,683 records have withheld supporting count fields (Number of Discharges = N/A and Number of Readmissions = Too Few to Report) while reporting official numeric values for ERR, Predicted Rate, and Expected Rate. Withheld supporting counts do not automatically invalidate a published numeric ERR.
- Exactly 205 records report Number of Discharges = 0 with Footnote 7 ('No cases met the criteria for this measure') and ERR = N/A. This is distinct from the statutory HRRP 25-eligible-discharge payment-reduction rule.
- 100.0% of the 11,720 numeric ERR records mathematically reconcile with Predicted Rate / Expected Rate within the 0.0001 audit screening tolerance selected for this validation (maximum absolute discrepancy is 0.000065, consistent with publication rounding of 4-decimal published rates).
- Observed numeric values range from 0.4698 to 1.6297 for ERR, 1.9080% to 28.1643% for Predicted Rate, 3.0876% to 26.8654% for Expected Rate, 0 to 3,672 for Discharges, and 11 to 847 for Readmissions. Zero negative rates, zero zero-rates, and zero instances of readmissions exceeding discharges were observed.
- Exactly 377 records carry Footnote 29 ('This measure was calculated using partial performance period data due to a CMS-approved exception'). All 377 publish numeric ERR values (239 with numeric counts, 138 with withheld counts). These records represent valid published outcomes based on a partial reporting window (Extraordinary Circumstances Exception); future benchmarking should flag them and evaluate sensitivity with and without these records.
- Numeric ERR availability reflects public CMS data publication, not eligibility for the official HRRP payment reduction penalty.
