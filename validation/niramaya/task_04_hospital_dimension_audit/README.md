# Niramaya — Validation Task 04: Hospital Dimension Audit and Join Feasibility

## Overview

This directory contains the complete implementation, documentation, and factual evidence deliverables for **Validation Task 04: Hospital Dimension Audit and Join Feasibility** of Project **Niramaya** (incorporating targeted corrections for neutral diagnostic interpretations, geographic profiling, and hardened integrity validation).

The primary objective of this task is to determine whether the CMS **Hospital General Information (HGI)** dataset can reliably function as a hospital-level dimension table for the **FY 2026 CMS Hospital Readmissions Reduction Program (HRRP)** fact dataset.

The audit was conducted strictly using standard-library Python against the two complete, unmodified local raw CSV files located in `../data/raw/`:
1. `FY_2026_Hospital_Readmissions_Reduction_Program_Hospital.csv` (HRRP fact dataset; 18,330 rows, 12 columns, 3,055 distinct hospitals)
2. `Hospital_General_Information.csv` (HGI dimension dataset; 5,419 rows, 38 columns, 5,419 distinct hospitals)

Neither raw dataset has been modified, resaved, or committed to version control.

---

## Executive Summary of Findings

| Evaluation Area | Key Factual Finding | Assessment & Recommendation |
| :--- | :--- | :--- |
| **Raw Integrity & Decoding** | Strict UTF-8 decoding validated across 100% of rows (0 decode errors; 0 malformed rows) | **Strictly Validated (0 decode errors)** |
| **HGI Primary Key Uniqueness** | Exactly 5,419 distinct `Facility ID` values across 5,419 rows | **100.0% Unique Primary Key (0 duplicate IDs)** |
| **HRRP Fact Grain & Uniformity** | Exactly 6 condition records per hospital across all 3,055 facilities | **100.0% Uniform Cartesian Grain** (6 × 3,055 = 18,330) |
| **HRRP-to-HGI Join Coverage** | 3,035 of 3,055 distinct HRRP facilities match HGI | **99.35% Facility Match Rate** (0.65% unmatched) |
| **HGI-to-HRRP Representation** | 3,035 of 5,419 HGI facilities appear in HRRP | **56.01% Representation** (43.99% non-HRRP facilities) |
| **Unmatched HGI Breakdown** | 2,384 non-matched facilities (1,382 CAH, 624 Psych, 132 VA, 94 Childrens, 72 Acute Care, 43 REH, 32 DoD, 5 Long-term) | Non-representation does not by itself establish statutory exemption |
| **Fact Row Multiplication** | Exactly 0 fact rows multiplied (1.0x multiplication factor) | **Zero Row Multiplication** (Exact 1:N cardinality) |
| **Inner Join vs Left Join Impact** | Inner join causes the loss of 120 fact rows (39 published ERR); Left outer join retains 100% of rows | **LEFT OUTER JOIN Strongly Recommended** |
| **State Level Concordance** | 3,035 of 3,035 matched facilities have identical State codes | **100.0% State Concordance (0 mismatches)** |
| **Facility Name Consistency** | 2,983 exact matches (98.29%); 52 text differences (2 formatting-only, 50 normalized text) | Textual comparison results; causes unverified |
| **Hospital Type Variance** | Exactly 100.0% of matched HRRP hospitals are `Acute Care Hospitals` | **Zero Variance in matched cohort** (Cohort filter only) |
| **Hospital Ownership** | 10 distinct classes (48.6% non-profit, 20.4% proprietary, 7.9% other non-profit) | Optional exploratory segmentation (temporal caveat) |
| **Geographic Profiling** | State (51 groups, stable); County (998 groups, 443 single-hospital); ZIP (2,768 groups, 2,544 single-hospital) | State preferred; County/ZIP require group-size checks |
| **Temporal Compatibility** | HGI is a July 2026 CASPER snapshot; HRRP is a 2021–2024 performance window | Sourced from current state; temporal caveats required |

