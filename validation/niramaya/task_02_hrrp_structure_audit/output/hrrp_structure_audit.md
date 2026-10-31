# NIRAMAYA — HRRP STRUCTURE AND DATA-GRAIN AUDIT REPORT

> **Project:** Niramaya  
> **Task:** Task 02 — HRRP Structure and Data-Grain Audit  
> **Audit Date & Time (UTC):** 2026-10-31T14:00:06Z  
> **Audit Date & Time (Local):** 2026-10-31 19:30:06 +0530  
> **Execution Command:** `python validation/niramaya/task_02_hrrp_structure_audit/audit_hrrp_structure.py --data-file ../data/raw/FY_2026_Hospital_Readmissions_Reduction_Program_Hospital.csv --output-dir validation/niramaya/task_02_hrrp_structure_audit/output`  

---

## 1. Executive Summary

This audit evaluates the complete FY 2026 CMS Hospital Readmissions Reduction Program (HRRP) dataset to verify its structure, condition grain, business key uniqueness, facility coverage, and temporal consistency.

| Evaluation Area | Key Finding | Status / Assessment |
| :--- | :--- | :--- |
| **Dataset Dimensions** | 18,330 rows × 12 columns | Complete dataset verified |
| **Expected Measures** | All 6 expected measure codes present | 100% matched (0 missing, 0 unexpected) |
| **Hospital Grain Uniformity** | Exactly 3,055 hospitals for each measure | Perfectly uniform across all 6 measures |
| **Candidate Business Key** | `Facility ID` + `Measure Name` + `Start Date` + `End Date` | **Strictly Unique** (0 duplicate key groups) |
| **Facility-Level Coverage** | 3,055 hospitals with all 6 measures | **100% Complete** (0 Incomplete, 0 Exception) |
| **Reporting Period** | `07/01/2021` to `06/30/2024` for 100% of rows | Perfectly uniform & consistent |
| **Facility Identity Consistency** | 1 Name and 1 State per `Facility ID` | **100% Consistent** (0 conflicting entities) |
| **Geographic Scope** | 51 distinct jurisdictions (50 states + DC) | All standard 2-letter postal codes |
| **Data Integrity Defects** | 0 malformed rows, 0 exact duplicates, 0 blank keys | Clean raw structural integrity |

---

## 2. Dataset Overview & Source

