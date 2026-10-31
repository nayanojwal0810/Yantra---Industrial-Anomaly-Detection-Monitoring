# Niramaya — Validation Task 05: Analytical Viability and Business Usefulness

## Overview

This directory contains the complete implementation, documentation, and factual evidence deliverables for **Validation Task 05: Analytical Viability and Business Usefulness** of Project **Niramaya**.

The primary objective of this task is to determine whether the published Excess Readmission Ratio (ERR) data from the CMS **FY 2026 Hospital Readmissions Reduction Program (HRRP)**, joined with the **Hospital General Information (HGI)** dimension snapshot, supports defensible descriptive and diagnostic analytics across:
1. Six condition measures.
2. Hospital-level ERR distributions within each condition.
3. State-level differences within each condition.
4. Optional exploratory hospital ownership and emergency-service segments (July 2026 snapshot context only).
5. Sensitivity to records carrying Footnote 29.

The audit was conducted strictly using standard-library Python against the two complete, unmodified local raw CSV files located in `../data/raw/`:
1. `FY_2026_Hospital_Readmissions_Reduction_Program_Hospital.csv` (HRRP fact dataset; 18,330 rows, 12 columns, 3,055 distinct hospitals)
2. `Hospital_General_Information.csv` (HGI dimension dataset; 5,419 rows, 38 columns, 5,419 distinct hospitals)

Neither raw dataset has been modified, resaved, or committed to version control.

---

## Executive Summary of Findings

| Evaluation Domain | Key Factual Finding | Assessment & Analytical Viability |
| :--- | :--- | :--- |
| **Dataset Reconfirmation** | 18,330 HRRP rows (3,055 facilities × 6 measures); 5,419 unique HGI IDs; 1.0x join factor | **100.0% Uniform Fact Grain (0 row multiplication)** |
| **Numeric ERR Availability** | Exactly 11,720 numeric ERR records (63.94%); 6,610 nonnumeric records (36.06%) | **100.0% Concordant with Predicted & Expected Rates** |
| **Condition Sample Breadth** | High: PN (2,715) & HF (2,621); Moderate: COPD (2,323), AMI (1,736), Hip/Knee (1,447); Restricted: CABG (878) | **Condition-Specific Benchmarking Feasible** (CABG restricted to surgical centers) |
| **Distribution & Spread** | Unweighted facility means: 1.0011 to 1.0040; medians: 0.9916 to 1.0000; IQRs: 0.0574 to 0.1890 | **Sufficient Observed Spread for Relative Benchmarking** |
| **Footnote 29 Sensitivity** | 377 records carry Footnote 29 (all 377 numeric); excluding them shifts means by ≤ 0.0005, medians by ≤ 0.0003, and % > 1 by ≤ 0.16% | **Negligible Impact on Descriptive Distributions** (Safe to retain) |
| **State-Level Feasibility** | 51 jurisdictions (50 states + DC); 0 empty cells; 20 of 306 cells (6.54%) have < 5 numeric records (primarily CABG) | **Feasible for Major States/Conditions; Small States Require Caution** |
| **HGI Segment Feasibility** | 10 ownership classes (48.6% non-profit private) and 2 emergency-services classes (90.9% Yes) | **Exploratory Only; July 2026 Snapshot; Not Causal** |
| **Operational Boundaries** | Data supports relative benchmarking and cohort identification; cannot support causal claims or patient-level outcomes | **Strict Methodological Guardrails Documented** |

---

## Audit Script Execution

The standalone audit script is self-contained and relies exclusively on the Python standard library.

### Execution Command

```bash
# From repository root (validation-repo/):
python validation/niramaya/task_05_analytical_viability/audit_analytical_viability.py \
    --hrrp-file ../data/raw/FY_2026_Hospital_Readmissions_Reduction_Program_Hospital.csv \
    --hgi-file ../data/raw/Hospital_General_Information.csv \
    --output-dir validation/niramaya/task_05_analytical_viability/output
```

---

## Directory Deliverables

The audit generates seven core artifacts in `output/`:

1. `analytical_viability.json`: Complete, machine-readable audit results with all metadata, checks, distributions, and findings.
2. `analytical_viability.md`: Comprehensive, human-readable technical report covering all dimensions and guidelines.
3. `condition_viability_summary.csv`: Full condition-level profile across all six measures, documenting total records, availability counts, footnote breakdowns, minimum, maximum, mean, median, standard deviation, percentiles (P05, P25, P75, P95), IQR, and exact threshold counts (`< 1.0`, `= 1.0`, `> 1.0`).
4. `footnote_29_sensitivity.csv`: Side-by-side sensitivity comparison between All Published Numeric ERR records versus Records Excluding Footnote 29, reporting sample sizes, means, medians, P25, P75, percentages above 1.0, and differences across each condition and the overall pool.
5. `state_condition_summary.csv`: Factual profiling across all 51 jurisdictions and 6 measures (306 state-condition cells), reporting hospital counts, numeric ERR availability, median, mean, counts and percentages above 1.0, and subcohort reliability flags.
6. `hospital_group_condition_summary.csv`: Exploratory profiling across 10 Hospital Ownership classes and 2 Emergency Services classes (plus the unmatched cohort) across all 6 measures (84 cells), documenting facility counts, numeric ERR availability, medians, means, counts and percentages above 1.0, subcohort flags, and temporal caveats.
7. `execution_environment.txt`: System configuration and reproducibility record (Python version, OS, command line, input paths, file hashes).