---

## Audit Script Execution

The standalone audit script is self-contained and relies exclusively on the Python standard library.

### Execution Command

```bash
# From repository root (validation-repo/):
python validation/niramaya/task_04_hospital_dimension_audit/audit_hospital_dimension_join.py \
    --hrrp-file ../data/raw/FY_2026_Hospital_Readmissions_Reduction_Program_Hospital.csv \
    --hgi-file ../data/raw/Hospital_General_Information.csv \
    --output-dir validation/niramaya/task_04_hospital_dimension_audit/output
```

---

## Directory Deliverables

The audit generates eight core artifacts in `output/`:

1. `hospital_dimension_join_audit.json`: Complete, machine-readable audit results with all counts, coverage metrics, inventory, distributions, and diagnostic findings.
2. `hospital_dimension_join_audit.md`: Comprehensive, human-readable evaluation report covering all dimensions and guidelines.
3. `hgi_field_inventory.csv`: Exhaustive profiling of all 38 HGI columns (data types, missingness, distinct counts, sample values, analytical roles, and temporal caveats).
4. `hrrp_hgi_join_coverage.csv`: Quantitative summary table comparing coverage at both facility and fact-row levels, documenting row multiplication and join loss.
5. `hospital_dimension_attribute_profile.csv`: Category-level frequency distributions and missingness across all 5,419 HGI records versus the 3,035 matched HRRP records (profiling 16 candidate attributes including geographic fields).
6. `hospital_id_join_exceptions.csv`: Complete listing of all 20 unmatched HRRP facilities, including their measure counts, published numeric ERR counts, candidate current HGI hospital type, and neutral diagnostic notes.
7. `hospital_name_state_mismatches.csv`: Detailed audit of the 52 matched facilities exhibiting facility name differences, categorized strictly by textual normalization.
8. `execution_environment.txt`: System configuration and reproducibility record (Python version, OS, command line, input paths).

---

## Key Methodological & Empirical Findings

### 1. Dimension Key Uniqueness & Fact Grain
- **Hospital General Information (HGI):** Contains 5,419 rows and 5,419 distinct `Facility ID` values. There are **0 duplicate IDs**, **0 blank IDs**, and **0 malformed records**. Every `Facility ID` matches the 6-character alphanumeric pattern `^[0-9A-Za-z]{6}$` (5,255 are 6-digit integers, and 164 are alphanumeric federal/military CCNs).
- **HRRP Fact Table:** Contains 18,330 rows across 3,055 distinct hospitals. Every hospital has **exactly 6 condition records** (100.0% uniform Cartesian grain).
- **Relational Cardinality:** Joining HGI to HRRP creates an exact **One-to-Many (1:N)** relationship. Because HGI keys are 100% unique, the join produces **zero row multiplication**.

### 2. Join Coverage & Loss Analysis
- **Facility Level:** 3,035 of the 3,055 HRRP hospitals match HGI (**99.35% match rate**). Exactly 20 hospitals (0.65%) are unmatched.
- **HGI Representation Breakdown:** 3,035 of 5,419 HGI facilities appear in HRRP (56.01%). The 2,384 non-matched HGI facilities include Critical Access Hospitals (1,382), Psychiatric (624), VA (132), Children's (94), Rural Emergency Hospitals (43), DoD (32), Long-term (5), and **72 current Acute Care Hospitals**. Non-representation in this HRRP dataset does not by itself establish statutory exemption.
- **Fact Row Level:**
  - In an **INNER JOIN**, exactly 120 HRRP fact records are dropped. Crucially, these 120 dropped records contain **39 published numeric Excess Readmission Ratios** across 15 active hospitals.
  - In a **LEFT OUTER JOIN**, **100% of the 18,330 HRRP fact records** and all 11,720 published numeric ERR outcomes are retained.
  - **Operational Rule:** Benchmarking pipelines must use a **LEFT OUTER JOIN** to prevent silent data loss.

