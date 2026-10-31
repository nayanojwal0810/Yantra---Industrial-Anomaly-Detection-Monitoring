# Task V5.2.1: Missing Outcomes, Attrition & Missing-Data Feasibility Audit

**Project:** Niyati  
**Repository:** `nayanojwal0810/Yantra---Industrial-Anomaly-Detection-Monitoring`  
**Branch:** `project2/urja-validation`  
**Directory:** `validation/V5_missingness_attrition_audit/`  
**Dataset Source:** Dryad (`doi:10.5061/dryad.nzs7h4551`)  
**Raw Archive:** `doi_10_5061_dryad_nzs7h4551__v20260226.zip`  
**Authoritative Data File:** `digitalECD_26Feb2026.dta`  
**Original Replication File:** `Trial_Analysis_Replication_File_26Feb2026.do`  

---

## 1. Executive Summary

This audit independently investigates the structure of missing outcomes, endline survey completion, sample exclusions, and missing-data patterns in the Peru Digital Early Childhood Development (ECD) trial. Utilizing the authoritative released dataset ($N = 2,461$ enrolled participants across $K = 159$ populated clusters), we evaluate whether primary outcome missingness is benign or whether it introduces potential selection bias and threats to internal validity.

### Two Distinct Outcome-Availability Definitions:
1. **Primary Attrition Metric: Raw GSED Missingness (`miss_raw_gsed == 1`)**
   - Defined as participants without a valid recorded numerical endline score (`el_gsed_dscore` is missing).
   - Exactly **$307$ participants** ($12.47\%$ of the enrolled cohort) have missing raw GSED scores ($278$ pre-survey non-participants plus $29$ survey-completed participants without a recorded raw GSED score).
   - This constitutes the authoritative, primary outcome non-observation / attrition measure for all attrition models.
2. **Secondary Sensitivity Metric: Standardized Outcome Unavailable (`miss_outcome == 1`)**
   - Defined as participants without a valid standardized developmental outcome (`gsed_Z` is missing).
   - Exactly **$312$ participants** ($12.68\%$ of the enrolled cohort) do not have standardized scores. This encompasses the $307$ raw-GSED missing participants plus **$5$ children dropped due to singleton 10-day age bands** (brackets with $n=1$ where within-sample standard deviation cannot be calculated in Stata).
   - These $5$ singleton cases are explicitly classified as technical outcome-construction exclusions, not participant attrition.

### Key Audit Findings:
1. **Sample Flow & Discrepancy Resolution:**
   - **The 29-case gap is RESOLVED WITH DIRECT EVIDENCE:** Exactly $2,183$ caregiver-child dyads completed the endline household survey (`final_status == 1`). Of these, exactly $29$ participants have `final_status == 1` but no recorded raw GSED score (`el_gsed_dscore` is missing), leaving exactly $2,154$ recorded raw GSED scores ($2,183 - 29 = 2,154$). The released dataset establishes that the score is absent; it does not establish whether the assessment was not administered or was administered but not recorded.
   - **The 20-case gap remains UNRESOLVED WITH AVAILABLE SOURCES:** Released data and local replication code account for exactly $312$ exclusions ($307$ missing raw GSED scores plus $5$ singleton 10-day age-band technical drops), yielding the exact primary analysis sample of $N = 2,149$ ($2,461 - 312 = 2,149$). The footnote in published Table 2 states that $332$ children were excluded due to missing outcome data. If $332$ had been excluded, the analysis sample would be $2,129$, directly contradicting Table 2's reported $N = 2,149$. The cause of the $20$-participant difference ($332 - 312 = 20$) is unknown with available sources.
2. **Marked Differential Attrition Across Treatment Arms ($p < 0.001$):**
   - **Afini (Digital):** Suffered the highest raw GSED missingness at **$15.59\%$** ($183 / 1,174$).
   - **Control:** Intermediate raw GSED missingness at **$10.93\%$** ($106 / 970$).
   - **Home Visits:** Lowest raw GSED missingness at **$5.68\%$** ($18 / 317$).
   - In cluster-robust linear probability models (CR1), Digital raw missingness was $+4.66$ percentage points higher than Control ($SE = 1.69\%, p_{\text{LPM}} = 0.0058$; conservative $df=67$, $p_{\text{cons}} = 0.0075$; Odds Ratio $= 1.505$ [95% CI: $1.118, 2.026$], $p_{\text{Logit}} = 0.0070$).
   - Home Visits raw missingness was $-5.25$ percentage points lower than Control ($SE = 1.65\%, p_{\text{LPM}} = 0.0015$; conservative $df=18$, $p_{\text{cons}} = 0.0052$; Odds Ratio $= 0.491$ [95% CI: $0.301, 0.799$], $p_{\text{Logit}} = 0.0042$).
   - The direct contrast between active modalities is substantial: Home Visits achieved a **$9.91$ percentage point lower raw missingness rate** than Digital ($5.68\%$ vs $15.59\%$, $SE = 1.69\%, z = -5.876, p_{\text{LPM}} = 4.19 \times 10^{-9}$; conservative $df=18$, $p_{\text{cons}} = 1.45 \times 10^{-5}$), corresponding to a $67.4\%$ reduction in the odds of missingness (Odds Ratio $= 0.326$ [95% CI: $0.205, 0.518$], $p_{\text{Logit}} = 2.14 \times 10^{-6}$).
