# Task V1 / V1.1: Dataset Forensic Audit & Targeted Audit Closure

**Project:** Niyati  
**Dataset Source:** Dryad ([doi:10.5061/dryad.nzs7h4551](https://doi.org/10.5061/dryad.nzs7h4551))  
**Study Title:** Digital support systems to improve child development in Peru: A cluster-randomized controlled open label trial  
**Working Branch:** `project2/urja-validation`  
**Execution Date:** 2026-10-31  

---

## 1. Executive Summary

This report documents the forensic audit of the downloaded dataset package for Task V1 and the targeted closure of three key investigation areas in Task V1.1:
1. **Primary Outcome Derivation & Missingness:** Reconstructed the standardized GSED primary outcome calculation (`gsed_Z`) from the original Stata replication script (`Trial_Analysis_Replication_File_26Feb2026.do`). The derived primary outcome yields exactly 2,149 valid observations (matching the published Table 2 primary analysis sample) and 312 missing observations. These 312 missing observations decompose into 307 raw outcome non-responses and 5 observations in singleton 10-day age groups with undefined group variance. The published figure of 332 exclusions leaves an unexplained 20-participant discrepancy ($332 - 312 = 20$) that cannot be resolved from the released data or code and is labeled **UNRESOLVED**.
2. **Intervention Tracking by Treatment Arm:** Cross-tabulated `number_session`, `weeks_active`, and `program_time` against assigned treatment arms (`arm_itt`). Home visit tracking (`number_session`) is recorded solely within the Home Visits arm ($n=317$). Digital platform tracking (`weeks_active`, `program_time`) is recorded for all 1,174 Afini-assigned participants and additionally for 4 Control-assigned participants (IDs: 288, 925, 1399, 2326; positive activity values). This finding is consistent with published text reporting four control households erroneously accessing intervention services and with the Stata replication script's compliance definition.
3. **CSV vs. DTA Equivalence:** Verified that `digitalECD_26Feb2026.dta` and `digitalECD_26Feb2026.csv` share an identical set of 2,461 participant IDs and 40 variables. Applying Stata value labels to categoricals and ISO normalization to dates demonstrates 100% content equivalence (0 substantive mismatches across all 2,461 records and 40 variables).

---

## 2. Dataset Package Inventory

The raw download package is located at `data/raw/doi_10_5061_dryad_nzs7h4551__v20260226.zip` (1,166,114 bytes; SHA-256: `dd962c2934877e75aaf1cd536500ada87d9ae1feae81ca9423eae5712b0daaea`).

Contents of the package:
1. `digitalECD_26Feb2026.dta` (511,847 bytes; SHA-256: `f36f442bb6b5e530e2127742a55e894e394f52927dd5e89f729d4df27f015d65`): Authoritative Stata binary dataset preserving native variable labels and value mappings.
2. `digitalECD_26Feb2026.csv` (590,790 bytes; SHA-256: `43fa7eba954449feeacdfbb1a8f6c8e9bb6ba61e5d1d4a50948dcf16846dce8a`): Delimited backup with value-labeled columns exported as strings.
3. `DigitalECD_codebook_26Feb2026.log` (34,029 bytes; SHA-256: `d3239de0b00d9361795d1be9fccd14a50f446b15f55bf933f4cf81a6a2bb5ed9`): Stata log containing variable descriptions and value label dictionaries.
4. `Trial_Analysis_Replication_File_26Feb2026.do` (26,889 bytes; SHA-256: `5afca792c88d3ae4ccedd1c9daeff3c14da19a23129cfab702875f434f616281`): Official Stata DO replication script.
5. `README.md` (1,809 bytes; SHA-256: `25adbb6cf7c2b45efd3db3d2ce8bb384e54c50945becbae05ab04d35c927800b`): Study dataset documentation.

Detailed hashes and sizes are cataloged in [file_manifest.csv](file:///d:/Niyati/validation/V1_dataset_audit/outputs/file_manifest.csv).

---

## 3. CSV vs. DTA Equivalence Audit (Investigation C)

A complete participant- and variable-level comparison between `digitalECD_26Feb2026.dta` and `digitalECD_26Feb2026.csv` was conducted using `ID` as the matching key:
- **Participant ID Completeness & Uniqueness:** Both files contain complete, strictly unique IDs (range 1 to 2,461; 0 missing).
- **ID Set & Variable Match:** Exactly the same 2,461 participant IDs and 40 columns in both files.
- **Missingness Consistency:** 0 missingness mismatches across all 2,461 observations and 40 variables.
- **Categorical Variables (11 columns):** Applying Stata value labels to DTA numeric codes produces 0 non-null content differences with CSV string values (`arm_itt`, `child_female`, `final_status`, `provincia`, `el_afinidata4`, `el_dass_*`, `bl_mo_educ_level`, `bl_fa_educ_level`, `bl_f_b`).
- **Date Variables (2 columns):** Normalizing Stata elapsed dates and CSV date strings (`%d%b%Y`) to ISO YYYY-MM-DD produces 0 content differences (`el_date_gsed`, `bl_int_date`).
- **Numeric Variables (27 columns):** All numeric values match within floating-point tolerance (maximum absolute difference $\le 4.44 \times 10^{-16}$).
- **Conclusion:** The CSV and DTA datasets are **100% content-equivalent**. Differences are strictly representational (native Stata encodings vs. text export).

Details are cataloged in [csv_dta_equivalence.csv](file:///d:/Niyati/validation/V1_dataset_audit/outputs/csv_dta_equivalence.csv).

---

## 4. Dataset Structure & Key Variables

- **Dimensions:** 2,461 rows (individual child/caregiver pairs) and 40 columns.
- **Participant Identifier:** `ID` (Numeric float, values 1 to 2,461; 100% unique, 0 missing).
- **Cluster Identifier:** `cluster` (Numeric float, values 1 to 164; 159 populated clusters, sizes 1 to 42, mean 15.48).
- **Treatment Assignment:** `arm_itt` (Codes 1.0, 2.0, 3.0; 0 missing).
- **Primary Outcome Variables:**
  - `el_gsed_dscore`: Raw Global Scales for Early Development (GSED) d-score.
  - `el_gsed_daz`: Age-adjusted GSED DAZ score.
  - `gsed_Z`: Derived age-standardized score normalized within 10-day age groups per replication script.
- **Secondary Outcomes:** CREDI scores (`el_overall`, `el_z_overall`), maternal mental health (`el_dass_*`), stimulation activities (`el_mics_tot`), parenting beliefs (`el_parent_beliefs`), screen time (`el_afinidata1`), caregiver interaction (`el_omci_*`).

Full variable profiles, types, and ranges are cataloged in [column_profile.csv](file:///d:/Niyati/validation/V1_dataset_audit/outputs/column_profile.csv).

---

## 5. Duplicate Checks

- **Full-row duplicates:** 0 exact duplicate rows across all 40 variables.
- **Candidate participant identifier (`ID`):** 2,461 unique values out of 2,461 observations (0 duplicates, 0 missing).
- **Cluster grouping (`cluster`):** 159 unique clusters representing multi-participant groupings as expected in a cluster-randomized trial.

Details are cataloged in [duplicate_checks.csv](file:///d:/Niyati/validation/V1_dataset_audit/outputs/duplicate_checks.csv).

---

## 6. Treatment-Group Counts

Treatment allocation across the trial arms (0 missing assignments):

| Arm Code | Group Name | Description | Observations | Percentage |
| :---: | :--- | :--- | :---: | :---: |
| `1` | **Control** | Control group | 970 | 39.41% |
| `2` | **Home visits** | Traditional home visits intervention | 317 | 12.88% |
| `3` | **Afini** | Digital support system (Afini platform) | 1,174 | 47.70% |
| **Total** | | | **2,461** | **100.00%** |

Details are cataloged in [treatment_group_counts.csv](file:///d:/Niyati/validation/V1_dataset_audit/outputs/treatment_group_counts.csv).

---

## 7. Intervention Tracking Activity by Arm (Investigation B)

Cross-tabulation of intervention tracking variables against treatment assignment:

| Variable | Treatment Arm | Assigned (N) | Missing | Non-Missing | Zero (=0) | Positive (>0) | Min | Max | Tracking Activity vs. Assignment Disposition |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`number_session`** | Control (1) | 970 | 970 | 0 | 0 | 0 | — | — | 100% missing; no home visits recorded outside HV arm. |
| | Home visits (2) | 317 | 0 | 317 | 23 | 294 | 0.0 | 41.0 | 100% non-missing (23 zero sessions, 294 positive sessions). |
| | Afini (3) | 1,174 | 1,174 | 0 | 0 | 0 | — | — | 100% missing; no home visits recorded outside HV arm. |
| | **Total** | **2,461** | **2,144** | **317** | **23** | **294** | **0.0** | **41.0** | Structural tracking for Home Visits arm ($n=317$). |
| **`weeks_active`** | Control (1) | 970 | 966 | 4 | 0 | 4 | 3.0 | 42.0 | 4 non-missing positive records (IDs: 288, 925, 1399, 2326; values: 22, 42, 29, 3 weeks). |
| | Home visits (2) | 317 | 317 | 0 | 0 | 0 | — | — | 100% missing; no digital tracking recorded for HV arm. |
| | Afini (3) | 1,174 | 0 | 1,174 | 168 | 1,006 | 0.0 | 129.0 | 100% non-missing in Afini group (168 zero, 1,006 positive weeks). |
| | **Total** | **2,461** | **1,283** | **1,178** | **168** | **1,010** | **0.0** | **129.0** | Recorded for Afini arm ($n=1,174$) plus 4 Control records. |
| **`program_time`** | Control (1) | 970 | 966 | 4 | 0 | 4 | 6.0 | 67.0 | 4 non-missing positive records (IDs: 288, 925, 1399, 2326; values: 35, 67, 51, 6 weeks). |
| | Home visits (2) | 317 | 317 | 0 | 0 | 0 | — | — | 100% missing; no digital tracking recorded for HV arm. |
| | Afini (3) | 1,174 | 0 | 1,174 | 168 | 1,006 | 0.0 | 175.0 | 100% non-missing in Afini group (168 zero, 1,006 positive weeks). |
| | **Total** | **2,461** | **1,283** | **1,178** | **168** | **1,010** | **0.0** | **175.0** | Recorded for Afini arm ($n=1,174$) plus 4 Control records. |

### Context of the Four Control Tracking Records:
- The presence of tracking data for 4 Control-assigned participants is consistent with published study text noting that four control households erroneously received/accessed intervention services.
- This is further confirmed by the original Stata replication script (`Trial_Analysis_Replication_File_26Feb2026.do`), which explicitly defines control compliance as:
  ```stata
  replace compliant = 1 if arm_itt ==1 
  replace compliant = 0 if arm_itt ==1 & number_session > 0 & number_session !=. 
  replace compliant = 0 if arm_itt ==1 & weeks_active !=. 
  ```

Details are cataloged in [intervention_tracking_by_arm.csv](file:///d:/Niyati/validation/V1_dataset_audit/outputs/intervention_tracking_by_arm.csv).

---

## 8. Missingness Findings

Missingness across all 40 variables:
1. **Complete (0% missing, 8 variables):** `ID`, `arm_itt`, `cluster`, `child_female`, `final_status`, `provincia`, `distrito`, `bl_child_sib_tot`.
2. **Moderate missingness (0.01% – 20.00%, 29 variables):**
   - Baseline covariates: 3 (0.12%) missing in `bl_int_date`, `bl_childage`, `bl_z_overall`; up to 351 (14.26%) in `bl_fa_educ_level`.
   - Secondary outcomes: 304 to 397 missing (12.35% to 16.13%).
   - Primary outcome missingness:
     - Raw GSED d-score (`el_gsed_dscore`): 307 missing (12.47%).
     - Age-adjusted GSED (`el_gsed_daz`): 313 missing (12.72%).
     - Derived standardized GSED (`gsed_Z`): 312 missing (12.68%).
3. **Substantial missingness (>20.00%, 3 variables):**
   - `number_session`: 2,144 missing (87.12%). Structural missingness; recorded solely for Home Visits arm ($n=317$).
   - `weeks_active` & `program_time`: 1,283 missing (52.13%). Structural missingness; recorded for Afini arm ($n=1,174$) plus 4 Control records ($n=1,178$ non-missing total).

### Primary Outcome Missingness by Treatment Arm

| Outcome Metric | Control (n=970) | Home Visits (n=317) | Afini (n=1,174) | Total (n=2,461) |
| :--- | :---: | :---: | :---: | :---: |
| **Raw GSED (`el_gsed_dscore`)** | 106 (10.93%) | 18 (5.68%) | 183 (15.59%) | 307 (12.47%) |
| **Age-Adjusted GSED (`el_gsed_daz`)** | 108 (11.13%) | 19 (5.99%) | 186 (15.84%) | 313 (12.72%) |
| **Normalized GSED (`gsed_Z`)** | 106 (10.93%) | 20 (6.31%) | 186 (15.84%) | 312 (12.68%) |

Details are cataloged in [missingness.csv](file:///d:/Niyati/validation/V1_dataset_audit/outputs/missingness.csv).

---

## 9. Primary Outcome Derivation & Reconciliation (Investigation A)

### Reconstructed Standardization Formula
From `Trial_Analysis_Replication_File_26Feb2026.do`:
```stata
gen gsed_agemonths = int(el_gsed_age/10)
bysort gsed_agemonths: egen gsed_mean = mean(el_gsed_dscore)
bysort gsed_agemonths: egen gsed_sd = sd(el_gsed_dscore)
gen gsed_Z = (el_gsed_dscore-gsed_mean)/gsed_sd
```

### Mutually Exclusive Sample Reconciliation

| Step | Metric Name | Count | Pct of Enrolled | Definition / Mechanism | Verification Status |
| :---: | :--- | :---: | :---: | :--- | :---: |
| 1 | **Total Enrolled Base** | 2,461 | 100.0% | Total participants randomized across all three arms. | **VERIFIED** |
| 2 | **Raw Assessed Participants** | 2,154 | 87.53% | Participants with non-missing raw GSED d-score (`el_gsed_dscore`). | **VERIFIED** |
| 3 | **Raw Outcome Non-Response** | 307 | 12.47% | Participants unassessed at endline (loss to follow-up, refusal, migration, death). | **VERIFIED** |
| 4 | **Missing Assessment Age** | 0 | 0.0% | Raw score observed but missing assessment age (`el_gsed_age`). Complete for all 2,154. | **VERIFIED** |
| 5 | **Total 10-Day Age Groups** | 58 | — | Distinct age brackets populated by assessed participants (brackets 73 to 146). | **VERIFIED** |
| 6 | **Singleton Age Groups (n=1)** | 5 | — | Age brackets containing exactly one assessed child (brackets 73, 126, 131, 137, 146). | **VERIFIED** |
| 7 | **Undefined Standardization Variance** | 5 | 0.20% | Observations in singleton brackets where Stata sample standard deviation `sd()` is undefined ($n=1$). Participant IDs: 442, 773, 934, 1159, 1866. | **VERIFIED** |
| 8 | **Additional Sample Restrictions** | 0 | 0.0% | Any explicit drop, keep, or filter conditions in replication DO file prior to primary regression. | **VERIFIED** |
| 9 | **Recreated Analysis Sample (`gsed_Z`)** | **2,149** | 87.32% | Valid derived standardized GSED scores ($2,154 - 5 = 2,149$). Exactly matches published Table 2 sample. | **VERIFIED** |
| 10 | **Total Actual Exclusions** | **312** | 12.68% | Mutually exclusive sum: 307 raw non-response + 5 undefined variance drops ($2,461 - 312 = 2,149$). | **VERIFIED** |
| 11 | **Published Exclusion Figure** | **332** | 13.49% | Reported exclusions due to missing outcome in published study text. Leaves a 20-case discrepancy against actual data ($2,461 - 332 = 2,129 \neq 2,149$). | **UNRESOLVED** |

### Reconciliation Finding:
- The derived standardized score `gsed_Z` yields exactly **2,149** non-missing observations, perfectly matching the primary analysis sample reported in Table 2 of the publication.
- The 312 missing values in `gsed_Z` are strictly accounted for by 307 raw unassessed children plus 5 children dropped due to undefined standard deviation in singleton age brackets.
- The published text figure of 332 exclusions differs by 20 participants from the actual 312 exclusions observed in the dataset. Because neither the released data nor the replication script specifies an additional 20 exclusions, this discrepancy remains **UNRESOLVED**.

Details are cataloged in [gsed_outcome_reconciliation.csv](file:///d:/Niyati/validation/V1_dataset_audit/outputs/gsed_outcome_reconciliation.csv) and [participant_count_reconciliation.csv](file:///d:/Niyati/validation/V1_dataset_audit/outputs/participant_count_reconciliation.csv).

---

## 10. Data-Quality Observations

1. **Documented Sentinel Codes:** Variable `el_afinidata4` contains `-77` in 2 observations, designated in the codebook as "Don't know / refuse".
2. **Differential Follow-up:** Endline outcome missingness is higher in the Afini digital arm (15.84%) than in Control (10.93%) or Home Visits (6.31%).
3. **Cluster Index Discontinuity:** Cluster IDs range from 1 to 164 with 159 populated clusters (5 cluster indices unused).

---

## 11. Items for Investigation in Later Tasks (V2+)

1. **Cluster Randomization Verification:** Validate cluster balance and intra-cluster correlation (ICC) across arms.
2. **Baseline Covariate Balance:** Audit baseline equivalence on demographic and socioeconomic variables across the 3 arms.
3. **Differential Attrition Analysis:** Investigate mechanisms and predictors of participant follow-up and attrition across treatment arms.
4. **Multiple Imputation Replication:** Evaluate the chained equations imputation setup specified in the replication DO file.

---

## 12. Audit Output Manifest

All output files are located in `validation/V1_dataset_audit/outputs/`:
- `file_manifest.csv`: File paths, sizes, types, and SHA-256 hashes.
- `dataset_inventory.csv`: Dataset dimensions, schemas, and memory footprint.
- `column_profile.csv`: 40-variable profile, data types, ranges, unique counts, and roles.
- `missingness.csv`: Column-level missingness and primary outcome missingness stratified by arm.
- `duplicate_checks.csv`: Row deduplication and candidate identifier assessments.
- `treatment_group_counts.csv`: Treatment assignment frequencies and percentages.
- `participant_count_reconciliation.csv`: Arithmetic reconciliation of reported vs observed counts.
- `gsed_outcome_reconciliation.csv`: Detailed mutually exclusive GSED outcome derivation and missingness source breakdown (V1.1).
- `intervention_tracking_by_arm.csv`: Cross-tabulation of tracking variables by treatment assignment (V1.1).
- `csv_dta_equivalence.csv`: Participant- and variable-level CSV vs. DTA equivalence audit (V1.1).
- `v1_summary.json`: Machine-readable summary of all audit metrics and findings.
