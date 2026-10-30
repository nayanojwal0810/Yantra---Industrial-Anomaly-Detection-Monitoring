# Task V1: Dataset Forensic Audit

**Project:** Niyati  
**Dataset Source:** Dryad ([doi:10.5061/dryad.nzs7h4551](https://doi.org/10.5061/dryad.nzs7h4551))  
**Study Title:** Digital support systems to improve child development in Peru: A cluster-randomized controlled open label trial  
**Working Branch:** `project2/urja-validation`  
**Execution Date:** 2026-10-31  

---

## 1. Executive Summary

This folder contains the forensic audit of the downloaded dataset package for Task V1. The audit verified package integrity, evaluated dataset structures, profiled all 40 variables, audited missingness and duplicates, verified treatment arm distributions, and conducted a mathematical reconciliation between reported participant figures and observed data.

---

## 2. Dataset Files Discovered

The raw package is located at `data/raw/doi_10_5061_dryad_nzs7h4551__v20260226.zip` (1,166,114 bytes; SHA-256: `dd962c2934877e75aaf1cd536500ada87d9ae1feae81ca9423eae5712b0daaea`).

Contents of the package:
1. `digitalECD_26Feb2026.dta` (511,847 bytes; SHA-256: `f36f442bb6b5e530e2127742a55e894e394f52927dd5e89f729d4df27f015d65`): Stata binary dataset containing variable labels and value mappings.
2. `digitalECD_26Feb2026.csv` (590,790 bytes; SHA-256: `43fa7eba954449feeacdfbb1a8f6c8e9bb6ba61e5d1d4a50948dcf16846dce8a`): Delimited tabular backup with categorical variables pre-labeled as strings.
3. `DigitalECD_codebook_26Feb2026.log` (34,029 bytes; SHA-256: `d3239de0b00d9361795d1be9fccd14a50f446b15f55bf933f4cf81a6a2bb5ed9`): Stata log containing variable descriptions and value label dictionaries.
4. `Trial_Analysis_Replication_File_26Feb2026.do` (26,889 bytes; SHA-256: `5afca792c88d3ae4ccedd1c9daeff3c14da19a23129cfab702875f434f616281`): Official Stata DO replication script.
5. `README.md` (1,809 bytes; SHA-256: `25adbb6cf7c2b45efd3db3d2ce8bb384e54c50945becbae05ab04d35c927800b`): Dataset description and provenance metadata.

Detailed hashes and sizes are cataloged in [file_manifest.csv](file:///d:/Niyati/validation/V1_dataset_audit/outputs/file_manifest.csv).

---

## 3. Main Dataset Identification & Dimensions

- **Primary Dataset:** `digitalECD_26Feb2026.dta` is identified as the authoritative primary individual-level dataset because it preserves full native variable definitions, variable labels, and categorical value encodings.
- **Backup Dataset:** `digitalECD_26Feb2026.csv` provides identical observation and variable counts.
- **Dimensions:** 2,461 rows (individual child/caregiver pairs) and 40 columns.
- **Memory Consumption:** ~0.56 MB (`.dta`), ~1.00 MB (`.csv`).

Details are cataloged in [dataset_inventory.csv](file:///d:/Niyati/validation/V1_dataset_audit/outputs/dataset_inventory.csv).

---

## 4. Key Variables & Identifiers

- **Participant Identifier:** `ID` (Numeric float, values 1 to 2,461). Perfectly unique across all 2,461 rows, 0 missing.
- **Cluster Identifier:** `cluster` (Numeric float, values 1 to 164). Identifies 159 distinct randomization clusters; cluster size ranges from 1 to 42 participants (mean 15.48).
- **Treatment Assignment:** `arm_itt` (Categorical numeric 1 to 3). Complete with 0 missing values.
- **Primary Outcome Variables:**
  - `el_gsed_dscore`: Raw Global Scales for Early Development (GSED) d-score.
  - `el_gsed_daz`: Age-adjusted GSED DAZ score.
  - `gsed_Z`: Derived age-standardized score normalized within 10-day age groups (per replication DO script).
- **Secondary Outcomes:** CREDI scores (`el_overall`, `el_z_overall`), maternal mental health (`el_dass_*`), stimulation activities (`el_mics_tot`), parenting beliefs (`el_parent_beliefs`), screen time (`el_afinidata1`), caregiver interaction (`el_omci_*`).

Full variable descriptions, types, and ranges are cataloged in [column_profile.csv](file:///d:/Niyati/validation/V1_dataset_audit/outputs/column_profile.csv).

---

## 5. Duplicate Checks

- **Full-row duplicates:** 0 duplicate rows across all 40 variables.
- **Candidate participant identifier (`ID`):** 2,461 unique values out of 2,461 rows (100% unique, 0 duplicates, 0 missing).
- **Cluster grouping (`cluster`):** 159 unique clusters representing multi-participant groupings as expected in a cluster-randomized trial.

Details are cataloged in [duplicate_checks.csv](file:///d:/Niyati/validation/V1_dataset_audit/outputs/duplicate_checks.csv).

---

## 6. Treatment-Group Counts

The trial comprises three arms with zero missing assignment values:

| Arm Code | Group Name | Description | Observations | Percentage |
| :---: | :--- | :--- | :---: | :---: |
| `1` | **Control** | Control group | 970 | 39.41% |
| `2` | **Home visits** | Traditional home visits intervention | 317 | 12.88% |
| `3` | **Afini** | Digital support system (Afini platform) | 1,174 | 47.70% |
| **Total** | | | **2,461** | **100.00%** |

Details are cataloged in [treatment_group_counts.csv](file:///d:/Niyati/validation/V1_dataset_audit/outputs/treatment_group_counts.csv).

---

## 7. Missingness Findings

Missingness across the 40 variables falls into three distinct tiers:
1. **Complete (0% missing, 8 variables):** `ID`, `arm_itt`, `cluster`, `child_female`, `final_status`, `provincia`, `distrito`, `bl_child_sib_tot`.
2. **Moderate missingness (0.01% - 20.00%, 29 variables):**
   - Baseline covariates: 3 (0.12%) missing in `bl_int_date`, `bl_childage`, `bl_z_overall`; up to 351 (14.26%) in `bl_fa_educ_level`.
   - Primary outcome missingness:
     - `el_gsed_dscore`: 307 missing (12.47%).
     - `el_gsed_daz`: 313 missing (12.72%).
     - `gsed_Z` (derived): 312 missing (12.68%).
   - Secondary outcomes: 304 to 397 missing (12.35% to 16.13%).
3. **Substantial missingness (>20.00%, 3 variables):**
   - `number_session`: 2,144 missing (87.12%). Structural: recorded only for Home Visits arm participants (n=317).
   - `weeks_active` and `program_time`: 1,283 missing (52.13%). Structural: recorded primarily for Afini platform participants (n=1,174).

### Primary Outcome Missingness by Treatment Arm

| Outcome Metric | Control (n=970) | Home Visits (n=317) | Afini (n=1,174) | Total (n=2,461) |
| :--- | :---: | :---: | :---: | :---: |
| **Raw GSED (`el_gsed_dscore`)** | 106 (10.93%) | 18 (5.68%) | 183 (15.59%) | 307 (12.47%) |
| **Age-Adjusted GSED (`el_gsed_daz`)** | 108 (11.13%) | 19 (5.99%) | 186 (15.84%) | 313 (12.72%) |
| **Normalized GSED (`gsed_Z`)** | 106 (10.93%) | 20 (6.31%) | 186 (15.84%) | 312 (12.68%) |

Details are cataloged in [missingness.csv](file:///d:/Niyati/validation/V1_dataset_audit/outputs/missingness.csv).

---

## 8. Participant Count Reconciliation

### Reported vs. Observed Comparison

| Metric | Reported Figure | Observed Figure | Discrepancy | Status / Forensic Finding |
| :--- | :---: | :---: | :---: | :--- |
| **Total Enrolled** | 2,461 | 2,461 | 0 | **Exact Match**: Total rows in dataset equal 2,461. |
| **Primary Outcome Exclusions** | 332 | 312 | -20 | **Discrepancy Documented**: Observed missing in `gsed_Z` is 312. Reported exclusions (332) overstate actual exclusions by 20. |
| **Primary Analysis Sample** | 2,149 | 2,149 | 0 | **Exact Match**: Observed sample with valid `gsed_Z` is exactly 2,149. |
| **Arithmetic Balance** | 2,129 | 2,149 | +20 | **Reconciled**: 2,461 - 312 = 2,149. The reported 2,129 (2,461 - 332) was based on the erroneous 332 exclusion figure. |

### Forensic Derivation of the Analysis Sample
- In the raw data, 2,154 children had a valid `el_gsed_dscore` (307 unassessed).
- Per the replication DO script, `gsed_Z` standardizes scores within 10-day age groups (`int(el_gsed_age/10)`).
- Exactly 5 children were the sole observation in their 10-day age bracket (brackets 73, 126, 131, 137, 146). The sample standard deviation is undefined ($n=1$), yielding missing values for `gsed_Z`.
- 2,154 raw observed - 5 single-bracket cases = **2,149**, exactly matching the reported primary analysis sample.
- Total exclusions from 2,461 enrolled to 2,149 analysis sample are $2,461 - 2,149 = \mathbf{312}$, not 332.

Details are cataloged in [participant_count_reconciliation.csv](file:///d:/Niyati/validation/V1_dataset_audit/outputs/participant_count_reconciliation.csv).

---

## 9. Important Data-Quality Observations

1. **Documented Sentinel Codes:** Variable `el_afinidata4` contains the value `-77` in 2 observations. The codebook confirms this is the designated code for "Don't know / refuse".
2. **Differential Missingness in Outcomes:** Primary outcome attrition is higher in the Afini digital arm (15.84%) than in Control (10.93%) or Home Visits (6.31%).
3. **Cluster Index Discontinuity:** Cluster numbers span from 1 to 164, but exactly 159 clusters are populated.

---

## 10. Items for Investigation in Later Tasks (V2+)

1. **Cluster Randomization Verification:** Validate cluster balance and intra-cluster correlation (ICC) across arms.
2. **Baseline Covariate Balance:** Audit baseline equivalence on demographic and socioeconomic variables across the 3 arms.
3. **Differential Attrition Analysis:** Investigate mechanisms and predictors of participant follow-up and attrition across treatment arms.
4. **Multiple Imputation Replication:** Evaluate the chained equations imputation setup specified in the replication DO file.

---

## 11. Audit Artifacts Generated

All output files are located in `validation/V1_dataset_audit/outputs/`:
- `file_manifest.csv`
- `dataset_inventory.csv`
- `column_profile.csv`
- `missingness.csv`
- `duplicate_checks.csv`
- `treatment_group_counts.csv`
- `participant_count_reconciliation.csv`
- `v1_summary.json`
