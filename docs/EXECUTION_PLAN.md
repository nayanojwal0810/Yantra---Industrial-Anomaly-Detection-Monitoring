# Execution Plan and Acceptance Gates

This is a controlled plan. The decision-maker updates it after reviewing each Antigravity report. Do not execute all phases in one agent run.

## Phase 0 — Workspace and repository setup
**Goal:** Have a clean project workspace and track decisions.  
**Work:** Create/open the local workspace in Antigravity; create a Git repository; commit the starter docs; ensure raw data and model artifacts are not accidentally committed.  
**Accept when:** The folder opens cleanly, Git works, a first commit exists, and no secrets or large unapproved data files are present.

## Phase 1 — Dataset, license, and reproducibility audit (current phase)
**Goal:** Determine whether the candidate source is suitable before investing in implementation.  
**Work:** Inspect the full upstream repository, source documentation, license text and any dataset-specific notices, CSV inventory/schema/labels, class/run distribution, time ordering, missing values, duplicate rows, preprocessing scripts, existing models/evaluation, and dependency/runtime requirements. Run small read-only/loadability checks where possible. Assess whether run-level holdout evaluation is feasible.  
**Deliverable:** `reports/audit/initial_data_audit.md`, plus brief execution evidence and exact source commit/revision.  
**Do not:** Build the app, choose a winning model, copy data into the final repo before license/size review, or claim validated performance.  
**Gate 1:** Decision-maker approves the dataset and split design, requests fixes to the audit, or rejects/replaces the source.

## Phase 2 — Data contract and exploratory analysis
**Goal:** Convert audit findings into an explicit, tested data contract.  
**Work:** Define file discovery, required/optional columns, timestamp handling, label parsing, types, missing/duplicate policies, feature/metadata exclusions, and a run manifest. Produce EDA summaries and plots that help answer domain questions.  
**Deliverables:** data dictionary, run manifest, validation code, EDA report and tests.  
**Gate 2:** Data validation passes on every selected run; the leakage/exclusion policy and split manifest are approved.

## Phase 3 — Evaluation protocol and baseline
**Goal:** Establish a trustworthy reference before tuning candidate models.  
**Work:** Define train/validation/test runs and metrics before modeling; implement a simple statistical baseline; document threshold calibration using training/validation data only. Use grouped/run-level splits where feasible.  
**Deliverables:** deterministic split manifest, baseline evaluation artifacts, tests proving test data is not used to fit preprocessing or choose thresholds.  
**Gate 3:** Decision-maker approves protocol and baseline report. If too few independent runs support a convincing holdout, change the claims or use a carefully documented leave-one-run/scenario-out protocol.

## Phase 4 — Classical-model comparison
**Goal:** Compare four appropriate methods under the approved protocol.  
**Candidate models:** Isolation Forest, One-Class SVM, Local Outlier Factor in novelty mode, and PCA reconstruction error. Baseline remains separate.  
**Work:** Implement models behind a common interface, fit scalers/preprocessors correctly, log parameters and artifacts, evaluate all methods with comparable data and thresholds, and record failures as well as successes. Tune only on training/validation runs.  
**Deliverables:** tracked experiments, run-level results, model comparison table/plots, error analysis and reproducibility commands.  
**Gate 4:** Select a model based on the approved use case and evidence, including false alarms. No model has to win just because it is more complex.

## Phase 5 — Inference package and API
**Goal:** Make the selected pipeline usable outside a notebook/script.  
**Work:** Package the fitted preprocessing and detector; implement input validation, predictable output schema, version/model metadata, error handling, logging and API tests. Add a reload consistency test.  
**Deliverables:** FastAPI service, request/response examples, unit/integration tests.  
**Gate 5:** API can load the saved model and score valid data; invalid data is rejected clearly; inference results match the pipeline's direct predictions.

## Phase 6 — Dashboard
**Goal:** Make model behavior inspectable and useful to a human.  
**Work:** Streamlit interface to select a recorded run, display sensor trends, show anomaly score/threshold and alert regions, and summarize run-level metrics. State clearly that this is recorded data/replay, not a live production feed. Avoid chart overload.  
**Deliverables:** working dashboard and simple user guide.  
**Gate 6:** End-to-end demo works on at least one normal and one fault run, with results consistent with the API.

## Phase 7 — Proportionate MLOps and hardening
**Goal:** Add lifecycle and reliability practices that solve specific problems.  
**Work:** MLflow tracking for parameters/metrics/artifacts; configuration and dependency pinning; Docker image or Compose setup if needed for the API/dashboard; GitHub Actions for linting/tests; simple model-quality gate; clear model/data provenance. Test local CPU operation.  
**Deliverables:** reproducible local run instructions, experiment records, CI workflow and smoke tests.  
**Gate 7:** A clean checkout can install/run the documented workflow; CI succeeds; model artifacts can be traced to a run/config/source revision.

## Phase 8 — Final verification and documentation
**Goal:** Deliver a reliable, understandable portfolio project.  
**Work:** Run from a clean environment; test documented commands; review failure paths; document architecture, how to reproduce results, model comparison, errors, limitations, data attribution/license, and technical decisions. Only then polish visuals and resume bullets using actual measured results.  
**Deliverables:** final README, architecture diagram, experiment report, demo steps/screenshots, setup guide, limitations, and defensible resume summary.  
**Gate 8:** No unsupported claims; core commands pass; owner can explain the system and important trade-offs.

## Cross-phase guardrails
- One task per Antigravity prompt. Agent returns files changed, commands executed, test output, unresolved questions and recommendations with evidence.
- Do not combine large refactors with model experiments.
- Use small commits and inspect diffs. Ask the decision-maker before changing dependencies, model families, splits, labels, metrics, product scope, or architecture.
- Keep raw data out of Git unless license and storage are confirmed and committing it is intentionally approved.
- GPU is optional. The final selected classical-ML pipeline must run on CPU; Colab may be used for convenient experimentation but should not be a runtime dependency.
