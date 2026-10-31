# Niramaya — Validation Task 04: Hospital Dimension Audit and Join Feasibility

## Overview

This directory contains the complete implementation, documentation, and factual evidence deliverables for **Validation Task 04: Hospital Dimension Audit and Join Feasibility** of Project **Niramaya**.

The primary objective of this task is to determine whether the CMS **Hospital General Information (HGI)** dataset can reliably function as a hospital-level dimension table for the **FY 2026 CMS Hospital Readmissions Reduction Program (HRRP)** fact dataset.

The audit was conducted strictly using standard-library Python against the two complete, unmodified local raw CSV files located in `../data/raw/`:
1. `FY_2026_Hospital_Readmissions_Reduction_Program_Hospital.csv` (HRRP fact dataset; 18,330 rows, 12 columns, 3,055 distinct hospitals)
2. `Hospital_General_Information.csv` (HGI dimension dataset; 5,419 rows, 38 columns, 5,419 distinct hospitals)

Neither raw dataset has been modified, resaved, or committed to version control.

---

## Executive Summary of Findings

| Evaluation Area | Key Factual Finding | Assessment & Recommendation |
| :--- | :--- | :--- |
| **HGI Primary Key Uniqueness** | Exactly 5,419 distinct `Facility ID` values across 5,419 rows | **100.0% Unique Primary Key (0 duplicate IDs)** |
| **HRRP Fact Grain & Uniformity** | Exactly 6 condition records per hospital across all 3,055 facilities | **100.0% Uniform Cartesian Grain** (6 × 3,055 = 18,330) |
| **HRRP-to-HGI Join Coverage** | 3,035 of 3,055 distinct HRRP facilities match HGI | **99.35% Facility Match Rate** (0.65% unmatched) |
| **HGI-to-HRRP Representation** | 3,035 of 5,419 HGI facilities appear in HRRP | **56.01% Representation** (43.99% non-HRRP facilities) |
| **Fact Row Multiplication** | Exactly 0 fact rows multiplied (1.0x multiplication factor) | **Zero Row Multiplication** (Exact 1:N cardinality) |
| **Inner Join vs Left Join Impact** | Inner join causes the loss of 120 fact rows (39 published ERR); Left outer join retains 100% of rows | **LEFT OUTER JOIN Strongly Recommended** |
| **State Level Concordance** | 3,035 of 3,035 matched facilities have identical State codes | **100.0% State Concordance (0 mismatches)** |
| **Facility Name Consistency** | 2,983 exact matches (98.29%); 52 name mismatches (1.71%) | Rebranding, acquisitions, or corporate renaming |
| **Hospital Type Variance** | Exactly 100.0% of matched HRRP hospitals are `Acute Care Hospitals` | **Zero Variance in matched cohort** (Cohort filter only) |
| **Hospital Ownership** | 10 distinct classes (48.6% non-profit, 20.4% proprietary, 7.9% other non-profit) | Usable with clear temporal caveat |
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
5. `hospital_dimension_attribute_profile.csv`: Category-level frequency distributions and missingness across all 5,419 HGI records versus the 3,035 matched HRRP records.
6. `hospital_id_join_exceptions.csv`: Complete listing of all 20 unmatched HRRP facilities, including their measure counts, published numeric ERR counts, and diagnostic match explanations.
7. `hospital_name_state_mismatches.csv`: Detailed audit of the 52 matched facilities exhibiting facility name discrepancies between HRRP historical records and HGI current records.
8. `execution_environment.txt`: System configuration and reproducibility record (Python version, OS, command line, input paths).

---

## Key Methodological & Empirical Findings

### 1. Dimension Key Uniqueness & Fact Grain
- **Hospital General Information (HGI):** Contains 5,419 rows and 5,419 distinct `Facility ID` values. There are **0 duplicate IDs**, **0 blank IDs**, and **0 malformed records**. Every `Facility ID` matches the 6-character alphanumeric pattern `^[0-9A-Za-z]{6}$` (5,255 are 6-digit integers, and 164 are alphanumeric federal/military CCNs).
- **HRRP Fact Table:** Contains 18,330 rows across 3,055 distinct hospitals. Every hospital has **exactly 6 condition records** (100.0% uniform Cartesian grain).
- **Relational Cardinality:** Joining HGI to HRRP creates an exact **One-to-Many (1:N)** relationship. Because HGI keys are 100% unique, the join produces **zero row multiplication**.

### 2. Join Coverage & Loss Analysis
- **Facility Level:** 3,035 of the 3,055 HRRP hospitals match HGI (**99.35% match rate**). Exactly 20 hospitals (0.65%) are unmatched.
- **Fact Row Level:**
  - In an **INNER JOIN**, exactly 120 HRRP fact records are dropped. Crucially, these 120 dropped records contain **39 published numeric Excess Readmission Ratios** across 15 active hospitals.
  - In a **LEFT OUTER JOIN**, **100% of the 18,330 HRRP fact records** and all 11,720 published numeric ERR values are retained.
  - **Operational Rule:** Benchmarking pipelines must use a **LEFT OUTER JOIN** to prevent silent data loss.

