# Candidate Problem and Dataset Validation

## Objective

Find and validate a genuinely useful, feasible problem for a portfolio project whose primary modeling focus will be deep learning, supported by meaningful classical ML comparisons, software engineering, basic data engineering, and proportionate MLOps. No NLP. Do not choose algorithms or architecture before validating the problem and data.

This is a validation workspace only. Do not reuse, modify, inspect for reuse, or cite previous project work elsewhere in the repository. Limit changes to the `validation/` directory.

## Candidate areas to test

Treat these as hypotheses, not decisions:

1. Water distribution event diagnosis using WDSEventDB: https://github.com/Moazeni-s-Concise-Lab/WDSEventDB
2. HVAC fault diagnosis using public LBNL / OpenEI fault-detection data: https://data.openei.org/submissions/5763
3. HPC thermal-risk analysis using HazardNet: https://zenodo.org/records/10050368

You may nominate one or two stronger alternatives only if they have clearly superior evidence, manageable data size, accessible licensing, a credible ML/DL task, and a concrete real-world user need. Avoid broad generic projects.

## Non-negotiable rules

- Do not select a candidate because it sounds novel. Prove the specific need and identify closely related work or existing tools.
- Do not fabricate results, benchmark numbers, paper findings, download sizes, licenses, citations, or availability.
- Verify the original source, license, access method, data layout, labels and metadata.
- Do not download or commit large data files. Use metadata, HTTP headers, repository APIs, or a small sample where possible. Any sample download must be justified and documented.
- Do not train final models or build an application yet.
- Do not choose model architecture, stack or hyperparameters yet. Identify only model families that may be suitable, and state what evidence would justify them.
- If dataset class labels are derived from simulation setup, event identifiers, filenames, timestamps, or known scenario definitions, investigate whether apparent prediction is trivial or leaks the answer.
- For time-series data, distinguish rows from independent episodes, runs, machines, devices, and fault events. Explain the correct evaluation unit and feasible split strategy.
- Treat synthetically injected faults differently from real field faults. State what conclusions each dataset can and cannot support.
- Confirm data terms and license for both source data and code. Never imply that public availability means unrestricted reuse.
- Keep all changes inside `validation/`. Do not modify root README, docs, src, tests, reports, models, configs, data, or workflows. Do not remove any existing content.
- The agent executes research and audits only; the project owner retains all project decisions. Clearly separate facts, assumptions, and recommendations.

## Required investigation

### 1. Candidate data audit

For each candidate, report:
- Canonical project/data page, paper or technical documentation, published date and access date.
- Exact download/access route and whether it works.
- License for data, code, and paper separately if different.
- Approximate download size, extracted size if available, file types, schema, units and sampling rate.
- Counts at every meaningful level: rows, time windows, runs, devices, sites, fault episodes, classes and normal examples. Do not substitute row count for independent sample count.
- Label definitions, label provenance, class balance, missingness, repeated values, duplicate windows, sensor channels and timestamps.
- Data-generating process: real field/lab/simulation/hybrid; how faults are injected; operating regimes; train/test overlap risks.
- Whether a realistic evaluation can be run on a free CPU or limited free GPU, with estimates and assumptions.

### 2. Problem and novelty audit

For each candidate:
- Identify a specific stakeholder, decision and operational cost of the problem.
- Search academic papers, benchmark papers, GitHub implementations and relevant industry materials.
- Include at least 5 highly relevant sources when available, prioritizing original papers, official dataset pages, and maintained project repositories.
- Summarize existing approaches and what has already been solved. Do not call ordinary leakage-safe splits, explainability, drift plots, or deployment novelty by themselves.
- Propose up to 3 possible problem framings that solve a concrete gap. Each must be testable with available data.
- For each framing, explain the new value, required labels/data, realistic baseline, primary metric, likely limitation, and why it is not just a feature bundle.
- Reject any framing that cannot be credibly tested with available data.

### 3. Modeling suitability