---

## Key Methodological & Empirical Findings

### 1. Analytical Dataset Reconfirmation
- **Cartesian Uniformity:** HRRP contains 18,330 rows across 3,055 distinct hospitals. Every facility has exactly 6 condition records (`3,055 × 6 = 18,330`; 100.0% uniform Cartesian grain).
- **Primary Key Uniqueness:** HGI contains 5,419 rows and 5,419 distinct `Facility ID` values (100.0% unique primary key).
- **Left Join Integrity:** Exactly 3,035 HRRP facilities match HGI, and 20 facilities are unmatched. Joining HGI dimension fields preserves the exact 18,330 fact rows (multiplication factor: 1.0x).
- **Numeric ERR Availability:** Exactly 11,720 numeric ERR values (63.94%) and 6,610 nonnumeric values (36.06%).
- **Rate Concordance:** Exactly 100% of numeric ERR records have numeric Predicted and Expected Readmission Rates; exactly 100% of nonnumeric ERR records have nonnumeric Predicted and Expected rates (0 rate discrepancies).

### 2. Condition-Level Analytical Viability
Unweighted facility-level descriptive statistics were computed for each condition across all 3,055 hospitals:

| Measure Code | Measure Description | Total Hospitals | Numeric ERR (Count / %) | Nonnumeric (Count / %) | ERR Min | ERR Max | Mean | Median | StdDev | IQR (P25–P75) | % < 1.0 | % = 1.0 | % > 1.0 |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `READM-30-AMI-HRRP` | Acute Myocardial Infarction (AMI) | 3,055 | 1,736 (56.82%) | 1,319 (43.18%) | 0.6839 | 1.2639 | 1.001755 | 0.9994 | 0.066824 | 0.0814 (0.9608–1.0422) | 50.35% | 0.00% | 49.65% |
| `READM-30-CABG-HRRP` | Coronary Artery Bypass Graft (CABG) | 3,055 | 878 (28.74%) | 2,177 (71.26%) | 0.7434 | 1.4237 | 1.001789 | 1.0000 | 0.096565 | 0.1247 (0.9377–1.0624) | 50.00% | 0.11% | 49.89% |
| `READM-30-COPD-HRRP` | Chronic Obstructive Pulmonary Disease (COPD) | 3,055 | 2,323 (76.04%) | 732 (23.96%) | 0.8681 | 1.2545 | 1.001133 | 0.9969 | 0.045972 | 0.0574 (0.9707–1.0281) | 52.65% | 0.13% | 47.22% |
| `READM-30-HF-HRRP` | Heart Failure (HF) | 3,055 | 2,621 (85.79%) | 434 (14.21%) | 0.7137 | 1.3606 | 1.001439 | 0.9983 | 0.065035 | 0.0808 (0.9606–1.0414) | 51.05% | 0.04% | 48.91% |
| `READM-30-HIP-KNEE-HRRP` | Elective Primary Total Hip/Knee Replacement | 3,055 | 1,447 (47.36%) | 1,608 (52.64%) | 0.4698 | 1.6297 | 1.003985 | 0.9916 | 0.155675 | 0.1890 (0.9000–1.0890) | 52.11% | 0.00% | 47.89% |
| `READM-30-PN-HRRP` | Pneumonia (PN) | 3,055 | 2,715 (88.87%) | 340 (11.13%) | 0.7967 | 1.4255 | 1.001486 | 0.9955 | 0.066296 | 0.0793 (0.9595–1.0388) | 53.11% | 0.07% | 46.81% |

### 3. Footnote Breakdown & Reasons for Missingness
Every single nonnumeric ERR value is fully accounted for by CMS suppression footnotes:
- **Footnote 1 (`Number of cases/patients too few to report`):** Accounts for 3,150 suppressed records (predominantly Hip/Knee: 1,114; AMI: 933; COPD: 526).
- **Footnote 5 (`Results not available for the reporting period`):** Accounts for 3,255 suppressed records (predominantly CABG: 1,975; Hip/Knee: 397; AMI: 319).
- **Footnote 7 (`No cases met criteria`):** Accounts for 205 suppressed records (predominantly Hip/Knee: 97; AMI: 67).
- **Footnote 29 (`Approved exception`):** Accounts for 377 records across the dataset; all 377 records contain published numeric ERR values.
- **Blank Footnotes:** Exactly 11,343 records have blank footnotes; all 11,343 have published numeric ERR values.

