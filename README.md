# Industrial Process Health Monitoring and Fault Alerting

**Status:** Planning and data-validation stage. This is a workspace starter pack, not a completed ML project.

## Project goal
Build a local, reproducible machine-learning application that analyzes recorded fluid-mixing process sensor data, detects anomalous behavior, and helps a user inspect sensor trends and alerts. The goal is a credible Machine Learning Engineer portfolio project combining classical ML, sound evaluation, software engineering, and proportionate MLOps.

## Working rules
- ChatGPT is the technical decision-maker and implementation planner.
- Antigravity is the implementation worker. It writes/executes only the tasks specified in the active prompt; it must not silently make major modeling, evaluation, architecture, or scope decisions.
- The user runs Antigravity and returns its report, relevant diffs, test output, and questions to ChatGPT before the next stage.
- Work in small, reviewable checkpoints. Do not start the next phase until the current checkpoint is accepted.
- Never invent metrics, claim tests passed without running them, or claim live factory/production validation. The application uses recorded data unless a real live integration is explicitly built later.
- The final README and resume wording will be polished after the project works and the results are measured.

## First task
Open `prompts/00_DATASET_AND_REPRODUCIBILITY_AUDIT.md` and give that prompt to Antigravity. Do not start model development or application coding yet.

## Planned deliverable (subject to the audit)
- A reproducible data-validation and training/evaluation pipeline.
- A fair comparison of four classical anomaly-detection approaches plus a simple statistical baseline, if the data supports this.
- A FastAPI inference endpoint and a Streamlit dashboard for inspecting recorded runs.
- Tests, experiment tracking, containerized local execution, a small CI workflow, and practical documentation.

## Starter workspace layout
- `docs/PROJECT_BRIEF.md` — problem, scope, and boundaries.
- `docs/EXECUTION_PLAN.md` — phased plan and acceptance gates.
- `docs/WORKING_AGREEMENT.md` — role and change-control rules.
- `docs/DECISION_LOG.md` — record approved technical decisions and evidence.
- `docs/CHECKPOINT_TRACKER.md` — current checkpoint tracker.
- `prompts/00_DATASET_AND_REPRODUCIBILITY_AUDIT.md` — the only prompt to run first.
- `data/` — local data; raw/processed datasets are not committed by default.
- `reports/` — audit, evaluation, and final reports.
- `src/`, `tests/`, `configs/`, `.github/workflows/` — implementation folders to populate only after the audit passes.

## Proposed source dataset
- Repository: https://github.com/MalteRamonat/fluid-mixing-anomaly-benchmark
- Paper: https://doi.org/10.1109/ACCESS.2025.3592815

The source is a candidate, not an unconditional commitment. The audit must verify the actual files, labels, data provenance, license scope, split feasibility, and baseline reproducibility before we commit to the dataset.

## Repository and file access
Antigravity can work with the local workspace you open for it. ChatGPT cannot directly inspect files on your computer just because a folder exists locally. To review the project here, share the GitHub repository URL after pushing/connecting it, or upload the relevant files and Antigravity's report in this conversation. Do not share passwords, tokens, or secrets.
