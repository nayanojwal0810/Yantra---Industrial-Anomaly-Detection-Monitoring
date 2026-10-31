# NIRAMAYA — RAW DATA FILE INTEGRITY AUDIT REPORT

> **Project:** Niramaya  
> **Task:** Task 01 — Raw Data File Integrity Audit  
> **Audit Date & Time (UTC):** 2026-10-31T13:53:04Z  
> **Audit Date & Time (Local):** 2026-10-31 19:23:04 +0530  
> **Execution Command:** `python validation/niramaya/task_01_raw_file_audit/audit_raw_files.py --data-dir ../data/raw --output-dir validation/niramaya/task_01_raw_file_audit/output`  

---

## 1. Executive Summary

This audit establishes the integrity, structure, encoding, and catalogue alignment of the two primary local CMS raw datasets required for Project Niramaya:
1. **HRRP Dataset:** `FY_2026_Hospital_Readmissions_Reduction_Program_Hospital.csv`
2. **Hospital General Information Dataset:** `Hospital_General_Information.csv`

| Metric / Property | HRRP Dataset | Hospital General Information |
| :--- | :--- | :--- |
| **File Existence & Type** | Regular File (Exists) | Regular File (Exists) |
| **File Size (bytes / MB)** | 2,068,464 bytes (1.9726 MB) | 1,450,767 bytes (1.3836 MB) |
| **SHA-256 Checksum** | `7e7915dd2751a1e59ac46dbc9194fb781e820962a04d47c31344ea2bb30c91f6` | `f874f09fef895a1ccf5bb7392dcbb2be05c9860339261b093fe00f0c1b013480` |
| **UTF-8 BOM Present** | No (Standard UTF-8) | No (Standard UTF-8) |
| **Encoding Used** | `utf-8` | `utf-8` |
| **Actual Data Rows** | **18,330** (Ref: 18,330) | **5,419** (Ref: 5,419) |
| **Actual Columns** | **12** (Ref: 12) | **38** (Ref: 38) |
| **Catalogue Counts Match** | Exact Match | Exact Match |
| **Required Columns Status** | All 12 Present | All 5 Present |
| **Facility ID Integrity** | Intact 6-char text (3,055 unique IDs, 0 blank) | Intact 6-char text (5,419 unique IDs, 0 blank) |
| **Leading Zeroes Preserved** | Yes (`010001` preserved; 3,354 occurrences) | Yes (`010001` preserved; 854 occurrences) |
| **Malformed Rows** | 0 rows | 0 rows |
| **Exact Duplicate Rows** | 0 rows | 0 rows |

---

## 2. File A: FY 2026 Hospital Readmissions Reduction Program (HRRP) Hospital

