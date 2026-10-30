# Urja — Task 1: Dataset Acquisition, Source Verification & Integrity Audit Report

**Project Name:** Urja  
**Task Number:** Task 1  
**Working Directory:** `validation/urja/task_01/`  
**Git Branch:** `project2/urja-validation`  
**Audit Date:** 2026-10-30  
**Overall Recommendation:** **PASS**

---

## 1. Executive Summary

Task 1 establishes the empirical, cryptographic, and legal foundation for **Project Urja**, which investigates the effectiveness of non-price household electricity conservation information interventions in Bangladesh.

All objective criteria defined in the project instructions have been satisfied:
1. **Source Authentication:** The original repository deposit on Harvard Dataverse (`doi:10.7910/DVN/4FLFRE`) was verified via the official Dataverse REST API.
2. **Licence Verification:** The dataset package is officially dedicated to the public domain under **CC0 1.0 Universal** (`CC0-1.0`), explicitly permitting public portfolio use, adaptation, and research redistribution. The associated research paper is published under **CC BY-NC 4.0**.
3. **Cryptographic Integrity:** The downloaded file `Replication package - Ahsanuzzaman et al 2024 JEEM-1.zip` matches the official Dataverse MD5 checksum (`7d22412f622a0845ac4e78d989ef9999`) and byte size (`2,145,810 bytes`) exactly.
4. **Data Readability & Structure:** The archive contains 11 distinct items, including 6 data tables across Stata `.dta` and Excel `.xlsx` formats, 4 Stata `.do` replication scripts, and a comprehensive `0 README.docx` documentation file. All 6 data tables were parsed in-memory with a 100% success rate without altering the raw archive.
5. **Panel Structure Validated:** The primary RCT panel dataset (`replication_data.dta`) comprises 15,882 observations across 20 variables, representing 2,394 distinct households tracked over 7 survey rounds (`Round 0` baseline through `Round 6`). Missingness patterns correspond precisely to documented survey schedules and attrition (146 households attrited after Round 0).
6. **Reproducibility & Safeguards:** An automated audit script (`audit_dataset.py`) and a unit test suite (`test_audit_dataset.py`, 7 passing tests) confirm the audit is 100% reproducible and strictly read-only.

---

## 2. Original Source Metadata

The original research dataset was queried and verified directly from the Harvard Dataverse REST API:

- **Dataset Title:** Replication Data for: Non-price energy conservation information and household energy consumption in a developing country: Evidence from an RCT
- **Persistent Identifier (PID):** `doi:10.7910/DVN/4FLFRE`
- **Dataverse ID:** 11904926
- **Depositor:** Shaikh Eskander (Universitat Autònoma de Barcelona & London School of Economics; `smsu_isku@hotmail.com`)
- **Date of Deposit:** 2025-08-12
- **Publication / Release Date:** 2025-08-13T20:52:16Z
- **Subject:** Social Sciences
- **Dataset Description:** "Data and code for replicating the results of the paper 'Non-price energy conservation information and household energy consumption in a developing country: Evidence from an RCT'."
- **Related Publication Citation:**
  > Ahsanuzzaman, Eskander, S., Islam, A. and Wang, L.C., 2024. Non-price energy conservation information and household energy consumption in a developing country: Evidence from an RCT. *Journal of Environmental Economics and Management*, 127, p.103022.
