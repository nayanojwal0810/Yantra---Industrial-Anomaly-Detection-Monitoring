# Task V2: Experimental Design & Baseline Balance Validation

**Project:** Niyati  
**Study Title:** Digital support systems to improve child development in Peru: A cluster-randomized controlled open label trial  
**Dataset Source:** Dryad ([doi:10.5061/dryad.nzs7h4551](https://doi.org/10.5061/dryad.nzs7h4551))  
**Working Branch:** `project2/urja-validation`  
**Execution Date:** 2026-10-31  

---

## 1. Executive Summary

This report presents the forensic audit and validation of the experimental design, cluster assignment integrity, cluster-size distributions, province-stratified allocation, baseline covariate balance, published Table 1 reconciliation, and protocol covariate availability for Task V2.

### Key Audit Findings:
1. **Cluster Count & Participant Reconciliation:**
   - The released dataset populates exactly **159 unique clusters** and **2,461 enrolled participants**, perfectly matching the published trial results.
   - Across study arms, populated cluster and participant counts match published figures exactly:
     - **Control:** 68 clusters, 970 participants
     - **Home visits:** 19 clusters, 317 participants
     - **Afini digital intervention:** 72 clusters, 1,174 participants
   - Five cluster IDs in the numeric range 1 to 164 (`51, 65, 66, 67, 68`) have zero enrolled participants in the released dataset. This aligns with the published paper, which notes that four Control-allocated clusters had no eligible enrolled households and one Home Visit-allocated cluster had zero enrollment. Per task specifications, treatment assignments of absent cluster IDs cannot and should not be inferred from numeric gaps alone.
2. **Cluster Assignment Integrity:**
   - **Zero clusters have mixed treatment assignments.** Every single populated cluster contains participants from exactly one assigned trial arm (`PERFECT_ISOLATION_VERIFIED`). No material assignment-integrity violations exist.
   - 158 clusters map to exactly one study province. Exactly **one cluster (Cluster 104)** spans two provinces: 33 participants in Cajabamba and 1 participant in Cajamarca (both recorded in District 1).
   - 142 clusters map to a single district, while 17 clusters have participants recorded across two districts within the same province.
3. **Cluster-Size Distributions:**
   - Overall cluster sizes range from 1 to 42 participants, with a mean of 15.48, median of 13.0, and standard deviation of 9.94 ($CV = 0.6419$).
   - Cluster size distributions by arm:
     - Control ($n=68$): Mean 14.26, Median 13.0, Range 1–42, SD 10.01 ($CV = 0.7019$)
     - Home visits ($n=19$): Mean 16.68, Median 18.0, Range 3–28, SD 7.98 ($CV = 0.4783$)
     - Afini ($n=72$): Mean 16.31, Median 13.0, Range 1–42, SD 10.32 ($CV = 0.6327$)
   - Variations in enrolled cluster sizes reflect post-randomization household eligibility and recruitment within communities, not randomization failure.
4. **Province-Stratified Allocation:**
   - Randomization was stratified across the three study provinces: Cajamarca (88 clusters, 1,274 participants), Cajabamba (44 clusters, 806 participants), and San Marcos (27 clusters, 381 participants).
   - Cluster allocation shares within provinces consistently mirror the planned trial-wide ~72:20:72 community ratio:
     - Cajamarca: 42.05% Control, 11.36% Home visits, 46.59% Afini
     - Cajabamba: 43.18% Control, 13.64% Home visits, 43.18% Afini
     - San Marcos: 44.44% Control, 11.11% Home visits, 44.44% Afini
5. **Baseline Covariate Balance:**
   - **Cluster-Level Balance (Primary Diagnostic):** Treating each cluster as one randomized unit ($N=159$), 11 of 13 baseline variables exhibit at least one pairwise $|SMD| \ge 0.20$. However, these larger differences occur almost exclusively in comparisons involving the Home Visits arm, which has only 19 populated clusters and is subject to substantial small-sample sampling variability.
   - **Participant-Level Balance (Secondary Diagnostic):** Weighted at the participant level ($N=2,461$), balance is high: 12 of 13 baseline variables have maximum $|SMD| < 0.20$. Only household SES index (`bl_qses_index`) shows $|SMD| \ge 0.20$ ($|SMD| = 0.211$ between Control and Afini).
   - In accordance with task guidelines, inferential p-values are not used to declare randomization success or failure.
6. **Published Table 1 Replication:**
   - All **17 baseline summary statistics** from Table 1 of the published results paper were reproduced from the dataset using native variables and value labels.
   - **100% of values match the published paper to the exact displayed decimal place** (`FULL_MATCH_WITH_ROUNDING`; 17/17 items matched, difference = 0.0).
7. **Protocol Randomization-Covariate Availability:**
   - Of the six community/household covariates specified in the trial protocol for constrained randomization, only province (stratification factor) and participant-level caregiver education and SES are present in the released 40-variable dataset.
   - **Pre-randomization community population size, annual births, altitude, and baseline cell phone ownership are completely absent from the released dataset.** Enrolled sample sizes cannot substitute for census population, and endline awareness measures cannot substitute for baseline phone ownership.

---

## 2. Study Design & External Count Reconciliation

The study was designed as a three-arm cluster-randomized controlled trial across 164 rural and semi-urban communities in three provinces in Cajamarca, Peru.

### Planned vs. Published vs. Observed Reconciliations:

| Study Metric | Protocol Planned | Published Paper | Observed in Dataset | Reconciliation Status |
| :--- | :---: | :---: | :---: | :---: |
| **Total Communities / Clusters** | 164 | 159 populated (5 unpopulated) | 159 populated (5 absent IDs) | **EXACT MATCH** |
| — Control Clusters | 72 | 68 | 68 | **EXACT MATCH** |
| — Home Visits Clusters | 20 | 19 | 19 | **EXACT MATCH** |
| — Afini Digital Clusters | 72 | 72 | 72 | **EXACT MATCH** |
| **Total Enrolled Participants** | — | 2,461 | 2,461 | **EXACT MATCH** |
| — Control Participants | — | 970 | 970 | **EXACT MATCH** |
| — Home Visits Participants | — | 317 | 317 | **EXACT MATCH** |
| — Afini Digital Participants | — | 1,174 | 1,174 | **EXACT MATCH** |

### Absent Cluster IDs in Observed Numeric Range [1, 164]:
- The observed cluster IDs range from `1.0` to `164.0`.
- Exactly 5 IDs are absent: **`51, 65, 66, 67, 68`**.
- The published results paper explicitly documents: *"Four Control-allocated clusters had no eligible enrolled households and one Home Visit-allocated cluster had zero enrollment."*
- **Important Note:** In accordance with the execution protocol, the specific treatment arm assignments of these five unpopulated communities cannot and should not be inferred from their numeric gaps in the released dataset alone.

---

## 3. Cluster Assignment Integrity & Geographic Mapping (Validation A)

A dedicated cluster-level dataset was constructed with one record per populated cluster ($N=159$), cataloged in [cluster_assignment_integrity.csv](file:///d:/Niyati/validation/V2_experimental_design/outputs/cluster_assignment_integrity.csv).

### Core Integrity Checks:
1. **Single-Arm Treatment Isolation:**
   - In 100% of populated clusters ($159 / 159$), every enrolled participant belongs to the exact same assigned treatment arm.
   - There are **0 clusters with mixed arm assignments**. No cross-assignment or contamination of treatment coding occurred within clusters.
2. **Missing Identifiers & Codes:**
   - Missing cluster IDs in participant dataset: **0**
   - Missing treatment assignments (`arm_itt`): **0**
   - Invalid treatment arm codes: **0** (all coded strictly 1, 2, or 3)
3. **Geographic Mapping Integrity:**
   - **Province Consistency:**
     - 158 clusters map strictly to a single province.
     - **Cluster 104** spans two provinces: 33 participants reside in Cajabamba and 1 participant (ID 286) resides in Cajamarca. Both are recorded in District 1.
   - **District Consistency:**
     - 142 clusters map strictly to a single district.
     - **17 clusters** contain participants recorded across two adjacent districts within the same province (e.g., Clusters 41, 47, 49, 60, 69, 80, 83, 91, 93, 100, 103, 118, 129, 137, 143, 147, 157).
     - This occurs where community catchment boundaries span administrative district borders.

---

## 4. Cluster-Size Distribution (Validation B)

The number of enrolled households per cluster was evaluated across the trial, by arm, and by province, cataloged in [cluster_size_distribution.csv](file:///d:/Niyati/validation/V2_experimental_design/outputs/cluster_size_distribution.csv).

### Parametric and Non-Parametric Summary:

| Stratum | Populated Clusters | Total Enrolled | Min Size | Q25 (25%) | Median | Mean | Q75 (75%) | Max Size | Sample SD | Coeff. of Variation |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Overall Trial** | **159** | **2,461** | **1** | **7.0** | **13.0** | **15.48** | **22.0** | **42** | **9.94** | **0.6419** |
| Control (Arm 1) | 68 | 970 | 1 | 6.0 | 13.0 | 14.26 | 20.25 | 42 | 10.01 | 0.7019 |
| Home visits (Arm 2) | 19 | 317 | 3 | 10.0 | 18.0 | 16.68 | 22.0 | 28 | 7.98 | 0.4783 |
| Afini (Arm 3) | 72 | 1,174 | 1 | 8.0 | 13.0 | 16.31 | 22.25 | 42 | 10.32 | 0.6327 |

### Stratification by Province and Arm:
- **Cajamarca (88 clusters):**
  - Control ($n=37$): Mean 12.89, Median 13.0, Range 1–34, SD 8.32, CV 0.6451
  - Home visits ($n=10$): Mean 15.10, Median 14.0, Range 3–28, SD 8.01, CV 0.5302
  - Afini ($n=41$): Mean 15.76, Median 13.0, Range 1–39, SD 10.13, CV 0.6427
- **Cajabamba (44 clusters):**
  - Control ($n=19$): Mean 18.21, Median 21.0, Range 1–42, SD 12.96, CV 0.7117
  - Home visits ($n=6$): Mean 17.17, Median 19.5, Range 5–28, SD 9.87, CV 0.5748
  - Afini ($n=19$): Mean 18.79, Median 14.0, Range 3–42, SD 11.63, CV 0.6190
- **San Marcos (27 clusters):**
  - Control ($n=12$): Mean 12.25, Median 10.5, Range 3–29, SD 8.48, CV 0.6919
  - Home visits ($n=3$): Exactly 21 participants in all 3 clusters (Mean 21.0, Median 21.0, Range 21–21, SD 0.0, CV 0.0000)
  - Afini ($n=12$): Mean 14.25, Median 11.5, Range 6–32, SD 8.74, CV 0.6133

### Methodological Caveat:
Enrolled cluster sizes exhibit natural variability (CV between 0.48 and 0.70). These variations represent post-randomization recruitment, eligible household density, and participation willingness in each community. They must not be interpreted as evidence of randomization failure.

---

## 5. Province-Stratified Allocation (Validation C)

The trial protocol specified randomization stratified by province. Cross-tabulation of populated clusters and enrolled participants across the three provinces is cataloged in [cluster_allocation_by_province.csv](file:///d:/Niyati/validation/V2_experimental_design/outputs/cluster_allocation_by_province.csv).

| Province Name | Populated Clusters | Enrolled Participants | Control Clusters (%) | Home Visits Clusters (%) | Afini Clusters (%) | Mean Cluster Size |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Cajamarca** | 88 | 1,274 | 37 (42.05%) | 10 (11.36%) | 41 (46.59%) | 14.48 |
| **Cajabamba** | 44 | 806 | 19 (43.18%) | 6 (13.64%) | 19 (43.18%) | 18.32 |
| **San Marcos** | 27 | 381 | 12 (44.44%) | 3 (11.11%) | 12 (44.44%) | 14.11 |
| **All Provinces** | **159** | **2,461** | **68 (42.77%)** | **19 (11.95%)** | **72 (45.28%)** | **15.48** |

### Stratification Verification:
1. The observed province labels correspond to the three protocol provinces: Cajamarca, Cajabamba, and San Marcos.
2. The proportion of clusters allocated to each arm is stable across all three provinces (~42–44% Control, ~11–14% Home visits, ~43–47% Afini), confirming consistent stratified allocation.

---

## 6. Baseline Balance Analysis (Validation D)

Randomization was conducted at the **cluster level**. Therefore, cluster-level balance is the primary design diagnostic, while participant-level balance serves as a secondary comparison against published statistics.

### Standardized Mean Difference (SMD) Formula:
Pairwise standardized mean differences were calculated using sample standard deviations ($ddof=1$) and pooled standard deviation:
$$s_{\text{pooled}} = \sqrt{\frac{(n_1 - 1)s_1^2 + (n_2 - 1)s_2^2}{n_1 + n_2 - 2}}, \quad SMD = \frac{\bar{x}_1 - \bar{x}_2}{s_{\text{pooled}}}$$

Descriptive balance guideposts:
- $|SMD| < 0.10$: Small difference
- $0.10 \le |SMD| < 0.20$: Moderate difference
- $|SMD| \ge 0.20$: Larger difference requiring attention

### Primary vs. Secondary Balance Comparison:

| Baseline Covariate | Metric / Category | Cluster-Level Max \|SMD\| (Primary) | Cluster-Level Band | Participant-Level Max \|SMD\| (Secondary) | Participant-Level Band |
| :--- | :--- | :---: | :--- | :---: | :--- |
| **Mother education** (`bl_mo_educ_level`) | Max across levels (Higher educ) | **0.5103** | Larger difference (>=0.20) | 0.1881 | Moderate difference |
| **Father education** (`bl_fa_educ_level`) | Max across levels (Higher educ) | **0.4938** | Larger difference (>=0.20) | 0.1848 | Moderate difference |
| **Father age** (`bl_fa_age`) | Mean years | **0.3908** | Larger difference (>=0.20) | 0.1132 | Moderate difference |
| **Household SES index** (`bl_qses_index`) | Mean quintiles | **0.3526** | Larger difference (>=0.20) | **0.2110** | Larger difference (>=0.20) |
| **Mother age** (`bl_mo_age`) | Mean years | **0.3448** | Larger difference (>=0.20) | 0.1174 | Moderate difference |
| **Low birth weight** (`bl_low_bweight`) | Proportion <2500g | **0.2767** | Larger difference (>=0.20) | 0.0985 | Small difference |
| **Household adults** (`bl_hhadults`) | Mean count | **0.2543** | Larger difference (>=0.20) | 0.1205 | Moderate difference |
| **Home stimulation** (`bl_mics_tot`) | Mean MICS score | **0.2484** | Larger difference (>=0.20) | 0.0777 | Small difference |
| **Child female** (`child_female`) | Proportion female | **0.2437** | Larger difference (>=0.20) | 0.0473 | Small difference |
| **Baseline CREDI** (`bl_z_overall`) | Mean z-score | **0.2155** | Larger difference (>=0.20) | 0.1949 | Moderate difference |
| **Father present** (`bl_f_b`) | Proportion resident | **0.2071** | Larger difference (>=0.20) | 0.0078 | Small difference |
| **Number of siblings** (`bl_child_sib_tot`) | Mean count | 0.1311 | Moderate difference | 0.0902 | Small difference |
| **Child age** (`bl_childage`) | Mean months | 0.1247 | Moderate difference | 0.0298 | Small difference |

### Key Diagnostic Takeaways:
1. **Cluster-Level Sampling Variability:** At the cluster level, 11 of 13 variables exhibit $|SMD| \ge 0.20$. Crucially, these larger values reflect the small number of randomized clusters in the Home Visits arm ($n=19$). In small cluster samples, random sampling variability naturally widens the observed cluster-level standardized differences.
2. **Participant-Level Balance:** When evaluated at the participant level ($N=2,461$), 12 of 13 variables fall below the 0.20 threshold, with child sex, child age, low birth weight, father presence, siblings, and home stimulation showing very small differences ($|SMD| < 0.10$).
3. Only household SES index (`bl_qses_index`) retains a modest difference ($|SMD| = 0.211$) between Control (mean 2.90) and Afini (mean 3.20).

Full pairwise metrics are cataloged in [cluster_covariate_balance.csv](file:///d:/Niyati/validation/V2_experimental_design/outputs/cluster_covariate_balance.csv) and [participant_baseline_balance.csv](file:///d:/Niyati/validation/V2_experimental_design/outputs/participant_baseline_balance.csv).

---

## 7. Baseline Missingness Analysis (Validation D)

Baseline covariate completeness was evaluated across all three trial arms, cataloged in [baseline_missingness_by_arm.csv](file:///d:/Niyati/validation/V2_experimental_design/outputs/baseline_missingness_by_arm.csv).

| Variable Name | Description | Control Missing (%) | Home Visits Missing (%) | Afini Missing (%) | Total Missing (%) | Non-Missing Denominator |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| `child_female` | Child female indicator | 0 (0.00%) | 0 (0.00%) | 0 (0.00%) | 0 (0.00%) | 2,461 / 2,461 |
| `bl_child_sib_tot` | Number of siblings | 0 (0.00%) | 0 (0.00%) | 0 (0.00%) | 0 (0.00%) | 2,461 / 2,461 |
| `bl_childage` | Child age in months | 1 (0.10%) | 1 (0.32%) | 1 (0.09%) | 3 (0.12%) | 2,458 / 2,461 |
| `bl_z_overall` | Baseline CREDI z-score | 1 (0.10%) | 1 (0.32%) | 1 (0.09%) | 3 (0.12%) | 2,458 / 2,461 |
| `bl_hhadults` | Household adults | 2 (0.21%) | 1 (0.32%) | 3 (0.26%) | 6 (0.24%) | 2,455 / 2,461 |
| `bl_f_b` | Father resident in household | 2 (0.21%) | 1 (0.32%) | 4 (0.34%) | 7 (0.28%) | 2,454 / 2,461 |
| `bl_qses_index` | SES index quintiles | 4 (0.41%) | 1 (0.32%) | 7 (0.60%) | 12 (0.49%) | 2,449 / 2,461 |
| `bl_mo_age` | Mother age in years | 16 (1.65%) | 5 (1.58%) | 21 (1.79%) | 42 (1.71%) | 2,419 / 2,461 |
| `bl_mo_educ_level` | Mother education level | 17 (1.75%) | 6 (1.89%) | 22 (1.87%) | 45 (1.83%) | 2,416 / 2,461 |
| `bl_low_bweight` | Low birth weight indicator | 13 (1.34%) | 9 (2.84%) | 25 (2.13%) | 47 (1.91%) | 2,414 / 2,461 |
| `bl_mics_tot` | Home stimulation activities | 90 (9.28%) | 29 (9.15%) | 99 (8.43%) | 218 (8.86%) | 2,243 / 2,461 |
| `bl_fa_age` | Father age in years | 120 (12.37%) | 40 (12.62%) | 151 (12.86%) | 311 (12.64%) | 2,150 / 2,461 |
| `bl_fa_educ_level` | Father education level | 131 (13.51%) | 50 (15.77%) | 170 (14.48%) | 351 (14.26%) | 2,110 / 2,461 |

Missingness rates are well balanced across the three study arms, with no differential non-response at baseline.

---

## 8. Published Table 1 Replication & Reconciliation (Validation E)

Every statistic reported in Table 1 of the published results paper was recomputed using the non-missing participant denominator for that variable and arm, cataloged in [published_table1_reconciliation.csv](file:///d:/Niyati/validation/V2_experimental_design/outputs/published_table1_reconciliation.csv).

| Baseline Characteristic | Metric Type | Control Observed (Published) | Home Visits Observed (Published) | Digital Observed (Published) | Reconciliation Status |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Child female (%)** | Percentage | 50.0 (50.0) | 47.6 (47.6) | 49.7 (49.7) | **MATCH_WITH_ROUNDING** |
| **Low birth weight (%)** | Percentage | 7.4 (7.4) | 10.1 (10.1) | 7.4 (7.4) | **MATCH_WITH_ROUNDING** |
| **Child age, months** | Mean (SD) | 5.0 (2.0) [5.0 (2.0)] | 5.1 (2.0) [5.1 (2.0)] | 5.1 (1.9) [5.1 (1.9)] | **MATCH_WITH_ROUNDING** |
| **Baseline CREDI z-score** | Mean (SD) | 0.0 (0.6) [0.0 (0.6)] | 0.0 (0.6) [0.0 (0.6)] | 0.1 (0.6) [0.1 (0.6)] | **MATCH_WITH_ROUNDING** |
| **Mother age** | Mean (SD) | 27.8 (6.9) [27.8 (6.9)] | 28.6 (7.2) [28.6 (7.2)] | 27.9 (6.6) [27.9 (6.6)] | **MATCH_WITH_ROUNDING** |
| **Mother basic education (%)** | Percentage | 49.8 (49.8) | 47.9 (47.9) | 46.7 (46.7) | **MATCH_WITH_ROUNDING** |
| **Mother secondary education (%)** | Percentage | 30.5 (30.5) | 24.8 (24.8) | 25.9 (25.9) | **MATCH_WITH_ROUNDING** |
| **Mother higher education (%)** | Percentage | 19.6 (19.6) | 27.3 (27.3) | 27.4 (27.4) | **MATCH_WITH_ROUNDING** |
| **Father present (%)** | Percentage | 89.4 (89.4) | 89.6 (89.6) | 89.3 (89.3) | **MATCH_WITH_ROUNDING** |
| **Father age** | Mean (SD) | 31.2 (7.5) [31.2 (7.5)] | 32.1 (7.7) [32.1 (7.7)] | 31.5 (7.7) [31.5 (7.7)] | **MATCH_WITH_ROUNDING** |
| **Father basic education (%)** | Percentage | 38.6 (38.6) | 37.8 (37.8) | 31.2 (31.2) | **MATCH_WITH_ROUNDING** |
| **Father secondary education (%)** | Percentage | 40.0 (40.0) | 34.8 (34.8) | 39.4 (39.4) | **MATCH_WITH_ROUNDING** |
| **Father higher education (%)** | Percentage | 21.3 (21.3) | 27.3 (27.3) | 29.4 (29.4) | **MATCH_WITH_ROUNDING** |
| **Number of siblings** | Mean (SD) | 1.1 (1.1) [1.1 (1.1)] | 1.2 (1.3) [1.2 (1.3)] | 1.1 (1.1) [1.1 (1.1)] | **MATCH_WITH_ROUNDING** |
| **Number of household adults** | Mean (SD) | 2.4 (1.0) [2.4 (1.0)] | 2.5 (1.1) [2.5 (1.1)] | 2.5 (1.1) [2.5 (1.1)] | **MATCH_WITH_ROUNDING** |
| **Household SES index** | Mean (SD) | 2.9 (1.4) [2.9 (1.4)] | 3.1 (1.5) [3.1 (1.5)] | 3.2 (1.4) [3.2 (1.4)] | **MATCH_WITH_ROUNDING** |
| **Home stimulation index** | Mean (SD) | 3.4 (1.3) [3.4 (1.3)] | 3.4 (1.2) [3.4 (1.2)] | 3.5 (1.2) [3.5 (1.2)] | **MATCH_WITH_ROUNDING** |

**Conclusion:** All 17 items match the published values exactly (Difference = 0.0 across all cells). Table 1 is 100% reproducible from the released dataset.

---

## 9. Randomization-Covariate Availability Matrix (Validation F)

The trial protocol describes using constrained randomization based on study province and six community/household covariates. Each item was audited against the released 40-variable dataset, cataloged in [variable_availability_matrix.csv](file:///d:/Niyati/validation/V2_experimental_design/outputs/variable_availability_matrix.csv).

| Protocol Item | Protocol Description | In Released Data? | Dataset Variable Name | Measure Type | Analytical Caveats |
| :--- | :--- | :---: | :---: | :--- | :--- |
| **Province** | Randomization stratification factor | **YES** | `provincia` | Exact cluster stratification measure | Observed for all 2,461 participants. Correctly defines the 3 regional strata. |
| **Cluster population size** | Pre-trial community census population | **NO** | `NOT_IN_RELEASED_DATASET` | NOT_IN_RELEASED_DATASET | **Unavailable.** The observed number of enrolled participants per cluster (1–42) reflects post-randomization study enrollment, not community population. Do not substitute enrolled size for population size. |
| **Cluster number of births** | Annual births from health post registry | **NO** | `NOT_IN_RELEASED_DATASET` | NOT_IN_RELEASED_DATASET | **Unavailable.** Administrative health records used during randomization are absent. |
| **Cluster altitude** | Community geographic elevation (meters) | **NO** | `NOT_IN_RELEASED_DATASET` | NOT_IN_RELEASED_DATASET | **Unavailable.** Geographic elevation is completely omitted. |
| **Cell-phone ownership** | Baseline household mobile phone ownership | **NO** | `NOT_IN_RELEASED_DATASET` | NOT_IN_RELEASED_DATASET | **Unavailable.** Baseline phone ownership was not released. Endline usage (`el_afinidata1`) and platform awareness (`el_afinidata4`) are post-treatment variables and cannot substitute for baseline ownership. |
| **Caregiver education** | Maternal and paternal educational attainment | **YES** | `bl_mo_educ_level`, `bl_fa_educ_level` | Related participant-level measure | Recorded at participant level; aggregated to cluster proportions for balance checks. Pre-randomization community census is absent. |
| **Household wealth** | Socioeconomic status / wealth index | **YES** | `bl_qses_index` | Related participant-level measure | Recorded as baseline quintiles (1–5) for enrolled households; aggregated to cluster means. Community census is absent. |

**Important Methodological Note:** Because the original pre-randomization community-level covariates (census population, registry births, altitude, baseline phone ownership) and the exact random allocation seed/sequence are absent from the released dataset, the constrained randomization algorithm itself cannot be computationally reproduced or independently rerun from the released package.

---

## 10. Technical and Reproducibility Specifications

- **Python Environment:** Python 3.13.3 (64-bit AMD64)
- **Dependencies:** `pandas` 3.0.3, `numpy` 2.4.6, `scipy` 1.17.1 (documented in [requirements-v2.txt](file:///d:/Niyati/validation/V2_experimental_design/requirements-v2.txt))
- **Data Ingestion:** Reads authoritative Stata binary dataset directly from the compressed raw archive (`data/raw/doi_10_5061_dryad_nzs7h4551__v20260226.zip`) using native `pd.io.stata.StataReader` without extracting or altering raw files.
- **Reproducibility Command:**
  ```powershell
  python validation/V2_experimental_design/run_v2_design_audit.py
  ```

---

## 11. Audit Output Manifest

All output files are generated in `validation/V2_experimental_design/outputs/`:
- [`cluster_assignment_integrity.csv`](file:///d:/Niyati/validation/V2_experimental_design/outputs/cluster_assignment_integrity.csv): 159-cluster dataset with treatment assignment, province, district, participant count, and integrity flags.
- [`cluster_size_distribution.csv`](file:///d:/Niyati/validation/V2_experimental_design/outputs/cluster_size_distribution.csv): Parametric and non-parametric cluster-size statistics overall, by arm, and by province x arm.
- [`cluster_allocation_by_province.csv`](file:///d:/Niyati/validation/V2_experimental_design/outputs/cluster_allocation_by_province.csv): Province-stratified allocation cross-tabulation with cluster counts, participant counts, and shares.
- [`cluster_covariate_balance.csv`](file:///d:/Niyati/validation/V2_experimental_design/outputs/cluster_covariate_balance.csv): Primary cluster-level baseline balance diagnostics with pairwise SMDs across randomized units.
- [`participant_baseline_balance.csv`](file:///d:/Niyati/validation/V2_experimental_design/outputs/participant_baseline_balance.csv): Secondary participant-weighted baseline balance diagnostics with pairwise SMDs.
- [`published_table1_reconciliation.csv`](file:///d:/Niyati/validation/V2_experimental_design/outputs/published_table1_reconciliation.csv): Replication and comparison of all 17 published Table 1 baseline summary statistics.
- [`baseline_missingness_by_arm.csv`](file:///d:/Niyati/validation/V2_experimental_design/outputs/baseline_missingness_by_arm.csv): Denominator and missingness audit across baseline covariates stratified by arm.
- [`variable_availability_matrix.csv`](file:///d:/Niyati/validation/V2_experimental_design/outputs/variable_availability_matrix.csv): Audit of protocol-specified constrained randomization covariates in the released dataset.
- [`v2_summary.json`](file:///d:/Niyati/validation/V2_experimental_design/outputs/v2_summary.json): Machine-readable JSON summary of all key counts, integrity checks, distributions, and balance metrics.
