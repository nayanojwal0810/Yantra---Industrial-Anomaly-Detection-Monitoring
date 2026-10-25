# Project Brief

## Working title
**Industrial Process Health Monitoring and Fault Alerting**

## User problem
Operators and engineers need help noticing unusual behavior in multivariate process sensors during industrial operations. This project evaluates whether classical anomaly-detection methods can screen recorded fluid-mixing process runs for anomalous behavior and present whole-run health assessments and sensor traces in an understandable local application. 

Because recorded runs are annotated as complete experimental conditions (100% anomalous or 100% normal) without within-run transition timestamps, the system operates as a **whole-run process-health screening tool** rather than a real-time fault-onset or detection-delay detector.

## Intended user
A process/data engineer inspecting recorded runs, comparing sensor behavior, and reviewing candidate anomaly alerts. This is a portfolio prototype, not a safety-critical control system.

## Why this is a useful ML engineering project
It connects the end-to-end ML lifecycle: data validation, leakage-aware evaluation, model comparison, model artifact management, inference, monitoring-oriented visualization, automated testing, reproducible environments, and documentation.

## Approved data source
- Public repository: https://github.com/MalteRamonat/fluid-mixing-anomaly-benchmark
- Paper DOI: https://doi.org/10.1109/ACCESS.2025.3592815
- Audited commit: `07b9565c794da01b46ec76c442f416d509d6b73b`

The source was audited in Checkpoint 1 (`reports/audit/initial_data_audit.md`) and approved for whole-run evaluation across 54 standardized 50-column runs (excluding `dataset_0` due to schema discrepancy). Only real physical recordings are used; simulation outputs are excluded.

## Working ML plan
Compare a simple statistical threshold baseline with four classical approaches:
1. Isolation Forest.
2. One-Class SVM.
3. Local Outlier Factor in novelty-detection mode where appropriate.
4. PCA reconstruction error as a multivariate anomaly score.

These are candidates rather than guaranteed final choices. If one is incompatible with the data or evaluation design, the decision-maker will replace it with a better-justified classical method. Deep learning is out of scope for this project.

## Evaluation principles
- **Split unit:** Split strictly by whole process runs/experiments (fixed manifest: 20 train normal, 8 validation, 26 test). Never mix adjacent rows or windows from the same run across train, validation, or test.
- **Label boundaries:** Fault-onset timing and detection delay are unsupported by the ground truth annotations and must not be claimed.
- **Feature isolation:** Keep labels, fault names, file names, timestamps, IDs, and other non-predictive metadata out of model features.
- **Preprocessing isolation:** Fit preprocessing scalers strictly on training-normal data; transform validation and test without refitting.
- **Threshold calibration safeguard:** Set and calibrate anomaly decision thresholds strictly on normal validation data. Final test labels must never be accessed to tune thresholds, select hyperparameters, or choose models.
- **Reporting:** Report run-level false alarms on normal runs, fault detection rates across multiple fault categories, and point-level summary curves with documented caveats. Never rely on accuracy alone for imbalanced data.
- **Uncertainty & limitations:** Categories with only 1–2 runs must be reported as exploratory. Do not promise a particular score before experiments are run.

## Product output
If the audit passes, the intended final result is a local CPU-friendly app with:
- A repeatable data-validation and training/evaluation command.
- Versioned/traceable model artifacts and tracked experiments.
- A FastAPI endpoint for validated inference.
- A Streamlit dashboard to choose recorded process runs, inspect sensor traces, and review anomaly scores/alerts.
- Tests, Docker-based local execution, a minimal CI workflow, and useful setup/limitations documentation.

The dashboard must label recorded-data replay clearly. It must not imply that a real factory or live control system is connected.

## Non-goals
- No deep-learning models in this project.
- No claims of deployment in an operational factory.
- No aim to beat state-of-the-art research results or recreate every experiment in the source paper.
- No Kubernetes, Kafka, Spark, or cloud infrastructure unless a concrete, demonstrated requirement appears.
- No invented metrics, fabricated screenshots, or aspirational results presented as measured results.

## Success criteria
1. Dataset and licensing review passed and documented.
2. Evaluation protocol approved before comparisons are run.
3. All compared methods use a fair, reproducible pipeline.
4. Evaluation results include errors/false alarms and a discussion of limitations.
5. An ordinary user can follow the documentation to reproduce the supported workflow locally.
6. API, dashboard, model artifact loading, and automated tests work together.
7. Core design decisions are understandable and explainable by the project owner in an interview.
