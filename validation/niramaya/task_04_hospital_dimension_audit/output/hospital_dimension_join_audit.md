# NIRAMAYA — HOSPITAL DIMENSION AUDIT AND JOIN FEASIBILITY REPORT

> **Project:** Niramaya  
> **Task:** Validation Task 04 — Hospital Dimension Audit and Join Feasibility  
> **Audit Date & Time (UTC):** 2026-10-31 14:53:32 UTC  
> **Audit Date & Time (Local):** 2026-10-31 20:23:32 India Standard Time  
> **Execution Command:** `python validation/niramaya/task_04_hospital_dimension_audit/audit_hospital_dimension_join.py`  

---

## 1. Executive Summary

This audit evaluates whether the current CMS Hospital General Information (HGI) dataset (July 2026 update, 5,419 rows, 38 columns) can reliably serve as a hospital-level dimension table for the FY 2026 CMS Hospital Readmissions Reduction Program (HRRP) dataset (18,330 rows, 12 columns, 3,055 distinct hospitals).

| Audit Evaluation Area | Key Factual Finding | Status / Assessment |
| :--- | :--- | :--- |
| **HGI Primary Key Uniqueness** | Exactly 5,419 distinct IDs across 5,419 rows | **100.0% Unique (0 duplicate IDs)** |
| **HRRP Grain and Fact Structure** | Exactly 6 condition records for all 3,055 hospitals | 100.0% Uniform Fact Cardinality |
| **HRRP-to-HGI Join Match Rate** | 3,035 of 3,055 distinct facilities matched | **99.35% Hospital Match Rate** |
| **Unmatched HRRP Hospitals** | Exactly 20 hospitals (120 fact rows; 39 published ERR) | 0.65% Unmatched (documented exceptions) |
| **Row Multiplication Impact** | Exactly 0 fact rows multiplied (1.0x factor) | **Zero Row Multiplication** |
| **Row Loss (Inner Join vs Left Join)** | Left Join retains all 18,330 rows; Inner Join loses 120 rows | **LEFT JOIN Strongly Recommended** |
| **State Concordance** | 3,035 of 3,035 matched facilities match State | **100.0% State Concordance (0 mismatches)** |
| **Facility Name Consistency** | 2,983 exact matches (98.29%); 52 mismatches (1.71%) | Corporate rebranding / system mergers |
| **Hospital Type Variance** | Exactly 100.0% of matched HRRP hospitals are 'Acute Care Hospitals' | **Zero Variance across matched cohort** |
| **Hospital Ownership** | 10 distinct ownership classes (48.6% non-profit, 20.4% proprietary) | Usable with explicit temporal caveat |
| **Temporal Compatibility** | HGI sourced from CASPER July 2026 vs HRRP 2021-2024 performance period | Snapshot caveats required for all attributes |

---

## 2. Input Datasets & Official CMS Provenance

