# Yantra — Candidate Problem & Dataset Validation

This branch (`validation/problem-feasibility-review`) is an isolated, temporary validation workspace. It is used to audit candidate industrial anomaly detection problems and datasets before any project selection, model architecture, or application code is approved.

> [!NOTE]
> This repository does not currently contain a trained model or production application. All ongoing work is strictly focused on data audits, literature verification, and evaluation feasibility.

## Current Validation Status

- **Status:** Candidate validation in progress. Modeling-value and reproducibility gate completed.
- **Active Task Gate:** [Modeling Value and Reproducibility Gate (`validation/prompts/02_MODELING_VALUE_AND_REPRODUCIBILITY_GATE.md`)](validation/prompts/02_MODELING_VALUE_AND_REPRODUCIBILITY_GATE.md)
- **Gate 02 Results:** [Modeling Value Gate Results (`validation/review/modeling_value_gate_results.md`)](validation/review/modeling_value_gate_results.md)
- **Executive Comparison & Matrix:** [Candidate Comparison Report (`validation/research/candidate_comparison.md`)](validation/research/candidate_comparison.md)
- **Decision-Maker Review:** [Decision-Maker Review 02 (`validation/review/decision_maker_review_02.md`)](validation/review/decision_maker_review_02.md)
- **Branch Cleanup Record:** [Legacy Cleanup Manifest (`validation/review/branch_cleanup.md`)](validation/review/branch_cleanup.md)

## Workspace Organization

```
validation/
├── prompts/              # Task specifications and gate definitions
│   ├── 00_CANDIDATE_VALIDATION.md
│   ├── 01_FCU_FEASIBILITY_AND_NOVELTY_GATE.md
│   └── 02_MODELING_VALUE_AND_REPRODUCIBILITY_GATE.md
├── research/             # Empirical audits, literature reviews, and logs
│   ├── candidate_comparison.md
│   ├── data_audit.md
│   ├── related_work.md
│   ├── feasibility_and_evaluation.md
│   ├── sources.md
│   └── agent_execution_log.md
├── review/               # Technical decision reviews, gate results, and evidence
│   ├── decision_maker_review.md
│   ├── decision_maker_review_02.md
│   ├── feasibility_gate_results.md
│   ├── modeling_value_gate_results.md
│   ├── branch_cleanup.md
│   └── evidence/         # Committed machine-readable audit and pilot metrics
│       ├── audit_summary.json
│       ├── aggregation_summary.json
│       └── pilot_evaluation_summary.json
└── scripts/              # Reproducible extraction, audit, downsampling, and pilot scripts
    ├── extract_fcu_subset.py
    ├── audit_fcu_subset.py
    ├── resample_fcu_subset.py
    └── run_pilot_experiment.py
```
