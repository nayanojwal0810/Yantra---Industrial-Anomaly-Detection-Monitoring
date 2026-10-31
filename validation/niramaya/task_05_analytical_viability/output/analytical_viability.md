# Niramaya — Validation Task 05: Analytical Viability and Business Usefulness Audit Report

> **Project:** Niramaya  
> **Task:** Validation Task 05 — Analytical Viability and Business Usefulness  
> **Audit Date & Time (UTC):** 2026-10-31 15:29:32 UTC  
> **Audit Date & Time (Local):** 2026-10-31 20:59:32 India Standard Time  
> **Execution Command:** `validation/niramaya/task_05_analytical_viability/audit_analytical_viability.py --hrrp-file ../data/raw/FY_2026_Hospital_Readmissions_Reduction_Program_Hospital.csv --hgi-file ../data/raw/Hospital_General_Information.csv --output-dir validation/niramaya/task_05_analytical_viability/output`  

---

## 1. Executive Summary & Audit Overview

This deliverable provides an empirical feasibility assessment evaluating whether the CMS **FY 2026 Hospital Readmissions Reduction Program (HRRP)** dataset, joined with the **Hospital General Information (HGI)** dimension snapshot, supports defensible descriptive and diagnostic analytics.

The evaluation was performed strictly using standard-library Python across the complete, unmodified raw CSV datasets:
1. `FY_2026_Hospital_Readmissions_Reduction_Program_Hospital.csv` (18,330 records, 3,055 facilities)
2. `Hospital_General_Information.csv` (5,419 records, 5,419 facilities)

### Key Empirical Findings

| Evaluation Domain | Factual Finding | Feasibility & Analytical Utility |
| :--- | :--- | :--- |
| **Dataset Reconfirmation** | 18,330 HRRP rows (3,055 facilities × 6 measures); 5,419 unique HGI IDs; 1.0x join factor | **100.0% Uniform Fact Grain (0 row multiplication)** |
| **Numeric ERR Availability** | 11,720 numeric ERR records (63.94%); 6,610 nonnumeric (36.06%) | **100% Concordant with Predicted & Expected Rates** |
| **Condition Sample Sizes** | High: PN (2,715) & HF (2,621); Moderate: COPD (2,323), AMI (1,736), Hip/Knee (1,447); Sparse: CABG (878) | **Condition-Specific Benchmarking Feasible** (CABG restricted) |
| **Observed Variation** | Means range from 1.0011 to 1.0040; medians range from 0.9916 to 1.0000; IQRs range from 0.0574 to 0.1890 | **Sufficient Spread for Relative Descriptive Benchmarking** |
| **Footnote 29 Sensitivity** | 377 numeric records carry Footnote 29; excluding them shifts means by ≤ 0.0005 and medians by ≤ 0.0003 | **Negligible Impact on Descriptive Distributions** |
| **State-Level Comparisons** | 51 jurisdictions; 0 empty cells; 20 of 306 cells (6.54%) have < 5 numeric records (primarily CABG) | **Feasible for Major States/Conditions; Small States Require Caution** |
| **HGI Segment Comparisons** | Profiled 10 ownership classes and 2 emergency-services classes | **Exploratory Only; July 2026 Snapshot; Not Causal** |

---

## 2. Analytical Dataset Reconfirmation

Schema integrity, primary key uniqueness, and Cartesian uniformity were validated across 100% of rows:

- **HRRP Raw Rows:** 18,330 rows across 3,055 distinct facilities.
- **Measure Grain:** Exactly 6 condition measures per hospital (3,055 × 6 = 18,330; 100.0% uniform Cartesian grain).
- **Numeric ERR Availability:** Exactly 11,720 numeric ERR values (63.94%) and 6,610 nonnumeric values (36.06%).
- **Rate Concordance:** Exactly 100% of numeric ERR values have numeric Predicted and Expected Readmission Rates; exactly 100% of nonnumeric ERR values have nonnumeric Predicted and Expected rates.
- **HGI Dimension Table:** Exactly 5,419 rows and 5,419 unique Facility IDs (100.0% primary key uniqueness).
- **Join Integrity:** Left outer join on `Facility ID` yields exactly 3,035 matched facilities (18,210 fact rows) and 20 unmatched facilities (120 fact rows), with exactly **zero row multiplication** (factor: 1.0x).

---

## 3. Condition-Level Analytical Viability & Distribution Analysis

Unweighted facility-level descriptive statistics were calculated for each of the six condition measures across all 3,055 facilities.