3. **Evidence Against Missing Completely at Random (MCAR):**
   - Observed associations between outcome missingness, treatment assignment, and baseline characteristics provide strong evidence against MCAR.
   - In multivariable models ($N = 2,373$ complete baseline cases), raw GSED missingness is significantly predicted by:
     - **Younger maternal age:** LPM coef $= -0.0051$ ($p_{\text{LPM}} = 3.31 \times 10^{-6}$); AOR $= 0.9493$ [95% CI: $0.9280, 0.9711$] ($p_{\text{Logit}} = 6.98 \times 10^{-6}$).
     - **Low birth weight:** LPM coef $= +0.0585$ ($p_{\text{LPM}} = 0.0386$); AOR $= 1.5957$ [95% CI: $1.0731, 2.3729$] ($p_{\text{Logit}} = 0.0210$).
     - **Fewer household adults:** LPM coef $= -0.0151$ ($p_{\text{LPM}} = 0.0065$); AOR $= 0.8555$ [95% CI: $0.7568, 0.9671$] ($p_{\text{Logit}} = 0.0126$).
     - **Treatment assignment:** Home Visits significantly reduces missingness (LPM coef $= -0.0548$, $p_{\text{LPM}} = 0.0021$; AOR $= 0.4225$, $p_{\text{Logit}} = 0.0066$), while Afini significantly increases missingness (LPM coef $= +0.0590$, $p_{\text{LPM}} = 0.0007$; AOR $= 1.7043$, $p_{\text{Logit}} = 0.0009$).
4. **Feasibility of Missing-Data Strategies for Niyati:**
   - **Complete-case analysis** (the published Table 2 approach) is vulnerable to selection bias because attrited children were disproportionately from vulnerable households and from the Digital arm.
   - **Multiple Imputation under MAR** is technically feasible for full-cohort sensitivity analysis ($N = 2,461$) because $71.34\%$ of raw-GSED attriters ($219 / 307$) have fully intact baseline profiles across all 13 baseline variables. However, MAR is an inherently untestable assumption. Child deaths ($10$ cases) represent survival truncation rather than ordinary continuous missingness; post-death developmental scores cannot be imputed as if the child were alive. Furthermore, V3 diagnostics concerned baseline covariate imputation in the assessed complete cases; they do not constitute validation of a full-cohort primary-outcome imputation model.
   - **Inverse Probability Weighting (IPW):** Descriptively, no populated cluster experienced 100% missingness (all 159 clusters had observed participants), but individual-level positivity, propensity score overlap, weight distributions, and truncation sensitivity have not yet been established.
   - **MNAR sensitivity analysis:** Plausible bounds for MNAR delta-adjustment require substantive, context-specific justification and must not be pre-committed as an established range.

---

## 2. Sample-Flow Reconstruction & Discrepancy Resolution

The sample flow from initial randomized enrollment ($N = 2,461$) to the final analysis sample ($N = 2,149$) was audited against the raw dataset (`digitalECD_26Feb2026.dta`), the Stata replication DO script (`Trial_Analysis_Replication_File_26Feb2026.do`), and the published manuscript.

### Table 2.1: Authoritative Sample-Flow Reconciliation

| Step | Stage / Quantity | Dataset Count | Published Benchmark | Difference | Classification Status | Evidence & Resolution Mechanism |
| :---: | :--- | :---: | :---: | :---: | :--- | :--- |
| **1** | **Enrolled caregiver-child dyads** | **2,461** | 2,461 | $0$ | `RESOLVED_WITH_DIRECT_EVIDENCE` | Total participants enrolled and randomized across 159 populated clusters (Control=970, Home visits=317, Afini=1174). Exactly verified from dataset. |
| **2** | **Endline surveys completed (`final_status == 1`)** | **2,183** | 2,183 | $0$ | `RESOLVED_WITH_DIRECT_EVIDENCE` | Participants with `final_status == 1` ('endline participated'). Published paper reports 2,183 endline surveys completed. Exactly verified from dataset. |
| **3** | **Pre-survey attriters / non-participants** | **278** | 278 | $0$ | `RESOLVED_WITH_DIRECT_EVIDENCE` | Households not participating in endline survey: 10 child deaths (`code 2`), 100 moved away (`code 3`), 65 refusals (`code 4`), and 103 unreached after 4+ visits (`code 5`). ($2,461 - 2,183 = 278$). |
| **4** | **Survey completed but unrecorded raw GSED score** | **29** | 29 | $0$ | `RESOLVED_WITH_DIRECT_EVIDENCE` | **Resolves the 29-case gap:** Twenty-nine participants have `final_status == 1` but no recorded raw GSED score. The released dataset establishes that the score is absent; it does not establish whether the assessment was not administered or was administered but not recorded. ($2,183 - 29 = 2,154$). |
| **5** | **Recorded raw GSED outcome scores** | **2,154** | 2,154 | $0$ | `RESOLVED_WITH_DIRECT_EVIDENCE` | Caregiver-child dyads with a valid recorded numerical endline GSED raw score (`el_gsed_dscore` notna). Exactly verified from dataset. |
| **6** | **Missing raw GSED outcome scores (Definition A)** | **307** | 307 | $0$ | `RESOLVED_WITH_DIRECT_EVIDENCE` | **Primary Attrition Metric:** 278 pre-survey non-participants plus 29 survey-completed participants without a recorded raw GSED score ($278 + 29 = 307$). Primary measure of outcome non-observation. |
| **7** | **Singleton 10-day age-band exclusions** | **5** | 5 | $0$ | `RESOLVED_WITH_DIRECT_EVIDENCE` | Children assessed for raw GSED but falling into 10-day age brackets with $n=1$ where sample standard deviation is undefined in Stata (brackets 73, 126, 131, 137, 146). These 5 children are technical outcome-construction exclusions, NOT participant attrition. |
| **8** | **Final primary analysis sample (Table 2)** | **2,149** | 2,149 | $0$ | `RESOLVED_WITH_DIRECT_EVIDENCE` | Participants with valid derived `gsed_Z` scores ($2,154 - 5 = 2,149$). Exactly matches the primary analysis sample $N$ reported in published Table 2. |
| **9** | **Standardized outcome unavailable (Definition B)** | **312** | 312 | $0$ | `RESOLVED_WITH_DIRECT_EVIDENCE` | Mutually exclusive sum: 307 participants with missing raw GSED scores + 5 singleton age-band technical drops = 312 total exclusions ($2,461 - 312 = 2,149$). |
| **10** | **Missing-outcome exclusions reported in paper text** | **312** | 332 | **$-20$** | `UNRESOLVED_WITH_AVAILABLE_SOURCES` | The released data and local replication code account for 312 exclusions, while the paper footnote reports 332 exclusions. The cause of the 20-participant difference ($332 - 312 = 20$) is unknown with available sources. If 332 were excluded, the sample size would be 2,129 rather than 2,149. |

