# Task V5: Missing Outcomes, Attrition & Missing-Data Feasibility Audit

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

### Key Audit Findings:
1. **Sample Flow & Discrepancy Resolution:**
   - **The 29-case discrepancy is RESOLVED WITH DIRECT EVIDENCE:** Exactly $2,183$ caregiver-child dyads completed the endline household survey (`final_status == 1`). Of these, $29$ participants did not have the direct child Global Scales for Early Development (GSED) developmental assessment administered or recorded (`el_gsed_dscore` is missing), leaving exactly $2,154$ recorded raw GSED scores ($2,183 - 29 = 2,154$).
   - **The 20-case discrepancy is UNRESOLVED WITH AVAILABLE SOURCES:** Actual exclusions in the dataset and replication DO script total exactly $312$ participants ($307$ missing raw GSED assessments plus $5$ singleton 10-day age-band drops), yielding the exact primary analysis sample of $N = 2,149$ ($2,461 - 312 = 2,149$). The footnote in published Table 2 states that $332$ children were excluded. If $332$ were excluded, the sample size would be $2,129$, directly contradicting Table 2's reported $N = 2,149$. This represents an authorial drafting or calculation error in the manuscript text that cannot be reconciled from released data or code.
2. **Marked Differential Attrition Across Treatment Arms ($p < 0.001$):**
   - **Afini (Digital):** Suffered the highest outcome missingness at **$15.84\%$** ($186 / 1,174$).
   - **Control:** Intermediate missingness at **$10.93\%$** ($106 / 970$).
   - **Home Visits:** Lowest missingness at **$6.31\%$** ($20 / 317$).
   - In cluster-robust linear probability models (CR1), Digital attrition was $+4.92$ percentage points higher than Control ($p = 0.0038$), while Home Visits attrition was $-4.62$ percentage points lower than Control ($p = 0.0051$; conservative $df=18$, $p = 0.0118$).
   - The direct contrast between active modalities is substantial: Home Visits achieved a **$9.53$ percentage point lower attrition rate** than Digital ($z = -5.636, p < 10^{-5}$; conservative $df=18$, $p = 0.000024$), corresponding to a $64.2\%$ reduction in the odds of missingness (Odds Ratio $= 0.358$).
