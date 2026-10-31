# Task V4: Statistical Precision, Small-Cluster Inference & Power Audit

**Project:** Niyati  
**Working Directory:** `validation/V4_power_precision_audit/`  
**Repository:** `nayanojwal0810/Yantra---Industrial-Anomaly-Detection-Monitoring`  
**Branch:** `project2/urja-validation`  
**Authoritative Data Source:** `data/raw/doi_10_5061_dryad_nzs7h4551__v20260226.zip` (`digitalECD_26Feb2026.dta`)  
**Base Commit:** `90f4fa61b92930d628cadde4ae47d70da64cc6c9`

---

## 1. Executive Summary & Core Audit Verdicts

This audit independently evaluates the statistical precision, small-cluster inference properties, pairwise treatment contrasts, and prospective statistical power of the cluster-randomized trial reported in:
> *Digital support systems to improve child development in Peru: A cluster-randomized controlled open label trial*.

All analyses utilize the authoritative enrolled sample ($N = 2,461$ across $K = 159$ clusters) and the primary analysis sample ($N = 2,149$ valid `gsed_Z` outcomes across the same $K = 159$ clusters), identically reproducing the primary outcome derivation validated in V1–V3.

### Core Verdicts

1. **Extreme Cluster Allocation Asymmetry:**  
   The trial assigned 68 clusters (42.8%) to Control, 72 clusters (45.3%) to Digital (Afini), but only **19 clusters (11.9%)** to Home Visits. Control and Digital arms have **3.58$\times$ and 3.79$\times$ more clusters** than Home Visits, respectively. This severe structural imbalance severely constrains the statistical precision of any comparison involving Home Visits.
2. **Severe Cluster-Size Imbalance:**  
   Across all arms, cluster sizes vary by up to 42-fold (ranging from singletons $n=1$ to $n=42$). The coefficient of variation of cluster size ($CV$) is **0.702** in Control, **0.478** in Home Visits, **0.633** in Digital, and **0.642** overall (0.6419 enrolled, 0.6450 analysis). Across the entire trial, the largest 10% of clusters (16 clusters) contain **22.84%** of all enrolled participants (562 / 2,461) and **22.99%** of analysis participants (494 / 2,149). Within individual arms, the top deciles account for 24.54% (Control, 7 clusters), 17.67% (Home Visits, 2 clusters), and 24.87% (Digital, 8 clusters).
3. **Substantial Effective Sample Size Degradation:**  
   At the empirical null-model intracluster correlation coefficient ($\rho = 0.03202$), design effects range between **1.624 and 1.699** across arms, and **1.668** (1.6679) for the overall trial. Effective sample sizes are degraded by approximately **40%** relative to nominal counts:
   - **Control:** nominal $N = 970 \rightarrow N_{\text{eff}} = 588.0$ (60.62%)
   - **Home Visits:** nominal $N = 317 \rightarrow N_{\text{eff}} = 195.2$ (61.57%)
   - **Digital:** nominal $N = 1,174 \rightarrow N_{\text{eff}} = 690.9$ (58.85%)
   - **Total Trial:** nominal $N = 2,461 \rightarrow N_{\text{eff}} = 1,475.5$ (59.96%)
4. **Disparity in Estimator Precision:**  
   The cluster-robust standard error for Home Visits vs Control ($SE = 0.0689$ adjusted, $0.0662$ unadjusted) is **over 50% larger** than that for Digital vs Control ($SE = 0.0447$ adjusted, $0.0450$ unadjusted). Consequently, confidence intervals for Home Visits are 54% wider.
5. **Direct Active-Intervention Contrast (Home Visits vs Digital):**  
   From the full covariance matrix of the multiple-imputation model ($M=250$, seed `20260226`), the adjusted difference between Home Visits and Digital is:
   $$\hat{\Delta} = +0.0596\text{ SD},\quad SE = 0.0682,\quad t = 0.875,\quad p = 0.3831,\quad 95\%\text{ CI } [-0.0750,\, +0.1943]\text{ SD}$$
   The difference is statistically non-significant.