Generated data file:
- [`sample_flow_reconciliation.csv`](file:///D:/Niyati/validation/V5_missingness_attrition_audit/outputs/sample_flow_reconciliation.csv)

---

## 3. Outcome Missingness by Randomized Arm

Primary outcome missingness is substantially and significantly differential across the three randomized trial arms. All primary attrition models use `miss_raw_gsed` as the dependent variable.

### Table 3.1: Outcome Missingness and Attrition by Treatment Arm

| Trial Arm | Enrolled ($N$) | Observed Raw GSED | Missing Raw GSED | Raw GSED Missing % | Arm Rate 95% CI | Singleton Age Drops | Final Analysis Sample ($N$) | Total Exclusions ($N$) | Standardized Unavailable % | Diff vs Control (pp) | Cluster SE (CR1) | Diff 95% CI | $p$-value (CR1) | $p$-value (Cons. $df$) | Odds Ratio vs Control | OR 95% CI | OR $p$-value |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Control** | $970$ | $864$ | $106$ | **$10.93\%$** | $[8.63\%,\, 13.23\%]$ | $0$ | $864$ | $106$ | $10.93\%$ | Baseline | — | — | — | — | $1.000$ (Ref.) | — | — |
| **Home Visits** | $317$ | $299$ | $18$ | **$5.68\%$** | $[3.34\%,\, 8.02\%]$ | $2$ | $297$ | $20$ | $6.31\%$ | **$-5.25$** | $1.65\%$ | $[-8.49\%,\, -2.01\%]$ | $0.0015$ | **$0.0052$** | **$0.491$** | $[0.301,\, 0.799]$ | $0.0042$ |
| **Afini (Digital)** | $1,174$ | $991$ | $183$ | **$15.59\%$** | $[13.19\%,\, 17.98\%]$ | $3$ | $988$ | $186$ | $15.84\%$ | **$+4.66$** | $1.69\%$ | $[+1.35\%,\, +7.97\%]$ | $0.0058$ | **$0.0075$** | **$1.505$** | $[1.118,\, 2.026]$ | $0.0070$ |
| **Direct Contrast (HV vs Afini)** | $1,491$ | $1,290$ | $201$ | **$13.48\%$** | — | $5$ | $1,285$ | $206$ | $13.82\%$ | **$-9.91$** | $1.69\%$ | $[-13.21\%,\, -6.60\%]$ | **$4.19 \times 10^{-9}$** | **$1.45 \times 10^{-5}$** | **$0.326$** | $[0.205,\, 0.518]$ | **$2.14 \times 10^{-6}$** |
| **Total Trial** | **2,461** | **2,154** | **307** | **$12.47\%$** | $[10.87\%,\, 14.08\%]$ | **5** | **2,149** | **312** | **$12.68\%$** | — | — | — | — | — | — | — | — |

*Notes on Statistical Models:*
- Primary models (LPM and Logistic) evaluate raw GSED missingness (`miss_raw_gsed`). Standard errors and confidence intervals use Liang-Zeger cluster-robust standard errors (CR1) clustered on `cluster` ($K = 159$).
- Conservative small-cluster degrees of freedom follow Cameron & Miller (2015): $df_{\text{cons}} = \min(K_a, K_b) - 1$. For comparisons involving Home Visits ($K_{\text{HV}} = 19$), $df_{\text{cons}} = 18$. For Digital vs Control ($K_{\text{Dig}} = 72, K_{\text{Ctrl}} = 68$), $df_{\text{cons}} = 67$.
- In the Control reference row, no contrast $p$-value or difference is reported.
- Separate confidence intervals are reported for arm rates (e.g., Control rate CI $[8.63\%, 13.23\%]$) versus differences vs Control (e.g., HV diff CI $[-8.49\%, -2.01\%]$).
- All pairwise differences remain statistically significant under both standard CR1 and conservative degrees of freedom ($p < 0.01$).
- Direct contrast $p$-values are computed using numerically stable survival functions (`stats.norm.sf` and `stats.t.sf`) and preserved without zero-rounding.

Generated data file:
- [`outcome_missingness_by_arm.csv`](file:///D:/Niyati/validation/V5_missingness_attrition_audit/outputs/outcome_missingness_by_arm.csv)

---

## 4. Cluster-Level Missingness Distributions & Concentration

We evaluated the distribution of primary outcome missingness across the $159$ populated clusters for both primary raw GSED missingness ($N = 307$) and secondary standardized outcome unavailability ($N = 312$), including explicit singleton technical-exclusion distributions.

### Table 4.1: Cluster-Level Missingness and Singleton Summary

| Stratum & Metric | Classification | Clusters ($K$) | Enrolled ($N$) | Missing ($N$) | Mean Rate | SD | Median | IQR | Min Rate | Max Rate | Zero-Missing ($N$, %) | Top 10% Share (%) | Top 20% Share (%) | Singleton Drops ($N$) | Affected Clusters ($N$, %) | Max per Cluster | Singleton Concentration Profile |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Total Trial (Primary: Raw GSED)** | `PRIMARY_RAW_GSED` | $159$ | $2,461$ | $307$ | **$11.96\%$** | $11.41\%$ | $10.26\%$ | $18.18\%$ | $0.00\%$ | $75.00\%$ | $42$ ($26.42\%$) | **$34.53\%$** | **$53.75\%$** | $5$ | $5$ ($3.14\%$) | $1$ | 5 singletons across 5 clusters (1 each in clusters 5, 19, 58, 81, 136). |
| **Control (Primary: Raw GSED)** | `PRIMARY_RAW_GSED` | $68$ | $970$ | $106$ | $10.90\%$ | $12.95\%$ | $8.45\%$ | $15.25\%$ | $0.00\%$ | $75.00\%$ | $21$ ($30.88\%$) | $37.74\%$ | $58.49\%$ | $0$ | $0$ ($0.00\%$) | $0$ | 0 singleton exclusions across 68 clusters. |
| **Home Visits (Primary: Raw GSED)** | `PRIMARY_RAW_GSED` | $19$ | $317$ | $18$ | **$4.56\%$** | $5.26\%$ | $3.57\%$ | $7.85\%$ | $0.00\%$ | **$14.29\%$** | $9$ ($47.37\%$) | $33.33\%$ | $55.56\%$ | $2$ | $2$ ($10.53\%$) | $1$ | 2 singletons across 2 clusters (1 each in clusters 81, 136). |
| **Afini (Primary: Raw GSED)** | `PRIMARY_RAW_GSED` | $72$ | $1,174$ | $183$ | **$14.92\%$** | $9.99\%$ | $15.38\%$ | $13.32\%$ | $0.00\%$ | **$42.86\%$** | $12$ ($16.67\%$) | $30.05\%$ | $46.99\%$ | $3$ | $3$ ($4.17\%$) | $1$ | 3 singletons across 3 clusters (1 each in clusters 5, 19, 58). |
| **Total Trial (Secondary: Standardized)** | `SECONDARY_STANDARDIZED` | $159$ | $2,461$ | $312$ | **$12.14\%$** | $11.39\%$ | $10.53\%$ | $19.26\%$ | $0.00\%$ | $75.00\%$ | $41$ ($25.79\%$) | **$34.62\%$** | **$53.53\%$** | $5$ | $5$ ($3.14\%$) | $1$ | 5 singletons across 5 clusters (1 each in clusters 5, 19, 58, 81, 136). |
| **Control (Secondary: Standardized)** | `SECONDARY_STANDARDIZED` | $68$ | $970$ | $106$ | $10.90\%$ | $12.95\%$ | $8.45\%$ | $15.25\%$ | $0.00\%$ | $75.00\%$ | $21$ ($30.88\%$) | $37.74\%$ | $58.49\%$ | $0$ | $0$ ($0.00\%$) | $0$ | 0 singleton exclusions across 68 clusters. |
| **Home Visits (Secondary: Standardized)** | `SECONDARY_STANDARDIZED` | $19$ | $317$ | $20$ | **$5.44\%$** | $5.49\%$ | $4.76\%$ | $9.35\%$ | $0.00\%$ | **$14.29\%$** | $8$ ($42.11\%$) | $30.00\%$ | $50.00\%$ | $2$ | $2$ ($10.53\%$) | $1$ | 2 singletons across 2 clusters (1 each in clusters 81, 136). |
| **Afini (Secondary: Standardized)** | `SECONDARY_STANDARDIZED` | $72$ | $1,174$ | $186$ | **$15.09\%$** | $10.02\%$ | $15.59\%$ | $13.32\%$ | $0.00\%$ | **$42.86\%$** | $12$ ($16.67\%$) | $30.11\%$ | $47.31\%$ | $3$ | $3$ ($4.17\%$) | $1$ | 3 singletons across 3 clusters (1 each in clusters 5, 19, 58). |

### Key Cluster Findings:
1. **Dispersion:** For raw GSED missingness, $42$ of $159$ clusters ($26.42\%$) experienced zero missingness. In Home Visits, nearly half ($47.37\%$, $9 / 19$) had zero missing raw outcomes, compared to only $16.67\%$ ($12 / 72$) in Afini.
2. **Cluster Boundedness in Home Visits:** In the Home Visits arm, no cluster had a raw missingness rate higher than $14.29\%$. In Afini, individual cluster missingness reached up to $42.86\%$.
3. **Concentration:** The top $10\%$ of clusters with highest raw missing counts ($16$ clusters) account for $34.53\%$ ($106 / 307$) of all missing outcomes, while the top $20\%$ account for over half ($53.75\%$, $165 / 307$).
4. **Singleton Technical Exclusions Distribution:** All $5$ singleton age-band technical drops are completely dispersed: exactly $1$ drop per cluster across $5$ separate clusters (Control: $0$; Home Visits: $2$ clusters [$81, 136$]; Afini: $3$ clusters [$5, 19, 58$]). No cluster experienced more than a single technical drop.

Generated data file:
- [`cluster_missingness_summary.csv`](file:///D:/Niyati/validation/V5_missingness_attrition_audit/outputs/cluster_missingness_summary.csv)

---

## 5. Baseline Characteristic Associations & Predictors of Missingness

We audited whether baseline characteristics differ between participants who completed the raw GSED outcome assessment ($N = 2,154$) and those with missing raw GSED outcomes ($N = 307$).

### Table 5.1: Baseline Covariate Availability and Differential Missingness

> [!NOTE]
> The bivariate chi-square tests below are unadjusted, exploratory descriptive comparisons of covariate non-response across outcome availability groups. They are not cluster-robust inferential evidence.

| Variable Name | Description | Domain | Total Missing ($N$, %) | Missing in Raw GSED Observed ($N=2,154$) | Missing in Raw GSED Missing ($N=307$) | Unadjusted $\chi^2$ Stat | $p$-value | Differential Baseline Missingness Note |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| `bl_z_overall` | Baseline CREDI score (Z-score) | Child Development | $3$ ($0.12\%$) | $0$ ($0.00\%$) | $3$ ($0.98\%$) | $13.813$ | $0.0002$ | Exploratory unadjusted test; not cluster-robust. |
| `bl_childage` | Baseline child age (completed months) | Child Demographics | $3$ ($0.12\%$) | $0$ ($0.00\%$) | $3$ ($0.98\%$) | $13.813$ | $0.0002$ | Exploratory unadjusted test; not cluster-robust. |
| `child_female` | Child sex (female = 1) | Child Demographics | $0$ ($0.00\%$) | $0$ ($0.00\%$) | $0$ ($0.00\%$) | $0.000$ | $1.0000$ | Exploratory unadjusted test; not cluster-robust. |
| `bl_low_bweight` | Low birth weight ($<2500$g = 1) | Child Health | $47$ ($1.91\%$) | $38$ ($1.76\%$) | $9$ ($2.93\%$) | $1.381$ | $0.2399$ | Exploratory unadjusted test; not cluster-robust. |
| `bl_mo_age` | Mother's age (years) | Caregiver Demographics | $42$ ($1.71\%$) | $33$ ($1.53\%$) | $9$ ($2.93\%$) | $2.359$ | $0.1246$ | Exploratory unadjusted test; not cluster-robust. |
| `bl_mo_educ_level` | Mother's education level (1-6) | Caregiver Demographics | $45$ ($1.83\%$) | $35$ ($1.62\%$) | $10$ ($3.26\%$) | $3.131$ | $0.0768$ | Exploratory unadjusted test; not cluster-robust. |
| `bl_fa_age` | Father's age (years) | Caregiver Demographics | $311$ ($12.64\%$) | $262$ ($12.16\%$) | $49$ ($15.96\%$) | $3.174$ | $0.0748$ | Exploratory unadjusted test; not cluster-robust. |
| `bl_fa_educ_level` | Father's education level (1-6) | Caregiver Demographics | $351$ ($14.26\%$) | $295$ ($13.70\%$) | $56$ ($18.24\%$) | $4.176$ | $0.0410$ | Exploratory unadjusted test; not cluster-robust. |
| `bl_child_sib_tot` | Number of siblings in household | Household Structure | $0$ ($0.00\%$) | $0$ ($0.00\%$) | $0$ ($0.00\%$) | $0.000$ | $1.0000$ | Exploratory unadjusted test; not cluster-robust. |
| `bl_hhadults` | Number of adults in household | Household Structure | $6$ ($0.24\%$) | $3$ ($0.14\%$) | $3$ ($0.98\%$) | $4.694$ | $0.0303$ | Exploratory unadjusted test; not cluster-robust. |
| `bl_f_b` | Father lives in household (1=Yes) | Household Structure | $7$ ($0.28\%$) | $4$ ($0.19\%$) | $3$ ($0.98\%$) | $3.472$ | $0.0624$ | Exploratory unadjusted test; not cluster-robust. |
| `bl_qses_index` | SES index quintile (1-5) | Socioeconomic Status | $12$ ($0.49\%$) | $9$ ($0.42\%$) | $3$ ($0.98\%$) | $0.772$ | $0.3797$ | Exploratory unadjusted test; not cluster-robust. |
| `bl_mics_tot` | MICS stimulation activities (0-6) | Home Environment | $218$ ($8.86\%$) | $191$ ($8.87\%$) | $27$ ($8.79\%$) | $0.000$ | $1.0000$ | Exploratory unadjusted test; not cluster-robust. |
| `provincia` | Province of residence | Geography | $0$ ($0.00\%$) | $0$ ($0.00\%$) | $0$ ($0.00\%$) | $0.000$ | $1.0000$ | Exploratory unadjusted test; not cluster-robust. |
| `distrito` | District of residence | Geography | $0$ ($0.00\%$) | $0$ ($0.00\%$) | $0$ ($0.00\%$) | $0.000$ | $1.0000$ | Exploratory unadjusted test; not cluster-robust. |

### Table 5.2: Multivariable Missingness Prediction Models

We fit cluster-robust linear probability models (LPM) and logistic regression models predicting raw GSED missingness (`miss_raw_gsed = 1`, $N = 2,373$ complete baseline cases):

- **Predictors included in model ($11$):** `hv`, `afini`, `bl_z_overall`, `bl_childage`, `child_female`, `bl_low_bweight`, `bl_mo_age`, `bl_child_sib_tot`, `bl_hhadults`, `bl_f_b`, `bl_qses_index`.
- **Baseline predictors excluded from multivariable formula ($4$):**
  - `bl_fa_age` ($311$ missing, $12.64\%$): excluded due to substantial missingness (>8-14%).
  - `bl_fa_educ_level` ($351$ missing, $14.26\%$): excluded due to substantial missingness (>8-14%).
  - `bl_mics_tot` ($218$ missing, $8.86\%$): excluded due to substantial missingness (>8-14%).
  - `bl_mo_educ_level` ($45$ missing, $1.83\%$): excluded due to its categorical specification in the selected model (not due to substantial missingness).

| Predictor Variable | LPM Coef. ($\beta$) | Cluster SE | 95% CI (LPM) | $p$-value (LPM) | Adjusted Odds Ratio (AOR) | 95% CI (AOR) | $p$-value (Logit) | Substantive Interpretation |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Intercept** | $+0.3009$ | $0.0463$ | $[+0.2102,\, +0.3916]$ | $7.79 \times 10^{-11}$ | $0.7523$ | $[0.3409,\, 1.6602]$ | $0.4810$ | Baseline missingness anchor. |
| **Home Visits (`hv`)** | **$-0.0548$** | $0.0178$ | $[-0.0897,\, -0.0200]$ | **$0.0021$** | **$0.4225$** | $[0.2269,\, 0.7867]$ | **$0.0066$** | Decreases raw missingness probability by $5.48$ pp ($57.8\%$ lower odds). |
| **Afini (`afini`)** | **$+0.0590$** | $0.0173$ | $[+0.0251,\, +0.0930]$ | **$0.0007$** | **$1.7043$** | $[1.2425,\, 2.3377]$ | **$0.0009$** | Increases raw missingness probability by $5.90$ pp ($70.4\%$ higher odds). |
| **Mother's Age (`bl_mo_age`)** | **$-0.0051$** | $0.0011$ | $[-0.0073,\, -0.0030]$ | **$3.31 \times 10^{-6}$** | **$0.9493$** | $[0.9280,\, 0.9711]$ | **$6.98 \times 10^{-6}$** | Strong protective factor: older mothers have significantly lower attrition. |
| **Low Birth Weight (`bl_low_bweight`)** | **$+0.0585$** | $0.0283$ | $[+0.0031,\, +0.1139]$ | **$0.0386$** | **$1.5957$** | $[1.0731,\, 2.3729]$ | **$0.0210$** | Infant vulnerability: low birth weight infants have $5.85$ pp higher missingness. |
| **Household Adults (`bl_hhadults`)** | **$-0.0151$** | $0.0056$ | $[-0.0261,\, -0.0042]$ | **$0.0065$** | **$0.8555$** | $[0.7568,\, 0.9671]$ | **$0.0126$** | Caregiver capacity: more adults in household reduce missingness probability. |
| **Baseline CREDI (`bl_z_overall`)** | $-0.0181$ | $0.0131$ | $[-0.0437,\, +0.0075]$ | $0.1659$ | $0.8499$ | $[0.6703,\, 1.0777]$ | $0.1794$ | Directionally negative: lower baseline development associates with higher attrition. |
| **Child Age (`bl_childage`)** | $-0.0005$ | $0.0039$ | $[-0.0081,\, +0.0072]$ | $0.9003$ | $0.9965$ | $[0.9248,\, 1.0737]$ | $0.9264$ | No independent association. |
| **Child Sex (`child_female`)** | $-0.0252$ | $0.0139$ | $[-0.0525,\, +0.0020]$ | $0.0698$ | $0.7925$ | $[0.6112,\, 1.0275]$ | $0.0792$ | Female infants have non-significantly lower missingness. |
| **Father in HH (`bl_f_b`)** | $-0.0304$ | $0.0220$ | $[-0.0735,\, +0.0126]$ | $0.1659$ | $0.7727$ | $[0.5473,\, 1.0911]$ | $0.1430$ | Non-significant protective trend. |
| **SES Quintile (`bl_qses_index`)** | $+0.0052$ | $0.0051$ | $[-0.0048,\, +0.0153]$ | $0.3086$ | $1.0549$ | $[0.9547,\, 1.1655]$ | $0.2937$ | No independent linear gradient after controlling for other indicators. |
| **Siblings Count (`bl_child_sib_tot`)** | $+0.0042$ | $0.0065$ | $[-0.0084,\, +0.0169]$ | $0.5108$ | $1.0513$ | $[0.9140,\, 1.2094]$ | $0.4834$ | No independent association. |

Generated data files:
- [`baseline_missingness_summary.csv`](file:///D:/Niyati/validation/V5_missingness_attrition_audit/outputs/baseline_missingness_summary.csv)
- [`missingness_association_models.csv`](file:///D:/Niyati/validation/V5_missingness_attrition_audit/outputs/missingness_association_models.csv)

---

## 6. Missing-Data Patterns & Reason Documentation

We mapped the joint missingness structure across raw GSED availability and $13$ key baseline variables across the entire enrolled cohort ($N = 2,461$).

### Table 6.1: Predominant Joint Missingness Patterns

| Pattern ID | Raw GSED Outcome Status | Missing Baseline Variables | Frequency Count ($N$) | Frequency Share (%) | Cumulative Share (%) | Singleton Age Exclusions | Substantive Profile |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **Pattern 01** | **Observed Raw GSED** | **None (Fully Complete Baseline)** | **$1,632$** | **$66.31\%$** | $66.31\%$ | $4$ | Observed raw GSED; fully complete baseline across all 13 covariates. (Includes 4 singleton drops). |
| **Pattern 02** | **Missing Raw GSED (Attrited)** | **None (Fully Complete Baseline)** | **$219$** | **$8.90\%$** | $75.21\%$ | $0$ | **Raw GSED attriters with completely intact baseline profiles ($219 / 307 = 71.34\%$ of all raw attriters).** |
| **Pattern 03** | Observed Raw GSED | `bl_fa_age, bl_fa_educ_level` | $213$ | $8.66\%$ | $83.87\%$ | $1$ | Observed raw GSED; missing father demographics. (Includes 1 singleton drop). |
| **Pattern 04** | Observed Raw GSED | `bl_mics_tot` | $161$ | $6.54\%$ | $90.41\%$ | $0$ | Observed raw GSED; missing baseline home stimulation count. |
| **Pattern 05** | Missing Raw GSED (Attrited) | `bl_fa_age, bl_fa_educ_level` | $42$ | $1.71\%$ | $92.12\%$ | $0$ | Raw GSED attriter with missing father demographics. |
| **Pattern 06** | Observed Raw GSED | `bl_fa_educ_level` only | $39$ | $1.58\%$ | $93.70\%$ | $0$ | Observed raw GSED; missing father education only. |
| **Pattern 07** | Observed Raw GSED | `bl_low_bweight` only | $28$ | $1.14\%$ | $94.84\%$ | $0$ | Observed raw GSED; missing birth weight indicator. |
| **Pattern 08** | Observed Raw GSED | `bl_fa_age, bl_fa_educ_level, bl_mics_tot` | $26$ | $1.06\%$ | $95.90\%$ | $0$ | Observed raw GSED; multiple missing baseline indicators. |
| **Pattern 09** | Missing Raw GSED (Attrited) | `bl_mics_tot` only | $22$ | $0.89\%$ | $96.79\%$ | $0$ | Raw GSED attriter with missing baseline home stimulation count. |
| **Pattern 10** | Observed Raw GSED | `bl_mo_age, bl_mo_educ_level` | $20$ | $0.81\%$ | $97.60\%$ | $0$ | Observed raw GSED; missing maternal demographics. |
| **Patterns 11–31** | Mixed | Remaining minor combinations | $59$ | $2.40\%$ | $100.00\%$ | $0$ | 21 distinct sparse residual patterns ($1$ to $8$ participants each). |

*Reconciliation Note on Baseline Completeness:*
- Among the $307$ raw GSED attriters, exactly **$219$ ($71.34\%$)** have completely intact baseline profiles across all 13 baseline variables.
- When evaluating the $312$ standardized outcome unavailable cases, $4$ singleton age-band excluded children also have complete baseline profiles, yielding $219 + 4 = 223$ ($71.47\%$).

### Table 6.2: Documented Attrition Reasons vs. Speculative Explanations

In accordance with strict audit integrity rules, we separate directly documented facts from unverified assumptions:

| Category | Finding / Reason | Empirical Evidence in Released Dataset / Codebook | Analytical Implications |
| :--- | :--- | :--- | :--- |
| **Directly Documented** | **Child Mortality** ($N=10$) | Explicitly recorded in `final_status == 2` ("child died"). | Survival truncation; cannot be imputed under standard continuous MAR missingness paradigms. |
| **Directly Documented** | **Household Migration** ($N=100$) | Explicitly recorded in `final_status == 3` ("moved away"). | True geographic attrition; higher in Digital ($5.03\%$) than Home Visits ($2.52\%$). |
| **Directly Documented** | **Explicit Refusal** ($N=65$) | Explicitly recorded in `final_status == 4` ("refused"). | Active caregiver refusal; nearly $6\times$ higher in Digital ($3.75\%$) than Home Visits ($0.63\%$). |
| **Directly Documented** | **Unreached After 4+ Visits** ($N=103$) | Explicitly recorded in `final_status == 5` ("no contact after 4+ visits"). | Fieldwork exhaustion; $> 3\times$ higher in Digital ($5.20\%$) than Home Visits ($1.58\%$). |
| **Directly Documented** | **Completed Survey, Unrecorded Raw GSED** ($N=29$) | Twenty-nine participants have `final_status == 1` but no recorded raw GSED score. | The released dataset establishes that the score is absent; it does not establish whether the assessment was not administered or was administered but not recorded. |
| **Directly Documented** | **Singleton Age-Band Exclusions** ($N=5$) | Assessed raw GSED recorded, but `gsed_sd` undefined ($n=1$). | Methodological drop during within-sample age standardization in Stata DO script. Not participant attrition. |
| **Unverified / Speculative** | **Digital Device / Connectivity Loss** | **NO direct variable in dataset.** | Plausible mechanism for higher Digital refusal/unreached rates, but unverified. |
| **Unverified / Speculative** | **Intervention Dissatisfaction** | **NO exit survey data recorded for dropouts.** | Plausible behavioral mechanism for refusal, but cannot be established from data. |

Generated data file:
- [`missing_pattern_summary.csv`](file:///D:/Niyati/validation/V5_missingness_attrition_audit/outputs/missing_pattern_summary.csv)

---

## 7. MAR / MNAR & Imputation Feasibility Assessment

We conducted a methodological feasibility evaluation of four alternative missing-data handling strategies for the eventual Niyati analysis.

### Table 7.1: Comparative Missing-Data Strategies Evaluation

| Strategy Name | Target Parameter | Underlying Assumptions | Empirical Data Support in Niyati | Methodological Strengths | Methodological Vulnerabilities & Diagnostic Limitations | Final Audit Recommendation for Niyati |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Complete-Case Analysis** *(Published Table 2)* | ITT Effect in Assessed Subsample ($N = 2,149$) | Assumes MCAR: $Y_{\text{miss}} \perp Y \mid (T, \mathbf{X})$. | **Strong evidence against MCAR:** Missingness differs by arm ($5.68\%$ in HV vs $15.59\%$ in Afini, $p < 0.001$) and correlates with maternal age, low birth weight, and household size. | Simple, transparent, exact match to published study sample. | Discards $312$ cases ($12.68\%$: 307 raw GSED missing + 5 singleton drops). Severe risk of selection bias due to differential Digital attrition. | **Retain strictly as primary replication benchmark.** Must NOT be the sole basis for substantive decision-making. |
| **Multiple Imputation for Primary Outcome (under MAR)** | Full-Cohort ITT Effect ($N = 2,461$) | Assumes MAR: $P(R=1 \mid Y, \mathbf{X}, T) = P(R=1 \mid \mathbf{X}, T)$. Correct imputation model. | **Strong observed predictor base:** $71.34\%$ of raw attriters ($219/307$) have full baseline profiles; $95.11\%$ have complete multivariable covariates. | Recovers full randomized sample ($N=2,461$). Restores ITT principle. Incorporates cluster structure and baseline predictors. | MAR is an untestable assumption. Child mortality ($N=10$) is survival truncation, not ordinary missingness; developmental scores after death cannot be imputed as if the child were alive. Crucially, V3 diagnostics concerned baseline covariate imputation in the assessed complete cases; they do NOT constitute validation of a full-cohort primary-outcome imputation model. | **Recommended as primary full-cohort sensitivity analysis**, provided that child deaths are handled separately in a defined estimand, clustering is respected, and support restrictions are enforced. |
| **Inverse Probability Weighting (IPW)** | Weighted Average Treatment Effect (Re-weighted to $N=2,461$) | Selection on observables & Positivity: $P(R=1 \mid \mathbf{X}, T) > 0$. | **Descriptive finding:** No populated cluster experienced 100% missingness (all 159 clusters had observed participants). However, individual-level positivity, propensity score overlap, weight distributions, and truncation sensitivity have not yet been established. | Does not require specifying conditional outcome distribution for non-responders. Re-weights complete cases to baseline cohort. | Potential weight instability if extreme. Does not address unobserved confounding (MNAR) or truncation by death. | **Feasible secondary sensitivity check**, but must be preceded by formal diagnostics evaluating propensity overlap, weight bounds, and effective sample size before being accepted. |
| **MNAR Tipping-Point / Delta-Adjustment** | Robustness Boundary for Treatment Effects | Assumes MNAR: $E[Y_{\text{miss}} \mid \mathbf{X}, T] = E[Y_{\text{obs}} \mid \mathbf{X}, T] + \delta_T$. | **Substantively motivated:** $65$ explicit refusals, $103$ unreached; Digital attrition was $2.7\times$ higher than Home Visits. | Directly models informative attrition without assuming benign dropouts. Transparently reveals tipping point where effects vanish. | Plausible bounds for $\delta$ require substantive justification and must NOT be pre-committed as an established range. Generates a sensitivity boundary rather than a single point estimate. | **Strongly recommended as the definitive stress-test** for Niyati. Plausible candidate ranges should be justified transparently to determine whether differential Digital attrition could overturn trial findings. |

Generated data file:
- [`imputation_feasibility.csv`](file:///D:/Niyati/validation/V5_missingness_attrition_audit/outputs/imputation_feasibility.csv)

---

## 8. Verification Manifest & Output Catalog

All generated outputs are located in [`validation/V5_missingness_attrition_audit/outputs/`](file:///D:/Niyati/validation/V5_missingness_attrition_audit/outputs/):

| Output File | Description | Record Count |
| :--- | :--- | :---: |
| [`sample_flow_reconciliation.csv`](file:///D:/Niyati/validation/V5_missingness_attrition_audit/outputs/sample_flow_reconciliation.csv) | Step-by-step sample-flow reconstruction, resolving the 29-case gap and explaining the 20-case footnote gap. | 10 rows |
| [`outcome_missingness_by_arm.csv`](file:///D:/Niyati/validation/V5_missingness_attrition_audit/outputs/outcome_missingness_by_arm.csv) | Primary outcome missingness rates by randomized arm with cluster-robust LPM and logistic models and conservative $df$. | 5 rows |
| [`cluster_missingness_summary.csv`](file:///D:/Niyati/validation/V5_missingness_attrition_audit/outputs/cluster_missingness_summary.csv) | Cluster-level missingness distributions, quartile dispersions, zero-missing counts, top 10%/20% shares, and singleton drop distributions across all 8 strata. | 8 rows |
| [`baseline_missingness_summary.csv`](file:///D:/Niyati/validation/V5_missingness_attrition_audit/outputs/baseline_missingness_summary.csv) | Baseline covariate missingness rates overall and contrasted by primary outcome observation status with exploratory $\chi^2$ tests. | 15 rows |
| [`missingness_association_models.csv`](file:///D:/Niyati/validation/V5_missingness_attrition_audit/outputs/missingness_association_models.csv) | Comprehensive regression models (arm-only LPM, bivariate LPM, multivariable LPM, arm-only Logistic, and multivariable Logistic) predicting missingness. | 55 rows |
| [`missing_pattern_summary.csv`](file:///D:/Niyati/validation/V5_missingness_attrition_audit/outputs/missing_pattern_summary.csv) | Mapping of all 31 distinct joint missingness patterns across outcome and 13 key baseline covariates. | 31 rows |
| [`imputation_feasibility.csv`](file:///D:/Niyati/validation/V5_missingness_attrition_audit/outputs/imputation_feasibility.csv) | Methodological comparative assessment of Complete-Case, MAR Imputation, IPW, and MNAR Tipping-Point strategies. | 4 rows |
| [`v5_summary.json`](file:///D:/Niyati/validation/V5_missingness_attrition_audit/outputs/v5_summary.json) | Complete machine-readable metadata summary of all sample flows, missingness models, tests, and feasibility verdicts. | 197 lines |

---

## 9. Implications for the Eventual Niyati Analysis

1. **Replication Integrity vs. Analytical Decision-Making:**
   - For exact replication of published Table 2, the complete-case sample of $N = 2,149$ must be utilized.
   - However, for independent decision-making regarding policy scale-up or intervention equivalence, complete-case results cannot be accepted uncritically. The marked differential raw missingness between Digital ($15.59\%$) and Home Visits ($5.68\%$) means that complete-case analysis compares a more heavily selected Digital sample against a more complete Home Visits sample.
2. **Mandatory Sensitivity Architecture:**
   - Any eventual Niyati causal inference pipeline must report:
     1. Primary Complete-Case Benchmark ($N = 2,149$).
     2. Full-Cohort Multiple Imputation under MAR ($N = 2,461$), utilizing bounded regression models for counts and separating mortality cases.
     3. Inverse Probability Weighting (IPW) following formal verification of individual-level overlap and weight boundedness.
     4. MNAR Tipping-Point Grid: evaluating whether an unobserved developmental deficit among Digital non-responders widens the active contrast in favor of Home Visits or alters statistical significance.