### 3. Factual Diagnostic Analysis of the 20 Unmatched Facilities
Same-state string-similarity diagnostic matching yielded the following inspectable findings:
- **Identical-Name Candidates under Different Facility IDs (4 facilities):**
  - `010008` (Crenshaw Community Hospital, AL) matches HGI `011308` (similarity: 1.00; candidate current HGI type: Critical Access Hospitals).
  - `330060` (Carthage Area Hospital, Inc, NY) matches HGI `331318` (similarity: 1.00; candidate current HGI type: Critical Access Hospitals).
  - `450143` (Ascension Seton Smithville, TX) matches HGI `671304` (similarity: 1.00; candidate current HGI type: Critical Access Hospitals).
  - `450411` (Eastland Memorial Hospital, TX) matches HGI `671303` (similarity: 1.00; candidate current HGI type: Critical Access Hospitals).
  - *Diagnostic Interpretation:* Identical-name facility candidate found in HGI under a different Facility ID. This suggests possible provider identity continuity, but CCN succession or conversion history is not established by the two datasets alone. The candidate must not be used as an accepted join.
- **Similar-Name Candidates (Similarity 0.70 to 0.94; 10 facilities):**
  - E.g., `010059` (0.81), `010120` (0.85), `050125` (0.71), `100092` (0.81), `260176` (0.80), `390326` (0.91), `390337` (0.89), `450271` (0.82), `450827` (0.82), `520215` (0.86).
  - *Diagnostic Interpretation:* Similar-name candidate identified in the current HGI snapshot. This is a string-similarity diagnostic only; hospital identity and operational relationship are unverified.
- **No High-Similarity Candidates (Similarity < 0.70; 6 facilities):**
  - E.g., `010018` (0.68), `040067` (0.66), `050589` (0.68), `070012` (0.63), `100047` (0.55), `240052` (0.58).
  - *Diagnostic Interpretation:* No high-similarity candidate identified in the current HGI snapshot. Operational status and reason for missing join are unknown from the datasets audited.
- **Facility ID Integrity:** Per strict validation guardrails, these diagnostic candidates were **not** used to force an artificial join. All 20 facilities remain strictly documented in `output/hospital_id_join_exceptions.csv`.

### 4. Textual Classification of Matched-Hospital Name Differences
- **State Code:** 3,035 of 3,035 matched facilities match State exactly (**100.00% concordance**, 0 mismatches).
- **Facility Name Comparison:**
  - Exact matches: 2,983 facilities (**98.29%**).
  - Formatting-only differences: 2 facilities (`FORMATTING_ONLY_DIFFERENCE`; differ only by case, whitespace, or punctuation).
  - Normalized text differences: 50 facilities (`NORMALIZED_TEXT_DIFFERENCE`; names differ after normalization).
  - *Interpretation:* These are textual string comparison results. The cause of each difference is not established by this audit. Both source names are preserved in `output/hospital_name_state_mismatches.csv`.