> [!IMPORTANT]
> These statistics represent equal-weighted facility-level descriptive metrics. They are not CMS national aggregate performance rates and are not patient-volume-weighted. Conditions must never be combined into a single hospital composite score.

| Measure Code | Measure Description | Total Hospitals | Numeric ERR (Count / %) | Nonnumeric (Count / %) | ERR Min | ERR Max | Mean | Median | StdDev | IQR (P25–P75) | % < 1.0 | % = 1.0 | % > 1.0 |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `READM-30-AMI-HRRP` | Acute Myocardial Infarction (AMI) 30-Day Readmission Rate | 3,055 | 1,736 (56.82%) | 1,319 (43.18%) | 0.6839 | 1.2639 | 1.001755 | 0.9994 | 0.066824 | 0.0814 (0.9608–1.0422) | 50.35% | 0.0% | 49.65% |
| `READM-30-CABG-HRRP` | Coronary Artery Bypass Graft (CABG) 30-Day Readmission Rate | 3,055 | 878 (28.74%) | 2,177 (71.26%) | 0.7434 | 1.4237 | 1.001789 | 1.0000 | 0.096565 | 0.1247 (0.9377–1.0624) | 50.0% | 0.11% | 49.89% |
| `READM-30-COPD-HRRP` | Chronic Obstructive Pulmonary Disease (COPD) 30-Day Readmission Rate | 3,055 | 2,323 (76.04%) | 732 (23.96%) | 0.8681 | 1.2545 | 1.001133 | 0.9969 | 0.045972 | 0.0574 (0.9707–1.0281) | 52.65% | 0.13% | 47.22% |
| `READM-30-HF-HRRP` | Heart Failure (HF) 30-Day Readmission Rate | 3,055 | 2,621 (85.79%) | 434 (14.21%) | 0.7137 | 1.3606 | 1.001439 | 0.9983 | 0.065035 | 0.0808 (0.9606–1.0414) | 51.05% | 0.04% | 48.91% |
| `READM-30-HIP-KNEE-HRRP` | Elective Primary Total Hip Arthroplasty (THA) and/or Total Knee Arthroplasty (TKA) 30-Day Readmission Rate | 3,055 | 1,447 (47.36%) | 1,608 (52.64%) | 0.4698 | 1.6297 | 1.003985 | 0.9916 | 0.155675 | 0.1890 (0.9000–1.0890) | 52.11% | 0.0% | 47.89% |
| `READM-30-PN-HRRP` | Pneumonia (PN) 30-Day Readmission Rate | 3,055 | 2,715 (88.87%) | 340 (11.13%) | 0.7967 | 1.4255 | 1.001486 | 0.9955 | 0.066296 | 0.0793 (0.9595–1.0388) | 53.11% | 0.07% | 46.81% |

### Condition-Level Footnote Breakdown

CMS footnotes document why measure results were not published or whether performance periods were modified:

| Measure Code | Blank (Standard) | Footnote 1 (Too Few Cases) | Footnote 5 (Not Available) | Footnote 7 (No Cases Met Criteria) | Footnote 29 (Approved Exception) | Total Records |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `READM-30-AMI-HRRP` | 1,675 | 933 | 319 | 67 | 61 | 3,055 |
| `READM-30-CABG-HRRP` | 844 | 184 | 1,975 | 18 | 34 | 3,055 |
| `READM-30-COPD-HRRP` | 2,252 | 526 | 199 | 7 | 71 | 3,055 |
| `READM-30-HF-HRRP` | 2,543 | 230 | 196 | 8 | 78 | 3,055 |
| `READM-30-HIP-KNEE-HRRP` | 1,397 | 1,114 | 397 | 97 | 50 | 3,055 |
| `READM-30-PN-HRRP` | 2,632 | 163 | 169 | 8 | 83 | 3,055 |

---

## 4. Observed Variation and Distribution Assessment

1. **Spread & Central Tendency:**
   - Across all six measures, the unweighted facility-level means (1.0011 to 1.0040) and medians (0.9916 to 1.0000) are tightly centered near 1.0000, consistent with risk-standardized ratio properties.
   - The difference between mean and median is minimal (ranging from 0.0018 for CABG to 0.0124 for Hip/Knee), indicating reasonably symmetric distributions without massive skewness.
2. **Interquartile Range & Dispersion:**
   - COPD exhibits the narrowest interquartile spread (IQR: 0.0574, P25: 0.9707 to P75: 1.0281; StdDev: 0.045972), reflecting relatively uniform readmission patterns across active acute care hospitals.
   - Elective Hip/Knee Replacement exhibits the widest interquartile spread (IQR: 0.1890, P25: 0.9000 to P75: 1.0890; StdDev: 0.155675), indicating substantial facility-level variation in risk-adjusted outcomes.
   - AMI, HF, and Pneumonia demonstrate moderate, highly comparable dispersions (IQRs: ~0.080, StdDevs: ~0.066).
