# Urja Task 2 — Study Design, Panel Feasibility & Candidate Suitability Findings

**Project Name:** Urja  
**Task:** Task 2 — Experiment Design, Panel Structure & Outcome Suitability Validation  
**Evaluation Date:** 2026-10-30  
**Repository Branch:** `project2/urja-validation`  
**Dataset Analyzed:** `replication_data.dta` (Harvard Dataverse `doi:10.7910/DVN/4FLFRE`)

---

## 1. Executive Feasibility Evaluation

This report delivers the structural feasibility assessment for Project Urja. Based strictly on empirical data audit, cryptographic file verification, and inspection of the replication package, the experimental design, panel structure, and outcome measurements **firmly support a rigorous household-level intervention evaluation**.

The dataset represents a genuine, high-quality, four-arm randomized field experiment conducted across 2,394 initial households and 2,248 retained panel households in Bangladesh. Panel integrity is exceptionally high (zero duplicate keys, zero within-household treatment assignment drift, and 98.93% complete panel outcome availability across the main intervention rounds).

---

## 2. Assessment of the Twelve Core Feasibility Criteria

### Question 1: Is there a clearly documented four-group experiment?
- **Verified Evidence:** The codebook (`0 README.docx`), replication do-files (`02 JEEM...tables.do`), and dataset value labels explicitly define four mutually exclusive experimental groups: T0 (Control, 586 initial / 550 retained), T1 (Neighbor comparison, 605 initial / 567 retained), T2 (Suburb comparison, 602 initial / 568 retained), and T3 (Knowledge advice, 601 initial / 563 retained).
- **Relevant Data Fields:** `treatment` (categorical / integer: 0, 1, 2, 3), Stata value label `treatment2`.
- **Result:** **CONFIRMED & VERIFIED**.
- **Limitations:** None. Group definitions are completely explicit and documented.

---

### Question 2: Can the actual treatment allocation be identified in the data?
- **Verified Evidence:** Every observation has an explicit non-null `treatment` value (0 missing values across all 15,882 rows). Cross-tabulation by household confirms that each household maintains exactly one immutable treatment status across all survey rounds (0 inconsistent households).
- **Relevant Data Fields:** `treatment`, `hid`.
- **Result:** **CONFIRMED & VERIFIED**.
- **Limitations:** None. Treatment assignment is 100% observable.

---

### Question 3: Is the randomisation unit established?
- **Verified Evidence:** Randomization was performed at the **individual household level (`hid`)** within 59 neighbourhood clusters (`nid`). Within 58 of the 59 neighbourhoods, households were assigned across all four treatment arms simultaneously. Standard errors are clustered at the household level (`cluster(hid)`) in all regression do-files to account for serial correlation across rounds.
- **Relevant Data Fields:** `hid`, `nid`, `treatment`.
- **Result:** **CONFIRMED & VERIFIED**.
- **Limitations:** Because multiple treatment arms coexist within the same physical neighbourhoods, potential spatial informational spillovers across neighbours must be evaluated (as addressed in Appendix Table S8).

---

### Question 4: Are household and neighbourhood identifiers sufficient to represent the assignment structure?
- **Verified Evidence:** Household IDs (`hid`) uniquely identify 2,394 distinct residential units with 0 missing values. Neighbourhood IDs (`nid`) identify 59 geographic clusters with 0 missing values. The combination `(hid, round)` forms an exact, unique primary key with 0 duplicates across the 15,882 dataset rows.
- **Relevant Data Fields:** `hid`, `nid`, `suburb`, `city`, `round`.
- **Result:** **CONFIRMED & VERIFIED**.
- **Limitations:** Sub-neighbourhood coordinates (GPS latitude/longitude) for individual dwellings are not released in `replication_data.dta` for participant privacy, but cluster-level `nid` is fully preserved.

---

### Question 5: Can the main electricity consumption outcome be measured across relevant rounds?
- **Verified Evidence:** Physical electricity consumption in kWh (`runit`) was directly transcribed and verified from monthly electric utility bills across Rounds 1 through 6. In the main intervention period (Rounds 1–4), `runit` is observed for 2,248 households in Round 1 (100%), 2,248 in Round 2 (100%), 2,246 in Round 3 (99.91%), and 2,226 in Round 4 (99.02%). In Round 6 (long-term follow-up), it is observed for 2,181 households (97.02%).
- **Relevant Data Fields:** `runit` (float32, continuous kWh).
- **Result:** **CONFIRMED & VERIFIED**.
- **Limitations:** Physical meter verification was not implemented in pre-baseline Round 0; Round 1 serves as the reference baseline period for verified consumption.

---

### Question 6: Can electricity bills be analysed as a complementary outcome?
- **Verified Evidence:** Verified monthly electricity bills in Bangladeshi Taka (`rbill`) are available for the exact same sample and rounds as `runit` (Rounds 1–6). Self-reported electricity bills (`sbill`) are available for Rounds 0 and 1, enabling parallel pre-trend testing between pre-baseline and baseline.
- **Relevant Data Fields:** `rbill` (verified monthly bill, BDT), `sbill` (self-reported bill, BDT).
- **Result:** **CONFIRMED & VERIFIED**.
- **Limitations:** Bills reflect progressive increasing-block tariff schedules in Bangladesh; changes in bills reflect both physical volume reductions and tariff tier shifts.

---

### Question 7: Can the intervention period be separated from later follow-up?
- **Verified Evidence:** The 7 survey rounds map to distinct, non-overlapping experimental phases:
  - *Pre-baseline:* Round 0 (Jan–Feb 2017).
  - *Baseline:* Round 1 (May 2017).
  - *Active Intervention Period:* Rounds 2, 3, 4 (June, August, November 2017).
  - *Scrutiny Subsample Test:* Round 5 (May–June 2018, N=1,200).
  - *Long-Term Persistence Follow-up:* Round 6 (August 2018, 15 months post-baseline, 9 months post-intervention).
