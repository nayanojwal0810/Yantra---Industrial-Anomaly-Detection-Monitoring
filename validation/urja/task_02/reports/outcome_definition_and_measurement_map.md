# Urja Task 2 — Outcome Definitions, Measurement Schedule & Availability Map

**Project:** Project Urja  
**Task:** Task 2 — Experiment Design, Panel Structure & Outcome Suitability Validation  
**Date:** 2026-10-30  
**Dataset:** `replication_data.dta` (Harvard Dataverse `doi:10.7910/DVN/4FLFRE`)

---

## 1. Outcome Variable Definitions & Verification Modes

The dataset tracks household energy outcomes through three distinct variables that capture physical energy volume, monetary expenditure, and reporting accuracy:

| Dataset Variable | Variable Label | Measurement Type | Physical / Monetary Unit | Observation Period | Survey Rounds Intended | Primary Role in Research Analysis |
|---|---|---|---|---|---|---|
| **`runit`** | Electricity use (last month, kWh), verified | **Direct physical verification** from official electric utility bill | Kilowatt-hours (**kWh**) | Monthly billing cycle | **Rounds 1–6** | **Primary physical energy outcome**; used in all main treatment effect regressions (Tables 5, 7, 8, 9, 10; Figures 4A, 5A/B, 6A/B, 7A–C, 8A–C, 9A/C). |
| **`rbill`** | Electricity bills (last month, in taka), verified | **Direct monetary verification** from official electric utility bill | Bangladeshi Taka (**BDT / Tk**) | Monthly billing cycle | **Rounds 1–6** | **Primary economic / expenditure outcome**; reflects tiered progressive tariffs and consumer financial burden (Tables 5, 7, 8, 9, 10; Figures 4B, 5C/D, 6C/D, 7D–F, 8D–F, 9B/D). |
| **`sbill`** | Electricity bills (last month, in taka), self-reported | **Survey recall / self-report** by respondent | Bangladeshi Taka (**BDT / Tk**) | Preceding calendar month | **Rounds 0 & 1** | **Pre-treatment trend and recall accuracy check**; used for baseline randomization balance and parallel pre-trends test (Table 4; Figure S2, S3). |

---

## 2. Measurement Schedule & Design-Induced Missingness

A fundamental finding of this audit is that **missing values in the dataset are predominantly structural design choices**, not unplanned data collection failures:

```text
Summary of Measurement Schedule by Design:
+---------+--------------------+--------------------+--------------------+
| Round   | sbill (Self-Report)| rbill (Verified)   | runit (Verified)   |
+---------+--------------------+--------------------+--------------------+
| Round 0 | Observed (100%)    | Missing by Design  | Missing by Design  |
| Round 1 | Observed (100%)    | Observed (100%)    | Observed (100%)    |
| Round 2 | Missing by Design  | Observed (100%)    | Observed (100%)    |
| Round 3 | Missing by Design  | Observed (99.91%)  | Observed (99.91%)  |
| Round 4 | Missing by Design  | Observed (99.02%)  | Observed (99.02%)  |
| Round 5 | Missing by Design  | Observed (38.57%)* | Observed (52.09%)* |
| Round 6 | Missing by Design  | Observed (97.02%)  | Observed (97.02%)  |
+---------+--------------------+--------------------+--------------------+
* In Round 5, data collection was intentionally targeted to the scrutiny subsample (1,200 households).
```

### Categorization of Missingness
1. **Missing by Survey Design:**
   - `sbill` in Rounds 2–6: 11,240 cells (100% missing by design; enumerators transitioned to physical bill verification).
   - `rbill` and `runit` in Round 0: 2,394 cells (100% missing by design; meter verifications were instituted at Round 1 baseline).
2. **Missing Due to Initial Household Attrition:**
   - 146 households attrited after Round 0 ($146 \times 6 = 876$ missing rows per variable in Rounds 1–6).
3. **Missing Due to Scrutiny Design Subsampling (Round 5):**
   - In Round 5, only 1,200 of the 2,248 retained households were targeted for survey to evaluate scrutiny effects. Of these, 1,171 verified consumption values were recorded.
4. **True Unplanned Survey Non-Response (Rounds 1–4, 6):**
   - Round 1: Exactly **0 missing values** across all 2,248 households (100.0% complete).
   - Round 2: Exactly **0 missing values** across all 2,248 households (100.0% complete).
   - Round 3: Exactly **2 missing values** (0.09% non-response; 2,246 observed).
   - Round 4: Exactly **22 missing values** (0.98% non-response; 2,226 observed).
   - Round 6: Exactly **67 missing values** (2.98% non-response; 2,181 observed).

---

## 3. Availability Matrix by Survey Round and Treatment Group

The table below presents the empirical counts and observed percentages for the primary verified physical consumption outcome (`runit`) across all survey rounds and experimental arms:

