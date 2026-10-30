# Urja — Task 2: Experiment Design, Panel Structure & Outcome Suitability Validation

## 1. Overview & Purpose

This directory contains the code, validation reports, and unit tests for **Task 2** of **Project Urja**.

**Task Objective:** Determine whether the empirical design, household panel structure, and outcome availability in the Bangladesh electricity conservation field experiment support a credible, defensible intervention evaluation.

**Scope of Investigation:**
- Verified experimental design, randomization unit, and treatment arms.
- Household and neighbourhood hierarchical cluster structure.
- Panel integrity, sample attrition, and key uniqueness across 7 survey rounds.
- Outcome measurement definitions, verified utility billing schedules, and design-induced missingness.
- Methodological mapping of original Stata replication specifications (`.do` files) to Python-compatible estimators.
- Objective assessment of 12 candidate feasibility criteria.

> [!NOTE]
> **Strict Non-Estimation Boundary:** Task 2 is strictly a structural feasibility audit. In accordance with task rules, it does NOT compute treatment-effect estimates, run regressions, conduct hypothesis tests, compute baseline balance p-values, or perform econometric modeling.

---

## 2. Directory Layout

```text
validation/urja/task_02/
├── README.md                                           # Task 2 documentation and execution guide
├── scripts/
│   └── validate_study_design.py                        # Reusable Python validation script
├── reports/
│   ├── experiment_design_summary.md                    # Detailed experimental design & timeline report
│   ├── treatment_assignment_audit.csv                  # Treatment counts, consistency & neighbourhood spread
│   ├── sample_flow_by_round.csv                        # Round-by-round sample flow and outcome counts
│   ├── household_panel_integrity.csv                   # Panel structure, key uniqueness & attribute checks
│   ├── outcome_definition_and_measurement_map.md       # Outcome definitions, units & measurement map
│   ├── outcome_availability_by_round_treatment.csv     # Complete round x treatment availability matrix
│   ├── household_outcome_coverage.csv                  # Household-level outcome coverage by period
│   ├── attrition_and_followup_audit.csv                # Baseline attrition & Round 5 scrutiny audit
│   ├── original_replication_specification_map.md       # Econometric model mapping from Stata do-files
│   └── task_02_feasibility_findings.md                 # 12 feasibility criteria evaluation report
└── tests/
    └── test_validate_study_design.py                   # 10 unit tests with synthetic data fixtures
```

---

## 3. Execution Instructions

### Running the Validation Script
Execute the validation script against the raw data directory containing the original Dataverse archive:

```bash
python validation/urja/task_02/scripts/validate_study_design.py \
  --raw-dir data/raw \
  --output-dir validation/urja/task_02/reports
```

### Running Unit Tests
All unit tests run on isolated synthetic datasets and do not touch or modify the raw research data:

```bash
# Using pytest
python -m pytest validation/urja/task_02/tests/test_validate_study_design.py -v

# Or using standard unittest
python -m unittest validation/urja/task_02/tests/test_validate_study_design.py -v
```

---

## 4. Key Findings Summary

| Evaluation Dimension | Verified Finding | Status |
|---|---|---|
| **Experimental Design** | 4-arm RCT (Control, Neighbor Comparison, Suburb Comparison, Knowledge Advice) | Verified |
| **Randomization Unit** | Individual Household (`hid`) within 59 neighbourhood clusters (`nid`) | Verified |
| **Initial Recruited Sample** | 2,394 households (Round 0 pre-baseline) | Verified |
| **Retained Panel Sample** | 2,248 households (Rounds 1 through 6) | Verified |
| **Baseline Attrition** | Exactly 146 households (6.10%); zero subsequent attrition | Verified |
| **Key Uniqueness** | Exactly 15,882 rows; 0 duplicate `(hid, round)` pairs; 0 missing IDs | Verified |
| **Assignment Stability** | 0 households change treatment group across rounds (100% constant) | Verified |
| **Primary Physical Outcome** | Verified electricity use in kWh (`runit`); 98.93% 4-round panel completeness | Verified |
| **Primary Economic Outcome** | Verified electricity bill in BDT (`rbill`); 98.93% 4-round panel completeness | Verified |
| **Long-Term Evaluation** | Round 6 conducted 15 months post-baseline; 96.09% 5-round panel completeness | Verified |
| **Scrutiny Test Subsample** | Exactly 1,200 households (300 per treatment arm) in Round 5 | Verified |
| **Replication Mapping** | Stata `reghdfe` DiD models map directly to Python `pyfixest` / `statsmodels` | Verified |
| **Feasibility Verdict** | All 12 feasibility criteria confirmed; candidate project fully supported | **PASS** |
