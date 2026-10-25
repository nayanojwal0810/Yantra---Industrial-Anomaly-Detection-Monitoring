# Yantra — Candidate Problem & Dataset Validation

This branch (`validation/problem-feasibility-review`) is an isolated, temporary validation workspace. It is used to audit candidate industrial anomaly detection problems and datasets before any project selection, model architecture, or application code is approved.

> [!NOTE]
> This repository does not currently contain a trained model or production application. All ongoing work is strictly focused on data audits, literature verification, and evaluation feasibility.

## Current Validation Status

- **Status:** Candidate validation in progress. Conditional candidate under gate review: LBNL / OpenEI Simulated Fan Coil Unit (FCU) Fault Detection & Diagnostics.
- **Active Task Gate:** [FCU Feasibility and Novelty Gate (`validation/prompts/01_FCU_FEASIBILITY_AND_NOVELTY_GATE.md`)](validation/prompts/01_FCU_FEASIBILITY_AND_NOVELTY_GATE.md)
- **Executive Comparison & Matrix:** [Candidate Comparison Report (`validation/research/candidate_comparison.md`)](validation/research/candidate_comparison.md)
- **Decision-Maker Review:** [Decision-Maker Review Ledger (`validation/review/decision_maker_review.md`)](validation/review/decision_maker_review.md)
- **Branch Cleanup Record:** [Legacy Cleanup Manifest (`validation/review/branch_cleanup.md`)](validation/review/branch_cleanup.md)

## Workspace Organization

```
validation/
├── prompts/              # Task specifications and gate definitions
│   ├── 00_CANDIDATE_VALIDATION.md
│   └── 01_FCU_FEASIBILITY_AND_NOVELTY_GATE.md
├── research/             # Empirical audits, literature reviews, and logs
│   ├── candidate_comparison.md
│   ├── data_audit.md
│   ├── related_work.md
│   ├── feasibility_and_evaluation.md
│   ├── sources.md
│   └── agent_execution_log.md
└── review/               # Technical decision reviews and cleanup manifests
    ├── decision_maker_review.md
    ├── feasibility_gate_results.md
    └── branch_cleanup.md
```
