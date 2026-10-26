# Yantra — Fresh ML/DL Project Selection

This is an isolated validation workspace on branch `validation/problem-feasibility-review`. The purpose is to find a strong, defensible ML/DL resume project before building any application or committing to an architecture.

## Current decision

The workflow has three separate gates: candidate discovery and shortlist selection; proper validation after the user selects the candidate; and an end-to-end execution plan only after the candidate passes validation. No implementation is started at the discovery gate.

- **Previous FCU/HVAC idea:** Rejected as the main project after a preliminary modeling-value pilot. Its evidence is retained as historical validation; do not continue implementing that project.
- **Current stage:** Fresh problem and dataset discovery across multiple domains. This stage ends with a ranked shortlist and recommended winner; the user selects which candidate advances.
- **Modeling direction:** Deep learning and classical ML are the core. Google Colab GPU is an intended resource; candidates must not be prematurely limited to tiny CPU-only models. Model complexity must be justified by the task and remain achievable and explainable.
- **Project goals:** Real problem, concrete differentiation, reliable evaluation, defensible model choices, and supporting software engineering/basic MLOps.
- **Not in scope:** NLP, LLM, RAG, or GenAI-centered project ideas.

## Active instructions

- [Fresh DL-First Project Discovery Gate (Colab GPU-Aware)](validation/prompts/03_BROAD_CANDIDATE_DISCOVERY.md)
- [Fresh Project Selection Brief](validation/review/fresh_project_selection_brief.md)

## Prior decision and evidence

- [Decision-Maker Review 03 — FCU rejection](validation/review/decision_maker_review_03.md)
- [Modeling Value Gate Results](validation/review/modeling_value_gate_results.md)
- [Candidate Comparison Report](validation/research/candidate_comparison.md)
- [Data Audit](validation/research/data_audit.md)
- [Related Work](validation/research/related_work.md)
- [Repository Cleanup Record](validation/review/branch_cleanup.md)

## Workspace organization

- `validation/prompts/` — task specifications and decision gates.
- `validation/research/` — source-backed discovery, dataset audits, prior-art review and execution log.
- `validation/review/` — decision briefs, gate results and machine-readable evidence.
- `validation/scripts/` — reusable scripts from the earlier FCU validation only.

## Repository safety

All new discovery work stays on `validation/problem-feasibility-review`. The `main` branch must remain unchanged. Do not commit raw datasets, secrets, caches, model weights or large binaries. Candidate ranking is not final project approval; the technical decision-maker reviews the evidence before the next gate.
