# Broad Candidate Problem Discovery Gate

## Objective

The LBNL FCU candidate has been rejected as the main dataset for the intended DL-centered portfolio project. Read the decision record first:

- `validation/review/decision_maker_review_03.md`
- `validation/review/modeling_value_gate_results.md`
- `validation/research/candidate_comparison.md`
- `validation/research/data_audit.md`
- `validation/research/related_work.md`
- `validation/research/sources.md`

Now conduct a fresh, broad, evidence-based discovery process to identify the best two or three replacement problem/data candidates. The goal is to find a genuine real-world problem where deep learning has a meaningful role, classical ML comparisons are informative, and an end-to-end software/data/MLOps system is practical on free resources.

This is discovery and validation only. Do not start final model training, application implementation, or the end-to-end project plan.

## Portfolio fit: the non-negotiable selection principles

This project is for a resume and technical interview. The best candidate is not the one with the most exotic model; it is the one that solves a meaningful problem, has a defensible ML/DL core, can be completed efficiently, and can be explained end to end by the project owner.

Optimize for all of the following:

1. **ML/DL remains the core.** The main technical contribution must involve a clear prediction, representation, temporal/spatial modeling, or decision problem where a neural model has a plausible role. Do not let APIs, dashboards, cloud infrastructure, data pipelines, or MLOps become the main contribution.
2. **Prefer lightweight, interpretable architecture choices.** Start from compact models (for example, a small CNN/TCN/GRU, compact vision backbone, or modest tabular model where appropriate). Do not assume transformers, large pretrained models, large GPUs, complex ensembles, multi-agent systems, or expensive training are necessary. Avoid architecture complexity unless a specific data property and experiment justify it.
3. **Efficient completion is a first-class criterion.** The first useful version should fit in a small public-data subset, modest local CPU or modest free compute, and a bounded number of experiments. Identify the minimum viable model and what can be postponed. Penalize candidates requiring extensive manual annotation, multi-gigabyte downloads, elaborate simulation, distributed training, or lengthy data preparation.
4. **Differentiation must be concrete and testable.** Find a specific operational decision, failure mode, constraint, or evaluation setting—not just “use DL on dataset X.” State what existing baselines and prior work already do, what remains plausibly useful, and how an experiment could disprove the proposed differentiation. Do not invent novelty.
5. **Interview defensibility is essential.** Prefer tasks where the owner can explain the data-generating process, labels, leakage risks, model choice, loss/objective, metrics, trade-offs, failure cases, deployment limits, and ethical/legal constraints without relying on black-box claims. Explicitly list likely interviewer questions and what evidence would support the answers.
6. **Software engineering and MLOps should be basic but high quality.** Aim for reproducible data/model pipelines, clear configuration, testing, experiment tracking, a small inference interface, containerization when useful, CI checks, and documented monitoring limits. Do not build an over-engineered platform or imply that MLOps alone creates model novelty.
7. **Choose the smallest model that credibly tests the hypothesis.** For each candidate, specify a compact first-pass baseline, one realistic classical ML comparator, and one lightweight DL family. Explain why each is relevant. Keep architecture choice provisional until data and labels are validated.
8. **Make trade-offs visible.** Score expected implementation effort, ease of explanation/defense, likely demo quality, and DL value separately in the decision matrix. A candidate with excellent benchmark scores but a complicated, weakly differentiated, hard-to-defend setup should rank below a simpler and more defensible candidate.

Do not select the most fashionable topic, largest dataset, or highest-complexity architecture by default. Prefer “distinctive because the problem framing and evidence are strong,” not “distinctive because it uses a complicated model.”

## Project constraints

- Main modeling emphasis: deep learning, with meaningful classical ML and simple baselines.
- No NLP, LLMs, RAG, generative AI, or text-modeling tasks. Those belong to the user's separate AI/GenAI project.
- Allowed domains and modalities are open: vibration/current/voltage waveforms, multivariate sensor time series, robotics, power/energy systems, industrial audio, computer vision, scientific sensors, or another well-supported domain. Do not limit the search to industrial anomaly detection only.
- Must address a specific real-world user need or operational decision, not just a benchmark label.
- Must offer a credible problem-level differentiator. Leakage-safe evaluation, explainability, Docker, APIs, drift plots, dashboards, monitoring, or using a recently released dataset do not count as differentiation by themselves.
- All resources must be publicly accessible and free to use under clearly understood terms. Verify the license, not just the download link. Unclear or missing data license is a hard-stop until resolved.
- Data must be practical: prefer a locally processed dataset or focused subset under 500 MB. A larger archive is acceptable only if a clearly justified, reliable selective-download path allows a useful small subset. Do not require a multi-GB full download as the default route.
- Must be feasible on local CPU or modest free compute. Do not assume paid cloud, a paid API, proprietary software, or a large GPU.
- The problem and dataset must support meaningful independent evaluation. Do not confuse rows, windows, augmented signals, or scenario files with independent physical systems, machines, test runs, or fault events.
- Keep the work and reports in simple, active English.

