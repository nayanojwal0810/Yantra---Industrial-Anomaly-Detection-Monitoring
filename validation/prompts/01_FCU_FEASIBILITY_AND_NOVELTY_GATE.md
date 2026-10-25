# FCU Feasibility and Novelty Gate

## Objective

Continue validation only. Candidate B (LBNL/OpenEI simulated Fan Coil Unit data) is a conditional data candidate, not an approved final project. The current framing, “Cross-Season Zero-Shot Nascent Fault Diagnostic,” is not approved yet.

Read these files first:
- validation/review/decision_maker_review.md
- validation/research/candidate_comparison.md
- validation/research/data_audit.md
- validation/research/related_work.md
- validation/research/feasibility_and_evaluation.md
- validation/research/sources.md
- validation/research/agent_execution_log.md

This task does not authorize application implementation, final model selection, or final model training.

## Git and branch requirements

Repository: nayanojwal0810/Yantra---Industrial-Anomaly-Detection-Monitoring
Required branch: validation/problem-feasibility-review
Remote: https://github.com/nayanojwal0810/Yantra---Industrial-Anomaly-Detection-Monitoring.git

Verify the remote, current branch, status, and recent commit before edits. Work only in validation/. Preserve all existing user work. Never change main, force-push, rewrite history, or include any files outside validation/. At the end, commit and push the validation updates to the required branch and verify the remote SHA and links.

## Important review corrections

- Primary LBNL paper is Granderson et al., Scientific Data 10, article 342 (2023), DOI 10.1038/s41597-023-02197-w. Do not use the incorrect DOI 10.1038/s41597-023-02206-8 or article 344.
- The official FCU page states 17 fault types at varying severity levels, 49 CSVs, HVACSIM+ simulation, 29 data points, one year, and 1-minute sampling. Do not call 48 fault CSVs 48 independent fault types or independent buildings.
- The FCU data is simulated on one FCU configuration using Des Moines weather, not live field data or field-confirmed physical-fault ground truth.
- Separate anomaly detection from fault diagnosis. A normal-only model scores anomalies; it does not identify root cause by itself.
- A held-out-season test within one simulated year is a seasonal stress test, not evidence of generalization to unseen buildings, years, climates, or real deployments.
- The literature already contains work on HVAC FDD generalization across unseen seasons: Zhong, Calautit, and Wu (2023), DOI 10.1016/j.energy.2023.128180.
- A 2026 SSRN preprint reports a robustness benchmark on LBNL DataFDD and a real AHU dataset involving noise, drift, bias, missingness, and downsampling. Include it as a preprint in the current prior-art review, not as peer-reviewed evidence: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7438633.
- Do not state CPU training runtimes, accuracy, saved memory, dataset conversion size, or preservation of subtle faults as measured facts unless you actually measure them.
- Do not call ASHRAE Guideline 36 an off-the-shelf fault-detection classifier. If a rules baseline is proposed, verify the exact rule and applicability to this FCU system.
- Do not preselect LightGBM or any deep architecture in this gate.

## Work required

### 1. Repair factual accuracy and evidence

Review all validation reports and correct:
- incorrect paper DOI/article number;
- scenario counts versus fault-type counts versus independent physical systems;
- simulated labels versus field ground truth;
- unmeasured runtime and storage claims;
- unsourced business/economic cost figures;
- inaccurate or overbroad claims of novelty.

Add source links beside relevant claims. Clearly label estimates and unverified items. Preserve the audit trail: do not hide earlier mistakes; note important corrections in the review or execution log.

### 2. Audit actual representative FCU data

Use official sources only:
- FCU source page: https://faultdetection.lbl.gov/dataset/simulated-fan-coil-unit-data-set/
- Full FDD data portal: https://faultdetection.lbl.gov/data/
- OpenEI submission: https://data.openei.org/submissions/5763
- Primary paper: https://www.nature.com/articles/s41597-023-02197-w

The official archive is about 518 MB. Do not commit data files. First determine whether one can reliably inspect selected ZIP members using HTTP range requests or another selective method. Avoid downloading the whole archive if selective extraction is practical. If that is not practical, document the blocker, expected disk use, and the smallest reasonable alternative before choosing a download approach. If you do download the full archive, keep it outside the repository and record its exact size and checksum.

Inspect at least:
- the normal/fault-free case;
- one specific fault type for which the inventory confirms low, medium, and high severity variants;
- the matching low/medium/high severity scenarios for that fault type, where available;
- optionally one second fault type with a different physical mechanism if it materially clarifies the task.

Derive exact filenames from the official inventory, not from guessed names.