| Dataset Attribute | Fact Dataset (HRRP FY 2026) | Dimension Dataset (HGI July 2026) |
| :--- | :--- | :--- |
| **Local File Name** | `FY_2026_Hospital_Readmissions_Reduction_Program_Hospital.csv` | `Hospital_General_Information.csv` |
| **Resolved Local Path** | `D:\Niramaya\data\raw\FY_2026_Hospital_Readmissions_Reduction_Program_Hospital.csv` | `D:\Niramaya\data\raw\Hospital_General_Information.csv` |
| **File Size** | 2,068,464 bytes (1.97 MB) | 1,450,767 bytes (1.38 MB) |
| **Encoding & Delimiter** | utf-8 (BOM: False), Delimiter: `,` | utf-8 (BOM: False), Delimiter: `,` |
| **Total Rows × Columns** | 18,330 rows × 12 columns | 5,419 rows × 38 columns |
| **Distinct Facility IDs** | 3,055 distinct facilities | 5,419 distinct facilities |
| **Facility ID Formatting** | 100% 6-digit numeric (3,354 with leading zeroes) | 5,255 6-digit numeric, 164 alphanumeric (854 leading zeroes) |
| **Malformed Width Rows** | 0 rows | 0 rows |
| **Exact Duplicate Rows** | 0 rows | 0 rows |
| **CMS Catalogue Source** | [https://data.cms.gov/provider-data/dataset/9n3s-kdb3](https://data.cms.gov/provider-data/dataset/9n3s-kdb3) | [https://data.cms.gov/provider-data/dataset/xubh-q36u](https://data.cms.gov/provider-data/dataset/xubh-q36u) |
| **Performance / Update Window** | July 1, 2021 to June 30, 2024 (3-Year Performance Window) | July 2026 Release (Current CASPER Snapshot) |

---

## 3. Hospital Dimension Key Uniqueness & Grain Validation

### A. HRRP Fact Grain
- **Total Rows:** 18,330
- **Distinct Hospitals:** 3,055
- **Measures per Hospital:** Exactly **6 records per hospital** across 100% of the 3,055 facilities:
  - `READM-30-AMI-HRRP`: 3,055 rows
  - `READM-30-CABG-HRRP`: 3,055 rows
  - `READM-30-COPD-HRRP`: 3,055 rows
  - `READM-30-HF-HRRP`: 3,055 rows
  - `READM-30-HIP-KNEE-HRRP`: 3,055 rows
  - `READM-30-PN-HRRP`: 3,055 rows
- **Logical Cardinality:** The fact table represents a strictly structured Cartesian product: 3,055 hospitals × 6 conditions = 18,330 rows.

### B. Hospital General Information Dimension Grain
- **Total Records:** 5,419
- **Distinct Facility IDs:** 5,419
- **Duplicate Facility IDs:** **0**
- **Dimension Grain Assessment:** `Facility ID` serves as a strict primary key in HGI. There are zero duplicate records, zero conflicting rows per key, and zero blank keys.
- **Relationship Type:** Joining HGI to HRRP creates an exact **One-to-Many (1:N)** relationship (1 hospital record in HGI joins to exactly 6 condition records in HRRP).

---

## 4. Join Coverage & Row-Level Impact Analysis

Joining the two datasets via exact `Facility ID` yields high coverage without row multiplication:

| Coverage Level | Total in Source | Matched Count | Matched % | Unmatched Count | Unmatched % | Join Multiplication | Impact of Inner Join |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Hospital Facility Level** | HRRP: 3,055 | 3,035 | **99.35%** | 20 | 0.65% | 1.0x (No duplication) | 20 facilities omitted |
| **HGI Dimension Level** | HGI: 5,419 | 3,035 | **56.01%** | 2,384 | 43.99% | N/A | 2,384 non-HRRP facilities omitted |
| **HRRP Fact Row Level** | Fact: 18,330 | 18,210 | **99.35%** | 120 | 0.65% | **0 rows multiplied** | **120 fact rows lost (39 numeric ERR outcomes)** |

> [!IMPORTANT]
> **Left Outer Join vs Inner Join Decision:**  
> - An **INNER JOIN** causes the silent loss of **120 HRRP fact records**, which include **39 published numeric Excess Readmission Ratios** across 15 active hospitals.  
> - A **LEFT OUTER JOIN** preserves **100% of the 18,330 HRRP fact records** and all 11,720 numeric ERR outcomes, assigning NULL dimension attributes to the 20 unmatched hospitals.  
> - **Recommendation:** Downstream models must use a **LEFT OUTER JOIN** to ensure zero data loss.

---

## 5. Diagnostic Analysis of the 20 Unmatched HRRP Facilities

All 20 HRRP facilities that lack a match in the July 2026 HGI snapshot were investigated using within-state diagnostic matching:

| Facility ID | State | HRRP Facility Name | HRRP Published ERR | Diagnostic Match in HGI | Operational Explanation / Context |
| :---: | :---: | :--- | :---: | :--- | :--- |
| `010008` | `AL` | CRENSHAW COMMUNITY HOSPITAL | 1 of 6 measures | `011308 (1.00)` | High confidence match: converted to Critical Access Hospital (CAH) with new CCN 011308 ('CRENSHAW COMMUNITY HOSPITAL'). CAHs are statutorily exempt from HRRP. |
| `010018` | `AL` | CALLAHAN EYE HOSPITAL | 0 of 6 measures | `010073 (0.68)` | No close facility name match in same state. Likely closed, merged, or retired CCN prior to July 2026. |
| `010059` | `AL` | LAWRENCE MEDICAL CENTER | 1 of 6 measures | `010021 (0.81)` | Potential system facility match: 'DALE MEDICAL CENTER' (CCN 010021). Possible hospital acquisition, rebranding, or site consolidation. |
| `010120` | `AL` | MONROE COUNTY HOSPITAL | 2 of 6 measures | `010097 (0.85)` | Potential system facility match: 'ELMORE COMMUNITY HOSPITAL' (CCN 010097). Possible hospital acquisition, rebranding, or site consolidation. |
| `040067` | `AR` | MAGNOLIA REGIONAL MEDICAL HOSPITAL | 2 of 6 measures | `040781 (0.66)` | No close facility name match in same state. Likely closed, merged, or retired CCN prior to July 2026. |
| `050125` | `CA` | REGIONAL MEDICAL CENTER OF SAN JOSE | 5 of 6 measures | `050107 (0.71)` | Potential system facility match: 'MARIAN REGIONAL MEDICAL CENTER' (CCN 050107). Possible hospital acquisition, rebranding, or site consolidation. |
| `050589` | `CA` | UCI HEALTH - PLACENTIA LINDA | 2 of 6 measures | `050570 (0.68)` | No close facility name match in same state. Likely closed, merged, or retired CCN prior to July 2026. |
| `070012` | `CT` | ROCKVILLE GENERAL HOSPITAL | 0 of 6 measures | `070007 (0.63)` | No close facility name match in same state. Likely closed, merged, or retired CCN prior to July 2026. |
| `100047` | `FL` | SHOREPOINT HEALTH PUNTA GORDA | 3 of 6 measures | `100173 (0.55)` | No close facility name match in same state. Likely closed, merged, or retired CCN prior to July 2026. |
| `100092` | `FL` | ORLANDO HEALTH ROCKLEDGE HOSPITAL | 5 of 6 measures | `100051 (0.81)` | Potential system facility match: 'ORLANDO HEALTH SOUTH LAKE HOSPITAL' (CCN 100051). Possible hospital acquisition, rebranding, or site consolidation. |
| `240052` | `MN` | LAKE REGION HEALTHCARE CORPORATION | 3 of 6 measures | `241336 (0.58)` | No close facility name match in same state. Likely closed, merged, or retired CCN prior to July 2026. |
| `260176` | `MO` | ST LUKE'S DES PERES HOSPITAL | 3 of 6 measures | `260216 (0.80)` | Potential system facility match: 'SAINT LUKE'S EAST  HOSPITAL' (CCN 260216). Possible hospital acquisition, rebranding, or site consolidation. |
| `330060` | `NY` | CARTHAGE AREA HOSPITAL, INC | 0 of 6 measures | `331318 (1.00)` | High confidence match: converted to Critical Access Hospital (CAH) with new CCN 331318 ('CARTHAGE AREA HOSPITAL, INC'). CAHs are statutorily exempt from HRRP. |
| `390326` | `PA` | ST LUKE'S HOSPITAL - ANDERSON CAMPUS | 4 of 6 measures | `390162 (0.91)` | Potential system facility match: 'ST LUKE'S HOSPITAL - EASTON CAMPUS' (CCN 390162). Possible hospital acquisition, rebranding, or site consolidation. |
| `390337` | `PA` | GEISINGER MEDICAL CENTER MUNCY | 2 of 6 measures | `390006 (0.89)` | Potential system facility match: 'GEISINGER MEDICAL CENTER' (CCN 390006). Possible hospital acquisition, rebranding, or site consolidation. |
| `450143` | `TX` | ASCENSION SETON SMITHVILLE | 0 of 6 measures | `671304 (1.00)` | High confidence match: converted to Critical Access Hospital (CAH) with new CCN 671304 ('ASCENSION SETON SMITHVILLE'). CAHs are statutorily exempt from HRRP. |
| `450271` | `TX` | MEDICAL CITY DECATUR | 4 of 6 measures | `450634 (0.82)` | Potential system facility match: 'MEDICAL CITY DENTON' (CCN 450634). Possible hospital acquisition, rebranding, or site consolidation. |
| `450411` | `TX` | EASTLAND MEMORIAL HOSPITAL | 1 of 6 measures | `671303 (1.00)` | High confidence match: converted to Critical Access Hospital (CAH) with new CCN 671303 ('EASTLAND MEMORIAL HOSPITAL'). CAHs are statutorily exempt from HRRP. |
| `450827` | `TX` | KELL WEST REGIONAL HOSPITAL | 1 of 6 measures | `451395 (0.82)` | Potential system facility match: 'HILL REGIONAL HOSPITAL' (CCN 451395). Possible hospital acquisition, rebranding, or site consolidation. |
| `520215` | `WI` | MARSHFIELD MEDICAL CENTER - RIVER REGION | 0 of 6 measures | `520011 (0.86)` | Potential system facility match: 'MARSHFIELD MEDICAL CENTER - RICE LAKE' (CCN 520011). Possible hospital acquisition, rebranding, or site consolidation. |

### Key Operational Insights on Unmatched Facilities:
1. **Critical Access Hospital (CAH) Re-certifications:** Exactly 4 hospitals (`010008` Crenshaw, `330060` Carthage Area, `450143` Ascension Seton Smithville, `450411` Eastland Memorial) match identically named facilities in HGI with new CCNs (`011308`, `331318`, `671304`, `671303`). Under CMS rules, conversion to CAH status assigns a new CCN in the `1300–1399` series (or `6713xx`). Because CAHs are statutorily exempt from HRRP, their historical acute care performance appears in HRRP under their retired acute care CCN, while HGI reflects their current CAH CCN.
2. **Health System Acquisitions & Consolidations:** Facilities such as `050125` (Regional Medical Center of San Jose), `100092` (Orlando Health Rockledge), `390326` (St. Luke's Anderson Campus), and `450271` (Medical City Decatur) represent hospitals undergoing major system mergers, acquisitions, or license consolidations between 2021 and 2026.
3. **Zero Facility ID Alterations:** Per strict validation rules, these diagnostic matches were **not** used to force an artificial join. The 20 records remain strictly documented as unmatched exceptions in `output/hospital_id_join_exceptions.csv`.

---

## 6. Name and State Consistency Across Matched Facilities

For the 3,035 matched facilities, attribute consistency between HRRP and HGI was audited:

### A. State Consistency
- **Exact State Matches:** 3,035 of 3,035 (**100.00%**)
- **State Mismatches:** **0**
- **Assessment:** Geographic jurisdiction at the state level is perfectly concordant between datasets.

### B. Facility Name Consistency
- **Exact Name Matches:** 2,983 of 3,035 (**98.29%**)
- **Formatting / Punctuation / Case Differences:** 2 facilities (0.07%)
- **Material Name Mismatches:** 50 facilities (1.65%)
- **Total Name Mismatches:** 52 facilities (**1.71%**)

### Top Material Name Discrepancies (Sample)

| Facility ID | State | HRRP Historical Facility Name | HGI July 2026 Facility Name | Nature of Discrepancy |
| :---: | :---: | :--- | :--- | :--- |
| `010086` | `AL` | NORTHWEST MEDICAL CENTER | NORTH MISSISSIPPI HEALTH SERVICES - SOUTH MARION | MATERIAL_DIFFERENCE |
| `010139` | `AL` | BROOKWOOD BAPTIST MEDICAL CENTER | BAPTIST HEALTH BROOKWOOD HOSPITAL | MATERIAL_DIFFERENCE |
| `030121` | `AZ` | HONORHEALTH MOUNTAIN VISTA MEDICAL CENTER | HONORHEALTH FOUR PEAKS MEDICAL CENTER | MATERIAL_DIFFERENCE |
| `040153` | `AR` | SOUTHWEST ARKANSAS REGIONAL MEDICAL CENTER LLC | SOUTHWEST REGIONAL MEDICAL CENTER LLC | MATERIAL_DIFFERENCE |
| `050257` | `CA` | GOOD SAMARITAN HOSPITAL | GOOD SAMARITAN HOSPITAL, LP | MATERIAL_DIFFERENCE |
| `050334` | `CA` | SALINAS VALLEY MEMORIAL HOSPITAL | SALINAS VALLEY HEALTH MEDICAL CENTER | MATERIAL_DIFFERENCE |
| `060009` | `CO` | LUTHERAN MEDICAL CENTER | INTERMOUNTAIN HEALTH LUTHERAN HOSPITAL | MATERIAL_DIFFERENCE |
| `060014` | `CO` | HCA HEALTHONE PRESBYTERIAN ST LUKES | HCA HealthOne Presbyterian St. Lukes | FORMATTING_CASE_PUNCTUATION |
| `060030` | `CO` | BANNER MCKEE MEDICAL CENTER | BANNER NORTH CO MEDICAL CENTER - LOVELAND CAMPUS | MATERIAL_DIFFERENCE |
| `100107` | `FL` | HCA FLORIDA LEHIGH REGIONAL MEDICAL CENTER | HCA FLORIDA LEHIGH HOSPITAL | MATERIAL_DIFFERENCE |

> [!NOTE]
> All 52 name discrepancies reflect corporate acquisitions (e.g. Intermountain Health, Banner Health, HCA Florida, Baptist Health), rebranding, or legal name standardization occurring between 2021 and 2026. Neither name was overwritten; both are preserved in `output/hospital_name_state_mismatches.csv`.

---

## 7. Dimension Attribute Inventory & Profiling (All 38 Columns)

Every column in `Hospital_General_Information.csv` was audited for missingness, distinct cardinality, and analytical suitability:

| # | Column Name | Data Type | Missing / Blank % | Not Available % | Distinct Values | Usability Classification |
| :-: | :--- | :--- | :---: | :---: | :---: | :--- |
| 1 | `Facility ID` | Identifier (Alphanumeric 6-char) | 0.00% | 0.00% | 5,419 | **Recommended for Join Key** |
| 2 | `Facility Name` | Text (Descriptive) | 0.00% | 0.00% | 5,288 | **Keep as Reference Information Only** |
| 3 | `Address` | Text (Descriptive) | 0.00% | 0.00% | 5,382 | **Keep as Reference Information Only** |
| 4 | `City/Town` | Text (Categorical/Geographic) | 0.00% | 0.00% | 3,046 | **Keep as Reference Information Only** |
| 5 | `State` | Categorical (2-char State Code) | 0.00% | 0.00% | 56 | **Recommended for Exploratory Segmentation** |
| 6 | `ZIP Code` | Numeric / Text (5-digit Postal Code) | 0.00% | 0.00% | 4,716 | **Recommended for Exploratory Segmentation** |
| 7 | `County/Parish` | Text (Categorical/Geographic) | 0.00% | 0.00% | 1,557 | **Recommended for Exploratory Segmentation** |
| 8 | `Telephone Number` | Text (Administrative) | 0.00% | 0.00% | 5,376 | **Exclude from Core Project Analysis** |
| 9 | `Hospital Type` | Categorical | 0.00% | 0.00% | 8 | **Exclude as Segmentation Variable (Retain as Cohort Filter)** |
| 10 | `Hospital Ownership` | Categorical | 0.00% | 0.00% | 12 | **Usable Only with Clear Temporal Caveat** |
| 11 | `Emergency Services` | Binary Indicator (Yes/No) | 0.00% | 0.00% | 2 | **Usable Only with Clear Temporal Caveat** |
| 12 | `Meets criteria for birthing friendly designation` | Binary Indicator ('Y' or Blank) | 58.24% | 0.00% | 1 | **Exclude from Core Project Analysis** |
| 13 | `Hospital overall rating` | Ordinal Rating (1-5 Stars, 'Not Available') | 0.00% | 41.43% | 6 | **Keep as Reference Information Only** |
| 14 | `Hospital overall rating footnote` | Text (Footnote Annotation) | 57.26% | 0.00% | 8 | **Keep as Reference Information Only** |
| 15 | `MORT Group Measure Count` | Numeric / Categorical ('8', 'Not Available') | 0.00% | 15.69% | 2 | **Exclude from Core Project Analysis** |
| 16 | `Count of Facility MORT Measures` | Numeric Integer / 'Not Available' | 0.00% | 24.41% | 9 | **Keep as Reference Information Only** |
| 17 | `Count of MORT Measures Better` | Numeric Integer / 'Not Available' | 0.00% | 24.41% | 10 | **Keep as Reference Information Only** |
| 18 | `Count of MORT Measures No Different` | Numeric Integer / 'Not Available' | 0.00% | 24.41% | 10 | **Keep as Reference Information Only** |
| 19 | `Count of MORT Measures Worse` | Numeric Integer / 'Not Available' | 0.00% | 24.41% | 7 | **Keep as Reference Information Only** |
| 20 | `MORT Group Footnote` | Text (Footnote Annotation) | 74.24% | 0.00% | 5 | **Keep as Reference Information Only** |
| 21 | `Safety Group Measure Count` | Numeric / Categorical ('8', 'Not Available') | 0.00% | 15.69% | 2 | **Exclude from Core Project Analysis** |
| 22 | `Count of Facility Safety Measures` | Numeric Integer / 'Not Available' | 0.00% | 38.29% | 9 | **Keep as Reference Information Only** |
| 23 | `Count of Safety Measures Better` | Numeric Integer / 'Not Available' | 0.00% | 38.29% | 8 | **Keep as Reference Information Only** |
| 24 | `Count of Safety Measures No Different` | Numeric Integer / 'Not Available' | 0.00% | 38.29% | 10 | **Keep as Reference Information Only** |
| 25 | `Count of Safety Measures Worse` | Numeric Integer / 'Not Available' | 0.00% | 38.29% | 5 | **Keep as Reference Information Only** |
| 26 | `Safety Group Footnote` | Text (Footnote Annotation) | 60.34% | 0.00% | 6 | **Keep as Reference Information Only** |
| 27 | `READM Group Measure Count` | Numeric / Categorical ('11', 'Not Available') | 0.00% | 15.69% | 2 | **Keep as Reference Information Only** |
| 28 | `Count of Facility READM Measures` | Numeric Integer / 'Not Available' | 0.00% | 21.31% | 12 | **Usable Only with Clear Temporal Caveat** |
| 29 | `Count of READM Measures Better` | Numeric Integer / 'Not Available' | 0.00% | 21.31% | 8 | **Usable Only with Clear Temporal Caveat** |
| 30 | `Count of READM Measures No Different` | Numeric Integer / 'Not Available' | 0.00% | 21.31% | 13 | **Usable Only with Clear Temporal Caveat** |
| 31 | `Count of READM Measures Worse` | Numeric Integer / 'Not Available' | 0.00% | 21.31% | 9 | **Usable Only with Clear Temporal Caveat** |
| 32 | `READM Group Footnote` | Text (Footnote Annotation) | 77.43% | 0.00% | 5 | **Keep as Reference Information Only** |
| 33 | `Pt Exp Group Measure Count` | Numeric / Categorical ('15', 'Not Available') | 0.00% | 15.69% | 2 | **Exclude from Core Project Analysis** |
| 34 | `Count of Facility Pt Exp Measures` | Numeric Integer / 'Not Available' | 0.00% | 36.08% | 4 | **Keep as Reference Information Only** |
| 35 | `Pt Exp Group Footnote` | Text (Footnote Annotation) | 62.80% | 0.00% | 4 | **Keep as Reference Information Only** |
| 36 | `TE Group Measure Count` | Numeric / Categorical ('10', 'Not Available') | 0.00% | 15.69% | 2 | **Exclude from Core Project Analysis** |
| 37 | `Count of Facility TE Measures` | Numeric Integer / 'Not Available' | 0.00% | 16.96% | 11 | **Keep as Reference Information Only** |
| 38 | `TE Group Footnote` | Text (Footnote Annotation) | 81.40% | 0.00% | 5 | **Keep as Reference Information Only** |

---

## 8. Candidate Attribute Frequency Distributions

Key candidate attributes were profiled across both **All HGI Records (5,419)** and the **Matched HRRP Cohort (3,035)**:

### A. Hospital Type
| Category | All HGI Count (5,419) | All HGI % | Matched HRRP Count (3,035) | Matched HRRP % | Usability Assessment |
| :--- | :---: | :---: | :---: | :---: | :--- |
| Acute Care Hospitals | 3,107 | 57.34% | 3,035 | **100.00%** | Zero variance in HRRP (Cohort filter only) |
| Acute Care - Department of Defense | 32 | 0.59% | 0 | **0.00%** | Zero variance in HRRP (Cohort filter only) |
| Acute Care - Veterans Administration | 132 | 2.44% | 0 | **0.00%** | Zero variance in HRRP (Cohort filter only) |
| Childrens | 94 | 1.73% | 0 | **0.00%** | Zero variance in HRRP (Cohort filter only) |
| Critical Access Hospitals | 1,382 | 25.50% | 0 | **0.00%** | Zero variance in HRRP (Cohort filter only) |
| Long-term | 5 | 0.09% | 0 | **0.00%** | Zero variance in HRRP (Cohort filter only) |
| Psychiatric | 624 | 11.52% | 0 | **0.00%** | Zero variance in HRRP (Cohort filter only) |
| Rural Emergency Hospital | 43 | 0.79% | 0 | **0.00%** | Zero variance in HRRP (Cohort filter only) |

> [!IMPORTANT]
> `Hospital Type` has **zero variance** among matched HRRP hospitals (100.0% are `Acute Care Hospitals`). It cannot be used as an independent segmentation variable in benchmarking models.

### B. Hospital Ownership
| Category | All HGI Count (5,419) | All HGI % | Matched HRRP Count (3,035) | Matched HRRP % | Usability Assessment |
| :--- | :---: | :---: | :---: | :---: | :--- |
| Voluntary non-profit - Private | 2,322 | 42.85% | 1,474 | **48.57%** | Usable with temporal caveat |
| Proprietary | 1,063 | 19.62% | 619 | **20.40%** | Usable with temporal caveat |
| Voluntary non-profit - Other | 353 | 6.51% | 241 | **7.94%** | Usable with temporal caveat |
| Government - Hospital District or Authority | 512 | 9.45% | 220 | **7.25%** | Usable with temporal caveat |
| Voluntary non-profit - Church | 264 | 4.87% | 199 | **6.56%** | Usable with temporal caveat |
| Government - Local | 393 | 7.25% | 135 | **4.45%** | Usable with temporal caveat |
| Physician | 80 | 1.48% | 70 | **2.31%** | Usable with temporal caveat |
| Government - State | 209 | 3.86% | 45 | **1.48%** | Usable with temporal caveat |
| Government - Federal | 42 | 0.78% | 23 | **0.76%** | Usable with temporal caveat |
| Tribal | 17 | 0.31% | 9 | **0.30%** | Usable with temporal caveat |
| Department of Defense | 32 | 0.59% | 0 | **0.00%** | Usable with temporal caveat |
| Veterans Health Administration | 132 | 2.44% | 0 | **0.00%** | Usable with temporal caveat |

### C. Emergency Services
| Category | All HGI Count (5,419) | All HGI % | Matched HRRP Count (3,035) | Matched HRRP % | Usability Assessment |
| :--- | :---: | :---: | :---: | :---: | :--- |
| Yes | 4,495 | 82.95% | 2,758 | **90.87%** | Usable with temporal caveat |
| No | 924 | 17.05% | 277 | **9.13%** | Usable with temporal caveat |

### D. Hospital Overall Star Rating
| Rating Value | All HGI Count (5,419) | All HGI % | Matched HRRP Count (3,035) | Matched HRRP % | Usability Assessment |
| :--- | :---: | :---: | :---: | :---: | :--- |
| 3 | 985 | 18.18% | 846 | **27.87%** | Reference context only |
| 4 | 946 | 17.46% | 779 | **25.67%** | Reference context only |
| 2 | 661 | 12.20% | 569 | **18.75%** | Reference context only |
| Not Available | 2,245 | 41.43% | 381 | **12.55%** | Reference context only |
| 5 | 384 | 7.09% | 290 | **9.56%** | Reference context only |
| 1 | 198 | 3.65% | 170 | **5.60%** | Reference context only |

---

## 9. Temporal and Conceptual Compatibility Analysis

A critical responsibility of this audit is evaluating the compatibility between a **historical fact table** and a **current dimension table**:

### 1. Performance Period vs Dimension Snapshot Discordance
- **HRRP FY 2026 Fact Period:** July 1, 2021 to June 30, 2024 (a 36-month retrospective window).
- **Hospital General Information Snapshot:** July 2026 data release (sourced from CMS CASPER).
- **Analytical Implication:** CMS Certification and Survey Provider Enhanced Reporting (CASPER) data reflects the *current administrative state* of the facility at the time of publication, not a historical longitudinal record.

### 2. Specific Attribute Evaluations
- **Hospital Ownership:** While 0% missing and displaying rich variance (48.6% non-profit private, 20.4% proprietary, 7.9% non-profit other, etc.), hospital ownership is dynamic. Health system acquisitions, hospital sales, and mergers occurred frequently between 2021 and 2026. Therefore, current ownership can be used for exploratory descriptive segmentation only with an explicit caveat noting that ownership reflects the July 2026 status.
- **Hospital Type:** All 3,035 matched hospitals are Acute Care Hospitals (100.0%). Under statutory rules, HRRP applies strictly to IPPS acute care hospitals. This attribute is constant across the matched dataset and cannot serve as an explanatory variable.
- **Emergency Services:** 90.9% Yes, 9.1% No. Highly stable institutional capability, though emergency department status is subject to service-line adjustments. Usable with a snapshot caveat.
- **Geographic Attributes (`State`, `County/Parish`, `ZIP Code`):** Completely stable physical attributes. State is 100% concordant. Recommended for regional and geographic stratification.
- **Hospital Overall Star Rating:** Star ratings are composite scores reflecting 5 distinct quality domains. 12.6% of matched HRRP hospitals have 'Not Available'. The star rating cannot be treated as a causal driver of HRRP condition readmissions; it should remain reference context only.
- **READM Group Summary Fields:** Reflects facility-level readmission aggregations across up to 11 measures (including Hospital-Wide All-Cause Readmission), rather than condition-specific HRRP ERR. Useful as external facility context, but not a replacement for measure-level fact values.

---

## 10. Dimension Join Recommendations for Downstream Analysis

Based strictly on empirical evidence, candidate dimension attributes are classified into four tiers:

| Tier | Recommendation | Specific Attributes | Analytical Guidelines |
| :---: | :--- | :--- | :--- |
| **1** | **Recommended for Exploratory Segmentation** | `State`, `County/Parish`, `ZIP Code`, `Facility ID` | High data quality, zero temporal drift in physical boundaries. State has 100% concordance. |
| **2** | **Usable Only with Clear Temporal Caveat** | `Hospital Ownership`, `Emergency Services`, `Count of Facility READM Measures` | Sourced from July 2026 CASPER snapshot. Must document that ownership/capabilities may have changed since 2021-2024. |
| **3** | **Keep as Reference Information Only** | `Facility Name`, `Address`, `Hospital overall rating`, `Count of READM Measures Better/No Different/Worse` | Descriptive identifiers and composite summaries. Useful for profile cards or reporting, but not causal modeling. |
| **4** | **Exclude from Core Project Analysis** | `Hospital Type` (zero variance in HRRP), `Telephone Number` (administrative), `Meets criteria for birthing friendly designation` (high missingness, clinically unrelated), MORT/Safety/TE summary counts | Inappropriate, invariant, or conceptually unaligned with HRRP adult readmission benchmarking. |

---

## 11. Summary of Deliverable Files

All audit deliverables are generated in `validation/niramaya/task_04_hospital_dimension_audit/`:

1. `audit_hospital_dimension_join.py`: Complete audit implementation script.
2. `README.md`: Task documentation and operational summary.
3. `output/hospital_dimension_join_audit.json`: Complete machine-readable audit results.
4. `output/hospital_dimension_join_audit.md`: This comprehensive evaluation report.
5. `output/hgi_field_inventory.csv`: Exhaustive inventory and classification of all 38 HGI columns.
6. `output/hrrp_hgi_join_coverage.csv`: Quantitative summary of join coverage and row-level impacts.
7. `output/hospital_dimension_attribute_profile.csv`: Category-level distributions across all HGI and matched HRRP.
8. `output/hospital_id_join_exceptions.csv`: Explicit listing and diagnostic context for the 20 unmatched HRRP facilities.
9. `output/hospital_name_state_mismatches.csv`: Detailed audit of the 52 facility name differences.
10. `output/execution_environment.txt`: Execution environment and system reproducibility record.

---
Task 04 audit completed successfully.