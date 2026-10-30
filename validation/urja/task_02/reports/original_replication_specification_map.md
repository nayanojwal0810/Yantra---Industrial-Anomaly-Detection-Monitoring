# Urja Task 2 — Original Replication Specification & Econometric Mapping

**Project:** Project Urja  
**Task:** Task 2 — Experiment Design, Panel Structure & Outcome Suitability Validation  
**Date:** 2026-10-30  
**Artifact Inspected:** Stata replication do-files from Harvard Dataverse release (`doi:10.7910/DVN/4FLFRE`)

---

## 1. Overview of Replication Code Structure

The Harvard Dataverse replication package includes four Stata `.do` files in the `Codes/` folder:

1. **`01 JEEM 2024 replication codes - main text figures.do` (778 lines):**
   - Generates Figures 1 through 9 for the main article text.
2. **`02 JEEM 2024 replication codes - main text tables.do` (728 lines):**
   - Generates Tables 1 through 10 for the main article text.
3. **`03 JEEM 2024 replication codes - appendix figures.do` (227 lines):**
   - Generates Figures S1 through S5 for the online supplementary appendix.
4. **`04 JEEM 2024 replication codes - appendix tables.do` (569 lines):**
   - Generates Tables S1 through S9 for the online supplementary appendix.

None of the scripts were executed in Task 2. This report provides a structural, econometric, and methodological mapping based on direct code inspection.

---

## 2. Core Econometric Estimator & Specification

Across both main and supplementary tables, the central econometric workhorse is the **two-way fixed effects Difference-in-Differences (DiD)** model estimated via Stata's `reghdfe` command.

### Standard Model Specification:
$$\text{Outcome}_{i,t} = \sum_{k=1}^3 \sum_{r} \beta_{k,r} (\text{Treatment}_{i,k} \times \text{Round}_{r}) + \alpha_r + \gamma_k + \delta_c + \varepsilon_{i,t}$$

Where:
- $\text{Outcome}_{i,t}$: Verified monthly electricity consumption in kWh (`runit`) or verified monthly bill in BDT (`rbill`) for household $i$ in round $t$.
- $\text{Treatment}_{i,k} \times \text{Round}_{r}$: Interaction between treatment group indicator $k \in \{1, 2, 3\}$ and survey round indicators $r$.
- $\alpha_r$: Survey round fixed effects (absorbing aggregate seasonal, climatic, and macroeconomic shocks).
- $\gamma_k$: Treatment group fixed effects (absorbing baseline time-invariant group differences).
- $\delta_c$: City / district fixed effects (`city`, absorbing regional geographic and utility provider disparities).
- $\varepsilon_{i,t}$: Idiosyncratic error term clustered at the **household level** (`cluster(hid)`) to accommodate serial correlation.

In Stata, this is written as:
```stata
quietly reghdfe runit i.treatment##round, abs(round treatment city) cluster(hid)
```

---

## 3. Main Text Tables Econometric Mapping (`02 JEEM...tables.do`)