- **File Name:** `FY_2026_Hospital_Readmissions_Reduction_Program_Hospital.csv`
- **Expected CMS Catalogue Source:** [https://data.cms.gov/provider-data/dataset/9n3s-kdb3](https://data.cms.gov/provider-data/dataset/9n3s-kdb3)
- **Direct Resource Download URL:** [https://data.cms.gov/provider-data/sites/default/files/resources/a171bc36c488d3e0dc33ec63abb469a6_1770163617/FY_2026_Hospital_Readmissions_Reduction_Program_Hospital.csv](https://data.cms.gov/provider-data/sites/default/files/resources/a171bc36c488d3e0dc33ec63abb469a6_1770163617/FY_2026_Hospital_Readmissions_Reduction_Program_Hospital.csv)
- **Resolved Local Path:** `D:\Niramaya\data\raw\FY_2026_Hospital_Readmissions_Reduction_Program_Hospital.csv`
- **File Size:** 2,068,464 bytes (1.9726 MB)
- **SHA-256 Checksum:** `7e7915dd2751a1e59ac46dbc9194fb781e820962a04d47c31344ea2bb30c91f6`
- **Encoding & BOM:** `utf-8` (UTF-8 BOM detected: `False`)

### Dimensions & Catalogue Comparison
- **Actual Data Rows:** 18,330
- **CMS Catalogue Reference Rows:** 18,330
- **Row Count Discrepancy:** +0
- **Actual Columns:** 12
- **CMS Catalogue Reference Columns:** 12
- **Column Count Discrepancy:** +0
- **Catalogue Status:** Exact match with CMS catalogue reference counts.

### Original Column Names
1. `Facility Name`
2. `Facility ID`
3. `State`
4. `Measure Name`
5. `Number of Discharges`
6. `Footnote`
7. `Excess Readmission Ratio`
8. `Predicted Readmission Rate`
9. `Expected Readmission Rate`
10. `Number of Readmissions`
11. `Start Date`
12. `End Date`

### Structural Header Validation
- **Empty Column Names:** 0 (None detected)
- **Duplicate Column Names:** 0 (None detected)

### Required Columns Verification
The following 12 required fields were verified against the CSV header:

| Required Column Name | Status | Matched Header Field |
| :--- | :--- | :--- |
| `Facility Name` | Present | `Facility Name` |
| `Facility ID` | Present | `Facility ID` |
| `State` | Present | `State` |
| `Measure Name` | Present | `Measure Name` |
| `Number of Discharges` | Present | `Number of Discharges` |
| `Footnote` | Present | `Footnote` |
| `Excess Readmission Ratio` | Present | `Excess Readmission Ratio` |
| `Predicted Readmission Rate` | Present | `Predicted Readmission Rate` |
| `Expected Readmission Rate` | Present | `Expected Readmission Rate` |
| `Number of Readmissions` | Present | `Number of Readmissions` |
| `Start Date` | Present | `Start Date` |
| `End Date` | Present | `End Date` |

### Facility ID Preservation & Integrity
- **Facility ID Column Found:** `Facility ID`
- **Total Facility ID Values:** 18,330
- **Blank / Empty Facility IDs:** 0
- **Unique Nonblank Facility IDs:** 3,055
- **String Length Distribution:** {6: 18330} (100% are exactly 6 characters)
- **Identifiers with Leading Zeroes:** 3,354
- **Leading Zeroes Preserved as Text:** `True` (e.g., `['010001', '010005', '010006']` retain the leading `'0'`)
- **Sample Identifiers:** `['010001', '010001', '010001', '010001', '010001']`

### Data Row Integrity & Exact Duplicates
- **Malformed Rows (width != 12):** 0
- **Exact Duplicate Rows Beyond First:** 0
- **Distinct Duplicated Patterns:** 0

---

## 3. File B: Hospital General Information

- **File Name:** `Hospital_General_Information.csv`
- **Expected CMS Catalogue Source:** [https://data.cms.gov/provider-data/dataset/xubh-q36u](https://data.cms.gov/provider-data/dataset/xubh-q36u)
- **Direct Resource Download URL:** [https://data.cms.gov/provider-data/sites/default/files/resources/893c372430d9d71a1c52737d01239d47_1785189955/Hospital_General_Information.csv](https://data.cms.gov/provider-data/sites/default/files/resources/893c372430d9d71a1c52737d01239d47_1785189955/Hospital_General_Information.csv)
- **Resolved Local Path:** `D:\Niramaya\data\raw\Hospital_General_Information.csv`
- **File Size:** 1,450,767 bytes (1.3836 MB)
- **SHA-256 Checksum:** `f874f09fef895a1ccf5bb7392dcbb2be05c9860339261b093fe00f0c1b013480`
- **Encoding & BOM:** `utf-8` (UTF-8 BOM detected: `False`)

### Dimensions & Catalogue Comparison
- **Actual Data Rows:** 5,419
- **CMS Catalogue Reference Rows:** 5,419
- **Row Count Discrepancy:** +0
- **Actual Columns:** 38
- **CMS Catalogue Reference Columns:** 38
- **Column Count Discrepancy:** +0
- **Catalogue Status:** Exact match with CMS catalogue reference counts.

### Original Column Names
1. `Facility ID`
2. `Facility Name`
3. `Address`
4. `City/Town`
5. `State`
6. `ZIP Code`
7. `County/Parish`
8. `Telephone Number`
9. `Hospital Type`
10. `Hospital Ownership`
11. `Emergency Services`
12. `Meets criteria for birthing friendly designation`
13. `Hospital overall rating`
14. `Hospital overall rating footnote`
15. `MORT Group Measure Count`
16. `Count of Facility MORT Measures`
17. `Count of MORT Measures Better`
18. `Count of MORT Measures No Different`
19. `Count of MORT Measures Worse`
20. `MORT Group Footnote`
21. `Safety Group Measure Count`
22. `Count of Facility Safety Measures`
23. `Count of Safety Measures Better`
24. `Count of Safety Measures No Different`
25. `Count of Safety Measures Worse`
26. `Safety Group Footnote`
27. `READM Group Measure Count`
28. `Count of Facility READM Measures`
29. `Count of READM Measures Better`
30. `Count of READM Measures No Different`
31. `Count of READM Measures Worse`
32. `READM Group Footnote`
33. `Pt Exp Group Measure Count`
34. `Count of Facility Pt Exp Measures`
35. `Pt Exp Group Footnote`
36. `TE Group Measure Count`
37. `Count of Facility TE Measures`
38. `TE Group Footnote`

### Structural Header Validation
- **Empty Column Names:** 0 (None detected)
- **Duplicate Column Names:** 0 (None detected)

### Required Columns Verification
The following 5 required fields were verified against the CSV header:

| Required Column Name | Status | Matched Header Field |
| :--- | :--- | :--- |
| `Facility ID` | Present | `Facility ID` |
| `Facility Name` | Present | `Facility Name` |
| `State` | Present | `State` |
| `Hospital Type` | Present | `Hospital Type` |
| `Hospital Ownership` | Present | `Hospital Ownership` |

### Facility ID Preservation & Integrity
- **Facility ID Column Found:** `Facility ID`
- **Total Facility ID Values:** 5,419
- **Blank / Empty Facility IDs:** 0
- **Unique Nonblank Facility IDs:** 5,419
- **String Length Distribution:** {6: 5419} (100% are exactly 6 characters)
- **Identifiers with Leading Zeroes:** 854
- **Leading Zeroes Preserved as Text:** `True` (e.g., `['010001', '010005', '010006']` retain the leading `'0'`)
- **Sample Identifiers:** `['010001', '010005', '010006', '010007', '010011']`

### Data Row Integrity & Exact Duplicates
- **Malformed Rows (width != 38):** 0
- **Exact Duplicate Rows Beyond First:** 0
- **Distinct Duplicated Patterns:** 0

---

## 4. Plain Factual Summary of Issues Requiring Attention

No raw-file integrity issues, anomalies, or structural defects were identified during this audit:
- Both files exist as regular readable files and have non-zero sizes.
- Both files use clean UTF-8 encoding without BOM corruption.
- Actual row counts (18,330 and 5,419) and column counts (12 and 38) match the CMS catalogue reference figures exactly.
- All required columns are present in both datasets.
- `Facility ID` fields are completely intact, contain zero blank values, retain 6-character text formatting, and preserve leading zeroes.
- There are zero malformed rows (no mismatched column widths).
- There are zero exact duplicate data rows in either dataset.

> [!NOTE]
> This audit is strictly confined to raw-file integrity verification. It does not evaluate hospital-level joins, condition-specific business keys, or overall project viability, which are reserved for subsequent validation tasks.