3. **Extreme Value Inspection:**
   - Minimum observed ERR is 0.4698 (Hip/Knee); maximum observed ERR is 1.6297 (Hip/Knee).
   - Extreme values do not heavily distort the central tendency: P05 and P95 percentiles demonstrate that 90% of hospitals fall within bounded intervals (e.g. 0.8964 to 1.1092 for Heart Failure).
   - Facilities with extreme ERR values represent genuine risk-adjusted statistical estimates published by CMS, not data entry errors, and must not be automatically winsorized or discarded.
4. **Sample Breadth Across Conditions:**
   - Pneumonia (2,715 hospitals; 88.87%) and Heart Failure (2,621 hospitals; 85.79%) offer extensive nationwide coverage.
   - CABG is restricted to 878 hospitals (28.74%), because coronary artery bypass surgery is performed only at specialized surgical facilities. Benchmarking for CABG must be restricted to cardiac surgery centers.

---

## 5. Footnote 29 Sensitivity Assessment

Footnote 29 applies when a hospital's measure was calculated using partial performance period data due to a CMS-approved Extraordinary Circumstances Exception.

Across the entire dataset, exactly **377 records** carry Footnote 29. Crucially, **all 377 records contain valid numeric ERR values**. To evaluate whether including these partial-period records introduces bias, descriptive statistics were compared between: (1) All published numeric records, and (2) Records excluding Footnote 29.

| Measure Code | FN 29 Records | Version 1: All Published (N / Mean / Med / % > 1) | Version 2: Excluding FN 29 (N / Mean / Med / % > 1) | Absolute Difference (Mean / Med / % > 1) |
| :--- | :---: | :---: | :---: | :---: |
| `READM-30-AMI-HRRP` | 61 | N=1,736 / 1.001755 / 0.9994 / 49.65% | N=1,675 / 1.001677 / 0.9994 / 49.55% | -0.000078 / -0.0000 / -0.10% |
| `READM-30-CABG-HRRP` | 34 | N=878 / 1.001789 / 1.0000 / 49.89% | N=844 / 1.002311 / 1.0000 / 49.88% | 0.000522 / 0.0000 / -0.00% |
| `READM-30-COPD-HRRP` | 71 | N=2,323 / 1.001133 / 0.9969 / 47.22% | N=2,252 / 1.001281 / 0.9972 / 47.38% | 0.000148 / 0.0002 / +0.16% |
| `READM-30-HF-HRRP` | 78 | N=2,621 / 1.001439 / 0.9983 / 48.91% | N=2,543 / 1.001729 / 0.9986 / 49.08% | 0.000290 / 0.0003 / +0.16% |
| `READM-30-HIP-KNEE-HRRP` | 50 | N=1,447 / 1.003985 / 0.9916 / 47.89% | N=1,397 / 1.004153 / 0.9915 / 47.89% | 0.000168 / -0.0001 / -0.00% |
| `READM-30-PN-HRRP` | 83 | N=2,715 / 1.001486 / 0.9955 / 46.81% | N=2,632 / 1.001754 / 0.9956 / 46.85% | 0.000268 / 0.0001 / +0.03% |
| `ALL_MEASURES_COMBINED` | 377 | N=11,720 / 1.001777 / 0.9973 / 48.15% | N=11,343 / 1.001980 / 0.9974 / 48.21% | 0.000203 / 0.0001 / +0.06% |

### Key Findings on Footnote 29 Sensitivity
- **Negligible Mean Impact:** Excluding Footnote 29 records changes condition-level means by at most **0.000522** (CABG) and by only **0.000203** across the combined pool.
- **Negligible Median Impact:** Condition-level medians change by at most **0.0003** (Heart Failure) and by **0.0001** overall.
- **Negligible Distribution Shift:** The proportion of hospitals with ERR > 1.0 shifts by at most **0.16%** (COPD and HF), with exactly zero shift in CABG and Hip/Knee.
- **Conclusion:** Footnote 29 records do not distort unweighted descriptive distributions. They represent valid CMS public reporting and can be safely retained in condition-specific benchmarking.

---

## 6. State-Level Comparison Feasibility

State was evaluated directly from the HRRP fact dataset across all 51 jurisdictions (50 states + District of Columbia) across the 6 condition measures (306 state-condition combinations).

