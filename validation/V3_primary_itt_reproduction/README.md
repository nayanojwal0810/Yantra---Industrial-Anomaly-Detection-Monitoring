# Task V3: Primary Outcome & ITT Results Reproduction

**Project:** Niyati  
**Study Title:** Digital support systems to improve child development in Peru: A cluster-randomized controlled open label trial  
**Dataset Source:** Dryad ([doi:10.5061/dryad.nzs7h4551](https://doi.org/10.5061/dryad.nzs7h4551))  
**Working Branch:** `project2/urja-validation`  
**Execution Date:** 2026-10-31  

---

## 1. Executive Summary

This report documents the independent forensic audit, outcome re-derivation, and econometric replication of the primary intention-to-treat (ITT) models published in **Table 2** of the results paper:
> *Fink et al., "Digital support systems to improve child development in Peru: A cluster-randomized controlled open label trial."*

Using only the authoritative raw data archive (`doi_10_5061_dryad_nzs7h4551__v20260226.zip`) and the authors' original Stata replication script (`Trial_Analysis_Replication_File_26Feb2026.do`), both the **unadjusted** and **adjusted** ITT models for the primary standardized Global Scale for Early Development (GSED) outcome were independently reconstructed in Python.

### Core Replication Verdict:
1. **Primary Outcome Re-derivation:** The primary outcome `gsed_Z` was reconstructed from raw child age (`el_gsed_age`) and raw GSED D-score (`el_gsed_dscore`) using exact 10-day age banding and sample standardization ($ddof=1$). The derivation yields exactly **2,149 valid outcome observations** and **312 exclusions** (307 missing raw scores + 5 singleton age-band cases), replicating Task V1/V2 counts with zero discrepancy.
2. **Unadjusted Table 2 Model:** Successfully replicated at published display precision (`MATCH_AT_PUBLISHED_PRECISION`). Both point estimates and 95% confidence intervals match published values to the exact two-decimal precision.
3. **Adjusted Table 2 Model:** Successfully replicated at published display precision (`MATCH_AT_PUBLISHED_PRECISION`) using chained equations multiple imputation (MICE) and Rubin's combination rules across $M=50$ imputations. Both point estimates and 95% confidence intervals match published values to the exact two-decimal precision.
4. **Preserved Discrepancy:** The aggregate 20-case gap between the published Table 2 note (reporting 332 exclusions) and the actual data/code (312 exclusions) is formally preserved as **UNRESOLVED**, without forcing assumptions or altering data.

### Table 2 Primary ITT Replication Summary:

| Model Specification | Intervention Arm | Published Coef | Python Coef (Raw) | Python Coef (Display) | Published 95% CI | Python 95% CI (Display) | Difference | Replication Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Unadjusted Model** | Home Visits vs. Control | **0.17** | 0.1669 | **0.17** | **0.04 to 0.30** | **0.04 to 0.30** | 0.00 | `MATCH_AT_PUBLISHED_PRECISION` |
| | Digital (Afini) vs. Control | **0.14** | 0.1394 | **0.14** | **0.05 to 0.23** | **0.05 to 0.23** | 0.00 | `MATCH_AT_PUBLISHED_PRECISION` |
| **Adjusted Model (MI)**| Home Visits vs. Control | **0.17** | 0.1654 | **0.17** | **0.03 to 0.30** | **0.03 to 0.30** | 0.00 | `MATCH_AT_PUBLISHED_PRECISION` |
| | Digital (Afini) vs. Control | **0.11** | 0.1056 | **0.11** | **0.02 to 0.19** | **0.02 to 0.19** | 0.00 | `MATCH_AT_PUBLISHED_PRECISION` |

*Notes:* Estimation sample is $N = 2,149$ participants across 159 clusters for all models. Standard errors are clustered at the community level (`cluster`). Degrees of freedom: $df = G - 1 = 158$ for unadjusted OLS; Barnard-Rubin adjusted $df \approx 155.9$ for multiple imputation.

---

## 2. Forensic Review of the Original Stata Specification (Step A)

The authors' primary analytical code resides in `Trial_Analysis_Replication_File_26Feb2026.do` inside the root of the raw ZIP package. A complete forensic audit was conducted, cataloged in [original_model_specification_audit.csv](file:///d:/Niyati/validation/V3_primary_itt_reproduction/outputs/original_model_specification_audit.csv).

### Exact Stata Commands & Line References:

1. **Primary Outcome Derivation (Lines 233–236):**
   ```stata
   gen gsed_agemonths = int(el_gsed_age/10)
   bysort gsed_agemonths: egen gsed_mean = mean(el_gsed_dscore)
   bysort gsed_agemonths: egen gsed_sd = sd(el_gsed_dscore)
   gen gsed_Z = (el_gsed_dscore-gsed_mean)/gsed_sd
   ```
2. **Treatment Indicators & Reference Group (Lines 26–27):**
   ```stata
   gen hv = arm_itt==2
   gen afini = arm_itt==3
   ```
   Control (`arm_itt == 1`) is the omitted reference arm, captured by the regression constant.
3. **Unadjusted Primary ITT Model (Lines 239–240):**
   ```stata
   reg gsed_Z hv afini, cluster(cluster)
   outreg2 using "Tables/table_impact_v2", replace excel ctitle(GSED - unadj) stats(coef ci) dec(2)
   ```
4. **Intraclass Correlation Diagnostic (Lines 244–245):**
   ```stata
   mixed gsed_Z || cluster:
   estat icc
   ```
5. **Pre-Imputation Covariate Cleaning & Recoding (Lines 391–402):**
   ```stata
   global covariates bl_childage child_female bl_low_bweight bl_z_overall bl_mo_age mom_sec mom_higher bl_f_b dad_sec dad_higher bl_fa_age bl_mics_tot bl_child_sib_tot bl_hhadults bl_qses_index
   replace bl_f_b = 0 if bl_f_b ==. & bl_fa_age ==.
   ```
   - *Household structure* is represented by **two distinct variables**: `bl_child_sib_tot` (total siblings) and `bl_hhadults` (adults in household).
   - Father presence `bl_f_b` is deterministically recoded to 0 when missing and father age is missing.
   - Mother education is split into `mom_sec` (completed secondary, `bl_mo_educ_level == 4`) and `mom_higher` (tertiary/higher, `bl_mo_educ_level == 5`), with incomplete secondary or less (`< 4`) as reference.
   - Father education is split into `dad_sec` (`bl_fa_educ_level == 4`) and `dad_higher` (`bl_fa_educ_level == 5`), with `< 4` as reference.
6. **Multiple Imputation Specification (Lines 404–420):**
   ```stata
   mi set wide
   drop mom_sec mom_higher dad_sec dad_higher
   mi register imputed bl_childage bl_low_bweight bl_z_overall bl_mo_age bl_mics_tot bl_hhadults bl_qses_index bl_fa_age bl_fa_educ_level bl_mo_educ_level
   mi register regular bl_child_sib_tot cluster child_female bl_f_b
   mi impute chained (regress) bl_childage bl_z_overall bl_mo_age bl_hhadults bl_fa_age (ologit) bl_mics_tot bl_qses_index bl_fa_educ_level bl_mo_educ_level (logit) bl_low_bweight = bl_child_sib_tot cluster child_female bl_f_b , add(250)
   ```
7. **Passive Education Indicator Derivation (Lines 422–427):**
   ```stata
   mi passive: gen mom_sec = bl_mo_educ_level==4
   mi passive: gen mom_higher = bl_mo_educ_level==5
   mi passive: gen dad_sec = bl_fa_educ_level==4
   mi passive: gen dad_higher = bl_fa_educ_level==5
   ```
8. **Adjusted Primary ITT Model (Lines 431–432):**
   ```stata
   mi estimate, post: reg gsed_Z hv afini $covariates, cluster(cluster)
   outreg2 using "Tables/table_impact_v2", append excel ctitle(GSED adjusted) stats(coef ci) dec(2)
   ```

### Key Forensic Findings:
- **Missing Random Seed:** Crucially, `Trial_Analysis_Replication_File_26Feb2026.do` **does not contain a `set seed` statement** before calling `mi impute chained`. Stata's chained imputation therefore relied on the default initial pseudo-random generator state.
- **Imputation Predictors:** Treatment arms (`hv`, `afini`) and primary outcome (`gsed_Z`) were **not included** in the imputation right-hand-side equations. Only `bl_child_sib_tot`, `cluster`, `child_female`, and `bl_f_b` were used as conditioning predictors.
- **Cluster Variable in Imputation:** The cluster identifier (`cluster`, 1 to 164) was included as a single continuous linear predictor, rather than as cluster fixed effects or multilevel random intercepts.

---

## 3. Primary Outcome Re-derivation (`gsed_Z`) (Step B)

The primary trial outcome is the age-standardized Global Scale for Early Development (GSED) D-score (`gsed_Z`).

### Mathematical Derivation:
1. **Age Banding:** Child age at endline (`el_gsed_age`, measured in completed days, ranging from 739 to 1,468 days) is divided by 10 and truncated towards zero:
   $$\text{gsed\_agemonths} = \left\lfloor \frac{\text{el\_gsed\_age}}{10} \right\rfloor$$
   Since age in days is strictly positive, truncation and mathematical floor are identical. This creates 58 discrete 10-day age bands.
2. **Age-Band Standardization:** Within each age band $b$, the sample mean $\bar{Y}_b$ and sample standard deviation $s_b$ ($ddof=1$) of raw GSED D-scores (`el_gsed_dscore`) are computed across all participating children:
   $$\text{gsed\_Z}_{ib} = \frac{\text{el\_gsed\_dscore}_{ib} - \bar{Y}_b}{s_b}$$
3. **Singleton Exclusions:** In 5 age bands (bands 73, 126, 131, 137, and 146), exactly $n=1$ child is observed. Because sample standard deviation with degrees of freedom $n - 1 = 0$ is mathematically undefined, both Stata and Python assign `NaN`. These 5 children are excluded from the standardized outcome sample.

### Outcome Reconciliation:

Cataloged in [primary_outcome_reconciliation.csv](file:///d:/Niyati/validation/V3_primary_itt_reproduction/outputs/primary_outcome_reconciliation.csv):

| Metric | V1 Audited Value | V3 Re-derived Value | Difference | Status | Methodological Interpretation |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Enrolled participants** | 2,461 | 2,461 | 0 | `MATCH` | Total observations in released dataset |
| **Recorded raw GSED scores** | 2,154 | 2,154 | 0 | `MATCH` | Participants with valid `el_gsed_dscore` |
| **Missing raw GSED scores** | 307 | 307 | 0 | `MATCH` | Endline GSED not administered or recorded |
| **Singleton age-band drops** | 5 | 5 | 0 | `MATCH` | 10-day age bands with $n=1$ (undefined sample SD) |
| **Valid derived GSED scores** | **2,149** | **2,149** | **0** | `MATCH` | **Primary estimation sample matching Table 2** |
| **Total recreated exclusions** | **312** | **312** | **0** | `MATCH` | Sum of missing raw (307) and singletons (5) |

---

## 4. Intention-to-Treat (ITT) Estimand & Allocation Integrity (Step C)

The primary analysis adheres strictly to intention-to-treat (ITT):
- **Reference Group:** Control arm (`arm_itt == 1`).
- **Home Visits Indicator:** `hv = 1` if `arm_itt == 2` else 0.
- **Digital / Afini Indicator:** `afini = 1` if `arm_itt == 3` else 0.
- **Estimands:** The parameters $\beta_{\text{HV}}$ and $\beta_{\text{Afini}}$ represent the average causal effect of assigned access to each intervention compared to Control in units of standardized GSED Z-score.

### Exposure vs. Assignment Distinction:
As established in Task V1 (Section 7) and Task V2 (Section 3), four Control-assigned participants recorded positive digital platform tracking (`weeks_active > 0`, `program_time > 0`). In accordance with ITT principles:
- No participants were dropped or reclassified due to exposure crossover.
- Analysis is conducted strictly on originally assigned arms (`arm_itt`).
- No direct statistical test between Home Visits and Afini is implied by the separate treatment coefficients.

---

## 5. Analysis Sample & Cluster Distribution

The analysis sample of $N = 2,149$ participants spans all 159 populated clusters, cataloged in [analysis_sample_reconciliation.csv](file:///d:/Niyati/validation/V3_primary_itt_reproduction/outputs/analysis_sample_reconciliation.csv):

| Treatment Arm | Enrolled Participants | Recorded Raw GSED | Missing Raw GSED | Singleton Drops | Valid Derived GSED (`gsed_Z`) | Analysis Share (%) | Total Excluded | Contributing Clusters | Total Clusters | Cluster Retention (%) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Control (1)** | 970 | 864 | 106 | 0 | **864** | 40.20% | 106 | 68 | 68 | 100.0% |
| **Home visits (2)**| 317 | 299 | 18 | 2 | **297** | 13.82% | 20 | 19 | 19 | 100.0% |
| **Afini (3)** | 1,174 | 991 | 183 | 3 | **988** | 45.97% | 186 | 72 | 72 | 100.0% |
| **Total Trial** | **2,461** | **2,154** | **307** | **5** | **2,149** | **100.00%** | **312** | **159** | **159** | **100.0%** |

*Key Takeaway:* Outcome attrition was low across all study arms (~10.9% in Control, ~6.3% in Home visits, ~15.8% in Afini). Every single populated cluster (159/159) retained at least one child with a valid primary outcome.

---

## 6. Unadjusted ITT Model Reproduction (Step D)

The unadjusted ITT model estimates:
$$\text{gsed\_Z}_{ij} = \beta_0 + \beta_{\text{HV}} \cdot \text{hv}_{ij} + \beta_{\text{Afini}} \cdot \text{afini}_{ij} + \varepsilon_{ij}$$

with standard errors adjusted for clustering at the community level (`cluster`).

### Estimation Details:
- **Sample Size:** $N = 2,149$ children.
- **Clusters:** $G = 159$ communities.
- **Variance Estimator:** Cluster-robust CRV1 covariance.
- **Finite-Cluster Degrees of Freedom:** Stata applies $df = G - 1 = 159 - 1 = 158$. Critical value $t_{0.975, 158} = 1.9751$.
- **R-squared:** $R^2 = 0.0053$; residual standard deviation $s = 0.9856$.

### Unadjusted Model Estimates:

| Coefficient | Point Estimate (Raw) | Display Coef | Cluster-Robust SE | $t$-statistic | $p$-value | 95% Confidence Interval | Published Table 2 | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Intercept ($\beta_0$)** | -0.0872 | -0.09 | 0.0329 | -2.649 | 0.0089 | [-0.1523, -0.0222] | — | Reference mean |
| **Home Visits ($\beta_{\text{HV}}$)** | **0.1669** | **0.17** | 0.0662 | 2.520 | 0.0127 | **[0.0361, 0.2977] $\rightarrow$ 0.04 to 0.30** | **0.17 (0.04 to 0.30)** | `MATCH_AT_PUBLISHED_PRECISION` |
| **Digital / Afini ($\beta_{\text{Afini}}$)**| **0.1394** | **0.14** | 0.0450 | 3.099 | 0.0023 | **[0.0506, 0.2283] $\rightarrow$ 0.05 to 0.23** | **0.14 (0.05 to 0.23)** | `MATCH_AT_PUBLISHED_PRECISION` |

### Intraclass Correlation (ICC):
Matching Stata lines 244–245 (`mixed gsed_Z || cluster:`), a null linear mixed-effects model with random intercepts was estimated:
- Cluster variance: $\hat{\sigma}_u^2 = 0.03154$
- Residual variance: $\hat{\sigma}_e^2 = 0.95336$
- **Intraclass Correlation (ICC):** $\text{ICC} = \frac{0.03154}{0.03154 + 0.95336} = \mathbf{0.03202}$ (~3.2%).
- In the conditional model (`mixed gsed_Z hv afini || cluster:`), ICC reduces slightly to **0.02830** (~2.8%).

---

## 7. Adjusted ITT Model Reproduction & Multiple Imputation (Step E)

The adjusted ITT model controls for the 15 protocol baseline covariates:
$$\text{gsed\_Z}_{ij} = \beta_0 + \beta_{\text{HV}} \cdot \text{hv}_{ij} + \beta_{\text{Afini}} \cdot \text{afini}_{ij} + \sum_{k=1}^{15} \gamma_k X_{kij} + \varepsilon_{ij}$$

### Why Multiple Imputation is Mandatory:
A complete-case regression (dropping any child with missing baseline covariates) discards **521 participants**, reducing the sample to $N = 1,628$ and losing 7 entire clusters ($G = 152$). Crucially, complete-case analysis produces severe collinearity between father presence (`bl_f_b`) and father age (`bl_fa_age`). Multiple imputation preserves the full $N = 2,149$ sample across all 159 clusters.

### Multiple Imputation Implementation:
- **Algorithm:** Multivariate Imputation by Chained Equations (MICE) using `IterativeImputer` with `BayesianRidge` drawing from the posterior distribution.
- **Imputed Covariates (10):** `bl_childage` (3 missing), `bl_low_bweight` (47 missing), `bl_z_overall` (3 missing), `bl_mo_age` (42 missing), `bl_mics_tot` (218 missing), `bl_hhadults` (6 missing), `bl_qses_index` (12 missing), `bl_fa_age` (311 missing), `bl_fa_educ_level` (351 missing), `bl_mo_educ_level` (45 missing).
- **Conditioning Predictors (4):** `bl_child_sib_tot`, `cluster`, `child_female`, `bl_f_b`.
- **Passive Transformations:** Indicators `mom_sec`, `mom_higher`, `dad_sec`, and `dad_higher` were generated post-imputation matching Stata lines 423–427.
- **Replications & Seed:** $M = 50$ imputations with random seed `20260226`.
- **Pooling (Rubin's Rules):** Parameter estimates $\bar{Q}$ and variance $T = \bar{U} + (1 + 1/M)B$ combined via Rubin's rules; small-sample degrees of freedom derived via Barnard-Rubin (1999) adjusted degrees of freedom ($\nu_{\text{adj}} \approx 155.9$).

Diagnostic metrics are detailed in [imputation_diagnostics.csv](file:///d:/Niyati/validation/V3_primary_itt_reproduction/outputs/imputation_diagnostics.csv).

### Adjusted Model Estimates:

| Coefficient | Point Estimate (Raw) | Display Coef | Pooled SE | Adjusted $df$ | $p$-value | 95% Confidence Interval | Published Table 2 | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Home Visits ($\beta_{\text{HV}}$)** | **0.1654** | **0.17** | 0.0691 | 155.9 | 0.0179 | **[0.0289, 0.3020] $\rightarrow$ 0.03 to 0.30** | **0.17 (0.03 to 0.30)** | `MATCH_AT_PUBLISHED_PRECISION` |
| **Digital / Afini ($\beta_{\text{Afini}}$)**| **0.1056** | **0.11** | 0.0446 | 155.9 | 0.0192 | **[0.0174, 0.1937] $\rightarrow$ 0.02 to 0.19** | **0.11 (0.02 to 0.19)** | `MATCH_AT_PUBLISHED_PRECISION` |

---

## 8. Reconciliation with Published Table 2 (Step F)

A direct item-by-item comparison against Table 2 of the published paper is cataloged in [itt_results_table2_reproduction.csv](file:///d:/Niyati/validation/V3_primary_itt_reproduction/outputs/itt_results_table2_reproduction.csv):

| Model | Treatment Comparison | Published Coef | Python Coef | Published 95% CI | Python 95% CI | Coef Diff | CI Diff | Replication Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Unadjusted** | Home Visits vs. Control | 0.17 | 0.17 | 0.04 to 0.30 | 0.04 to 0.30 | 0.00 | 0.00 | `MATCH_AT_PUBLISHED_PRECISION` |
| **Unadjusted** | Digital vs. Control | 0.14 | 0.14 | 0.05 to 0.23 | 0.05 to 0.23 | 0.00 | 0.00 | `MATCH_AT_PUBLISHED_PRECISION` |
| **Adjusted** | Home Visits vs. Control | 0.17 | 0.17 | 0.03 to 0.30 | 0.03 to 0.30 | 0.00 | 0.00 | `MATCH_AT_PUBLISHED_PRECISION` |
| **Adjusted** | Digital vs. Control | 0.11 | 0.11 | 0.02 to 0.19 | 0.02 to 0.19 | 0.00 | 0.00 | `MATCH_AT_PUBLISHED_PRECISION` |

**Verdict:** 4 out of 4 estimates and 4 out of 4 confidence intervals achieve `MATCH_AT_PUBLISHED_PRECISION`.

---

## 9. Sample Size Discrepancy Preservation (Step G)

In accordance with forensic accounting standards and Task V1/V2 findings:
- **Released Data & Stata Code:** Exactly 2,149 valid standardized GSED outcomes are observed, resulting from 312 exclusions (307 missing raw scores + 5 singleton age-band drops).
- **Published Table 2 Body:** Reports $N = 2,149$ children and 159 clusters.
- **Published Table 2 Footnote:** States: *"A total of 332 children were excluded due to missing outcome data."*
- **Discrepancy:** $332 - 312 = \mathbf{20}$ exclusions.

**Preservation Rule:** This 20-observation discrepancy is preserved as **UNRESOLVED**. No artificial records were added or removed to reconcile the footnote arithmetic. The empirical models reproduce the actual published regression estimates and sample size ($N = 2,149$).

---

## 10. Methodological Nuances & Limitations

1. **Absence of Random Seed in Author Code:** Because the original Stata do-file omitted a random seed before `mi impute chained`, an exact bit-for-bit replication of Stata's imputed values across $M=250$ chains is not possible. However, the Python MICE implementation demonstrates that point estimates and standard errors are stable to two decimal places, fully matching published numbers.
2. **Conditional Model Families:** Stata used ordered logit (`ologit`) for ordinal scales and binary logit (`logit`) for low birth weight. The Python implementation uses Bayesian ridge regression for conditional draws with discrete rounding/thresholding. The resulting pooled coefficients demonstrate that findings are robust to the specific chained-equation family.
3. **Finite-Sample Degrees of Freedom:** Replicating the published confidence intervals requires applying cluster-robust degrees of freedom ($df = 158$ for unadjusted OLS, and Barnard-Rubin adjusted $df \approx 155.9$ for multiple imputation). Assuming large-sample standard normal critical values ($z = 1.96$) yields slightly narrower confidence intervals.

---

## 11. Reproducibility & Output Manifest

### Python Environment & Dependencies:
- Python 3.13.3
- `pandas` 3.0.3, `numpy` 2.4.6, `scipy` 1.17.1, `statsmodels` 0.15.0, `scikit-learn` 1.9.0
- Documented in [requirements-v3.txt](file:///d:/Niyati/validation/V3_primary_itt_reproduction/requirements-v3.txt).

### Reproducibility Command:
```powershell
python validation/V3_primary_itt_reproduction/run_v3_itt_replication.py
```

### Generated Output Files:
All files are located in `validation/V3_primary_itt_reproduction/outputs/`:
- [`original_model_specification_audit.csv`](file:///d:/Niyati/validation/V3_primary_itt_reproduction/outputs/original_model_specification_audit.csv): Forensic audit of Stata commands, line numbers, covariates, and inference settings.
- [`primary_outcome_reconciliation.csv`](file:///d:/Niyati/validation/V3_primary_itt_reproduction/outputs/primary_outcome_reconciliation.csv): Primary GSED Z-score derivation reconciliation against V1 audited counts.
- [`analysis_sample_reconciliation.csv`](file:///d:/Niyati/validation/V3_primary_itt_reproduction/outputs/analysis_sample_reconciliation.csv): Sample size and cluster retention counts by arm.
- [`itt_results_table2_reproduction.csv`](file:///d:/Niyati/validation/V3_primary_itt_reproduction/outputs/itt_results_table2_reproduction.csv): Direct comparison of unadjusted and adjusted ITT estimates against published Table 2.
- [`imputation_diagnostics.csv`](file:///d:/Niyati/validation/V3_primary_itt_reproduction/outputs/imputation_diagnostics.csv): Multiple imputation diagnostics and Rubin combination variance components.
- [`model_diagnostics.csv`](file:///d:/Niyati/validation/V3_primary_itt_reproduction/outputs/model_diagnostics.csv): Outcome distribution, residual standard deviation, and intraclass correlation (ICC).
- [`v3_summary.json`](file:///d:/Niyati/validation/V3_primary_itt_reproduction/outputs/v3_summary.json): Complete machine-readable summary of Task V3 results.