6. **Equivalence and Non-Inferiority Refuted:**  
   The non-significant difference ($p = 0.3831$) **DOES NOT support any claim of clinical equivalence or non-inferiority** between Digital and Home Visits. The 95% confidence interval spans **0.269 SD** (widening to **0.289 SD** under conservative small-sample degrees of freedom $[-0.0847, +0.2040]$). This interval encompasses substantial Home Visits superiority (up to $+0.194$ SD, nearly matching the trial's target effect of $0.20$ SD) as well as Digital superiority (down to $-0.075$ SD).
7. **Underpowered Direct Active Contrast:**  
   The trial had only **11.0% statistical power** to detect the observed $0.06$ SD difference between Home Visits and Digital, and only **66.2% power** to detect an effect as large as $0.20$ SD. For 80% power, Home Visits vs Digital requires an effect size of at least **$0.236$ SD** ($0.247$ SD under conservative degrees of freedom).

---

## 2. Cluster Allocation & Size Imbalance Diagnostics

All 159 clusters were cross-referenced against trial records and provincial boundaries. No populated cluster contains mixed `arm_itt` assignments, confirming cluster assignment integrity. (Note: as established in the V1 audit, cluster assignment integrity does not imply the absence of individual-level exposure crossover, as four Control-assigned participants had positive digital tracking records).

### Table 2.1: Enrolled vs Analysis Sample Cluster Allocation

| Trial Arm | Populated Clusters ($K$) | Cluster Share (%) | Enrolled Part. ($N$) | Enrolled Part. Share (%) | Analysis Part. ($N$) | Analysis Part. Share (%) | Enrolled Mean Size ($\bar{n}$) | Enrolled $CV$ | Enrolled Min–Max | Top 10% Clusters Share (%) | Benchmark Reconciliation |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Control** | 68 | 42.77% | 970 | 39.41% | 864 | 40.20% | 14.26 | 0.702 | 1 – 42 | 24.54% (7 cl) | **MATCH** |
| **Home Visits** | 19 | 11.95% | 317 | 12.88% | 297 | 13.82% | 16.68 | 0.478 | 3 – 28 | 17.67% (2 cl) | **MATCH** |
| **Digital (Afini)** | 72 | 45.28% | 1,174 | 47.70% | 988 | 45.97% | 16.31 | 0.633 | 1 – 42 | 24.87% (8 cl) | **MATCH** |
| **Total Trial** | **159** | **100.0%** | **2,461** | **100.0%** | **2,149** | **100.0%** | **15.48** | **0.642** | **1 – 42** | **22.84% (16 cl)** | **MATCH** |

### Analytical Dimensions of Imbalance
- **Cluster Allocation Ratio:** Control has $68 / 19 = 3.58\times$ the clusters of Home Visits; Digital has $72 / 19 = 3.79\times$ the clusters of Home Visits.
- **Participant Allocation Ratio:** Control has $3.06\times$ and Digital has $3.70\times$ the enrolled participants of Home Visits.
- **Coefficient of Variation ($CV$):** With $CV = 0.702$ in Control, $0.478$ in Home Visits, and $0.633$ in Digital, and **0.642** overall (0.6419 enrolled, 0.6450 analysis), all arms far exceed the threshold ($CV > 0.23$) identified by Eldridge et al. (2006) where cluster-size variation substantially inflates design effects beyond standard equal-size approximations.
- **Top 10% Concentration (Within-Arm vs Trial-Wide):**
  - **Within-arm top 10%:** Control (7 clusters, 24.54% of arm sample), Home Visits (2 clusters, 17.67% of arm sample), Digital (8 clusters, 24.87% of arm sample).
  - **Trial-wide top 10%:** Across the entire trial, the top 16 largest clusters contain 562 of the 2,461 enrolled participants (**22.84%**) and 494 of the 2,149 analysis participants (**22.99%**). Arm-specific top-decile shares must not be added across arms to represent the trial-wide decile share.

Generated data files:
- [`cluster_size_summary.csv`](file:///D:/Niyati/validation/V4_power_precision_audit/outputs/cluster_size_summary.csv)
- [`cluster_size_distribution.csv`](file:///D:/Niyati/validation/V4_power_precision_audit/outputs/cluster_size_distribution.csv)
- [`cluster_size_imbalance_summary.csv`](file:///D:/Niyati/validation/V4_power_precision_audit/outputs/cluster_size_imbalance_summary.csv)

---

## 3. Design Effects & Effective Sample Size Sensitivity

Under variable cluster sizes, the design effect ($DE$) is calculated using the formula from Eldridge et al. (2006):
$$DE = 1 + \left[(CV^2 + 1)\bar{n} - 1\right]\rho$$
The effective sample size is:
$$N_{\text{eff}} = \frac{N}{DE}$$

We evaluate 5 ICC scenarios:
1. $\rho = 0.01$: Low clustering benchmark.
2. $\rho = 0.03$: Moderate clustering scenario.
3. $\rho = 0.03202$: **Empirical null-model ICC** estimated from the reconstructed primary outcome (`gsed_Z`) across all 159 clusters.
4. $\rho = 0.05$: Substantial clustering scenario.
5. $\rho = 0.10$: High clustering scenario.

### Table 3.1: Design Effect ($DE$) & Effective Sample Size ($N_{\text{eff}}$) Across Arms

| Arm | Metric | $\rho = 0.01$ | $\rho = 0.03$ | $\rho = 0.03202$ (Empirical) | $\rho = 0.05$ | $\rho = 0.10$ |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Control** ($N=970$) | Design Effect ($DE$) | 1.203 | 1.609 | **1.650** | 2.014 | 3.029 |
| | Effective $N$ ($N_{\text{eff}}$) | 806.4 | 603.0 | **588.0** | 481.6 | 320.3 |
| | % of Nominal $N$ | 83.1% | 62.2% | **60.6%** | 49.6% | 33.0% |
| **Home Visits** ($N=317$) | Design Effect ($DE$) | 1.195 | 1.585 | **1.624** | 1.975 | 2.950 |
| | Effective $N$ ($N_{\text{eff}}$) | 265.3 | 200.0 | **195.2** | 160.5 | 107.5 |
| | % of Nominal $N$ | 83.7% | 63.1% | **61.6%** | 50.6% | 33.9% |
| **Digital** ($N=1,174$) | Design Effect ($DE$) | 1.218 | 1.655 | **1.699** | 2.092 | 3.184 |
| | Effective $N$ ($N_{\text{eff}}$) | 963.6 | 709.3 | **690.9** | 561.2 | 368.7 |
| | % of Nominal $N$ | 82.1% | 60.4% | **58.9%** | 47.8% | 31.4% |
| **Total Trial** ($N=2,461$) | Design Effect ($DE$) | 1.209 | 1.626 | **1.668** | 2.043 | 3.086 |
| | Effective $N$ ($N_{\text{eff}}$) | 2,036.3 | 1,513.8 | **1,475.5** | 1,204.7 | 797.5 |
| | % of Nominal $N$ | 82.7% | 61.5% | **60.0%** | 48.9% | 32.4% |

Generated data files:
- [`design_effect_sensitivity.csv`](file:///D:/Niyati/validation/V4_power_precision_audit/outputs/design_effect_sensitivity.csv)
- [`effective_sample_size_sensitivity.csv`](file:///D:/Niyati/validation/V4_power_precision_audit/outputs/effective_sample_size_sensitivity.csv)

---

## 4. Direct Pairwise Treatment Contrasts

### Mathematical Formulation of Direct Contrasts

In the three-arm linear model with Control as the reference:
$$y_{ic} = \beta_0 + \beta_{\text{HV}} T_{\text{HV}, c} + \beta_{\text{Dig}} T_{\text{Dig}, c} + \mathbf{X}_{ic}'\boldsymbol{\gamma} + \varepsilon_{ic}$$

The comparisons against Control are directly given by the regression parameters:
$$\Delta_{\text{HV vs Ctrl}} = \beta_{\text{HV}},\quad \Delta_{\text{Dig vs Ctrl}} = \beta_{\text{Dig}}$$

The direct contrast between the two active interventions is:
$$\Delta_{\text{HV vs Dig}} = \beta_{\text{HV}} - \beta_{\text{Dig}}$$

Its standard error is **not** simply $\sqrt{SE(\beta_{\text{HV}})^2 + SE(\beta_{\text{Dig}})^2}$. Because both coefficients are estimated within the same regression model sharing a common reference group (Control) and error terms, their estimates have non-zero sampling covariance:
$$\operatorname{Var}\left(\hat{\beta}_{\text{HV}} - \hat{\beta}_{\text{Dig}}\right) = \operatorname{Var}\left(\hat{\beta}_{\text{HV}}\right) + \operatorname{Var}\left(\hat{\beta}_{\text{Dig}}\right) - 2\operatorname{Cov}\left(\hat{\beta}_{\text{HV}},\, \hat{\beta}_{\text{Dig}}\right)$$

In cluster-robust estimation (CR1), $\operatorname{Cov}\left(\hat{\beta}_{\text{HV}},\, \hat{\beta}_{\text{Dig}}\right) > 0$. Failing to subtract this positive covariance would overestimate the variance and inflate standard errors. For multiple imputation ($M=250$), Rubin's rules are applied to the contrast estimates and complete covariance matrices across all imputations.

### Table 4.1: Pairwise Contrasts — Unadjusted Model ($N=2,149, K=159, df=158$)

| Contrast Name | Point Est. | Display | Standard Error | Degrees of Freedom | 95% Confidence Interval | CI Width | $t$-stat | $p$-value | Interpretation |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Home Visits vs Control** | $+0.1669$ | $+0.17$ | $0.0662$ | $158.0$ | $[+0.0361,\, +0.2977]$ | $0.2616$ | $2.520$ | $0.0127$ | Statistically significant ($p < 0.05$). |
| **Digital vs Control** | $+0.1394$ | $+0.14$ | $0.0450$ | $158.0$ | $[+0.0506,\, +0.2283]$ | $0.1777$ | $3.099$ | $0.0023$ | Statistically significant ($p < 0.01$). |
| **Home Visits vs Digital** | $+0.0275$ | $+0.03$ | $0.0652$ | $158.0$ | $[-0.1012,\, +0.1562]$ | $0.2574$ | $0.422$ | $0.6738$ | **Non-significant ($p = 0.67$)**. Wide CI $[-0.10, +0.16]$. |

### Table 4.2: Pairwise Contrasts — Adjusted Model (Multiple Imputation $M=250$, Seed `20260226`)

| Contrast Name | Point Est. | Display | Standard Error | Barnard-Rubin $df$ | 95% Confidence Interval | CI Width | $t$-stat | $p$-value | Benchmark Type | V3.3 Benchmark | Diff. vs Benchmark | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- | :---: | :---: | :--- |
| **Home Visits vs Control** | $+0.1663$ | $+0.17$ | $0.0689$ | $155.9$ | $[+0.0302,\, +0.3024]$ | $0.2722$ | $2.413$ | $0.0170$ | `DIRECT_TREATMENT_COEFFICIENT` | $0.16626152216742296$ | $1.39 \times 10^{-16}$ | `EXACT_REPRODUCTION (<1e-6)` |
| **Digital vs Control** | $+0.1066$ | $+0.11$ | $0.0447$ | $155.8$ | $[+0.0184,\, +0.1948]$ | $0.1764$ | $2.388$ | $0.0182$ | `DIRECT_TREATMENT_COEFFICIENT` | $0.10663017547660632$ | $1.39 \times 10^{-17}$ | `EXACT_REPRODUCTION (<1e-6)` |
| **Home Visits vs Digital** | $+0.0596$ | $+0.06$ | $0.0682$ | $155.9$ | $[-0.0750,\, +0.1943]$ | $0.2693$ | $0.875$ | $0.3831$ | `ALGEBRAICALLY_DERIVED_CONTRAST` | $0.05963134669081664$ | $1.73 \times 10^{-16}$ | `DERIVED_FROM_V3_TREATMENT_COEFFICIENTS_WITHIN_1E-6` |

*Note on V3.3 Benchmark Verification & Distinct Contrast Classification:*
- Full-precision benchmark coefficients are read directly with `float_precision="round_trip"` from `validation/V3_primary_itt_reproduction/outputs/pooled_parameter_diagnostics.csv`:
  - `hv` parameter: $0.16626152216742296$ (V4: $0.16626152216742282$, absolute difference $= 1.3877787807814457 \times 10^{-16} < 10^{-6}$). Direct reproduction of independently reported V3.3 treatment coefficient.
  - `afini` parameter: $0.10663017547660632$ (V4: $0.10663017547660633$, absolute difference $= 1.3877787807814457 \times 10^{-17} < 10^{-6}$). Direct reproduction of independently reported V3.3 treatment coefficient.
- **Direct Active Contrast (Home Visits vs Digital):**
  - V3.3 did not independently estimate or report the direct active-intervention contrast between Home Visits and Digital.
  - The V3.3 benchmark is therefore derived algebraically from the two independently estimated treatment coefficients:
    $$\beta_{\text{V3, derived}} = \beta_{\text{HV}} - \beta_{\text{Digital}} = 0.16626152216742296 - 0.10663017547660632 = 0.05963134669081664\text{ SD}$$
  - The V4 estimated contrast is $0.05963134669081647\text{ SD}$.
  - Absolute numerical difference: $|0.05963134669081647 - 0.05963134669081664| = 1.734723475976807 \times 10^{-16} < 10^{-6}$.
  - Status is explicitly reported as `DERIVED_FROM_V3_TREATMENT_COEFFICIENTS_WITHIN_1E-6`. It is strictly not described as an independent V3.3 reproduction.
  - Substantive interpretation: Non-significant difference ($p = 0.3831$). The wide 95% CI $[-0.0750, +0.1943]$ (span $0.27$ SD) cannot rule out either substantial Home Visits superiority ($+0.19$ SD) or Digital superiority ($-0.08$ SD). Does NOT establish equivalence or non-inferiority.

Generated data files:
- [`unadjusted_pairwise_contrasts.csv`](file:///D:/Niyati/validation/V4_power_precision_audit/outputs/unadjusted_pairwise_contrasts.csv)
- [`adjusted_pairwise_contrasts.csv`](file:///D:/Niyati/validation/V4_power_precision_audit/outputs/adjusted_pairwise_contrasts.csv)

---

## 5. Small-Sample Cluster-Robust Inference Sensitivity

In cluster-randomized trials with unequal cluster sizes and small numbers of clusters in specific treatment arms ($K_{\text{HV}} = 19$), standard Liang-Zeger CR1 cluster-robust standard errors can suffer from finite-sample downward bias, producing anti-conservative $p$-values and artificially narrow confidence intervals (Cameron & Miller 2015; Imbens & Kolesár 2016).

### Audit Finding on Tooling Availability
1. **CR2 Bias-Reduced Covariance (`clubSandwich`):**  
   Per protocol rule 5.2, local environment inspection confirmed that neither R nor the R package `clubSandwich` (Pustejovsky & Tipton 2018) is installed on this host. In accordance with strict audit integrity guidelines, no ad-hoc, unvalidated Python re-implementation was fabricated.
2. **Wild Cluster Bootstrap (`wildboottest`):**  
   The Python library `wildboottest` is not installed locally. Furthermore, as demonstrated by MacKinnon & Webb (2017), when treatment is assigned to very few clusters ($K=19$), the wild cluster bootstrap exhibits asymmetric rejection rates and cannot serve as definitive proof of inference reliability.
3. **Conservative Degrees-of-Freedom Sensitivity:**  
   As specified in the audit instructions, we implement the conservative degrees-of-freedom correction recommended by Cameron & Miller (2015):
   $$df_{\text{conservative}} = \min(K_a, K_b) - 1$$
   - **HV vs Control ($19$ vs $68$ clusters):** $df_{\text{conservative}} = \min(19, 68) - 1 = 18$
   - **HV vs Digital ($19$ vs $72$ clusters):** $df_{\text{conservative}} = \min(19, 72) - 1 = 18$
   - **Digital vs Control ($72$ vs $68$ clusters):** $df_{\text{conservative}} = \min(72, 68) - 1 = 67$

For multiple imputation, this complete-data degrees of freedom ($\nu_{\text{com}} = 18$) is propagated into the Barnard-Rubin formula, reducing effective pooled degrees of freedom from $155.9$ to **$16.3$**.

### Table 5.1: Small-Sample Inference Sensitivity Comparison

| Contrast Name | Model | Inference Specification | $df$ | Critical $t_{0.025}$ | Point Est. | $SE$ | 95% Confidence Interval | CI Width | Width Inflation | $p$-value | Retains Sig.? |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **HV vs Control** | Unadj. | Conventional CR1 | $158.0$ | $1.975$ | $+0.1669$ | $0.0662$ | $[+0.0361,\, +0.2977]$ | $0.2615$ | Baseline | $0.0127$ | Yes |
| | Unadj. | Conservative $df$ | **$18.0$** | **$2.101$** | $+0.1669$ | $0.0662$ | $[+0.0278,\, +0.3060]$ | $0.2782$ | **$+6.37\%$** | $0.0213$ | Yes |
| | Adj. MI | Conventional Barnard-Rubin | $155.9$ | $1.975$ | $+0.1663$ | $0.0689$ | $[+0.0302,\, +0.3024]$ | $0.2722$ | Baseline | $0.0170$ | Yes |
| | Adj. MI | Conservative Barnard-Rubin | **$16.3$** | **$2.117$** | $+0.1663$ | $0.0689$ | $[+0.0204,\, +0.3121]$ | $0.2917$ | **$+7.17\%$** | $0.0280$ | Yes |
| **Digital vs Control** | Unadj. | Conventional CR1 | $158.0$ | $1.975$ | $+0.1394$ | $0.0450$ | $[+0.0505,\, +0.2283]$ | $0.1778$ | Baseline | $0.0023$ | Yes |
| | Unadj. | Conservative $df$ | **$67.0$** | **$1.996$** | $+0.1394$ | $0.0450$ | $[+0.0496,\, +0.2292]$ | $0.1796$ | **$+1.06\%$** | $0.0028$ | Yes |
| | Adj. MI | Conventional Barnard-Rubin | $155.8$ | $1.975$ | $+0.1066$ | $0.0447$ | $[+0.0184,\, +0.1948]$ | $0.1764$ | Baseline | $0.0182$ | Yes |
| | Adj. MI | Conservative Barnard-Rubin | **$65.0$** | **$1.997$** | $+0.1066$ | $0.0447$ | $[+0.0174,\, +0.1958]$ | $0.1784$ | **$+1.11\%$** | $0.0199$ | Yes |
| **HV vs Digital** | Unadj. | Conventional CR1 | $158.0$ | $1.975$ | $+0.0275$ | $0.0652$ | $[-0.1013,\, +0.1563]$ | $0.2576$ | Baseline | $0.6738$ | No |
| | Unadj. | Conservative $df$ | **$18.0$** | **$2.101$** | $+0.0275$ | $0.0652$ | $[-0.1095,\, +0.1645]$ | $0.2740$ | **$+6.37\%$** | $0.6782$ | No |
| | Adj. MI | Conventional Barnard-Rubin | $155.9$ | $1.975$ | $+0.0596$ | $0.0682$ | $[-0.0750,\, +0.1943]$ | $0.2693$ | Baseline | $0.3831$ | No |
| | Adj. MI | Conservative Barnard-Rubin | **$16.3$** | **$2.117$** | $+0.0596$ | $0.0682$ | $[-0.0847,\, +0.2040]$ | $0.2887$ | **$+7.18\%$** | $0.3945$ | No |

### Methodological Takeaways
1. **Home Visits vs Control Robustness:** The statistical significance of Home Visits vs Control survives conservative small-sample adjustment ($p = 0.0280 < 0.05$), although confidence intervals widen by $7.2\%$.
2. **Direct Active Comparison Imprecision:** For Home Visits vs Digital, conservative degrees of freedom widen the 95% confidence interval from $[-0.0750, 0.1943]$ to $[-0.0847, 0.2040]$ (a full $0.289$ SD span), further highlighting the severe lack of precision to distinguish between these treatments.

Generated data file:
- [`small_sample_inference_comparison.csv`](file:///D:/Niyati/validation/V4_power_precision_audit/outputs/small_sample_inference_comparison.csv)

---

## 6. Design-Based Minimum Detectable Effects (MDE) & Power Sensitivity

### Methodological Framework
In strict compliance with audit rules:
- **No retrospective observed-power calculations:** We do **not** calculate "observed power" using estimated effect sizes and sample $p$-values, as retrospective power is a mathematically redundant transformation of the $p$-value that carries no additional information and creates circular reasoning (Hoenig & Heisey 2001).
- **Prospective design-based formulation:** MDEs and statistical power are calculated based on trial design parameters across a prospective grid of hypothesized effect sizes: $\delta \in [0.05, 0.06, 0.10, 0.15, 0.20, 0.25]\text{ SD}$ across all 5 ICC scenarios ($\rho \in [0.01, 0.03, 0.03202, 0.05, 0.10]$), using the cluster-randomized trial formulas of Hayes & Bennett (1999):
  $$\operatorname{Var}(\hat{\Delta}) = \frac{DE_a}{N_a} + \frac{DE_b}{N_b}$$
  $$\text{MDE}_{80\%} = (t_{\alpha/2, df} + t_{\beta=0.20, df}) \cdot SE(\hat{\Delta}),\quad \text{MDE}_{90\%} = (t_{\alpha/2, df} + t_{\beta=0.10, df}) \cdot SE(\hat{\Delta})$$

### Table 6.1: Minimum Detectable Effects at Empirical ICC ($\rho = 0.03202$)

| Pairwise Comparison | Clusters ($K_a, K_b$) | Sample ($N_a, N_b$) | $SE(\hat{\Delta})$ | Conventional $df$ | $\text{MDE}_{80\%}$ (Std $df$) | $\text{MDE}_{90\%}$ (Std $df$) | Cons. $df$ | $\text{MDE}_{80\%}$ (Cons. $df$) | $\text{MDE}_{90\%}$ (Cons. $df$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Digital vs Control** | $72,\, 68$ | $988,\, 864$ | $0.0586$ | $138$ | **$0.165$ SD** | **$0.191$ SD** | $67$ | **$0.167$ SD** | **$0.193$ SD** |
| **Home Visits vs Control** | $19,\, 68$ | $297,\, 864$ | $0.0845$ | $85$ | **$0.240$ SD** | **$0.277$ SD** | $18$ | **$0.250$ SD** | **$0.290$ SD** |
| **Home Visits vs Digital** | $19,\, 72$ | $297,\, 988$ | $0.0832$ | $89$ | **$0.236$ SD** | **$0.273$ SD** | $18$ | **$0.247$ SD** | **$0.286$ SD** |

### Table 6.2: Statistical Power Sensitivity Grid at Empirical ICC ($\rho = 0.03202$)

| Hypothesized Effect Size ($\delta$) | Relevance / Benchmark | Digital vs Control Power | Home Visits vs Control Power | Home Visits vs Digital Power | Home Visits vs Digital Power (Cons. $df=18$) |
| :---: | :--- | :---: | :---: | :---: | :---: |
| **$0.05$ SD** | Small / negligible difference | $13.7\%$ | $8.8\%$ | $9.0\%$ | $8.5\%$ |
| **$0.06$ SD** | **Observed Adjusted Effect Diff** | **$18.1\%$** | **$10.7\%$** | **$11.0\%$** | **$10.2\%$** |
| **$0.10$ SD** | Digital vs Control observed effect | $40.0\%$ | $21.8\%$ | $22.6\%$ | $20.3\%$ |
| **$0.15$ SD** | Moderate intervention effect | $73.3\%$ | $42.6\%$ | $44.1\%$ | $39.9\%$ |
| **$0.20$ SD** | **Target Design Effect Size** | **$92.4\%$** | **$64.8\%$** | **$66.2\%$** | **$61.3\%$** |
| **$0.25$ SD** | Large intervention effect | $98.7\%$ | $82.7\%$ | $83.9\%$ | $79.8\%$ |

Generated data files:
- [`mde_sensitivity.csv`](file:///D:/Niyati/validation/V4_power_precision_audit/outputs/mde_sensitivity.csv)
- [`power_sensitivity.csv`](file:///D:/Niyati/validation/V4_power_precision_audit/outputs/power_sensitivity.csv)

---

## 7. Answers to the Eight Core Evaluation Questions

### Question 1: Is cluster allocation balanced across the three trial arms?
**Answer:**  
**No, cluster allocation is severely unbalanced.**  
The trial randomized 159 populated clusters into:
- **Control:** 68 clusters ($42.77\%$)
- **Digital (Afini):** 72 clusters ($45.28\%$)
- **Home Visits:** 19 clusters ($11.95\%$)

The Control arm received $3.58\times$ and the Digital arm received $3.79\times$ as many clusters as Home Visits. This extreme allocation asymmetry places the Home Visits arm right on the boundary of small-sample cluster inference ($K=19 < 20$) and drastically reduces the statistical information available for any comparison involving Home Visits.

---

### Question 2: Is cluster size balanced within and across trial arms?
**Answer:**  
**No, cluster size is severely unbalanced both within and across arms.**  
Across the trial, cluster sizes range from $1$ to $42$ enrolled participants ($1$ to $38$ in the analysis sample). The coefficient of variation of cluster size ($CV$) is:
- **Control:** $CV = 0.702$ (enrolled), $0.708$ (analysis)
- **Digital:** $CV = 0.633$ (enrolled), $0.640$ (analysis)
- **Home Visits:** $CV = 0.478$ (enrolled), $0.471$ (analysis)
- **Total Trial:** $CV = 0.642$ (0.6419 enrolled, 0.6450 analysis)

Under cluster-randomization theory (Eldridge et al. 2006), $CV > 0.23$ produces substantial variance inflation beyond standard equal-cluster power formulas. Across the entire trial, the largest 10% of clusters (16 clusters) contain **22.84%** of enrolled participants (562 / 2,461) and **22.99%** of analysis participants (494 / 2,149). Within individual arms, the top deciles account for 24.54% (Control, 7 clusters), 17.67% (Home Visits, 2 clusters), and 24.87% (Digital, 8 clusters).

---

### Question 3: How much does clustering reduce effective sample size across the trial arms?
**Answer:**  
**Clustering reduces the trial's effective sample size by approximately 40% across all arms.**  
At the empirical null-model ICC ($\rho = 0.03202$), design effects range between $1.624$ and $1.699$ across arms, and $1.668$ (1.6679) for the overall trial:
- **Control:** Nominal $N = 970 \rightarrow N_{\text{eff}} = 588.0$ (loss of $382.0$ participants, $39.38\%$; $60.62\%$ of nominal)
- **Home Visits:** Nominal $N = 317 \rightarrow N_{\text{eff}} = 195.2$ (loss of $121.8$ participants, $38.43\%$; $61.57\%$ of nominal)
- **Digital:** Nominal $N = 1,174 \rightarrow N_{\text{eff}} = 690.9$ (loss of $483.1$ participants, $41.15\%$; $58.85\%$ of nominal)
- **Trial Total:** Nominal $N = 2,461 \rightarrow N_{\text{eff}} = 1,475.5$ (loss of $985.5$ participants, $40.04\%$; $59.96\%$ of nominal)

If the true ICC were $0.05$, effective sample size would drop by **51.1%**; if $\rho = 0.10$, it would drop by **67.6%** ($N_{\text{eff}} = 797.5$).

---

### Question 4: How does the precision of the Home Visits versus Control comparison compare with the Digital versus Control comparison?
**Answer:**  
**The Digital vs Control comparison is estimated with substantially higher precision than Home Visits vs Control.**  
- **Standard Errors:**
  - Digital vs Control: $SE = 0.0450$ (unadjusted), $SE = 0.0447$ (adjusted)
  - Home Visits vs Control: $SE = 0.0662$ (unadjusted), $SE = 0.0689$ (adjusted)
  - Home Visits standard error is **$54.1\%$ larger** than Digital.
- **Confidence Interval Widths (Adjusted MI):**
  - Digital vs Control 95% CI: $[+0.0184,\, +0.1948]$ (width $= 0.1764\text{ SD}$)
  - Home Visits vs Control 95% CI: $[+0.0302,\, +0.3024]$ (width $= 0.2722\text{ SD}$)
  - Home Visits 95% CI is **$54.3\%$ wider**.

This precision disparity is directly caused by the unequal allocation of clusters ($19$ vs $72$).

---

### Question 5: What does the direct Home Visits versus Digital contrast show?
**Answer:**  
**The direct contrast shows a statistically non-significant difference in favor of Home Visits, but with very wide confidence bounds:**
- **Unadjusted Model:**
  $$\hat{\Delta} = +0.0275\text{ SD},\quad SE = 0.0652,\quad t = 0.422,\quad p = 0.6738,\quad 95\%\text{ CI } [-0.1012,\, +0.1562]$$
- **Adjusted Multiple-Imputation Model ($M=250$):**
  $$\hat{\Delta} = +0.0596\text{ SD},\quad SE = 0.0682,\quad t = 0.875,\quad p = 0.3831,\quad 95\%\text{ CI } [-0.0750,\, +0.1943]$$

While the point estimate indicates a $+0.06$ SD advantage for Home Visits, the difference is statistically indistinguishable from zero ($p = 0.3831$).

---

### Question 6: Are the trial's findings robust to small-sample cluster-robust inference corrections?
**Answer:**  
**Yes, the primary conclusions against Control remain statistically significant, but confidence intervals widen substantially.**  
Applying Cameron & Miller's conservative degrees of freedom ($df_{\text{conservative}} = \min(K_a, K_b) - 1$):
- **Home Visits vs Control ($df = 18$ unadjusted, $df = 16.3$ adjusted):**
  - Unadjusted: $p = 0.0127 \rightarrow 0.0213$; 95% CI $[+0.0278,\, +0.3060]$ (width $+6.4\%$).
  - Adjusted MI: $p = 0.0170 \rightarrow 0.0280$; 95% CI $[+0.0204,\, +0.3121]$ (width $+7.2\%$).
  - Significance at $\alpha = 0.05$ is **preserved**.
- **Digital vs Control ($df = 67$ unadjusted, $df = 65.0$ adjusted):**
  - Unadjusted: $p = 0.0023 \rightarrow 0.0028$; 95% CI $[+0.0496,\, +0.2292]$ (width $+1.1\%$).
  - Adjusted MI: $p = 0.0182 \rightarrow 0.0199$; 95% CI $[+0.0174,\, +0.1958]$ (width $+1.1\%$).
  - Significance at $\alpha = 0.05$ is **preserved**.
- **Home Visits vs Digital ($df = 18$ unadjusted, $df = 16.3$ adjusted):**
  - Adjusted MI 95% CI expands to **$[-0.0847,\, +0.2040]$** (span of $0.2887\text{ SD}$, $+7.2\%$).

---

### Question 7: What effect sizes was the trial realistically powered to detect?
**Answer:**  
At the empirical ICC ($\rho = 0.03202$):
- **Digital vs Control:**
  - $\text{MDE}_{80\%} = 0.165\text{ SD}$ ($0.167\text{ SD}$ conservative $df$).
  - Power to detect target effect ($0.20\text{ SD}$) is **$92.4\%$**.
  - **Verdict:** Adequately powered for its target design effect.
- **Home Visits vs Control:**
  - $\text{MDE}_{80\%} = 0.240\text{ SD}$ ($0.250\text{ SD}$ conservative $df$).
  - Power to detect target effect ($0.20\text{ SD}$) is **only $64.8\%$** ($61.3\%$ conservative $df$).
  - **Verdict:** Underpowered to detect effect sizes below $0.24$ SD.
- **Home Visits vs Digital:**
  - $\text{MDE}_{80\%} = 0.236\text{ SD}$ ($0.247\text{ SD}$ conservative $df$).
  - Power to detect the observed difference ($0.06\text{ SD}$) is **only $11.0\%$**.
  - Power to detect a difference of $0.20\text{ SD}$ is **only $66.2\%$**.
  - **Verdict:** Severely underpowered to detect modest or clinically meaningful differences between the active interventions.

---

### Question 8: Does the trial support a claim that Digital is equivalent or non-inferior to Home Visits?
**Answer:**  
# **NO. The trial DOES NOT support any claim that Digital is equivalent or non-inferior to Home Visits.**

This conclusion is grounded in foundational statistical principles:
1. **Absence of Evidence is Not Evidence of Absence:**  
   The non-significant $p$-value ($p = 0.3831$) demonstrates only that the trial lacked statistical precision to reject the null hypothesis; it is not positive evidence that the treatments have equivalent effects.
2. **Excessively Wide Confidence Bounds:**  
   The adjusted 95% confidence interval for Home Visits minus Digital is:
   $$[-0.0750,\, +0.1943]\text{ SD}\quad \left(\text{expanding to } [-0.0847,\, +0.2040]\text{ SD under conservative small-sample } df\right)$$
   This interval spans nearly **$0.27\text{ to } 0.29\text{ SD}$**. It cannot exclude:
   - Meaningful Home Visits superiority of up to **$+0.194$ SD** (which is essentially identical to the trial's target primary effect size of $0.20$ SD).
   - Moderate Digital superiority of down to **$-0.075$ SD**.
3. **Failure of Non-Inferiority Criteria:**  
   In standard clinical and educational trial practice, non-inferiority requires the lower bound of the 95% confidence interval for the novel treatment (Digital minus Home Visits: $[-0.1943,\, +0.0750]$) to lie above a pre-specified non-inferiority margin (typically $-\Delta_{\text{NI}} \ge -0.10$ or $-0.15$ SD). Here, the lower bound is **$-0.194$ SD**, decisively failing standard non-inferiority tests.
4. **Severe Lack of Statistical Power:**  
   With only 19 Home Visits clusters, the trial possessed only **11% statistical power** to detect the observed $0.06$ SD difference, and would have failed to detect differences as large as $0.23$ SD 80% of the time.

Any assertion that the Digital intervention is "as effective as" or "equivalent to" Home Visits based on these trial results is scientifically invalid.

---

## 8. Summary of Generated Output Files

All output files are located in `validation/V4_power_precision_audit/outputs/`:

| Output File | Description | Records |
| :--- | :--- | :---: |
| [`cluster_size_summary.csv`](file:///D:/Niyati/validation/V4_power_precision_audit/outputs/cluster_size_summary.csv) | Populated cluster counts, enrolled and analysis sample sizes, mean, median, SD, CV, min, max, percentiles, and top 10% share across arms. | 8 rows |
| [`cluster_size_distribution.csv`](file:///D:/Niyati/validation/V4_power_precision_audit/outputs/cluster_size_distribution.csv) | Full cluster-by-cluster breakdown for all 159 clusters with arm name, province, enrolled count, analysis count, and attrition. | 159 rows |
| [`cluster_size_imbalance_summary.csv`](file:///D:/Niyati/validation/V4_power_precision_audit/outputs/cluster_size_imbalance_summary.csv) | Diagnostics and ratios across 6 key dimensions of cluster imbalance (allocation, size range, CV, top decile share). | 6 rows |
| [`design_effect_sensitivity.csv`](file:///D:/Niyati/validation/V4_power_precision_audit/outputs/design_effect_sensitivity.csv) | Design effects ($DE$), effective sample sizes ($N_{\text{eff}}$), and percentage of nominal sample size across 5 ICC scenarios for each arm. | 20 rows |
| [`effective_sample_size_sensitivity.csv`](file:///D:/Niyati/validation/V4_power_precision_audit/outputs/effective_sample_size_sensitivity.csv) | Wide-format summary of effective sample size and design effects across all ICC scenarios. | 4 rows |
| [`unadjusted_pairwise_contrasts.csv`](file:///D:/Niyati/validation/V4_power_precision_audit/outputs/unadjusted_pairwise_contrasts.csv) | Direct pairwise treatment contrasts (HV vs Ctrl, Dig vs Ctrl, HV vs Dig) from unadjusted OLS model using full covariance matrix. | 3 rows |
| [`adjusted_pairwise_contrasts.csv`](file:///D:/Niyati/validation/V4_power_precision_audit/outputs/adjusted_pairwise_contrasts.csv) | Direct pairwise treatment contrasts from adjusted MI model ($M=250$, seed `20260226`) using full covariance matrix and Barnard-Rubin $df$. | 3 rows |
| [`small_sample_inference_comparison.csv`](file:///D:/Niyati/validation/V4_power_precision_audit/outputs/small_sample_inference_comparison.csv) | Sensitivity comparison of conventional CR1 / Barnard-Rubin vs conservative $df = \min(K_a, K_b) - 1$, with CR2 and bootstrap status. | 14 rows |
| [`mde_sensitivity.csv`](file:///D:/Niyati/validation/V4_power_precision_audit/outputs/mde_sensitivity.csv) | Design-based Minimum Detectable Effects (80% and 90% power) for all pairwise comparisons across 5 ICC scenarios under standard and conservative $df$. | 15 rows |
| [`power_sensitivity.csv`](file:///D:/Niyati/validation/V4_power_precision_audit/outputs/power_sensitivity.csv) | Prospective statistical power across effect sizes ($0.05, 0.06, 0.10, 0.15, 0.20, 0.25$ SD) and 5 ICC scenarios under standard and conservative $df$. | 90 rows |
| [`v4_summary.json`](file:///D:/Niyati/validation/V4_power_precision_audit/outputs/v4_summary.json) | Complete machine-readable metadata summary of all findings, reconciliation checks, models, sensitivities, and evaluation question answers. | 193 lines |

---

## 9. Verification Manifest & Software Environment

- **Python Version:** 3.13.3
- **Core Dependencies:**
  - `numpy`: 2.4.6
  - `pandas`: 3.0.3
  - `scipy`: 1.17.1
  - `statsmodels`: 0.15.0
- **External Tooling Status:**
  - R runtime / `clubSandwich`: Not installed locally (documented; conservative $df$ sensitivity executed).
  - `wildboottest`: Not installed locally (documented; econometric limitations recorded).
- **Reproduction Fidelity & Benchmark Verification:**
  - Unadjusted HV vs Control: $\beta = 0.1669, SE = 0.0662$ (Exact match).
  - Unadjusted Digital vs Control: $\beta = 0.1394, SE = 0.0450$ (Exact match).
  - Adjusted MI HV vs Control: $\beta = 0.1663, SE = 0.0689$ (Difference from V3.3 direct benchmark: $1.39 \times 10^{-16} < 10^{-6}$; exact reproduction of independently reported treatment coefficient).
  - Adjusted MI Digital vs Control: $\beta = 0.1066, SE = 0.0447$ (Difference from V3.3 direct benchmark: $1.39 \times 10^{-17} < 10^{-6}$; exact reproduction of independently reported treatment coefficient).
  - Adjusted MI Home Visits vs Digital: $\beta = 0.0596, SE = 0.0682$ (Difference from algebraically derived V3.3 contrast: $1.73 \times 10^{-16} < 10^{-6}$; verified consistent with derived treatment coefficients, not claimed as an independent V3.3 result).
  - Strict reproduction tolerance ($\text{diff} < 10^{-6}$): **VERIFIED & SATISFIED**.
  - Raw archive preserved intact: `doi_10_5061_dryad_nzs7h4551__v20260226.zip` untouched.