| Table # | Table Title | Dependent Variable(s) | Sample & Filters | Core Econometric Model / Command | Absorbed Fixed Effects & Cluster | Replication Role |
|---|---|---|---|---|---|---|
| **Table 1** | Timeline of survey | N/A (Descriptive timeline) | All recruited (N=2,394) and retained (N=2,248) | Summary statistics / metadata | None | Establishes the 7-round timeline and sample sizes. |
| **Table 2** | Baseline characteristics by treatment status | `runit`, `rbill`, `freq_ac`, `hh_outage`, `hh_rooms` | Round 1 retained sample (`round==1`, N=2,248) | OLS: `reg var i.treatment, r` | None; robust SE | Randomization balance check across baseline observables. |
| **Table 3** | Baseline characteristics by sub-samples | `runit`, `rbill`, `freq_ac`, `hh_outage`, `hh_rooms` | Round 1 subsamples (above/below median, efficiency types, Dhaka vs regional) | OLS: `reg var i.treatment if round==1 & <subsample>` | Clustered at `hid` | Assesses baseline balance across 12 distinct analytical sub-samples. |
| **Table 4** | Differences of pre-treatment trends | `sbill` (self-reported bill) | Rounds 0 & 1 (`keep if inlist(round, 0, 1) & attrited==0`) | DiD: `reghdfe sbill i.treatment##round` | `abs(round treatment city)`, cluster(`hid`) | **Parallel Pre-Trends Test:** Tests whether treatment groups had diverging consumption trends prior to intervention rollout. |
| **Table 5** | Short-term treatment effects | `runit` (kWh), `rbill` (BDT) | Rounds 1–4 (`keep if inlist(round, 1, 2, 3, 4)`) | DiD: `reghdfe outcome i.treatment##round` (all cities, Dhaka, Jashore/Khulna) | `abs(round treatment city)`, cluster(`hid`) | **Primary Empirical Results:** Main treatment effect estimates across the 6-month active intervention period. |
| **Table 6** | Power outage by city and treatment groups | `hh_outage` (outage frequency in past 3 days) | Round 1 baseline (`round==1`) | Means, SDs, and two-sample t-tests: `ttest hh_outage, by(dhaka)` | None | Explores infrastructure reliability context (power outages much higher in regional cities than Dhaka). |
| **Table 7** | Short-term treatment effects by baseline consumption type | `runit`, `rbill` | Rounds 1–4 stratified by `eff0==0` (above median) and `eff0==1` (below median) | DiD: `reghdfe outcome i.treatment##round if eff0==...` | `abs(round treatment city)`, cluster(`hid`) | Evaluates whether high baseline users conserve more than low baseline users. |
| **Table 8** | Treatment effects by pre-baseline median consumption | `runit`, `rbill` | Rounds 1–4 stratified by `user_nid_high1` and `user_sub_high1` | DiD: `reghdfe outcome i.treatment##round if inlist(treatment, 1, 3) & user_nid_high1==...` | `abs(round treatment city)`, cluster(`hid`) | Tests peer comparison effects specifically among above-median vs. below-median peer users. |
| **Table 9** | Treatment effects by pre-baseline efficiency type | `runit`, `rbill` | Rounds 1–4 stratified by 3 efficiency tiers (`eff_nid`, `eff_sub` = 1, 2, 3) | DiD: `reghdfe outcome i.treatment##round if inlist(treatment, 1, 3) & eff_nid==...` | `abs(round treatment city)`, cluster(`hid`) | Tests non-linear normative feedback (inefficient vs. average vs. efficient users). |
| **Table 10** | Long-term treatment effects | `runit`, `rbill` | Rounds 1, 2, 3, 4, 6 (`keep if inlist(round, 1, 2, 3, 4, 6)`) | DiD: `reghdfe outcome i.treatment##round` | `abs(round treatment city)`, cluster(`hid`) | **Persistence Analysis:** Evaluates whether energy savings persist 9 months after intervention conclusion (Round 6). |

---

## 4. Main Text Figures Mapping (`01 JEEM...figures.do`)

| Figure # | Title / Description | Source File / Variables | Time Period / Subsample | Plot Type & Graphical Construction |
|---|---|---|---|---|
| **Figure 1** | Electricity access and power outage in South Asia | `wdi_electricity.dta`: `access_urban`, `outage_firm`, `outage_number`, `outage_loss` | 2000–2020 cross-country WDI panel | Cross-country trendline overlay and bar chart comparing Bangladesh against South Asian peers. |
| **Figure 2** | Electricity demand projections | `electricity_demand.dta`: `world`, `oecd`, `non_oecd` | 2000–2040 projections | Time series line plot from ExxonMobil (2019) Outlook for Energy. |
| **Figure 4** | Average electricity use and bills by treatment group | `replication_data.dta`: `runit`, `rbill` | Rounds 1–4 by treatment | Two-panel connected line plot showing means and 95% confidence intervals across Rounds 1–4. |
| **Figure 5** | Neighbor vs. Knowledge treatment by median use | `replication_data.dta`: `runit`, `rbill` | Rounds 1–4, Treatments 1 & 3, stratified by `user_nid_high1` | Four-panel connected line plot comparing T1 and T3 trajectories for high vs. low baseline users. |
| **Figure 6** | Suburb vs. Knowledge treatment by median use | `replication_data.dta`: `runit`, `rbill` | Rounds 1–4, Treatments 2 & 3, stratified by `user_sub_high1` | Four-panel connected line plot comparing T2 and T3 trajectories for high vs. low baseline users. |
| **Figure 7** | Neighbor vs. Knowledge treatment by efficiency tier | `replication_data.dta`: `runit`, `rbill` | Rounds 1–4, Treatments 1 & 3, stratified by `eff_nid` (1, 2, 3) | Six-panel connected line plot displaying normative tiers (inefficient, average, efficient). |
| **Figure 8** | Suburb vs. Knowledge treatment by efficiency tier | `replication_data.dta`: `runit`, `rbill` | Rounds 1–4, Treatments 2 & 3, stratified by `eff_sub` (1, 2, 3) | Six-panel connected line plot displaying normative tiers for suburb comparisons. |
| **Figure 9** | Scrutiny and long-term effects | `replication_data.dta`: `runit`, `rbill` | Panel I: Round 6 by `followup`. Panel II: Round 1 vs. Round 6 | Four-panel plot displaying Hawthorne/scrutiny test results and long-term persistence across all four arms. |

