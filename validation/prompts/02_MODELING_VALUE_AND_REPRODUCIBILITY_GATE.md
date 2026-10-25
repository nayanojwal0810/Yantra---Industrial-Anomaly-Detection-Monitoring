# Modeling Value and Reproducibility Gate

## Objective

Decide whether the LBNL/OpenEI simulated Fan Coil Unit (FCU) dataset can support a defensible, DL-centered portfolio problem with meaningful classical ML comparison and practical engineering value. This is a small feasibility pilot, not final model selection, final training, or production implementation.

Read first:
- validation/review/decision_maker_review_02.md
- validation/review/feasibility_gate_results.md
- validation/research/candidate_comparison.md
- validation/research/data_audit.md
- validation/research/related_work.md
- validation/research/feasibility_and_evaluation.md
- validation/research/sources.md
- validation/research/agent_execution_log.md

Use the corrected official paper citation: Granderson et al., Scientific Data 10, article 342 (2023), DOI 10.1038/s41597-023-02197-w.

## Git requirements

Repository: nayanojwal0810/Yantra---Industrial-Anomaly-Detection-Monitoring
Branch: validation/problem-feasibility-review
Remote: https://github.com/nayanojwal0810/Yantra---Industrial-Anomaly-Detection-Monitoring.git

Verify remote, current branch, recent commit and working-tree status before editing. Work only within validation/, except for updating the root README if needed to keep its validation-workspace description accurate. Do not alter main or other branches. Preserve user changes. No force-push, history rewriting, raw dataset commits, large output files, secrets or credentials.

After work, run git diff --check, inspect the staged diff, commit and push to the required branch, then verify the remote branch SHA and links.

## Part A — Make the evidence reproducible

The prior report depends on scripts in the local Antigravity scratch folder that are not part of the repository. Do not treat Markdown claims as independently reproducible until the supporting code is committed.

1. Add reusable scripts under `validation/scripts/` for:
   - reading the official FCU ZIP central directory and extracting selected members without downloading the complete archive where HTTP Range works;
   - auditing selected CSVs (schema, timestamps, row counts, nulls, infinities, constant columns, sample intervals, label/scenario mapping);
   - reproducing the aggregation comparison and generating small summaries.
2. Refactor paths into command-line arguments or documented configuration. Do not hard-code a user-specific Windows scratch path.
3. Do not commit the CSVs. Scripts must accept a local directory or extract explicitly selected members into a temporary/out-of-repository directory. Document dependencies and exact commands.
4. Commit small machine-readable output summaries (JSON/CSV) under `validation/review/evidence/`. Include enough output to check the reported numbers, but no raw time-series data or large binaries.
5. State which figures were independently reproduced by the committed scripts, which are estimates, and which remain unverified.

If a script cannot reproduce a reported number, correct the report rather than editing the script to force the expected answer.

## Part B — Correct the current methodological problems

Update the reports and explicitly record the correction history.

1. **Downsampling:** Equal full-year means at 1-, 5-, and 15-minute rates are expected from regular block averaging; they do not by themselves prove detectability is preserved. Compare distributions, window-level signals and detection results. Report peak/transient changes as well.
2. **Aggregation semantics:** Never use numeric `max` as the generic aggregation for `FCU_CTRL`, where values mean shutdown=0, operate=1, setback=2. Use a semantically valid rule such as duration share/majority and record transitions, or retain categorical states with a suitable representation. Distinguish continuous measurements, analog actuator commands, and discrete modes.
3. **Time-to-detect:** The fault-scenario files represent conditions across a full year and do not define a verified fault-onset time. Do not report TTD from these files unless you define a separate, justified simulated-onset experiment and label it as synthetic. Prefer removing TTD for the current task.
4. **False alarms:** Split the single fault-free annual trajectory into contiguous training, normal-calibration and untouched normal-test blocks. Prevent window overlap across split boundaries using an embargo at least as long as the input window. Train only on normal training windows. Pick anomaly thresholds using normal calibration data only. Measure false alarms on untouched normal test windows. Never tune thresholds on fault scenarios.
5. **Shared environmental trajectory:** Fault files and the normal file share identical timestamps/weather. Use this as a controlled paired-simulation test and state that limitation. Do not claim independent field validation or unseen-building generalization.
6. **Scenario unit:** The 48 fault files are severity-specific simulated scenarios, not 48 independent buildings or real fault episodes. Summarize performance per scenario and per fault family; do not treat every minute as an independent sample.
7. **Diagnostic attribution:** A high reconstruction error on a sensor is not automatically a root-cause diagnosis. Define a transparent, pre-specified mapping from channel/physics residuals to a component/fault family, then check it against the known simulated scenario labels. If this cannot be validated, use the name “sensor-level anomaly attribution,” not “root-cause diagnosis.”
8. **Unsupported claims:** Correct the false-alarm metric units, label measured versus estimated time/storage claims, and remove or cite unsupported claims about operational alarm limits, financial costs, and training speed. Correct the old incorrect DOI if it appears in historical reports; preserve audit history by noting the correction rather than silently concealing it.
9. Do not describe the full 49-file Parquet collection as created or measured unless it was actually built. If extrapolated from selected files, label it as an estimate.

