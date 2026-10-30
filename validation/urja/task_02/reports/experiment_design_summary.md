# Urja Task 2 — Experiment Design and Treatment Allocation Summary

**Project:** Project Urja  
**Task:** Task 2 — Experiment Design, Panel Structure & Outcome Suitability Validation  
**Date:** 2026-10-30  
**Source Dataset:** Harvard Dataverse (`doi:10.7910/DVN/4FLFRE`)  
**Research Paper:** Ahsanuzzaman, Eskander, Islam, and Wang (2024), *Journal of Environmental Economics and Management* (JEEM), 127: 103022.

---

## 1. Study Objective & Research Context

The research evaluates the efficacy, behavioural mechanisms, and long-term persistence of **non-price informational interventions** designed to foster household electricity conservation in developing country residential contexts.

Unlike developed-country Opower-style interventions that operate primarily in temperate climates with universal grid reliability, this randomized field experiment investigates whether behavioural nudges (social comparison and actionable energy conservation advice) can reduce electricity consumption and household bills in **Bangladesh**, a developing country characterized by hot tropical climates, rapid urban energy demand growth, frequent load shedding (power outages), and tiered electricity tariffs.

---

## 2. Experimental Setting, Population & Recruitment

- **Country & Geography:** Bangladesh.
- **Urban Areas Surveyed:** 3 cities spanning 10 suburbs:
  - **Dhaka (Capital city, major metropolitan center):** 8 suburbs (Badda, Dhanmondi, Khilgaon, Mirpur, Mohammadpur, Puran Dhaka, Rayer Bazar, Uttara) comprising 53 neighbourhood clusters.
  - **Khulna (Major industrial port city, south-west):** 1 suburb (Khulna) comprising 3 neighbourhood clusters.
  - **Jashore (Regional commercial hub, south-west):** 1 suburb (Jashore) comprising 3 neighbourhood clusters.
  - **Total Neighbourhood Clusters (`nid`):** 59 distinct administrative/geographic clusters.
- **Recruitment & Sample Size:**
  - **Initial Recruited Sample (Pre-baseline Round 0):** 2,394 residential households.
  - **Retained Experimental Sample (Rounds 1–6):** 2,248 residential households.
  - **Baseline Attrition:** Exactly 146 households (6.10%) attrited after Round 0 before the post-baseline intervention delivery commenced.
  - **Eligibility:** Residential electricity consumers with dedicated electric utility meters receiving individual monthly utility bills.

---

## 3. Treatment Arms and Definitions

The randomized controlled trial features **four experimental arms** (one control group and three active information interventions):

| Group Code | Treatment Label | Target Mechanism | Documented Intervention Content | Initial Households (Round 0) | Retained Households (Rounds 1–6) |
|---|---|---|---|---|---|
| **T0** | **Control Group** | Baseline benchmark | Surveyed at regular intervals; received standard utility bills with **no social comparison feedback and no energy-saving advice**. | 586 | 550 |
| **T1** | **Neighbor Comparison** | Local social descriptive norms | Received comparative feedback cards reporting their own electricity consumption alongside the **median electricity consumption of immediate neighbours** living within the same neighbourhood cluster (`nid`). | 605 | 567 |
| **T2** | **Suburb Comparison** | Broader geographic social descriptive norms | Received comparative feedback cards reporting their own electricity consumption alongside the **median electricity consumption of households across their entire suburb**. | 602 | 568 |
| **T3** | **Practical Advice (Knowledge)** | Actionable technical guidance & awareness | Received customized, actionable **electricity conservation guidelines and practical tips** (e.g., efficient fan and lighting usage, refrigerator maintenance, AC temperature settings, eliminating phantom loads). | 601 | 563 |
| **Total** | **All Groups Combined** | Full RCT Universe | Four mutually exclusive randomized arms. | **2,394** | **2,248** |

---

## 4. Randomization Unit & Assignment Mechanism

### 4.1 Verified Assignment Level
- **Unit of Randomization:** **Individual Household (`hid`)**.
- **Evidence from Replication Data:**
  - Randomization was conducted **within neighbourhood clusters (`nid`)**, not cluster-randomized at the neighbourhood or suburb level.
  - Out of 59 neighbourhoods, **58 neighbourhoods contain households assigned to all four treatment groups (T0, T1, T2, T3)**. Exactly 1 smaller neighbourhood contains three treatment groups.
  - Within each neighbourhood, the four treatment groups are represented in roughly equal proportions.
  - Treatment assignment remains **100% constant across all survey rounds** for every single household (0 inconsistencies detected across 15,882 rows).