3. **Missing Completely at Random (MCAR) is Strictly Refuted:**
   - Beyond treatment arm assignment, outcome missingness is strongly associated with baseline vulnerability: younger maternal age ($p < 0.0001$, each additional year of mother's age decreases missingness probability by $\sim 0.53$ percentage points), low birth weight ($p = 0.028$, $+6.17$ percentage points higher missingness for infants $< 2500$g), and smaller household size ($p = 0.018$, each additional adult decreases missingness by $\sim 1.34$ percentage points).
4. **Feasibility of Missing-Data Strategies for Niyati:**
   - **Complete-case analysis** (the published Table 2 approach) is vulnerable to selection bias because attrited children were disproportionately from vulnerable households and from the Digital arm.
   - **Multiple imputation under Missing at Random (MAR)** is technically feasible for the full cohort ($N = 2,461$) because $71.5\%$ of outcome attriters have fully intact baseline covariate profiles. However, MAR cannot be tested or verified from observed data, and V3 diagnostic audits showed continuous baseline imputation models produced non-trivial support violations.
   - **MNAR tipping-point / delta-adjustment sensitivity analysis** is strongly recommended as the definitive stress-test for Niyati to determine the threshold of unobserved disadvantage among Digital attriters that would alter the trial's conclusions.

---

## 2. Sample-Flow Reconstruction & Discrepancy Resolution

The sample flow from initial randomized enrollment ($N = 2,461$) to the final analysis sample ($N = 2,149$) was audited against the raw dataset (`digitalECD_26Feb2026.dta`), the Stata replication DO script (`Trial_Analysis_Replication_File_26Feb2026.do`), and the published manuscript.

### Table 2.1: Authoritative Sample-Flow Reconciliation

| Step | Stage / Quantity | Dataset Count | Published Benchmark | Difference | Classification Status | Evidence & Resolution Mechanism |
| :---: | :--- | :---: | :---: | :---: | :--- | :--- |
| **1** | **Enrolled caregiver-child dyads** | **2,461** | 2,461 | $0$ | `RESOLVED_WITH_DIRECT_EVIDENCE` | Total enrolled sample randomized across 159 populated clusters (Control=970, Home visits=317, Afini=1174). Exactly verified. |
| **2** | **Endline surveys completed (`final_status == 1`)** | **2,183** | 2,183 | $0$ | `RESOLVED_WITH_DIRECT_EVIDENCE` | Caregiver-child dyads completing the endline survey. Verified by `final_status == 1` in dataset. Exactly matches paper text. |
| **3** | **Pre-survey attriters / non-participants** | **278** | 278 | $0$ | `RESOLVED_WITH_DIRECT_EVIDENCE` | Documented non-participants: 10 child deaths (`final_status=2`), 100 moved away (`code 3`), 65 refusals (`code 4`), 103 unreached after 4+ visits (`code 5`). ($2,461 - 2,183 = 278$). |
| **4** | **Survey completed but unassessed for raw GSED** | **29** | 29 | $0$ | `RESOLVED_WITH_DIRECT_EVIDENCE` | **Resolves the 29-case gap:** 29 participants completed endline survey interviews (`final_status=1`), but child GSED assessment was not administered/recorded (`el_gsed_dscore` is NaN). |
| **5** | **Recorded raw GSED outcome scores** | **2,154** | 2,154 | $0$ | `RESOLVED_WITH_DIRECT_EVIDENCE` | Caregiver-child dyads with valid numerical raw GSED developmental scores (`el_gsed_dscore` notna). ($2,183 - 29 = 2,154$). |
| **6** | **Missing raw GSED outcome scores** | **307** | 307 | $0$ | `RESOLVED_WITH_DIRECT_EVIDENCE` | Sum of 278 pre-survey non-participants + 29 survey-completed children without GSED assessment ($278 + 29 = 307$). |
| **7** | **Singleton 10-day age-band exclusions** | **5** | 5 | $0$ | `RESOLVED_WITH_DIRECT_EVIDENCE` | Assessed children falling into 10-day age brackets with $n=1$ where sample standard deviation `sd()` is undefined in Stata (brackets 73, 126, 131, 137, 146). |
| **8** | **Final primary analysis sample (Table 2)** | **2,149** | 2,149 | $0$ | `RESOLVED_WITH_DIRECT_EVIDENCE` | Valid derived within-sample standardized scores `gsed_Z` ($2,154 - 5 = 2,149$). Exactly matches published Table 2 sample. |
| **9** | **Total actual analysis sample exclusions** | **312** | 312 | $0$ | `RESOLVED_WITH_DIRECT_EVIDENCE` | Mutually exclusive sum: 307 missing raw GSED + 5 singleton age-band standardization drops ($307 + 5 = 312$). |
| **10** | **Missing-outcome exclusions reported in paper text** | **312** | 332 | **$-20$** | `UNRESOLVED_WITH_AVAILABLE_SOURCES` | Published Table 2 footnote states: *"A total of 332 children were excluded due to missing outcome data."* Actual data exclusions are 312. An extra 20 exclusions would yield $N=2,129$, contradicting Table 2 ($N=2,149$). Unresolved authorial text error. |

Generated data file:
- [`sample_flow_reconciliation.csv`](file:///D:/Niyati/validation/V5_missingness_attrition_audit/outputs/sample_flow_reconciliation.csv)

---

## 3. Outcome Missingness by Randomized Arm

Primary outcome missingness is substantially and significantly differential across the three randomized trial arms.

### Table 3.1: Outcome Missingness and Attrition by Treatment Arm

| Trial Arm | Enrolled ($N$) | Observed Raw GSED | Missing Raw GSED | Singleton Age Drops | Final Analysis Sample ($N$) | Total Exclusions ($N$) | Missingness Rate (%) | Difference vs Control (pp) | Cluster SE (CR1) | 95% Confidence Interval | $p$-value (CR1) | $p$-value (Cons. $df$) | Odds Ratio vs Control |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Control** | $970$ | $864$ | $106$ | $0$ | $864$ | $106$ | **$10.93\%$** | Baseline | — | $[8.64\%,\, 13.22\%]$ | — | — | $1.000$ (Ref.) |
| **Home Visits** | $317$ | $299$ | $18$ | $2$ | $297$ | $20$ | **$6.31\%$** | **$-4.62$** | $1.65\%$ | $[-7.85\%,\, -1.39\%]$ | $0.0051$ | **$0.0118$** | **$0.549$** |
| **Afini (Digital)** | $1,174$ | $991$ | $183$ | $3$ | $988$ | $186$ | **$15.84\%$** | **$+4.92$** | $1.70\%$ | $[+1.59\%,\, +8.24\%]$ | $0.0038$ | **$0.0051$** | **$1.534$** |
| **Direct Active Contrast (HV vs Digital)** | $1,491$ | $1,290$ | $201$ | $5$ | $1,285$ | $206$ | — | **$-9.53$** | $1.69\%$ | $[-12.85\%,\, -6.22\%]$ | $< 10^{-5}$ | **$0.000024$** | **$0.358$** |
| **Total Trial** | **2,461** | **2,154** | **307** | **5** | **2,149** | **312** | **$12.68\%$** | — | — | $[11.37\%,\, 13.99\%]$ | — | — | — |

*Notes on Statistical Inference:*
- Standard errors and confidence intervals are computed from linear probability models (LPM) and logistic models with Liang-Zeger cluster-robust standard errors (CR1) clustered on `cluster` ($K = 159$).
- Conservative small-sample degrees of freedom follow Cameron & Miller (2015): $df_{\text{cons}} = \min(K_a, K_b) - 1$. For comparisons involving Home Visits ($K_{\text{HV}} = 19$), $df_{\text{cons}} = 18$. For Digital vs Control ($K_{\text{Dig}} = 72, K_{\text{Ctrl}} = 68$), $df_{\text{cons}} = 67$.
- Even under the conservative degrees-of-freedom threshold, all pairwise differences in missingness rates remain statistically significant ($p < 0.05$).

Generated data file:
- [`outcome_missingness_by_arm.csv`](file:///D:/Niyati/validation/V5_missingness_attrition_audit/outputs/outcome_missingness_by_arm.csv)

---

## 4. Cluster-Level Missingness Distributions & Concentration

We evaluated the distribution of primary outcome missingness across the $159$ populated clusters to examine whether attrition is geographically dispersed or concentrated in specific clusters.

### Table 4.1: Cluster-Level Missingness Summary

| Stratum | Populated Clusters ($K$) | Enrolled Part. ($N$) | Missing Outcomes ($N$) | Mean Cluster Missing Rate | SD Missing Rate | Median Missing Rate | IQR Missing Rate | Min Cluster Missing Rate | Max Cluster Missing Rate | Zero-Missing Clusters ($N$, %) | Top 10% Clusters Missing Share (%) | Top 20% Clusters Missing Share (%) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Total Trial** | $159$ | $2,461$ | $312$ | **$12.14\%$** | $11.39\%$ | $10.53\%$ | $19.26\%$ | $0.00\%$ | $75.00\%$ | $41$ ($25.79\%$) | **$34.62\%$** ($108 / 312$) | **$53.53\%$** ($167 / 312$) |
| **Control** | $68$ | $970$ | $106$ | $10.90\%$ | $12.95\%$ | $8.45\%$ | $15.25\%$ | $0.00\%$ | $75.00\%$ | $21$ ($30.88\%$) | $37.74\%$ ($40 / 106$) | $58.49\%$ ($62 / 106$) |
| **Home Visits** | $19$ | $317$ | $20$ | **$5.44\%$** | $5.49\%$ | $4.76\%$ | $9.35\%$ | $0.00\%$ | **$14.29\%$** | $8$ ($42.11\%$) | $30.00\%$ ($6 / 20$) | $50.00\%$ ($10 / 20$) |
| **Afini (Digital)** | $72$ | $1,174$ | $186$ | **$15.09\%$** | $10.02\%$ | $15.59\%$ | $13.32\%$ | $0.00\%$ | **$42.86\%$** | $12$ ($16.67\%$) | $30.11\%$ ($56 / 186$) | $47.31\%$ ($88 / 186$) |

### Key Cluster Findings:
1. **Dispersion:** $41$ of $159$ clusters ($25.79\%$) experienced zero outcome missingness. In Home Visits, $42.11\%$ of clusters had zero missing outcomes, compared to only $16.67\%$ in Afini.
2. **Cluster Boundedness in Home Visits:** In the Home Visits arm, no cluster had a missingness rate higher than $14.29\%$. In contrast, in Afini, multiple clusters experienced missingness rates between $30\%$ and $42.86\%$.
3. **Concentration:** The top $10\%$ of clusters with highest missing counts ($16$ clusters) account for $34.62\%$ ($108 / 312$) of all missing outcomes, while the top $20\%$ ($32$ clusters) account for over half ($53.53\%$) of missing outcomes.

Generated data file:
- [`cluster_missingness_summary.csv`](file:///D:/Niyati/validation/V5_missingness_attrition_audit/outputs/cluster_missingness_summary.csv)

---

## 5. Baseline Characteristic Associations & Predictors of Missingness

We audited whether baseline characteristics differ between participants who completed the primary outcome assessment ($N = 2,149$) and those with missing outcomes ($N = 312$).

### Table 5.1: Baseline Covariate Availability and Differential Missingness

| Variable Name | Description | Domain | Total Missing ($N$, %) | Missing in Outcome Observed ($N=2,149$) | Missing in Outcome Missing ($N=312$) | $\chi^2$ Test Statistic | $p$-value | Differential Baseline Missingness? |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `bl_z_overall` | Baseline CREDI score (Z-score) | Child Development | $3$ ($0.12\%$) | $0$ ($0.00\%$) | $3$ ($0.96\%$) | $13.55$ | $0.0002$ | **YES ($p < 0.05$)** |
| `bl_childage` | Baseline child age (completed months) | Child Demographics | $3$ ($0.12\%$) | $0$ ($0.00\%$) | $3$ ($0.96\%$) | $13.55$ | $0.0002$ | **YES ($p < 0.05$)** |
| `child_female` | Child sex (female = 1) | Child Demographics | $0$ ($0.00\%$) | $0$ ($0.00\%$) | $0$ ($0.00\%$) | $0.00$ | $1.0000$ | NO |
| `bl_low_bweight` | Low birth weight ($<2500$g = 1) | Child Health | $47$ ($1.91\%$) | $38$ ($1.77\%$) | $9$ ($2.88\%$) | $1.27$ | $0.2606$ | NO |
| `bl_mo_age` | Mother's age (years) | Caregiver Demographics | $42$ ($1.71\%$) | $33$ ($1.54\%$) | $9$ ($2.88\%$) | $2.21$ | $0.1375$ | NO |
| `bl_mo_educ_level` | Mother's education level (1-6) | Caregiver Demographics | $45$ ($1.83\%$) | $35$ ($1.63\%$) | $10$ ($3.21\%$) | $2.95$ | $0.0862$ | NO |
| `bl_fa_age` | Father's age (years) | Caregiver Demographics | $311$ ($12.64\%$) | $261$ ($12.15\%$) | $50$ ($16.03\%$) | $3.37$ | $0.0663$ | NO |
| `bl_fa_educ_level` | Father's education level (1-6) | Caregiver Demographics | $351$ ($14.26\%$) | $294$ ($13.68\%$) | $57$ ($18.27\%$) | $4.32$ | $0.0376$ | **YES ($p < 0.05$)** |
| `bl_child_sib_tot` | Number of siblings in household | Household Structure | $0$ ($0.00\%$) | $0$ ($0.00\%$) | $0$ ($0.00\%$) | $0.00$ | $1.0000$ | NO |
| `bl_hhadults` | Number of adults in household | Household Structure | $6$ ($0.24\%$) | $3$ ($0.14\%$) | $3$ ($0.96\%$) | $4.57$ | $0.0326$ | **YES ($p < 0.05$)** |
| `bl_f_b` | Father lives in household (1=Yes) | Household Structure | $7$ ($0.28\%$) | $4$ ($0.19\%$) | $3$ ($0.96\%$) | $3.37$ | $0.0666$ | NO |
| `bl_qses_index` | SES index quintile (1-5) | Socioeconomic Status | $12$ ($0.49\%$) | $9$ ($0.42\%$) | $3$ ($0.96\%$) | $0.73$ | $0.3947$ | NO |
| `bl_mics_tot` | MICS stimulation activities (0-6) | Home Environment | $218$ ($8.86\%$) | $191$ ($8.89\%$) | $27$ ($8.65\%$) | $0.00$ | $0.9766$ | NO |
| `provincia` | Province of residence | Geography | $0$ ($0.00\%$) | $0$ ($0.00\%$) | $0$ ($0.00\%$) | $0.00$ | $1.0000$ | NO |
| `distrito` | District of residence | Geography | $0$ ($0.00\%$) | $0$ ($0.00\%$) | $0$ ($0.00\%$) | $0.00$ | $1.0000$ | NO |

### Table 5.2: Multivariable Missingness Prediction Models

We fit cluster-robust linear probability models (LPM) and logistic regression models predicting outcome missingness ($Y = 1$ if primary outcome missing, $0$ if observed; $N = 2,373$ complete baseline cases):

| Predictor Variable | LPM Coef. ($\beta$) | Cluster SE | 95% CI (LPM) | $p$-value (LPM) | Adjusted Odds Ratio (AOR) | 95% CI (AOR) | $p$-value (Logit) | Substantive Interpretation |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Intercept** | $+0.2943$ | $0.0453$ | $[+0.2056,\, +0.3830]$ | $< 0.0001$ | — | — | — | Baseline missingness anchor. |
| **Home Visits (`hv`)** | **$-0.0486$** | $0.0177$ | $[-0.0833,\, -0.0139]$ | **$0.0060$** | **$0.559$** | $[0.354,\, 0.884]$ | **$0.0129$** | Decreases missingness probability by $4.86$ pp ($44.1\%$ lower odds). |
| **Afini (`afini`)** | **$+0.0615$** | $0.0174$ | $[+0.0274,\, +0.0956]$ | **$0.0004$** | **$1.685$** | $[1.240,\, 2.290]$ | **$0.0009$** | Increases missingness probability by $6.15$ pp ($68.5\%$ higher odds). |
| **Mother's Age (`bl_mo_age`)** | **$-0.0053$** | $0.0011$ | $[-0.0075,\, -0.0031]$ | **$< 0.0001$** | **$0.950$** | $[0.929,\, 0.970]$ | **$< 0.0001$** | Strong protective factor: older mothers have significantly lower attrition. |
| **Low Birth Weight (`bl_low_bweight`)** | **$+0.0617$** | $0.0281$ | $[+0.0065,\, +0.1168]$ | **$0.0284$** | **$1.604$** | $[1.037,\, 2.481]$ | **$0.0337$** | Infant vulnerability: low birth weight infants have $6.17$ pp higher missingness. |
| **Household Adults (`bl_hhadults`)** | **$-0.0134$** | $0.0057$ | $[-0.0245,\, -0.0023]$ | **$0.0178$** | **$0.886$** | $[0.796,\, 0.986]$ | **$0.0267$** | Caregiver capacity: more adults in household reduce missingness probability. |
| **Baseline CREDI (`bl_z_overall`)** | $-0.0187$ | $0.0132$ | $[-0.0445,\, +0.0071]$ | $0.1555$ | $0.852$ | $[0.684,\, 1.062]$ | $0.1539$ | Directionally negative: lower baseline development associates with higher attrition. |
| **Child Age (`bl_childage`)** | $+0.0002$ | $0.0039$ | $[-0.0074,\, +0.0078]$ | $0.9665$ | $1.002$ | $[0.963,\, 1.042]$ | $0.9297$ | No independent association. |
| **Child Sex (`child_female`)** | $-0.0226$ | $0.0143$ | $[-0.0506,\, +0.0053]$ | $0.1124$ | $0.822$ | $[0.640,\, 1.056]$ | $0.1256$ | Female infants have non-significantly lower missingness. |
| **Father in HH (`bl_f_b`)** | $-0.0328$ | $0.0220$ | $[-0.0759,\, +0.0103]$ | $0.1365$ | $0.729$ | $[0.472,\, 1.127]$ | $0.1546$ | Non-significant protective trend. |
| **SES Quintile (`bl_qses_index`)** | $+0.0061$ | $0.0052$ | $[-0.0041,\, +0.0163]$ | $0.2386$ | $1.054$ | $[0.964,\, 1.152]$ | $0.2520$ | No independent linear gradient after controlling for other indicators. |

Generated data files:
- [`baseline_missingness_summary.csv`](file:///D:/Niyati/validation/V5_missingness_attrition_audit/outputs/baseline_missingness_summary.csv)
- [`missingness_association_models.csv`](file:///D:/Niyati/validation/V5_missingness_attrition_audit/outputs/missingness_association_models.csv)

---

## 6. Missing-Data Patterns & Reason Documentation

We mapped the joint missingness structure across the primary outcome and $13$ key baseline variables across the entire enrolled cohort ($N = 2,461$).

### Table 6.1: Predominant Joint Missingness Patterns

| Pattern ID | Outcome Status | Missing Baseline Variables | Count ($N$) | Share of Trial (%) | Cumulative Share (%) | Substantive Profile |
| :---: | :--- | :--- | :---: | :---: | :---: | :--- |
| **Pattern 01** | **Observed** | **None (Fully Complete Baseline)** | **$1,628$** | **$66.15\%$** | $66.15\%$ | Fully complete cases on outcome and all 13 baseline covariates. |
| **Pattern 02** | **Missing** | **None (Fully Complete Baseline)** | **$223$** | **$9.06\%$** | $75.21\%$ | **Outcome attriters with completely intact baseline profiles ($71.5\%$ of all attriters).** |
| **Pattern 03** | Observed | Father age, Father education | $212$ | $8.61\%$ | $83.83\%$ | Observed outcome; missing father demographic indicators. |
| **Pattern 04** | Observed | MICS stimulation activities | $161$ | $6.54\%$ | $90.37\%$ | Observed outcome; missing baseline home stimulation count. |
| **Pattern 05** | Missing | Father age, Father education | $43$ | $1.75\%$ | $92.12\%$ | Missing outcome and missing father demographics. |
| **Pattern 06** | Observed | Father education only | $39$ | $1.58\%$ | $93.70\%$ | Observed outcome; missing father education only. |
| **Pattern 07** | Observed | Low birth weight | $28$ | $1.14\%$ | $94.84\%$ | Observed outcome; missing birth weight indicator. |
| **Pattern 08** | Observed | Father age, education & MICS | $26$ | $1.06\%$ | $95.90\%$ | Observed outcome; multiple missing baseline indicators. |
| **Pattern 09** | Missing | MICS stimulation activities | $22$ | $0.89\%$ | $96.79\%$ | Missing outcome; missing baseline home stimulation count. |
| **Pattern 10** | Observed | Mother age, Mother education | $20$ | $0.81\%$ | $97.60\%$ | Observed outcome; missing maternal demographics. |
| **Patterns 11–31** | Mixed | Remaining minor combinations | $59$ | $2.40\%$ | $100.00\%$ | 21 distinct sparse residual patterns ($1$ to $8$ participants each). |

### Table 6.2: Documented Attrition Reasons vs. Speculative Explanations

In accordance with strict audit integrity rules, we separate directly documented facts from unverified assumptions:

| Category | Finding / Reason | Empirical Evidence in Released Dataset / Codebook | Analytical Implications |
| :--- | :--- | :--- | :--- |
| **Directly Documented** | **Child Mortality** ($N=10$) | Explicitly recorded in `final_status == 2` ("child died"). | Survival truncation; cannot be imputed under standard MAR missingness paradigms. |
| **Directly Documented** | **Household Migration** ($N=100$) | Explicitly recorded in `final_status == 3` ("moved away"). | True geographic attrition; higher in Digital ($5.03\%$) than Home Visits ($2.52\%$). |
| **Directly Documented** | **Explicit Refusal** ($N=65$) | Explicitly recorded in `final_status == 4` ("refused"). | Active caregiver refusal; nearly $6\times$ higher in Digital ($3.75\%$) than Home Visits ($0.63\%$). |
| **Directly Documented** | **Unreached After 4+ Visits** ($N=103$) | Explicitly recorded in `final_status == 5` ("no contact after 4+ visits"). | Fieldwork exhaustion; $> 3\times$ higher in Digital ($5.20\%$) than Home Visits ($1.58\%$). |
| **Directly Documented** | **Survey-Assessed, GSED Missing** ($N=29$) | `final_status == 1`, but `el_gsed_dscore` is missing. | Incomplete endline battery (child absent, asleep, uncooperative, or assessor unrecorded). |
| **Directly Documented** | **Singleton Age-Band Exclusions** ($N=5$) | Assessed raw GSED recorded, but `gsed_sd` undefined ($n=1$). | Methodological drop during within-sample age standardization in Stata DO script. |
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
| **Complete-Case Analysis** *(Published Table 2)* | ITT Effect in Assessed Subsample ($N = 2,149$) | Assumes MCAR: $Y_{\text{miss}} \perp Y \mid (T, \mathbf{X})$. | **Strongly violated:** Missingness differs by arm ($6.31\%$ vs $15.84\%$, $p < 0.001$) and vulnerability ($p < 0.05$). | Simple, transparent, exact match to published study sample. | Discards $312$ cases ($12.68\%$). Severe risk of selection bias due to differential Digital attrition. | **Retain as primary replication benchmark only.** Must NOT be the sole basis for substantive decision-making. |
| **Multiple Imputation for Primary Outcome (under MAR)** | Full-Cohort ITT Effect ($N = 2,461$) | Assumes MAR: $P(R=1 \mid Y, \mathbf{X}, T) = P(R=1 \mid \mathbf{X}, T)$. Correct imputation model. | **Strong observed predictor base:** $71.5\%$ of attriters have full baseline profiles; rich demographic and geographic predictors available. | Recovers full randomized sample ($N=2,461$). Restores ITT principle. Incorporates cluster structure and baseline predictors. | MAR is inherently unprovable. Child mortality ($N=10$) violates MAR. V3 continuous models showed support violations (e.g. $100\%$ invalid integer draws for `bl_hhadults`). | **Recommended as primary full-cohort sensitivity analysis**, provided that bounded models are used and mortality is handled separately. |
| **Inverse Probability Weighting (IPW)** | Weighted Average Treatment Effect (Re-weighted to $N=2,461$) | Selection on observables & Positivity: $P(R=1 \mid \mathbf{X}, T) > 0$. | **Empirically well-supported:** Positivity holds across all clusters (min cluster follow-up rate $= 25.0\%$). Strong selection model fit. | Does not require specifying conditional outcome distribution for non-responders. Re-weights complete cases to baseline cohort. | Potential weight instability if extreme. Does not address unobserved confounding (MNAR) or truncation by death. | **Feasible secondary sensitivity check** to assess whether re-weighting complete cases alters effect estimates. |
| **MNAR Tipping-Point / Delta-Adjustment** | Robustness Boundary for Treatment Effects | Assumes MNAR: $E[Y_{\text{miss}} \mid \mathbf{X}, T] = E[Y_{\text{obs}} \mid \mathbf{X}, T] + \delta_T$. | **Substantively compelling:** $65$ explicit refusals, $103$ unreached; Digital attrition was $2.5\times$ higher than Home Visits. | Directly models informative attrition without assuming benign dropouts. Transparently reveals tipping point where effects vanish. | Requires justification of plausible offset range $\delta$. Generates a sensitivity continuum rather than a single point estimate. | **Strongly recommended as the definitive stress-test** for Niyati. Varying $\delta \in [-0.30, +0.10]$ SD will establish robustness. |

Generated data file:
- [`imputation_feasibility.csv`](file:///D:/Niyati/validation/V5_missingness_attrition_audit/outputs/imputation_feasibility.csv)

---

## 8. Verification Manifest & Output Catalog

All generated outputs are located in [`validation/V5_missingness_attrition_audit/outputs/`](file:///D:/Niyati/validation/V5_missingness_attrition_audit/outputs/):

| Output File | Description | Record Count |
| :--- | :--- | :---: |
| [`sample_flow_reconciliation.csv`](file:///D:/Niyati/validation/V5_missingness_attrition_audit/outputs/sample_flow_reconciliation.csv) | Step-by-step sample-flow reconstruction, resolving the 29-case gap and explaining the 20-case footnote gap. | 10 rows |
| [`outcome_missingness_by_arm.csv`](file:///D:/Niyati/validation/V5_missingness_attrition_audit/outputs/outcome_missingness_by_arm.csv) | Primary outcome missingness rates by randomized arm with cluster-robust LPM and logistic models and conservative $df$. | 5 rows |
| [`cluster_missingness_summary.csv`](file:///D:/Niyati/validation/V5_missingness_attrition_audit/outputs/cluster_missingness_summary.csv) | Cluster-level missingness distributions, quartile dispersions, zero-missing counts, and top 10%/20% concentration shares. | 4 rows |
| [`baseline_missingness_summary.csv`](file:///D:/Niyati/validation/V5_missingness_attrition_audit/outputs/baseline_missingness_summary.csv) | Baseline covariate missingness rates overall and contrasted by primary outcome observation status with $\chi^2$ tests. | 15 rows |
| [`missingness_association_models.csv`](file:///D:/Niyati/validation/V5_missingness_attrition_audit/outputs/missingness_association_models.csv) | Comprehensive regression models (bivariate, arm-only, multivariable LPM, and multivariable Logistic) predicting missingness. | 40 rows |
| [`missing_pattern_summary.csv`](file:///D:/Niyati/validation/V5_missingness_attrition_audit/outputs/missing_pattern_summary.csv) | Mapping of all 31 distinct joint missingness patterns across outcome and 13 key baseline covariates. | 31 rows |
| [`imputation_feasibility.csv`](file:///D:/Niyati/validation/V5_missingness_attrition_audit/outputs/imputation_feasibility.csv) | Methodological comparative assessment of Complete-Case, MAR Imputation, IPW, and MNAR Tipping-Point strategies. | 4 rows |
| [`v5_summary.json`](file:///D:/Niyati/validation/V5_missingness_attrition_audit/outputs/v5_summary.json) | Complete machine-readable metadata summary of all sample flows, missingness models, tests, and feasibility verdicts. | 100 lines |

---

## 9. Implications for the Eventual Niyati Analysis

1. **Replication Integrity vs. Analytical Decision-Making:**
   - For exact replication of published Table 2, the complete-case sample of $N = 2,149$ must be utilized.
   - However, for independent decision-making regarding policy scale-up or intervention equivalence, complete-case results cannot be accepted uncritically. The marked differential attrition between Digital ($15.84\%$) and Home Visits ($6.31\%$) means that complete-case analysis compares a more heavily selected Digital sample against a more complete Home Visits sample.
2. **Mandatory Sensitivity Architecture:**
   - Any eventual Niyati causal inference pipeline must report:
     1. Primary Complete-Case Benchmark ($N = 2,149$).
     2. Full-Cohort Multiple Imputation under MAR ($N = 2,461$), utilizing bounded regression models for counts and separating mortality cases.
     3. Inverse Probability Weighting (IPW) using the validated multivariable selection model.
     4. MNAR Tipping-Point Grid: evaluating whether an unobserved developmental deficit of $\delta \in [-0.20, -0.05]$ SD among Digital non-responders widens the active contrast in favor of Home Visits or alters statistical significance.