## Git and repository requirements

Repository: `nayanojwal0810/Yantra---Industrial-Anomaly-Detection-Monitoring`

Required branch: `validation/problem-feasibility-review`

Remote: `https://github.com/nayanojwal0810/Yantra---Industrial-Anomaly-Detection-Monitoring.git`

Before editing, verify origin, current branch, status and recent commit. Do not alter `main` or any other branch. Work only under `validation/`, except for a small root README update if needed. Preserve prior reports and decision records; do not delete the FCU evidence. Do not force-push, rewrite history, or commit raw datasets, large binaries, secrets, caches, or model weights. Commit and push the new research to the required branch, then verify the remote SHA and report links.

## Candidate leads to investigate (hypotheses, not recommendations)

Use these as starting points, and expand beyond them if stronger candidates are found:

1. **Production wire-drawing telemetry** — https://zenodo.org/records/21526135
   - Record description reports 47,706 records at a 30-second cadence across three run-to-maintenance cycles, eight sequential machine blocks, motor current and vibration metrics, and a 10.2 MB public bundle including code.
   - Risks to verify: data license, target/label structure, independent maintenance cycles, leakage risks, whether the existing accompanying work already covers the proposed task, and whether the low-frequency aggregate signals support a useful DL problem.

2. **Industrial robot telemetry** — https://zenodo.org/records/17855686
   - Seven-axis joint-motion and energy telemetry under normal and intentionally altered operation; reported archive size 269.2 MB.
   - Hard-stop risk: the Zenodo page appears to have a blank license field. Verify terms from the authoritative source or disqualify it.

3. **Composite power-quality disturbances** — https://zenodo.org/records/22816322
   - Reported 100.9 MB CSV with 10 kHz experimental signals and 10 single/composite power-quality disturbance classes.
   - Verify license, number of independent recordings/experiments, exact label definitions, class balance, dataset generation method, and saturation of generic waveform classification.

4. **Paderborn bearing condition data** — https://mb.uni-paderborn.de/en/kat/research/bearing-datacenter/data-sets-and-download
   - High-resolution vibration/current signals across operating conditions.
   - Risks: CC BY-NC 4.0 restriction, dataset size, how to obtain a focused subset, how common the exact benchmark is, and whether the problem can genuinely stand out.

5. **MIMII DG industrial sound anomaly dataset** — https://zenodo.org/records/6529888
   - Five machine types with domain shifts; individual machine archives reported around 0.77–0.95 GB, 4.4 GB combined.
   - Risks: common benchmark, CC BY-NC-SA 4.0 terms, and size. Consider only if a useful, legally permitted subset is manageable and the problem is genuinely differentiated.

6. **High-resolution distribution power-quality monitoring** — https://repository.londonmet.ac.uk/11442/
   - Reported train/test files around 16 MB and 14 MB, with disturbance labels and features derived from industrial measurements.
   - Verify provenance, usage license, data access, labels, and whether minute-level aggregate features justify deep learning.

7. **Rotating-machine vibration with multiple failure types** — https://zenodo.org/records/10846291 and https://zenodo.org/records/14388093
   - Reported multi-file archives around 1.7 GB total, with individual files near 280 MB.
   - Verify license, independent runs, actual signal/label structure, and prior-art saturation before considering a subset.

8. **Additional candidates:** Search other domains, including electrical protection waveforms, non-NLP industrial vision, scientific sensor data, infrastructure monitoring, and process systems. Add at least two other candidates from independent, credible sources. Do not restrict the search to these starting points.

## Required research method

### 1. Breadth screen

Screen at least eight candidate problem/data pairs across at least four domains. Use multiple independent websites and prioritize:
- original data publishers and official dataset pages;
- peer-reviewed papers and data descriptors;
- the paper's code repository or maintained baseline implementation;
- authoritative license statements and direct file metadata;
- recent papers/preprints and comparable portfolio/open-source projects.

For every candidate, capture the exact source URLs, access date, publication date when available, license for data and code, download/subset size, labels, independent sample units, and key limitations. Do not guess a license or infer sample sufficiency from byte size or row count.

### 2. Deep audit of the top three candidates

Choose the top three only after the breadth screen, then inspect their official metadata or small samples where practical. Do not download large files without justification. Prefer direct preview, manifest, API metadata, HTTP headers, small sample, or one subset. Keep all downloaded material outside Git and record sizes/checksums.