Without selecting a final architecture:
- Determine whether the data structure supports meaningful DL (e.g., temporal sensor sequence modeling, representation learning, image analysis) and meaningful non-DL ML comparisons.
- Discuss simple statistical/rule baselines and two or more relevant classical ML families chosen based on data and assumptions, not popularity.
- Discuss suitable DL model families and what evidence must justify their use.
- Identify the risk that DL cannot outperform a simpler method and whether the project can still be valuable if that happens.
- Define an evaluation protocol that matches the real-world use case, with group/time/site/device/event isolation as appropriate.
- Choose metrics aligned with the problem and class imbalance. Explain false alarms and missed events, not just accuracy.
- Explicitly test possible shortcuts, leakage, overlap, spurious identifiers, and label artifacts.

### 4. Product and system feasibility

Evaluate whether a final project can credibly include:
- Reproducible ingestion and data validation.
- A small, reliable data preparation pipeline.
- Training and evaluation scripts, configuration and reproducible runs.
- A prediction interface or operator-facing workflow only if it adds value to the validated problem.
- Unit and integration tests; input validation and failure handling.
- Appropriate experiment tracking and model/data versioning.
- A local or low-cost deployment and small CI workflow.
- Basic monitoring based on meaningful data/model signals.
Do not add tools just to list technologies. Provide a minimal stack only after the candidate problem's needs are understood. Do not assume cloud credits.

### 5. Strict decision matrix

Score each candidate from 1–5 on:
- Real-world importance
- Specificity and differentiation of the problem
- Dataset quality and label credibility
- Independent event/sample sufficiency
- ML/DL suitability
- Evaluation validity
- Data size/access/license feasibility
- End-to-end engineering value
- Compute and time feasibility
- Interview defensibility

For every score, give evidence and uncertainty. Avoid false precision. Include hard-stop conditions. A candidate with no credible labels, no legal reuse path, or no feasible independent evaluation must not win due to a high average score.

### 6. Final recommendation

Deliver one of:
- Recommend a candidate conditionally with explicit gates,
- Recommend a different validated candidate,
- Reject all current candidates and explain why.

Do not start implementation. Define exactly which missing facts block a decision. Recommend only one next action that gives the highest information gain.

## Required deliverables under validation/

1. `research/candidate_comparison.md` — executive comparison, source-backed findings, decision matrix and recommendation.
2. `research/data_audit.md` — data-by-data structural and label audit; all counts must be sourced or actually inspected.
3. `research/related_work.md` — existing solutions, concrete gaps, and what would constitute real differentiation.
4. `research/feasibility_and_evaluation.md` — evaluation protocol options, risks, resources, and realistic limits.
5. `prompts/00_CANDIDATE_VALIDATION.md` — this prompt should be treated as the task specification; edit only to correct material errors, not to shrink the scope.
6. `research/sources.md` — URLs, source type, publication/access dates and which claims each source supports.
7. `research/agent_execution_log.md` — actions run, commands, small downloads, errors, checks and limitations.

Keep prose active and clear. Use simple English. Clearly label uncertain claims. Any statement that cannot be verified must say so. Do not polish public-facing README or resume bullets yet.

## Acceptance criteria

The work is not complete unless:
- Every candidate's original dataset source and license have been verified.
- Candidate comparison is based on actual inspected metadata/files where access permits, not only landing-page descriptions.
- Related-work checks include specific, relevant existing work and implementations.
- At least one promising candidate has a clearly testable problem gap and an honest fallback if DL adds no value.
- The evaluation protocol states the independent unit and how leakage/overlap will be prevented.
- Data/compute/time assumptions are explicit.
- The recommendation includes hard-stop gates and key unresolved risks.
- Every added/changed file is inside `validation/`.
- The final response lists files changed, work performed, evidence, blockers, and commands/tests run. Do not claim a test or download succeeded unless its output confirms success.

## Final response format

1. Summary recommendation (not an unconditional project selection).
2. Candidate comparison table with scores and evidence confidence.
3. Main findings and rejected ideas.
4. Open risks and hard-stop conditions.
5. File list.
6. Exact commands, checks and download actions performed, including failures.
7. Suggested next action for the decision-maker; do not proceed without their review.