- **Relevant Data Fields:** `round`, `followup`.
- **Result:** **CONFIRMED & VERIFIED**.
- **Limitations:** None. The timeline allows sharp econometric separation between contemporaneous short-term effects and long-term habit persistence.

---

### Question 8: Is household attrition measurable?
- **Verified Evidence:** Attrition is explicitly tracked by the indicator variable `attrited`. Exactly 146 households (6.10%) left the sample after Round 0 pre-baseline survey. Attrition rates are balanced across treatment arms: T0 (6.14%), T1 (6.28%), T2 (5.65%), and T3 (6.32%). No further panel attrition occurs between Round 1 and Round 6 (all 2,248 retained households remain in the survey roster).
- **Relevant Data Fields:** `attrited` (0=Remained, 1=Attrited after round 0).
- **Result:** **CONFIRMED & VERIFIED**.
- **Limitations:** Attrited households have only Round 0 pre-baseline data; verified post-intervention meter bills cannot be observed for them.

---

### Question 9: Are there enough valid observations in each treatment group and period for the planned analysis?
- **Verified Evidence:** The retained sample provides over 550 households per treatment group (T0: 550, T1: 567, T2: 568, T3: 563) tracked across multiple waves. In the main intervention panel (Rounds 1–4), this yields **8,968 total household-round observations**, with 98.93% of households having complete 4-round outcome data. In the long-term evaluation (Rounds 1, 2, 3, 4, 6), there are **11,137 valid observations**.
- **Relevant Data Fields:** `treatment`, `round`, `runit`, `rbill`.
- **Result:** **CONFIRMED & VERIFIED**.
- **Limitations:** Sub-sample stratifications (e.g., examining specific efficiency tiers within small regional cities like Jashore) have smaller cell sizes, which the original authors addressed by analyzing Dhaka separately.

---

### Question 10: Are there serious unresolved missingness or assignment problems?
- **Verified Evidence:** There are **zero missing values** in treatment assignment, household IDs, neighbourhood IDs, or survey rounds. Missingness in `sbill` in Rounds 2–6 and `rbill`/`runit` in Round 0 is structural by design. Unplanned survey non-response in Rounds 1–4 is below 1.0%, and in Round 6 is below 3.0%.
- **Relevant Data Fields:** All primary variables.
- **Result:** **CONFIRMED & VERIFIED (NO BLOCKERS)**.
- **Limitations:** Round 5 missingness (~47%) is intentional due to testing scrutiny effects on a 53% subsample.

---

### Question 11: Can the original research design be understood and reproduced in Python without needing proprietary software?
- **Verified Evidence:** All regression specifications in `02 JEEM...tables.do` are linear panel models (`reghdfe`) with round, treatment, and city fixed effects, clustered standard errors, and interaction terms. These specifications map directly to open-source Python econometric packages, specifically `pyfixest` (`feols`) or `statsmodels` with cluster-robust covariance matrices.
- **Relevant Data Fields:** Model formulas, fixed effect absorb lists, cluster variables.
- **Result:** **CONFIRMED & VERIFIED**.
- **Limitations:** Python scripts will need to replicate Stata's multi-way absorbed fixed effect degrees-of-freedom corrections precisely to match published standard errors to the third decimal place.

---

### Question 12: Can an intermediate-level analyst explain the resulting workflow?
- **Verified Evidence:** The workflow relies on standard, transparent applied econometric techniques: difference-in-differences, two-way fixed effects, baseline balance t-tests, and interaction models. The variables have clear physical and monetary interpretations without complex black-box transformations.
- **Relevant Data Fields:** All replication do-files and documentation.
- **Result:** **CONFIRMED & VERIFIED**.
- **Limitations:** None. The methodology is standard and well-documented in applied empirical economics.

---

## 3. Confirmed Empirical Facts vs. Open Methodological Questions

### Confirmed Empirical Facts:
1. **Four-Group RCT:** 1 control group and 3 distinct non-price information interventions (peer comparison at neighbour level, peer comparison at suburb level, and actionable conservation advice).
2. **Sample Size:** 2,394 initial households recruited; exactly 2,248 retained across all subsequent rounds; 146 attrited.
3. **Randomization Structure:** Individual household randomization conducted within 59 neighbourhood clusters across 3 cities (Dhaka, Khulna, Jashore).
4. **Data Hygiene:** 100% key uniqueness on `(hid, round)`; zero within-household treatment drift; zero infinite or negative consumption values.
5. **Outcome Completeness:** Verified physical energy use (`runit`, kWh) and verified bills (`rbill`, BDT) are available for >98.9% of retained households during the intervention period and >96% in the long-term follow-up.

### Open Methodological Questions for Subsequent Tasks:
1. **Baseline Balance Replication:** Confirm whether baseline observable characteristics (dwelling size, rooms, AC ownership, power outages, and April 2017 baseline usage) show statistical balance across the four groups in Python.
2. **Pre-Treatment Parallel Trends:** Estimate the Round 0 vs. Round 1 self-reported bill trends to formally verify parallel pre-trends prior to treatment rollout.
3. **Scrutiny Adjustment:** Determine the exact econometric specification to test for Hawthorne / scrutiny effects in Round 6 using Round 5 `followup` participation.
4. **Spatial Spillovers:** Formulate the Python representation of neighbourhood treatment intensity to evaluate potential information spillovers to control households.

---

## 4. Overall Conclusion

The experimental design, panel structure, and outcome data for **Project Urja** are thoroughly documented, structurally intact, and methodologically sound. The dataset fully supports the candidate project's evaluation goals.