## Part C — Run a small modeling-value pilot

This pilot is permitted to fit small baseline models only to decide whether the candidate is worth keeping. It is not final modeling, broad hyperparameter tuning, or a final architecture decision.

### Select representative scenarios

Use official ZIP inventory names; do not guess filenames. Include:
- one fault-free scenario;
- the 20% cooling-valve leakage case already inspected;
- at least three other low/minor-severity scenarios from different physical mechanisms, where the inventory supports them (for example damper/valve sticking, sensor bias, coil fouling, or filter/air blockage).
Prefer scenarios that test different mechanisms rather than multiple severities of the same fault. Record exact source filenames, fault names and severity. If a requested low severity does not exist, select and explain the lowest available severity.

### Compare three levels of approach

1. **Simple reference:** A small set of transparent physical/statistical rules based on available channels. Derive any fitted thresholds from normal training data only. Map each rule to an explicit physical relationship. Do not claim that ASHRAE Guideline 36 is an off-the-shelf classifier; cite the exact rule only if you can verify it applies to this FCU.
2. **Classical normal-only ML/statistical detector:** Choose one appropriate family for this unsupervised setting (for example robust Mahalanobis distance, Isolation Forest or One-Class SVM). Explain the choice; do not add LightGBM merely because it is popular.
3. **One small temporal DL feasibility probe:** Choose a compact sequence model solely to test whether temporal learning appears to add value. Keep it CPU-feasible or use an available free accelerator. Record the exact provisional architecture and reason, but do not call it the final model choice and do not over-tune it.

All approaches must use the same normal train/calibration/test protocol and same scenario evaluation windows where practical.

### Sampling-rate comparison

Compare 1-minute, 5-minute and 15-minute versions of the selected files. Use the same physical window duration across rates rather than changing real-time context without noting it. For example, a 60-minute window corresponds to 60, 12 and 4 time steps, respectively. This is an illustration; choose a sensible duration for the observed signal dynamics and explain it.

For each sampling rate:
- use semantically valid aggregation;
- report data size and processing time only when measured;
- report normal false-alarm rate on the untouched normal test period;
- report detection/alert rate for each selected fault scenario and macro-average across scenarios;
- report precision-recall results only with a clear window-label definition and a warning that adjacent windows are temporally dependent;
- report any brief physical patterns or transitions lost after aggregation;
- compare performance and compute cost without tuning against test labels.

For the pilot threshold, define a pre-set operating point derived from normal calibration data (for example the 99.5th percentile of calibration anomaly scores). Use the same principle for all anomaly-score detectors. Also show actual false alarms on the untouched normal test data; do not promise a specific false-alarm rate before measuring it.

Do not use time-to-detect unless a defensible onset time exists.

### Pass/fail logic

Candidate B is not automatically approved because the data can be loaded. Recommend keeping it for the main project only if:
- the evidence scripts reproduce the core data and aggregation findings;
- fault scenarios contain enough varied, measurable signals for a fair comparison;
- the simple rule does not trivially solve almost the entire intended task;
- the ML/DL pilot has a credible role beyond adding complexity;
- the chosen task can be evaluated without relying on unavailable labels or invalid time-to-detect metrics;
- a specific project-level differentiator remains defensible after prior-art review.

If a simple physical rule performs as well as the ML/DL approach across the intended scope, say so plainly. Do not invent reasons to keep deep learning. Recommend revising the task or rejecting the candidate for a DL-centered project.

## Required deliverables

1. `validation/review/modeling_value_gate_results.md` — pilot results, reproducibility evidence, scenario comparison, corrected task definition, limitations and pass/fail recommendation.
2. `validation/scripts/` — scripts needed to reproduce the core subset extraction, data audit and pilot evaluation (no raw data).
3. `validation/review/evidence/` — small machine-readable summaries of audited counts, aggregation findings and pilot metrics.
4. Update `validation/research/candidate_comparison.md`, `data_audit.md`, `related_work.md`, `feasibility_and_evaluation.md`, `sources.md` and `agent_execution_log.md` as required for correctness and reproducibility.
5. Keep `validation/review/branch_cleanup.md` as the record of cleanup; do not recreate the removed legacy folders.
6. Update root README only if needed to point to the active review and prompt; keep it short and factual.

## Final decision required

Recommend exactly one:
- **Keep FCU** with a precisely defined DL-centered task and a defensible project-level contribution;
- **Keep FCU as an engineering benchmark only**, acknowledging that it may not meet the differentiation requirement;
- **Reject FCU for this goal** and return to discovery of another domain/dataset.

Do not create the full end-to-end implementation plan yet. Wait for the decision-maker's review.

## Final response requirements

Be concise. State:
- the provisional decision and the key evidence;
- exact scripts/tests executed and any failures;
- which numbers are measured versus estimated;
- changed files;
- commit SHA and verified remote-push status;
- direct GitHub links to the key report, scripts and evidence files;
- the most important unresolved risk.