- **Coverage:** Exactly **0 of the 306 state-condition cells** have zero numeric records. Every state has at least one active hospital with a published ERR for each condition.
- **Sparse Cells (< 5 Numeric Hospitals):** Exactly **20 of 306 cells (6.54%)** contain fewer than 5 hospitals.
  - These sparse cells are heavily concentrated in specialized surgical measures (CABG: 10 states; Hip/Knee: 8 states) within small jurisdictions (e.g., AK, DC, DE, HI, ME, ND, VT, WY).
- **Methodological Guardrail:**
  - State-level comparisons are highly feasible for medical conditions (Pneumonia, Heart Failure, COPD) across moderate-to-large states.
  - For small states or specialized surgical measures, cell counts must be prominently displayed, and ranking or comparative claims must be avoided due to high sampling variability.

---

## 7. Optional HGI Segment Feasibility (Ownership & Emergency Services)

Using the exact Facility ID left join, two candidate operational attributes were evaluated from the July 2026 HGI snapshot:

### A. Hospital Ownership (10 Categories + Unmatched Cohort)
- **Matched Distribution:** Voluntary non-profit Private (1,474), Proprietary (619), Voluntary non-profit Other (241), Hospital District/Authority (220), Voluntary non-profit Church (199), Government Local (135), Physician (70), Government State (45), Government Federal (23), Tribal (9), plus 20 Unmatched HRRP facilities.
- **Feasibility:** Major ownership types (Private Non-profit, Proprietary, District, Church, Local Government) provide sufficient cell sizes (> 100 hospitals) for descriptive benchmarking.
- **Limitation:** Small categories (Tribal: 9 facilities; Federal: 23 facilities; State: 45 facilities) produce sparse condition-level cells (e.g., Tribal CABG has 0 numeric ERR values; Physician CABG has 14).

### B. Emergency Services (2 Categories + Unmatched Cohort)
- **Matched Distribution:** Emergency Services Yes (2,758 facilities; 90.87%), Emergency Services No (277 facilities; 9.13%), plus 20 Unmatched facilities.
- **Feasibility:** Both segments contain sufficient numbers of facilities for broad exploratory comparisons.

> [!WARNING]
> **Temporal Limitation:** HGI attributes represent a July 2026 CASPER snapshot, whereas HRRP reflects a 2021–2024 performance period. Ownership transitions or service changes may have occurred. These attributes must be treated as exploratory context only, not historical explanatory variables or causal drivers.

---

## 8. Business Usefulness, Analytical Boundaries, and Responsible Use Guidelines

### What the Data CAN Defensibly Support
1. **Condition-Specific Hospital Benchmarking:** Evaluating whether an individual hospital's published ERR falls above 1.0, below 1.0, or within specific interquartile bounds relative to peer facilities treating the same condition.
2. **Relative Cohort Identification:** Segmenting hospitals that achieved lower-than-expected readmission rates (ERR < 1.0) versus higher-than-expected readmission rates (ERR > 1.0).
3. **Broad Jurisdictional Exploration:** Identifying descriptive regional variations across well-populated states for common medical conditions (PN, HF, COPD).
4. **Exploratory Facility Context:** Examining how ERR distributions vary across broad ownership types or emergency service availability, with appropriate temporal caveats.
5. **Prioritizing Deep-Dive Investigations:** Flagging conditions or regions exhibiting wide dispersion (e.g., Hip/Knee) for targeted operational review.

### What the Data CANNOT Support (Explicit Analytical Limits)
1. **Patient-Level Outcomes or Clinical Causes:** HRRP provides facility-level risk-standardized summary ratios, not patient-level EHR records, clinical trajectories, or underlying reasons for readmission.
2. **Causal Claims:** Observed differences across states, ownership classes, or individual hospitals cannot be attributed causally to management quality, clinical protocols, or operational differences.
3. **Composite Hospital Performance Scores:** Combining the six condition measures into an overall hospital index is methodologically invalid because patient populations, sample sizes, and clinical risk models differ fundamentally.
4. **Current Hospital Performance:** The FY 2026 HRRP dataset reflects hospital discharges from July 1, 2021 through June 30, 2024. It does not reflect real-time or current performance.
5. **Official CMS Penalty Re-creation:** This dataset provides risk-standardized ratios only. Determining exact statutory reimbursement reductions requires CMS-specific payment adjustment formulas, baseline performance periods, and Net Medicare Inpatient Revenue weighting not present in this file.
6. **Patient-Volume Weighted Comparisons:** Without complete discharge and readmission counts across all hospitals (since low-volume counts are masked under Footnote 1), volume-weighted national benchmarks cannot be reliably computed.