For each finalist, establish:
- the actual user/stakeholder and operational decision;
- what the data measures and how labels are produced;
- the number of independent devices/machines/sites/runs/fault episodes;
- expected data and compute footprint for a credible experiment;
- whether the data can support a meaningful DL model and a fair classical ML baseline;
- likely simple baseline and why it may or may not solve the task;
- relevant prior art, existing tools and common student/portfolio projects;
- legal/data access blockers;
- what can and cannot be claimed from lab, simulated, or field data.

If actual data inspection is blocked, state the exact blocker and keep confidence low rather than pretending the audit passed.

### 3. Problem-level differentiation

For each finalist, propose no more than two precise, testable problem framings. Each must specify:
- primary user and decision;
- target and intended output;
- what makes it more useful than generic classification/anomaly detection;
- why the need matters in the real world;
- an evaluation design supported by the actual labels/data;
- independent evaluation unit and split logic;
- a realistic simple baseline, at least two relevant classical ML families, and plausible DL model families (do not choose a final architecture);
- metrics that reflect false alarms/missed events or operational benefit;
- the main way the idea could fail;
- a specific prior-art comparison that explains whether this is already solved.

A new dataset by itself is not a new problem. Do not invent an "unexplored gap." Explicitly reject generic classification if similar work already saturates it.

### 4. Strict decision matrix

Score each finalist from 1 to 5 on:
- real-world importance;
- problem specificity and differentiation;
- license and data access;
- label credibility and completeness;
- independent event/system sufficiency;
- DL suitability and a credible role for a lightweight model;
- value of classical ML comparisons;
- evaluation validity;
- data/compute/time feasibility;
- expected implementation effort (higher score = more manageable);
- ease of explaining and defending the full project in an interview;
- demo/resume value;
- software-engineering and basic-MLOps fit without over-engineering.

For every score, provide evidence, confidence and a short rationale. Keep hard stops separate from the average score: a missing license, unusable target, inaccessible data, invalid evaluation unit or unaffordable compute cannot be offset by high scores. Also include 5–8 likely interview questions for each finalist and the exact evidence, plots, tests or reasoning the project owner would need to answer them convincingly. Identify hard stops separately: missing/unclear license, inaccessible data, no usable target, too few independent runs for the intended claim, invalid labels, required paid resources, or no genuine task gap. Hard-stop failures cannot be offset by a high average score.

### 5. No implementation at this gate

Do not train final models or build an application. Small metadata parsing or read-only exploratory inspection is allowed. If a tiny benchmark experiment is required to establish feasibility, state the hypothesis first, limit it to the smallest useful test, log exactly what was run, and do not tune for a favorable outcome. Prefer deferring modeling to the next gate.

## Deliverables

Create these files under `validation/`:

1. `research/candidate_discovery.md` — executive shortlist, at least eight screened candidates, reasons for rejection/deprioritization, and top three finalists.
2. `research/discovery_data_audit.md` — source, license, download footprint, structure, labels, independent sample unit, compute, and caveats for the finalists.
3. `research/discovery_related_work.md` — existing research/tools, problem saturation, and evidence-backed differentiation or rejection for each finalist.
4. `research/discovery_sources.md` — source ledger with URLs, source type, publication/access dates, license evidence, and claims supported.
5. `review/discovery_gate.md` — calibrated decision matrix, hard stops, open uncertainties, and recommendation for the next joint decision.
6. `research/agent_execution_log.md` — append the commands, APIs, small downloads, checks, errors, and limitations for this discovery round without deleting the old audit history.
7. `review/candidate_shortlist.json` — small machine-readable shortlist with candidate name, domain, primary source URL, license status, approximate size, sample unit, strongest problem framing, key risk, score, confidence, and next validation gate.

Keep each report concise and evidence-rich. Do not copy long passages from papers; summarize them and link to the sources.

## Decision output

Recommend two or three finalists, ranked, and explain which one you believe deserves the next feasibility gate. Do not treat the rank as final project approval. The technical decision-maker will review the evidence and decide whether to select one or continue searching.

## Acceptance criteria

The task is complete only when:
- At least eight candidates across four or more domains were screened with sources.
- The top three have been checked against official dataset pages and actual metadata or a small data sample, where access allows.
- All license claims have explicit sources; unclear license is treated as a hard stop.
- Independent systems/runs are clearly separated from rows/windows.
- The proposed tasks are not generic label prediction disguised as novelty.
- The user’s no-NLP/no-GenAI boundary is respected.
- The solution fits free and manageable compute/data constraints.
- Each finalist includes evidence of real prior-art comparison and at least one credible failure mode.
- The previous FCU rejection and evidence remain preserved.
- All changes are under `validation/` except a necessary factual README link update.
- `git diff --check` passes, the staged changes are reviewed, and the commit is pushed to `validation/problem-feasibility-review`.
- The final response includes the verified commit SHA, direct GitHub links, ranked finalists, hard stops, and the main unresolved risk.

Do not create the full end-to-end implementation plan or begin project implementation. Stop for review after pushing the discovery reports.