### 5. Candidate Dimension Attribute Profiles
- **`Hospital Type` (100.0% Acute Care Hospitals):** Zero variance in the matched cohort. Retained as a current cohort filter only; not an independent segmentation variable.
- **`Hospital Ownership` (10 classes):** 48.6% Non-profit Private, 20.4% Proprietary, 7.9% Non-profit Other, 7.2% Hospital District/Authority, 6.6% Non-profit Church, 4.4% Local Government, 2.3% Physician, 1.5% State Government, 0.8% Federal Government, 0.3% Tribal. Zero missing values. Usable for optional exploratory segmentation with an explicit temporal caveat, noting that small categories require cautious interpretation.
- **`Emergency Services` (2 classes):** 90.9% Yes, 9.1% No. Zero missing values. Usable for optional exploratory segmentation with a temporal caveat.
- **`Hospital overall rating` (1 to 5 Stars):** 1-Star (5.6%), 2-Star (18.7%), 3-Star (27.9%), 4-Star (25.7%), 5-Star (9.6%), Not Available (12.6%). Current composite quality indicator; keep as reference information only (not causal).
- **`READM Group Summary Fields` (97.2% populated):** Covers up to 11 public-reporting measures. Useful as external facility profile context; must not be substituted for fact-level condition ERR.
- **Geographic Fields (`State`, `County/Parish`, `City/Town`, `ZIP Code`):**
  - `State` is preferred for broad regional comparisons (100% concordant, already present in HRRP).
  - `County/Parish` (998 groups in matched HRRP; 443 single-hospital counties) and `ZIP Code` (2,768 groups; 2,544 single-hospital ZIPs) are optional descriptive context subject to current-snapshot limitations and minimum group-size checks.
  - ZIP Code does not supply socioeconomic information without validated linkage to an external dataset.

---

## Dimension Attribute Classification & Recommendations

Based strictly on empirical findings, candidate dimension attributes are classified into four operational tiers:

```
+----------------------------------------------------------------------------------------------------+
| Tier 1: Recommended for Broad Regional Comparisons                                                |
| - State (100% concordance with HRRP, stable jurisdictional boundary, low cardinality)             |
| - Facility ID (Primary join key, 100% unique in HGI, 0 row multiplication)                         |
+----------------------------------------------------------------------------------------------------+
| Tier 2: Optional Exploratory Segmentation (Temporal Caveat Required)                               |
| - Hospital Ownership (Rich variance, 0% missing; reflects July 2026 snapshot, not 2021-24)         |
| - Emergency Services (90.9% Yes / 9.1% No; reflects current capability snapshot)                   |
| - County/Parish (Optional descriptive context; requires minimum group-size thresholding)           |
| - ZIP Code (Optional descriptive context; high cardinality; requires group-size checks)            |
+----------------------------------------------------------------------------------------------------+
| Tier 3: Keep as Reference Information Only                                                         |
| - Facility Name & Address (Descriptive identifiers; subject to rebranding and textual differences) |
| - City/Town (Descriptive municipal label; high cardinality and irregular scale)                    |
| - Hospital overall rating & Footnote (Composite star rating; 12.6% N/A; not causally comparable)   |
| - Count of Facility READM Measures & Counts Better/No Different/Worse (Facility-wide summary)      |
| - READM Group Measure Count & Group Footnote (Metadata on Hospital Compare 11-measure group)       |
+----------------------------------------------------------------------------------------------------+
| Tier 4: Exclude from Core Project Analysis                                                         |
| - Hospital Type (Invariant in matched cohort: 100.0% Acute Care Hospitals; cohort filter only)    |
| - Meets criteria for birthing friendly designation (37.3% blank in matched HRRP; perinatal only)  |
| - Telephone Number (Administrative contact only)                                                   |
| - MORT, Safety, Pt Exp, and TE Group Measure Counts & Performance Counts (Distinct domains)       |
+----------------------------------------------------------------------------------------------------+
```

---

## Technical and Methodological Guardrails

1. **Join Integrity:** Primary join must be performed on `Facility ID` (retaining leading zeroes and six-character formatting). Hospital name must **never** be used as the join key.
2. **Cardinality & Join Mode:** Joining HGI to HRRP preserves fact records without duplication (1.0x factor). A **LEFT OUTER JOIN** must be used so that the 20 unmatched hospitals (representing 120 fact rows and 39 published ERR outcomes) are not silently dropped.
3. **Temporal Integrity:** Analysts must not assume that current ownership, emergency services, or hospital names represent the facility's status during 2021–2024. All downstream models must explicitly document the snapshot date (July 2026).
4. **No Causal Assumptions:** Dimension attributes reflect institutional, geographic, and composite characteristics, not causal explanations for condition-specific risk-standardized Excess Readmission Ratios.
