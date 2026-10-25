# Decision-Maker Review: FCU Feasibility Gate

**Decision: Do not approve the final project definition yet. Keep the FCU dataset as a conditional candidate and run one focused modeling-value gate.**

The latest validation work is meaningfully stronger than the first audit: the worker selectively inspected five real CSV members from the official ZIP, checked the matching normal and fault trajectories, measured some downsampling effects, updated prior art, and cleaned inherited scaffolding on this branch. The branch comparison confirms it is ahead of `main` and has not diverged from the recorded `main` base.

However, the evidence is not yet enough to authorize the end-to-end project plan.

## What is accepted

- The official LBNL page describes 49 FCU CSV files, 17 fault types at different severities, one fault-free case, HVACSIM+ simulation, 29 data points, a one-year time span and one-minute sampling: https://faultdetection.lbl.gov/dataset/simulated-fan-coil-unit-data-set/
- The primary dataset paper citation is now corrected to Granderson et al., *Scientific Data* 10, article 342 (2023), DOI 10.1038/s41597-023-02197-w.
- Candidate A remains unsuitable for the DL-led project because the inspected dataset has too few independent fault episodes on one physical testbed.
- HazardNet remains a poor fit for the proposed supervised hazard task unless its missing label-generation/reproduction artifacts can be recovered and verified.
- The old inherited tracked scaffolding has been removed on the validation branch only. The branch diff reports `main` as the merge base, with `main` unchanged. Keep the cleanup branch-only.

## Why the FCU problem is not approved yet

### 1. The audit is not reproducible from the repository

The reports cite scripts under a local Antigravity scratch directory, but those scripts and machine-readable outputs are not committed. Another reviewer cannot reproduce the ZIP member extraction, audit counts or downsampling results from the repository. A detailed report is useful, but the supporting code matters.

### 2. The downsampling conclusion is too strong

The identical full-year means at 1, 5 and 15 minutes are expected when regularly sized blocks are averaged and all rows are retained. They do not prove that a model can still distinguish low-severity faults. The report also shows that the peak leak signal falls from 1.680 to 1.234 GPM at 15 minutes, a reduction of about 26.5%, so transient information does change.

The current aggregation rule also uses `max` for `FCU_CTRL`, whose documented values are shutdown=0, operate=1, and setback=2. Taking the numeric maximum is not a valid general aggregation for a categorical operating mode. The downsampling test must compare event/window-level distributions and detection outcomes using semantically valid aggregation, not only global averages.

### 3. The proposed metrics do not match the data structure

The inspected fault scenarios represent a fault condition for the full simulated year. They do not provide a clearly labeled fault-inception timestamp. Therefore, time-to-detect (TTD) measured from a real fault onset cannot be calculated from these files as currently defined. Remove TTD unless a separate, explicit and clearly synthetic onset experiment is justified.

### 4. Normal-only evaluation needs a real held-out normal segment

Definition 1 says to train using 100% of the normal file while reporting a false-alarm rate. It must hold out contiguous normal periods for threshold calibration and final normal evaluation. Report false alarms on the untouched normal test segment, and never tune the threshold on fault scenarios. State that scenarios share the same timestamps and weather trajectory as the normal baseline; this is a controlled counterfactual simulation, not independent field validation.

### 5. “Physics-residual diagnostic attribution” is not yet a validated diagnostic capability

A large sensor reconstruction error identifies an unusual channel; it does not automatically identify a physical root cause. The report needs a pre-defined mapping from measurable residuals to candidate components and a fair evaluation against the scenario's known simulated fault family. If this mapping cannot be validated, describe the result as *sensor-level anomaly attribution*, not root-cause diagnosis.

### 6. We have not shown that deep learning adds value

The 20% cooling-valve leak has a strong, persistent signature in the audited simulation, including flow while the command is closed. A simple physics rule may detect this case. That is useful, but not enough to justify a DL-led project. We must test a small number of distinct low-severity fault families and compare simple rules/statistical detection, relevant classical ML, and one small temporal deep-learning feasibility probe. This is a pilot only, not final model selection or final training.

### 7. Differentiation is still weak

The 2023 seasonal-generalization study already covers unseen-season HVAC FDD. The September 2026 SSRN preprint covers robustness to downsampling and sensor degradation on LBNL DataFDD and a real AHU dataset. Sources: https://doi.org/10.1016/j.energy.2023.128180 and https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7438633.

The project must not claim a new ML discovery. A reusable, well-tested engineering system can be a good portfolio project, but APIs, CI, MLflow and Docker alone are not genuine problem-level differentiation. We need evidence of a concrete technical challenge and useful outcome beyond packaging standard components.

## Decision

**Conditional continuation only.** Candidate B remains the best of the three audited data sources so far, but the final problem statement is not approved. The recommended “normal-only anomaly scoring with physics-residual attribution” is a hypothesis that must pass the next gate, not a final selection.

The next gate should answer one question: **Does this data support a defensible, ML/DL-centered task in which the model adds measurable value beyond straightforward physical rules, while keeping the claimed scope honest?**

Do not write the end-to-end implementation plan yet. Do not polish the public-facing project narrative. Do not start production application development.

## Required correction reminders

- Remove TTD from the current evaluation plan unless a fault-inception protocol is independently justified.
- Correct the false-alarm metric units: false alarms per 1,000 hours and a raw ratio are not the same unit.
- Remove or source claims such as a five-alarms-per-week operational limit, building energy cost figures, training runtimes and storage sizes that are not measured or directly sourced.
- Retain the corrected primary paper reference everywhere. If the execution log records the earlier incorrect DOI, annotate it as an old error or correct it consistently.
- Do not claim the full 49-file Parquet dataset was physically created if only five samples were processed; label full-dataset size as an estimate unless measured.
- Do not call the 48 scenario files 48 independent real-world events. They are simulated scenario files for one modeled FCU and shared weather year.

## Source evidence reviewed

- Official LBNL FCU dataset page: https://faultdetection.lbl.gov/dataset/simulated-fan-coil-unit-data-set/
- OpenEI dataset listing: https://data.openei.org/submissions/5763
- Primary dataset paper: https://www.nature.com/articles/s41597-023-02197-w
- Seasonal generalization paper: https://doi.org/10.1016/j.energy.2023.128180
- Current robustness preprint: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7438633