---

## 5. Supplementary Appendix Specifications (`04 JEEM...appendix tables.do`)

| Appendix Table # | Topic | Key Variables | Methodological Focus |
|---|---|---|---|
| **Table S1** | Survey areas | `suburb`, `treatment`, `attrited`, `followup` | Cross-tabulations detailing geographic distribution of retained, attrited, and followed-up households. |
| **Table S2** | Baseline balance in Dhaka city | `runit`, `rbill`, `freq_ac`, etc. | OLS balance checks restricted exclusively to Dhaka metropolitan households (`city==1`). |
| **Table S3** | Pre-treatment trends in Dhaka city | `sbill` | DiD parallel pre-trends test restricted to Dhaka city. |
| **Table S4** | Neighbor vs. Suburb comparison | `runit`, `rbill` | Direct pairwise difference-in-differences between peer comparison treatments T1 and T2. |
| **Table S5** | Treatment effects by baseline use in Dhaka | `runit`, `rbill` | Heterogeneous treatment effects by baseline usage restricted to Dhaka city. |
| **Table S6** | Treatment effects by efficiency type in Dhaka | `runit`, `rbill` | Heterogeneous treatment effects by efficiency tiers restricted to Dhaka city. |
| **Table S7** | Scrutinized vs. non-scrutinized baseline check | Baseline covariates by `followup2` | **Hawthorne Randomization Check:** Verifies that households selected for Round 5 scrutiny were balanced against non-scrutinized households. |
| **Table S8** | Spatial spillover effects | `runit`, `rbill` regressed on neighbourhood treatment intensity | Tests whether control households in neighbourhoods with high treatment density reduced consumption (spillovers). |
| **Table S9** | Treatment effects per square foot | `runit / flatsize`, `rbill / flatsize` | Normalized treatment effect estimates per unit of dwelling living area. |

---

## 6. Analytical Nuances & Python Translation Feasibility

1. **Replicability in Python:**
   - All regression specifications are standard linear panel fixed effects models.
   - They map cleanly to Python's `pyfixest` (`feols(..., vcov={'clustervar': 'hid'})`) or `statsmodels.formula.api` with explicit entity and time dummies.
   - Proprietary software (Stata) is **not strictly required** to reproduce the research findings.
2. **Treatment of Round 0:**
   - In Table 4, pre-treatment trends are evaluated using `sbill` in Rounds 0 and 1. In all subsequent treatment effect tables (Tables 5–10), estimation begins at Round 1 baseline using verified meter outcomes (`runit`, `rbill`).
3. **Treatment of Round 5:**
   - Round 5 is strictly a scrutiny evaluation round (N=1,200). It is correctly excluded from the main intervention DiD (Rounds 1–4) and from the primary long-term DiD (Table 10: Rounds 1, 2, 3, 4, 6) to avoid confounding.
4. **Sample Filters:**
   - Attrited households are excluded in analysis via `drop if attrited==1` or `if attrited==0`.
   - Complete data handling is transparent and reproducible across all scripts.