### 4. Observed Variation and Distribution Assessment
- **Center & Symmetry:** Across all six measures, unweighted facility means (1.0011 to 1.0040) and medians (0.9916 to 1.0000) are tightly centered near 1.0000. Mean-to-median differences are minimal (0.0018 for CABG to 0.0124 for Hip/Knee), showing good distributional balance.
- **Dispersion:** COPD has the narrowest spread (IQR: 0.0574; StdDev: 0.045972), whereas Elective Hip/Knee Replacement exhibits the widest spread (IQR: 0.1890; StdDev: 0.155675).
- **Extreme Values:** Extreme ERR values (min 0.4698 to max 1.6297) represent genuine CMS risk-adjusted calculations and do not distort central percentiles (P05 and P95 bound 90% of facilities). They must not be winsorized or discarded.
- **Sample Breadth:** Pneumonia (2,715) and Heart Failure (2,621) support broad nationwide benchmarking. CABG (878) is restricted to specialized surgical hospitals.

### 5. Footnote 29 Sensitivity Assessment
- Across all 6 measures and the combined pool of 11,720 numeric records, excluding Footnote 29 records produces negligible shifts:
  - **Mean change:** shifts by at most **0.000522** (CABG) and by only **0.000203** overall.
  - **Median change:** shifts by at most **0.0003** (Heart Failure) and by **0.0001** overall.
  - **Proportion with ERR > 1.0:** shifts by at most **0.16%** (COPD and HF), with zero shift in CABG and Hip/Knee.
- **Conclusion:** Footnote 29 records do not distort unweighted descriptive distributions and can be safely included in condition-specific benchmarking.

### 6. State-Level Comparison Feasibility
- Evaluated across all 51 jurisdictions (50 states + DC) and 6 measures (306 combinations).
- **Zero empty cells:** Every state has at least one hospital with a numeric ERR for each condition.
- **Sparse cells (< 5 hospitals):** 20 of 306 cells (6.54%) have fewer than 5 hospitals, concentrated in CABG (10 states) and Hip/Knee (8 states) in small states (AK, DC, DE, HI, ME, ND, VT, WY).
- **Methodological Guardrail:** State-level comparisons are feasible for common medical conditions across medium-to-large states. Small states require cell size disclosure and must not be ranked.

### 7. Optional HGI Segment Feasibility
- **Hospital Ownership:** 10 categories. Large categories (Private Non-profit: 1,474; Proprietary: 619; District: 220; Church: 199; Local Gov: 135) support descriptive comparisons. Small categories (Tribal: 9; Federal: 23; State: 45) produce sparse cells.
- **Emergency Services:** Yes (2,758) vs. No (277) both support broad comparisons.
- **Temporal Warning:** July 2026 HGI attributes must not be treated as historical explanatory factors for 2021–2024 performance.

---

## Business Usefulness & Analytical Boundaries

### What the Data CAN Defensibly Support
1. **Condition-Specific Hospital Benchmarking:** Relative evaluation of whether a hospital's published ERR is above 1.0, below 1.0, or in specific interquartile tiers relative to peers.
2. **Relative Cohort Identification:** Segmenting hospitals that achieved lower-than-expected readmissions (ERR < 1.0) versus higher-than-expected readmissions (ERR > 1.0).
3. **Broad Regional Exploration:** Descriptive regional variation across well-populated states for common medical conditions (PN, HF, COPD).
4. **Exploratory Facility Context:** Examining how ERR distributions vary across broad ownership types or emergency service availability, with temporal caveats.
5. **Prioritizing Areas for Investigation:** Flagging conditions or regions with high dispersion (e.g. Hip/Knee) for deeper clinical review.

### What the Data CANNOT Support (Explicit Boundaries)
1. **Patient-Level Outcomes or Clinical Causes:** No patient-level EHR data or reasons for readmission.
2. **Causal Explanations:** Differences across hospitals, states, or ownership types cannot be causally attributed to clinical quality or management.
3. **Composite Hospital Scores:** Combining six distinct condition measures into an overall hospital score is methodologically invalid.
4. **Current Performance:** Data reflects discharges from July 1, 2021 through June 30, 2024.
5. **Official CMS Penalty Re-creation:** Determining statutory reimbursement reductions requires payment adjustment formulas and Medicare revenue weights not in this file.
6. **Volume-Weighted Comparisons:** Incomplete discharge and readmission counts (masked under Footnote 1) prevent volume-weighted national benchmarks.