### 3. Diagnostic Analysis of the 20 Unmatched Facilities
Diagnostic within-state name matching revealed the operational reasons behind the 20 unmatched HRRP facilities:
- **Critical Access Hospital (CAH) Conversions (4 facilities):**
  - `010008` (Crenshaw Community Hospital, AL) matches HGI `011308` (1.00 name similarity).
  - `330060` (Carthage Area Hospital, NY) matches HGI `331318` (1.00 name similarity).
  - `450143` (Ascension Seton Smithville, TX) matches HGI `671304` (1.00 name similarity).
  - `450411` (Eastland Memorial Hospital, TX) matches HGI `671303` (1.00 name similarity).
  - *Context:* When an acute care hospital converts to Critical Access Hospital status, CMS re-certifies the facility under the `1300–1399` CCN series (or `6713xx`). Because CAHs are statutorily exempt from HRRP, their historical acute care performance appears under their retired acute care CCN in HRRP, but in the current July 2026 HGI snapshot they are listed under their new CAH CCN.
- **Health System Mergers, Acquisitions, & Consolidations (11 facilities):**
  - E.g., `050125` (Regional Medical Center of San Jose), `100092` (Orlando Health Rockledge Hospital), `390326` (St. Luke's Anderson Campus), `450271` (Medical City Decatur). These reflect facility closures, license transfers, or health system integrations between 2021 and 2026.
- **Facility ID Integrity:** Per strict validation guidelines, these diagnostic matches were **not** used to force an artificial join. The 20 records remain strictly documented in `output/hospital_id_join_exceptions.csv`.

### 4. Name & State Consistency
- **State Code:** 3,035 of 3,035 matched facilities match State exactly (**100.00% concordance**, 0 mismatches).
- **Facility Name:** 2,983 facilities match exactly (**98.29%**). Exactly 52 facilities exhibit discrepancies (2 minor case/punctuation variations; 50 material corporate renaming/rebranding instances such as Intermountain Health, Banner Health, HCA Florida, Baptist Health). Neither name was overwritten; both are preserved in `output/hospital_name_state_mismatches.csv`.

### 5. Candidate Dimension Attribute Profiles
- **`Hospital Type` (100.0% Acute Care Hospitals):** Every single matched HRRP hospital is classified as an `Acute Care Hospital`. There is **zero variance** in the matched cohort. `Hospital Type` cannot serve as an independent segmentation variable; its utility is strictly as a cohort validation check.
- **`Hospital Ownership` (10 classes):** 48.6% Non-profit Private, 20.4% Proprietary, 7.9% Non-profit Other, 7.2% Hospital District/Authority, 6.6% Non-profit Church, 4.4% Local Government, 2.3% Physician, 1.5% State Government, 0.8% Federal Government, 0.3% Tribal. Zero missing values. Usable for segmentation with an explicit temporal caveat.
- **`Emergency Services` (2 classes):** 90.9% Yes, 9.1% No. Zero missing values. Usable for segmentation with a temporal caveat.
- **`Hospital overall rating` (1 to 5 Stars):** 1-Star (5.6%), 2-Star (18.7%), 3-Star (27.9%), 4-Star (25.7%), 5-Star (9.6%), Not Available (12.6%). Sourced from a multi-domain composite (mortality, safety, readmission, patient experience, timely care). Must not be treated as a causal driver of HRRP readmissions; keep as reference context only.
- **`READM Group Measure Count` & Counts Better/No Different/Worse:** Reflects facility-wide performance across up to 11 public-reporting measures (including Hospital-Wide All-Cause Readmission), rather than the 6 specific HRRP condition measures. Useful as external facility profile context, but not a substitute for fact-level ERR.

---

## Dimension Attribute Classification & Recommendations

Based strictly on empirical findings, all 38 HGI attributes are classified into four operational tiers:

```
+----------------------------------------------------------------------------------------------------+
| Tier 1: Recommended for Exploratory Segmentation                                                  |
| - State (100% concordance, stable jurisdiction)                                                    |
| - County/Parish (Standard county jurisdiction, stable)                                             |
| - ZIP Code (Postal code clustering, socioeconomic linkage)                                         |
| - Facility ID (Primary join key, 100% unique in HGI)                                               |
+----------------------------------------------------------------------------------------------------+
| Tier 2: Usable Only with Clear Temporal Caveat                                                     |
| - Hospital Ownership (Rich variance, 0% missing; reflects July 2026 CASPER snapshot, not 2021-24)  |
| - Emergency Services (90.9% Yes / 9.1% No; reflects current capability snapshot)                   |
| - Count of Facility READM Measures (Facility readmissions breadth across 11 Hospital Compare items) |
+----------------------------------------------------------------------------------------------------+
| Tier 3: Keep as Reference Information Only                                                         |
| - Facility Name & Address (Descriptive identifiers; subject to rebranding)                         |
| - Hospital overall rating & Footnote (Composite star rating; 12.6% N/A; not causally comparable)   |
| - Count of READM Measures Better / No Different / Worse (Hospital-wide summary, not condition ERR) |
| - READM Group Measure Count & Group Footnote (Metadata on Hospital Compare 11-measure group)       |
+----------------------------------------------------------------------------------------------------+
| Tier 4: Exclude from Core Project Analysis                                                         |
| - Hospital Type (Invariant in matched cohort: 100.0% Acute Care Hospitals)                         |
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
4. **No Causal Assumptions:** Dimension attributes such as ownership or overall star rating reflect institutional and composite characteristics, not causal explanations for condition-specific risk-standardized Excess Readmission Ratios.