For the actual inspected files, verify and report:
- full schema, timestamp format/range, row counts, sampling interval, units, missing values, duplicated timestamps, irregular intervals, invalid/infinite values, constant channels, and channel semantics;
- how fault labels are represented and how each row receives its scenario label;
- whether the fault is continuously injected for the full year or only for certain operational periods;
- whether exact timestamps and external weather schedules match across scenario files;
- class/label frequency only at the level the data genuinely supports;
- whether the small set of inspected files supports a credible evaluation of low-severity faults.

Do not infer general dataset quality from one file without labeling the limits.

### 3. Validate the downsampling assumption with a small, auditable test

Using only the selected representative files, compare 1-minute, 5-minute, and 15-minute data. Keep the raw sample unchanged. Test reasonable aggregation choices for continuous measurements versus control/status/command points; do not apply one averaging rule to every channel without checking its meaning.

The goal is not to train a final model. Quantify whether lower sampling rates suppress or preserve signals that distinguish the selected low-severity scenario from the normal case, and whether behavior differs by season. Use appropriate descriptive measures and plots/tables, such as:
- channel-wise distributions and missingness after resampling;
- differences between normal and low-severity conditions, by operating season;
- whether brief events or transitions disappear after aggregation;
- file sizes and processing memory/time only if actually measured.

Do not claim that these checks prove model-level detectability. Clearly state what they can and cannot establish.

### 4. Reassess the problem and current prior art

The current framing combines cross-season robustness, low-severity fault detection, and fault diagnosis. Separate them and assess them as distinct tasks.

Search carefully for existing work on:
- unseen-season HVAC fault detection/diagnosis;
- low-severity or incipient fault detection with HVAC time series;
- downsampling effects on fault detection;
- robustness to sensor noise, bias, drift and missing data;
- use of LBNL FCU or other LBNL FDD subsets;
- current preprints and implementations.

At minimum, directly assess how the 2023 seasonal-generalization paper and the 2026 SSRN robustness preprint overlap with this project. Include newer relevant work found during the research and identify the access/publication status of each source.

Do not say “unsolved” or “novel” unless the evidence supports that exact claim. If the current problem angle is too close to existing work, state that plainly.

### 5. Compare viable problem definitions

Offer no more than three problem definitions, all grounded in evidence and the actual data. They may include a narrower FCU task or a different candidate if a stronger, similarly feasible dataset/problem emerges.

For each definition, specify:
- one primary user and operational decision;
- exact target (binary anomaly detection, fault-type diagnosis, severity generalization, or something else);
- information available at training time and inference time;
- the independent evaluation unit;
- evaluation split and why it answers the question;
- primary metric and false-alarm/missed-event trade-off;
- what can be claimed from simulated data and what cannot;
- the genuine differentiation from existing projects and publications;
- data and compute burden;
- the reason the framing might fail.

Do not choose a model architecture or technology stack yet. Do not inflate differentiation with explainability, leakage-safe splits, an API, Docker, monitoring, or a dashboard alone.

### 6. Decision and deliverables

Create:
1. validation/review/feasibility_gate_results.md — actual sample audit, downsampling results, framing comparison, confidence and final gate recommendation.
2. Update validation/research/candidate_comparison.md with corrected counts, citations, and a calibrated score/confidence.
3. Update validation/research/data_audit.md with the representative-file evidence and limits.
4. Update validation/research/related_work.md with the 2023 seasonal paper and current 2026 preprint, plus other relevant work found.
5. Update validation/research/feasibility_and_evaluation.md only where evidence changes the task or split options.
6. Update validation/research/sources.md and validation/research/agent_execution_log.md with new sources, actions, checks, results, failures, and measured versus estimated quantities.

Recommend one outcome:
- keep Candidate B but replace the current framing with a specific defensible task;
- keep Candidate B only as a generic engineering benchmark and say it likely does not meet the differentiation target;
- reject Candidate B and return to discovery.

Do not create the full end-to-end execution plan yet. It will be prepared only after the project problem is approved.

## Acceptance requirements

- Actual data files must be inspected or a clear technical blocker must be documented; inventory PDF alone is not enough for the downsampling gate.
- The paper DOI/article-number correction is applied consistently.
- Current prior art is considered; the 2023 seasonal paper and 2026 SSRN preprint are explicitly assessed.
- The recommended task does not conflate detection with diagnosis.
- No invented metrics or unmeasured runtime claims remain.
- Downsampling is recommended only if the observed evidence supports it; otherwise keep higher resolution or reject the assumption.
- All edits remain within validation/.
- Changes pass git diff --check.
- All required changes are committed and pushed to validation/problem-feasibility-review, and the remote state is verified.
- Final response includes direct GitHub links and the actual pushed commit SHA, and is concise.