| Survey Round | Treatment Arm | Total Households (N) | Observed `runit` | Missing `runit` | Observed (%) | Missing (%) |
|---|---|---|---|---|---|---|
| **Round 0** | Control (T0) | 586 | 0 | 586 | 0.00% | 100.00% (By Design) |
| | Neighbor (T1) | 605 | 0 | 605 | 0.00% | 100.00% (By Design) |
| | Suburb (T2) | 602 | 0 | 602 | 0.00% | 100.00% (By Design) |
| | Knowledge (T3) | 601 | 0 | 601 | 0.00% | 100.00% (By Design) |
| **Round 1** | Control (T0) | 550 | 550 | 0 | **100.00%** | 0.00% |
| | Neighbor (T1) | 567 | 567 | 0 | **100.00%** | 0.00% |
| | Suburb (T2) | 568 | 568 | 0 | **100.00%** | 0.00% |
| | Knowledge (T3) | 563 | 563 | 0 | **100.00%** | 0.00% |
| **Round 2** | Control (T0) | 550 | 550 | 0 | **100.00%** | 0.00% |
| | Neighbor (T1) | 567 | 567 | 0 | **100.00%** | 0.00% |
| | Suburb (T2) | 568 | 568 | 0 | **100.00%** | 0.00% |
| | Knowledge (T3) | 563 | 563 | 0 | **100.00%** | 0.00% |
| **Round 3** | Control (T0) | 550 | 549 | 1 | **99.82%** | 0.18% |
| | Neighbor (T1) | 567 | 567 | 0 | **100.00%** | 0.00% |
| | Suburb (T2) | 568 | 567 | 1 | **99.82%** | 0.18% |
| | Knowledge (T3) | 563 | 563 | 0 | **100.00%** | 0.00% |
| **Round 4** | Control (T0) | 550 | 548 | 2 | **99.64%** | 0.36% |
| | Neighbor (T1) | 567 | 561 | 6 | **98.94%** | 1.06% |
| | Suburb (T2) | 568 | 563 | 5 | **99.12%** | 0.88% |
| | Knowledge (T3) | 563 | 554 | 9 | **98.40%** | 1.60% |
| **Round 5** | Control (T0) | 550 | 293 | 257 | 53.27% | 46.73% (Subsample) |
| | Neighbor (T1) | 567 | 294 | 273 | 51.85% | 48.15% (Subsample) |
| | Suburb (T2) | 568 | 290 | 278 | 51.06% | 48.94% (Subsample) |
| | Knowledge (T3) | 563 | 294 | 269 | 52.22% | 47.78% (Subsample) |
| **Round 6** | Control (T0) | 550 | 526 | 24 | **95.64%** | 4.36% |
| | Neighbor (T1) | 567 | 554 | 13 | **97.71%** | 2.29% |
| | Suburb (T2) | 568 | 558 | 10 | **98.24%** | 1.76% |
| | Knowledge (T3) | 563 | 543 | 20 | **96.45%** | 3.55% |

*Key Takeaway:* Availability of verified energy consumption is virtually complete (>98.4% across all treatment arms in Rounds 1–4, and >95.6% in Round 6), with no evidence of differential attrition or treatment-correlated non-response.

---

## 4. Household-Level Longitudinal Outcome Coverage

Auditing longitudinal panel completeness at the household unit level produces the following coverage metrics:

1. **Main Intervention Period (Rounds 1, 2, 3, 4):**
   - **Target Universe:** 2,248 retained panel households.
   - **Observed in all 4 rounds:** **2,224 households (98.93%)**.
   - **Missing exactly 1 round:** **24 households (1.07%)**.
   - **Missing 2 or more rounds:** **0 households (0.00%)**.
   - **Zero observed values:** **0 households (0.00%)**.
2. **Full Longitudinal Scope (Rounds 1, 2, 3, 4, and 6):**
   - **Target Universe:** 2,248 retained panel households.
   - **Observed in all 5 rounds:** **2,160 households (96.09%)**.
   - **Missing exactly 1 round:** **85 households (3.78%)**.
   - **Missing exactly 2 rounds:** **3 households (0.13%)**.
   - **Missing 3 or more rounds:** **0 households (0.00%)**.
   - **Zero observed values:** **0 households (0.00%)**.
3. **Pre-Baseline & Baseline (`sbill`, Rounds 0 & 1):**
   - **Target Universe:** 2,394 initially recruited households.
   - **Observed in both Rounds 0 and 1:** **2,248 households (93.90%)**.
   - **Observed in Round 0 only (attrited):** **146 households (6.10%)**.
   - **Zero observed values:** **0 households (0.00%)**.

---

## 5. Outcome Mapping & Suitability for Econometric Evaluation

| Research Question | Dataset Outcome Variable | Key Rounds Utilized | Model Specification Suitability |
|---|---|---|---|
| **Short-Term Electricity Savings (kWh)** | `runit` | Rounds 1 (Baseline), 2, 3, 4 (Intervention) | Highly suitable; 98.93% balanced panel, 0 missing in baseline. |
| **Short-Term Bill Savings (BDT)** | `rbill` | Rounds 1 (Baseline), 2, 3, 4 (Intervention) | Highly suitable; captures financial relief under increasing block tariff. |
| **Long-Term Habit Persistence** | `runit`, `rbill` | Rounds 1 (Baseline) vs. 6 (15 months later) | Highly suitable; 96.09% complete 5-round coverage. |
| **Pre-Treatment Parallel Trends** | `sbill` | Rounds 0 (Pre-baseline) vs. 1 (Baseline) | Highly suitable; 100% complete for retained households. |
| **Hawthorne / Scrutiny Testing** | `runit`, `rbill` | Round 6 stratified by Round 5 `followup` | Highly suitable; exactly 300 households per arm surveyed in Round 5. |

### Conclusion on Outcome Suitability
The outcomes `runit` and `rbill` are directly verified from utility meters and bills, completely avoid survey recall bias during the post-treatment phases, exhibit exceptionally high panel continuity (>96%), and fully support both short-term difference-in-differences and long-term persistence evaluations.