### 4.2 Econometric Clustering Rationale
- Standard errors in all econometric specifications (`02 JEEM 2024 replication codes - main text tables.do`) are clustered at the **household level (`cluster(hid)`)**.
- This clustering accounts for intra-household serial correlation across the panel's repeated measurement rounds, consistent with household-level random assignment.

---

## 5. Survey Rounds and Measurement Timeline

The study encompasses **seven discrete survey rounds** spanning January 2017 to August 2018:

```text
Timeline Overview:
[Round 0: Jan-Feb 2017] --> Randomization --> [Round 1: May 2017] --> Intervention Delivery (Rounds 2-4)
Pre-baseline (self-report)                    Baseline (verified)      Active monthly feedback
                                                                               |
                                                                               v
[Round 6: Aug 2018] <---- Scrutiny Test <---- [Round 5: May-Jun 2018] <--- [Round 4: Nov 2017]
Long-term Persistence     (Subsample N=1,200)  (Intermediate check)        Primary Endline
(15 months post-base)
```

### Round-by-Round Definitions and Functional Roles

| Survey Round | Calendar Window | Billed Period Measured | Measurement Mode | Functional Experimental Role | Households Present |
|---|---|---|---|---|---|
| **Round 0** | Jan–Feb 2017 | Dec 2016 / Jan 2017 | Self-reported bill (`sbill`, BDT) | **Pre-baseline Survey:** Initial household recruitment, dwelling characteristics, baseline demographics, prior to random assignment. | 2,394 |
| **Round 1** | May 2017 | April 2017 | Physical utility bill verification (`runit` kWh, `rbill` BDT, `sbill` BDT) | **Official Baseline Survey:** Enumerators physically verified meter bills from April 2017 immediately prior to intervention rollout. | 2,248 |
| **Round 2** | June 2017 | May/June 2017 | Physical utility bill verification (`runit`, `rbill`) | **Intervention Round 1:** First post-treatment wave following the initial delivery of informational cards. | 2,248 |
| **Round 3** | August 2017 | July/August 2017 | Physical utility bill verification (`runit`, `rbill`) | **Intervention Round 2:** Second active intervention measurement wave. | 2,248 |
| **Round 4** | November 2017 | Oct/Nov 2017 | Physical utility bill verification (`runit`, `rbill`) | **Intervention Round 3 / Primary Endline:** Conclusion of the active 6-month informational intervention period. | 2,248 |
| **Round 5** | May–June 2018 | April/May 2018 | Physical utility bill verification (`runit`, `rbill`) | **Scrutiny Test Subsample:** Randomized intermediate survey of exactly 1,200 households (300 per treatment arm) to empirically test for Hawthorne/scrutiny effects. | 2,248 |
| **Round 6** | August 2018 | July/August 2018 | Physical utility bill verification (`runit`, `rbill`) | **Long-Term Persistence Evaluation:** Comprehensive follow-up conducted **15 months after baseline and 9 months after intervention termination** to evaluate habit persistence. | 2,248 |

---

## 6. Documented Discrepancies and Clarifications

A careful audit of the research paper, `0 README.docx`, and the Stata replication scripts identified two minor documentation nuances that must be clearly noted:

1. **Pre-baseline vs. Baseline Terminology:**
   - In informal descriptions, authors sometimes refer to pre-treatment data generally. However, in code and formal tables, **Round 1 is strictly the baseline** (with verified meter readings), while **Round 0 is pre-baseline** (with self-reported bills).
   - In DiD models for verified consumption (`runit` and `rbill`), Round 1 serves as the reference pre-treatment period ($t=1$), because verified meter readings were not collected in Round 0.
2. **Round 5 Scrutiny Design:**
   - The paper notes that 1,250 households were targeted for scrutiny testing in Round 5. In the actual released dataset (`replication_data.dta`), exactly **1,200 households** have `followup == "Followed up"` in Round 5 (precisely 300 in each of the four treatment arms), while the remaining 1,048 retained households have `followup == "Not followed up"`.
   - In the long-term evaluation regressions (Table 10), the authors estimate models on Rounds 1, 2, 3, 4, and 6 (`keep if inlist(round, 1,2,3,4,6)`), deliberately setting aside Round 5 so that the long-term persistence estimate is not conflated with the intermediate scrutiny test wave.

---

## 7. Conclusion on Experimental Design

The empirical evidence from `replication_data.dta` and the replication scripts confirms:
1. A valid, well-balanced **four-arm randomized field trial**.
2. Individual household random assignment stratified across 59 neighbourhood clusters.
3. Completely consistent treatment allocation with zero within-household assignment drift.
4. Clean separation between the active intervention period (Rounds 1–4) and the long-term persistence follow-up (Round 6).