- **Related Publication DOI:** [10.1016/j.jeem.2024.103022](https://doi.org/10.1016/j.jeem.2024.103022)
- **Related Publication URL:** [https://www.sciencedirect.com/science/article/pii/S0095069624000962](https://www.sciencedirect.com/science/article/pii/S0095069624000962)

---

## 3. Dataset Version

- **Dataverse Version Number:** 1.0 (Major: 1, Minor: 0)
- **Version State:** `RELEASED`
- **Version Release Timestamp:** `2025-08-13T20:52:16Z`
- **Correspondence:** The locally acquired dataset corresponds identically to Version 1.0 of the official Dataverse release.

---

## 4. Licence and Intended-Use Verification

A mandatory distinction must be made between the research paper and the replication dataset:

### 4.1 Research Paper Licence
- **Licence:** Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)
- **Permitted Uses:** Sharing, copying, and adapting text and figures with proper attribution, strictly for non-commercial purposes.

### 4.2 Research Dataset Licence
- **Licence Name:** CC0 1.0 Universal (Public Domain Dedication)
- **SPDX Identifier:** `CC0-1.0`
- **Licence URI:** [http://creativecommons.org/publicdomain/zero/1.0](http://creativecommons.org/publicdomain/zero/1.0)
- **Terms of Use Field:** `null` (No additional restrictive covenants specified)
- **Portfolio Reuse Evaluation:** Under CC0 1.0, the depositor has waived all copyright and related rights worldwide. Technical audit, econometric replication, methodology demonstration, and open portfolio hosting of the analysis are fully legally permissible.
- **Data Governance Policy:** Despite CC0 public domain status, raw data files are preserved intact locally and excluded from Git commits via `.gitignore` and selective staging.

---

## 5. Original File Listing (Dataverse Release)

The official Harvard Dataverse release contains exactly **1 package file**:

| Filename | Dataverse File ID | Size (Bytes) | Format | Checksum (Algorithm: Value) |
|---|---|---|---|---|
| `Replication package - Ahsanuzzaman et al 2024 JEEM-1.zip` | 11904927 | 2,145,810 | application/zip | MD5: `7d22412f622a0845ac4e78d989ef9999` |

---

## 6. Local File Inventory

Inspection of `Urja/data/raw/` confirms the presence of the original downloaded package:

| File Name | Local Path | Size (Bytes) | Readable Size | Local MD5 | Local SHA-256 |
|---|---|---|---|---|---|
| `Replication package - Ahsanuzzaman et al 2024 JEEM-1.zip` | `data/raw/Replication package - Ahsanuzzaman et al 2024 JEEM-1.zip` | 2,145,810 | 2.05 MB | `7d22412f622a0845ac4e78d989ef9999` | `8fcedee8296a028142f1b7b747bdf83b38e6296e66e4fe2f90fbb7d32f2fbe9b` |

---

## 7. Source-to-Local Comparison

- **Expected Files:** 1
- **Found Files:** 1
- **Missing Files:** 0
- **Unexpected Extra Files:** 0
- **Size Comparison:** 2,145,810 bytes vs. 2,145,810 bytes (**Exact Match**)
- **Official Checksum Comparison:** MD5 `7d22412f622a0845ac4e78d989ef9999` vs. `7d22412f622a0845ac4e78d989ef9999` (**Exact Match**)
- **Integrity Assessment:** The local file is authentic, complete, and uncorrupted.

---

## 8. File Integrity & Archive Contents

In accordance with Stage C restrictions, the archive was inspected directly in-memory using Python's `zipfile` module without unpacking to disk.

The archive contains 11 core functional files (excluding macOS `.DS_Store` and resource forks):

| Internal Archive Path | Size (Bytes) | Format | Role | Readability |
|---|---|---|---|---|
| `Replication package - Ahsanuzzaman et al 2024 JEEM/0 README.docx` | 27,296 | Word docx | Documentation / Codebook | Readable |
| `Replication package - Ahsanuzzaman et al 2024 JEEM/Codes/01 JEEM 2024 replication codes - main text figures.do` | 40,918 | Stata .do | Replication Script (Main Figures) | Readable |
| `Replication package - Ahsanuzzaman et al 2024 JEEM/Codes/02 JEEM 2024 replication codes - main text tables.do` | 28,194 | Stata .do | Replication Script (Main Tables) | Readable |
| `Replication package - Ahsanuzzaman et al 2024 JEEM/Codes/03 JEEM 2024 replication codes - appendix figures.do` | 9,697 | Stata .do | Replication Script (Appendix Figures) | Readable |
| `Replication package - Ahsanuzzaman et al 2024 JEEM/Codes/04 JEEM 2024 replication codes - appendix tables.do` | 19,898 | Stata .do | Replication Script (Appendix Tables) | Readable |
| `Replication package - Ahsanuzzaman et al 2024 JEEM/Data/replication_data.dta` | 765,728 | Stata .dta (v118) | Primary RCT Household Panel Data | Readable |
| `Replication package - Ahsanuzzaman et al 2024 JEEM/Data/db_bangladesh.dta` | 24,641 | Stata .dta (v118) | GIS Administrative Boundaries | Readable |
| `Replication package - Ahsanuzzaman et al 2024 JEEM/Data/coord_bangladesh.dta` | 3,466,497 | Stata .dta (v118) | GIS Geographic Polygon Coordinates | Readable |
| `Replication package - Ahsanuzzaman et al 2024 JEEM/Data/electricity_demand.dta` | 3,195 | Stata .dta (v118) | Macro Demand Projections | Readable |
| `Replication package - Ahsanuzzaman et al 2024 JEEM/Data/wdi_electricity.dta` | 8,955 | Stata .dta (v118) | World Bank WDI Contextual Data | Readable |
| `Replication package - Ahsanuzzaman et al 2024 JEEM/Data/savings calculations.xlsx` | 10,903 | Excel .xlsx | Welfare & Net Benefit Calculations | Readable |

---

## 9. Data Formats and Dimensions

Each data table was read using format-native parsers (`pandas.io.stata.StataReader` for `.dta` and `openpyxl`/`pandas` for `.xlsx`):

| Table Name | File Format | Total Rows | Total Columns | Duplicate Rows | Missing Cells (%) | Readability Status |
|---|---|---|---|---|---|---|
| `replication_data.dta` | Stata dta (v118) | 15,882 | 20 | 0 | 15.60% | 100% Readable |
| `db_bangladesh.dta` | Stata dta (v118) | 66 | 20 | 0 | 0.00% | 100% Readable |
| `coord_bangladesh.dta` | Stata dta (v118) | 203,766 | 3 | 887 | 0.15% | 100% Readable |
| `electricity_demand.dta` | Stata dta (v118) | 8 | 4 | 0 | 0.00% | 100% Readable |
| `wdi_electricity.dta` | Stata dta (v118) | 55 | 9 | 0 | 30.30% | 100% Readable |
| `savings calculations.xlsx` | Excel xlsx | 20 | 4 | 4 | 26.25% | 100% Readable |

*Notes on structural properties:*
- In `coord_bangladesh.dta`, the 887 duplicated rows represent polygon ring closure points where start and end coordinates coincide in GIS boundary shapefiles.
- In `savings calculations.xlsx`, the 4 duplicate rows represent empty visual separator rows in the calculation template.
- In `replication_data.dta`, there are 0 duplicate rows across all 15,882 observations.

---

## 10. Schema Overview — Primary Dataset (`replication_data.dta`)

The 20 variables of `replication_data.dta` are documented in `0 README.docx` and validated through Stata variable labels:

| Field Name | Detected Dtype | Documented Description | Missing Count (%) | Distinct Values | Range [Min, Max] |
|---|---|---|---|---|---|
| `hid` | `int16` | Household unique identifying number | 0 (0.0%) | 2,394 | [1, 2394] |
| `round` | `category` | Survey rounds 0-6 | 0 (0.0%) | 7 | Categorical (Rounds 0–6) |
| `nid` | `int16` | Neighborhood unique identifying number | 0 (0.0%) | 59 | [101, 1005] |
| `suburb` | `category` | Area/suburb name and code | 0 (0.0%) | 10 | Categorical (10 suburbs) |
| `city` | `category` | City name | 0 (0.0%) | 3 | Categorical (3 cities) |
| `attrited` | `category` | Attrition status (0=Remained, 1=Attrited after round 0) | 0 (0.0%) | 2 | [0, 1] |
| `sbill` | `float32` | Self-reported monthly electricity bill (BDT, rounds 0 & 1) | 11,240 (70.8%) | 1,412 | [65.0, 9722.0] |
| `rbill` | `float32` | Verified monthly electricity bill (BDT, rounds 1-6) | 3,866 (24.3%) | 2,187 | [100.0, 9722.0] |
| `runit` | `float32` | Verified monthly electricity use (kWh, rounds 1-6) | 3,562 (22.4%) | 599 | [110.0, 1045.0] |
| `treatment` | `category` | Intervention group (T0=Control, T1=Neighbour, T2=Suburb, T3=Advice) | 0 (0.0%) | 4 | Categorical (T0–T3) |
| `user_sub_high1` | `category` | Baseline median use (suburb comparison: 0=Below, 1=Above) | 4,642 (29.2%) | 2 | [0, 1] |
| `user_nid_high1` | `category` | Baseline median use (neighbour comparison: 0=Below, 1=Above) | 4,642 (29.2%) | 2 | [0, 1] |
| `eff_sub` | `category` | Baseline efficiency level (suburb: 1=Inefficient, 2=Avg, 3=Efficient) | 4,642 (29.2%) | 3 | [1, 2, 3] |
| `eff_nid` | `category` | Baseline efficiency level (neighbour: 1=Inefficient, 2=Avg, 3=Efficient) | 4,642 (29.2%) | 3 | [1, 2, 3] |
| `followup` | `category` | Follow-up status in rounds 5 and 6 (0=No, 1=Yes) | 11,386 (71.7%) | 2 | [0, 1] |
| `eff0` | `category` | Baseline consumption type (0=Above median, 1=Below median) | 0 (0.0%) | 2 | [0, 1] |
| `flatsize` | `float64` | Flat dwelling size (square feet) | 321 (2.0%) | 103 | [620.0, 2600.0] |
| `hh_rooms` | `float64` | Number of rooms in dwelling | 321 (2.0%) | 9 | [1.0, 9.0] |
| `hh_outage` | `float64` | Outage frequency in past 3 days | 146 (0.9%) | 8 | [0.0, 7.0] |
| `freq_ac` | `float64` | Daily AC usage during hot months | 146 (0.9%) | 2 | [0.0, 1.0] |

---

## 11. Structural Quality Findings

1. **Panel Sample Balance & Attrition Structure:**
   - Round 0 (Baseline): Exactly 2,394 households observed.
   - Rounds 1 through 6: Exactly 2,248 households observed in each round.
   - Attrition: Exactly 146 households attrited after Round 0 ($2,394 - 2,248 = 146$).
   - Total rows: $146 \times 1 + 2,248 \times 7 = 15,882$. The panel structure is mathematically exact.
2. **Missingness Explanations:**
   - `sbill`: Self-reported bill was designed for baseline rounds 0 and 1; unobserved in subsequent rounds.
   - `rbill` and `runit`: Verified bills and kWh usage were collected in post-intervention survey rounds 1–6. Missing values in round 0 are expected design features.
   - `user_sub_high1` and `user_nid_high1`: Constructed indicators excluding attrited households and applicable to specific treatment branches.
   - `followup`: Indicates participation in the long-term persistence rounds 5 and 6.
3. **Identifier Integrity:**
   - Household identifier `hid` has **0 missing values**, with exactly 2,394 unique identifiers.
   - Neighborhood identifier `nid` has **0 missing values**, encompassing 59 clusters.
   - Suburb identifier `suburb` spans 10 distinct residential areas across 3 cities.
4. **Data Sanity:**
   - No infinite values (`inf` / `-inf`) detected across any numeric field.
   - No negative electricity consumption values or bills detected.
   - No row-level duplication exists in the primary dataset.

---

## 12. Missing or Unsupported Files

- **Missing Files:** None. All files documented in the Dataverse release manifest are present locally.
- **Unsupported Formats:** None. Stata `.dta` (v118), Excel `.xlsx`, Word `.docx`, and Stata `.do` files were parsed without dependency failures.

---

## 13. Critical Issues and Unresolved Questions

- **Resolved Issues:** 
  - *Data Licencing:* Confirmed as CC0 1.0 Universal on Harvard Dataverse, resolving any ambiguity regarding portfolio usage rights.
  - *Local Path Structure:* Confirmed `Urja/data/raw/` containing the original release archive.
- **Identified Nuances for Subsequent Tasks:**
  - Analysis must account for attrition (146 households) and ensure proper handling of Round 0 baseline bills (`sbill`) vs. verified meter readings (`rbill`, `runit`) in Rounds 1–6.

---

## 14. Evidence References and Source URLs

1. **Harvard Dataverse Landing Page:**  
   [https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/4FLFRE](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/4FLFRE)
2. **Harvard Dataverse REST API Endpoint:**  
   `https://dataverse.harvard.edu/api/datasets/:persistentId/?persistentId=doi:10.7910/DVN/4FLFRE`
3. **Journal Article (Elsevier JEEM):**  
   [https://doi.org/10.1016/j.jeem.2024.103022](https://doi.org/10.1016/j.jeem.2024.103022)
4. **Creative Commons Zero 1.0 Universal Legal Code:**  
   [https://creativecommons.org/publicdomain/zero/1.0/legalcode](https://creativecommons.org/publicdomain/zero/1.0/legalcode)
5. **Creative Commons Attribution-NonCommercial 4.0 International:**  
   [https://creativecommons.org/licenses/by-nc/4.0/](https://creativecommons.org/licenses/by-nc/4.0/)

---

## 15. Task 1 Checklist

| Audit Checklist Item | Result | Notes |
|---|---|---|
| Original Dataverse record verified | **VERIFIED** | API response confirmed PID `doi:10.7910/DVN/4FLFRE` |
| Dataset version identified | **VERIFIED** | Version 1.0 released 2025-08-13 |
| Dataset licence confirmed | **VERIFIED** | CC0 1.0 Universal (Public Domain Dedication) |
| Research paper licence confirmed | **VERIFIED** | CC BY-NC 4.0 (Non-commercial attribution) |
| Intended portfolio use permitted | **VERIFIED** | Allowed under CC0 1.0 |
| Local file presence verified | **VERIFIED** | `data/raw/Replication package - Ahsanuzzaman et al 2024 JEEM-1.zip` |
| File size matches original release | **VERIFIED** | Exactly 2,145,810 bytes |
| Checksum matches original release | **VERIFIED** | MD5 `7d22412f622a0845ac4e78d989ef9999` match |
| Local SHA-256 calculated | **VERIFIED** | `8fcedee8296a028142f1b7b747bdf83b38e6296e66e4fe2f90fbb7d32f2fbe9b` |
| Archive inspected in-memory | **VERIFIED** | Raw file unmodified; 11 contents catalogued |
| All data tables fully readable | **VERIFIED** | 6 data tables read without errors |
| Primary RCT dataset profiled | **VERIFIED** | 15,882 rows × 20 columns (2,394 households) |
| Panel structure documented | **VERIFIED** | 7 survey rounds (Rounds 0–6); 146 attrited units |
| Schema inventory generated | **VERIFIED** | 60 fields catalogued with descriptions |
| Quality profiles generated | **VERIFIED** | Missingness, duplicates, min/max documented |
| Reusable audit script created | **VERIFIED** | `scripts/audit_dataset.py` with CLI flags |
| Unit tests created & passing | **VERIFIED** | 7 passing tests via `pytest` and `unittest` |
| Raw data excluded from Git | **VERIFIED** | Only `validation/urja/task_01/` staged |
| Reproducibility verified | **VERIFIED** | Audit outputs rerun identically |

---

## 16. Decision Recommendation

**Final Recommendation:** **PASS**

**Justification:**
All criteria for a PASS recommendation under Section 12 are satisfied in full:
- Original Dataverse record is verified and authenticated.
- Intended-use permissions are clearly established (CC0 1.0).
- All original dataset files are present locally and match release specifications.
- Cryptographic integrity (MD5, SHA-256) is established.
- All data files can be read without conversion or raw-file modification.
- Schema and file dimensions are exhaustively documented.
- The audit script and test suite run successfully and reproducibly.
- No critical source, integrity, or legal blocker remains.