- **Input File:** `FY_2026_Hospital_Readmissions_Reduction_Program_Hospital.csv`
- **Resolved Local Path:** `D:\Niramaya\data\raw\FY_2026_Hospital_Readmissions_Reduction_Program_Hospital.csv`
- **CMS Provider Data Catalogue URL:** [https://data.cms.gov/provider-data/dataset/9n3s-kdb3](https://data.cms.gov/provider-data/dataset/9n3s-kdb3)
- **Direct CMS Resource URL:** [https://data.cms.gov/provider-data/sites/default/files/resources/a171bc36c488d3e0dc33ec63abb469a6_1770163617/FY_2026_Hospital_Readmissions_Reduction_Program_Hospital.csv](https://data.cms.gov/provider-data/sites/default/files/resources/a171bc36c488d3e0dc33ec63abb469a6_1770163617/FY_2026_Hospital_Readmissions_Reduction_Program_Hospital.csv)
- **Total Records Processed:** 18,330
- **Total Header Columns:** 12
- **Malformed Rows:** 0
- **Exact Duplicate Rows:** 0

### Key Field Blank Counts

| Field Name | Blank / Empty Count | Nonblank Count | % Blank |
| :--- | :--- | :--- | :--- |
| `Facility ID` | 0 | 18,330 | 0.00% |
| `Measure Name` | 0 | 18,330 | 0.00% |
| `Start Date` | 0 | 18,330 | 0.00% |
| `End Date` | 0 | 18,330 | 0.00% |
| `Facility Name` | 0 | 18,330 | 0.00% |
| `State` | 0 | 18,330 | 0.00% |

---

## 3. Required Measure Identifiers Audit

The CMS HRRP defines six clinical condition measures evaluated for 30-day hospital readmissions. This audit verified the presence, exact naming, and hospital volume for each measure code.

- **Expected Measure Codes:** 6
- **Observed Distinct Measure Codes:** 6
- **All Expected Codes Present:** `True`
- **Missing Expected Codes:** `[]`
- **Unexpected Codes Detected:** `[]`

### Breakdown by Clinical Measure

| # | Measure Code | Description | Raw Rows | Distinct Hospitals | Status |
| :-: | :--- | :--- | :--- | :--- | :--- |
| 1 | `READM-30-AMI-HRRP` | Acute Myocardial Infarction 30-Day Readmission | 3,055 | 3,055 | Expected (Verified) |
| 2 | `READM-30-CABG-HRRP` | Coronary Artery Bypass Graft 30-Day Readmission | 3,055 | 3,055 | Expected (Verified) |
| 3 | `READM-30-COPD-HRRP` | Chronic Obstructive Pulmonary Disease 30-Day Readmission | 3,055 | 3,055 | Expected (Verified) |
| 4 | `READM-30-HF-HRRP` | Heart Failure 30-Day Readmission | 3,055 | 3,055 | Expected (Verified) |
| 5 | `READM-30-HIP-KNEE-HRRP` | Elective Primary Total Hip/Knee Arthroplasty Readmission | 3,055 | 3,055 | Expected (Verified) |
| 6 | `READM-30-PN-HRRP` | Pneumonia 30-Day Readmission | 3,055 | 3,055 | Expected (Verified) |

> [!NOTE]
> Each of the six measures contains exactly 3,055 records across 3,055 distinct hospitals (3,055 × 6 = 18,330 rows).

---

## 4. Candidate Business Key & Data Grain Validation

The proposed natural business key for the HRRP dataset is:
> `Facility ID` + `Measure Name` + `Start Date` + `End Date`

This candidate key represents a specific hospital evaluated for a specific clinical condition over a specific CMS performance measurement window.

- **All Key Columns Present:** `True`
- **Blank Values in Candidate Key Columns:** None detected (all counts are 0)
- **Total Rows Evaluated:** 18,330
- **Total Distinct Candidate Key Tuples:** 18,330
- **Duplicated Candidate Key Groups:** 0
- **Extra Records Beyond First:** 0
- **Candidate Key Is Unique:** `True`

### Key Conflict Inspection
Because there are zero duplicate candidate key groups, no attribute conflicts exist across:
- `Facility Name`: 0 conflicts
- `State`: 0 conflicts
- `Number of Discharges`: 0 conflicts
- `Footnote`: 0 conflicts
- `Excess Readmission Ratio`: 0 conflicts
- `Predicted Readmission Rate`: 0 conflicts
- `Expected Readmission Rate`: 0 conflicts
- `Number of Readmissions`: 0 conflicts

An evidence artifact has been produced at `output/duplicate_business_keys.csv` containing standard headers and 0 data rows.

**Conclusion on Data Grain:** The candidate key `Facility ID + Measure Name + Start Date + End Date` is verified to be uniquely identifying across the entire dataset. It represents the exact data grain of the CMS HRRP dataset.

---

## 5. Facility-Level Measure Coverage

- **Total Unique Hospitals (Facility IDs):** 3,055
- **Hospitals with All 6 Expected Measures:** 3,055 (100.0%)
- **Hospitals with Fewer Than 6 Measures:** 0
- **Hospitals with Unexpected Measures:** 0
- **Hospitals with Duplicate Measure Records:** 0
- **Distribution of Measure Counts Per Hospital:** `{6: 3055}`

### Coverage Status Classification

| Coverage Status | Definition | Hospital Count | Percentage |
| :--- | :--- | :--- | :--- |
| **Complete** | All 6 expected measures present exactly once | 3,055 | 100.0% |
| **Incomplete** | One or more expected measures absent | 0 | 0.0% |
| **Exception** | Duplicate or unexpected measure records present | 0 | 0.0% |

A full facility-by-measure coverage matrix has been generated and saved to `output/facility_measure_coverage.csv` containing all 3,055 facilities.

---

## 6. Reporting Period Validation

- **Expected CMS FY 2026 Performance Window:** `07/01/2021` to `06/30/2024` (3-year rolling period)
- **Blank Start Dates:** 0
- **Blank End Dates:** 0
- **Invalid / Unparseable Start Dates:** 0
- **Invalid / Unparseable End Dates:** 0
- **Distinct Start Date Values:** `['07/01/2021']`
- **Distinct End Date Values:** `['06/30/2024']`
- **Records Matching Expected Period:** 18,330 (100.0%)
- **Records with Other Periods:** 0 (0.0%)
- **Hospital-Level Temporal Consistency:** All 3,055 hospitals have exactly 1 consistent reporting window across all 6 measures.
- **Measure-Level Temporal Consistency:** All 6 measures share the exact same reporting window.

---

## 7. Facility Identity Consistency

This evaluation establishes whether `Facility ID` reliably and uniquely identifies hospital entities and their jurisdictions.

- **Blank Facility IDs:** 0
- **Blank Facility Names:** 0
- **Blank States:** 0
- **Facilities Associated with Multiple Names (Raw):** 0
- **Facilities Associated with Multiple Names (Normalized):** 0
- **Facilities Associated with Multiple States (Raw):** 0
- **Facilities Associated with Multiple States (Normalized):** 0
- **Distinct Geographic Jurisdictions:** 51
- **Non-Standard State Code Formats:** `[]` (None detected)
- **Facility ID Evaluated as Reliable Entity Identifier:** `True`

### Geographic Jurisdictions Present
`AK, AL, AR, AZ, CA, CO, CT, DC, DE, FL, GA, HI, IA, ID, IL, IN, KS, KY, LA, MA, MD, ME, MI, MN, MO, MS, MT, NC, ND, NE, NH, NJ, NM, NV, NY, OH, OK, OR, PA, RI, SC, SD, TN, TX, UT, VA, VT, WA, WI, WV, WY`

---

## 8. Factual Summary of Issues Requiring Attention

No structural issues, grain anomalies, duplicate keys, or temporal inconsistencies were encountered during this audit:
- The complete dataset consists of 18,330 rows and 12 columns, with zero malformed rows and zero exact duplicate rows.
- All six expected CMS HRRP condition measures (`READM-30-AMI-HRRP`, `READM-30-COPD-HRRP`, `READM-30-CABG-HRRP`, `READM-30-HF-HRRP`, `READM-30-HIP-KNEE-HRRP`, `READM-30-PN-HRRP`) are present without omission or unexpected codes.
- Every hospital (all 3,055 facilities) has exactly 6 records, achieving 100% complete coverage across the expected measures.
- The proposed natural business key (`Facility ID + Measure Name + Start Date + End Date`) is strictly unique across all 18,330 rows.
- The reporting period is 100% uniform (`07/01/2021` to `06/30/2024`) across all records, hospitals, and measures.
- `Facility ID` consistently identifies a single hospital name and state across all records.

> [!NOTE]
> This audit is strictly confined to HRRP dataset structure, data grain, and entity consistency. It does not evaluate clinical performance, excess readmission ratios, or hospital metadata joins, which are reserved for subsequent validation tasks.
