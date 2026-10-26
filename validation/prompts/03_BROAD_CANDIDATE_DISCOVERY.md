# Fresh DL-First Project Discovery Gate (Colab GPU-Aware)

## Purpose

Start a genuinely fresh selection for the user's main ML/DL resume project. The old HVAC/FCU candidate has been rejected; preserve its validation records as history, but do not try to rescue that project or anchor the new search to previously listed candidates.

Read the current requirements first:
- validation/review/fresh_project_selection_brief.md
- validation/review/decision_maker_review_03.md

The task is to research and rank the best two or three candidate problem/data pairs. It is **not** to select a final architecture, start implementation, or produce the full project plan.

## What success looks like

Find a real and specific problem where a capable deep-learning model can make a meaningful contribution, classical ML comparisons are informative, the data and evaluation can support credible conclusions, and the completed project will be practical to demonstrate and defend in a technical interview.

The user is willing to use a GPU in Google Colab. **Do not compromise the ML/DL core by selecting an unnecessarily weak model just to keep the project CPU-only or tiny.** Equally, do not choose a large or fashionable model merely for appearance. Choose a model family suited to the data and problem, with a concrete hypothesis that can be tested against serious baselines.

## Hard boundaries

- The main contribution must be ML/DL. Software engineering, data engineering and MLOps should support the modeling work, not become the project's main novelty.
- No NLP, text-modeling, LLM, RAG, or GenAI-centered projects. This selection is for the user's separate ML/DL portfolio project.
- Search across domains and modalities, such as computer vision, audio signals, sensor/time series, robotics, energy/electrical systems, industrial processes, remote sensing, scientific imaging, agriculture, or other credible areas. Do not limit discovery to industrial anomaly detection.
- A public dataset alone is not a project idea. Specify the stakeholder, decision or real-world need.
- Do not claim novelty based only on a new dataset, a higher benchmark score without valid comparison, a deployment API, a dashboard, an explanation plot, Docker, CI, experiment tracking, or a generic robustness check.
- Keep the work feasible for one developer using public resources and Google Colab GPU when available. Paid APIs, paid cloud as a requirement, proprietary data/software, distributed training, very large-scale annotation, or multi-GPU orchestration are not acceptable defaults.
- Favor data that can be examined efficiently. Do not make full multi-gigabyte downloads the default when official previews, focused subsets or selective downloads exist. A larger dataset is acceptable if the specific modeling need warrants it and a reliable, manageable subset can be justified.
- Verify data-use terms from authoritative sources. Missing, conflicting, or unclear licenses must be explicit hard stops until resolved; do not infer rights from a working download link.
- Keep all claims honest: separate reported paper results, measured exploratory results, estimates and hypotheses. Never invent metrics or run results.

## Model-selection philosophy: strong but proportionate

Do not rank candidates higher simply because the model is small, and do not rank them higher simply because a model is complicated. Prioritize the task's ML/DL potential and the quality of the evidence.

For each finalist, identify realistic options at three levels:

1. **Simple baseline:** a transparent rule, majority/mean predictor, nearest-neighbor baseline, or appropriate simple statistical method.
2. **Classical ML baseline(s):** two relevant families where appropriate, such as gradient-boosted trees, Random Forest, SVM, logistic regression, Isolation Forest, or feature-based models. Explain what inputs each can fairly use.
3. **Credible DL families:** at least two plausible candidates where meaningful, chosen for the data type. Examples include a modern residual CNN or suitable pretrained vision backbone for images; object detection or segmentation models when spatial localization matters; 1D CNN/TCN/GRU/LSTM or a compact time-series transformer for temporal signals; audio CNNs for spectral/temporal audio; or suitable encoder architectures for scientific signals. These are options, not architecture decisions.

A pretrained model is allowed when its license, training-data implications and suitability are clear. Fine-tuning a capable pretrained backbone can be appropriate; do not assume training from scratch is always better. Do not use a transformer or deep architecture where the task/data offers no plausible reason for it.

For each candidate, explain:
- what useful structure DL could learn that a simple or feature-based approach may miss;
- the hypothesis and measurable result that would support that role;
- how a fair experiment could prove the hypothesis wrong;
- what a sensible fallback would be if the initial DL model does not beat the baselines.

The final project need not prove that DL beats every baseline on every metric. It must have a credible ML/DL contribution and a clear reason for the model comparison to matter. If a simple approach solves the task just as well, state that as a possible rejection outcome.

## GPU and completion budget

Google Colab GPU is an intended resource, not a guarantee of a particular card or uninterrupted availability. Do not assume a specific GPU type, memory capacity or session duration without evidence.

For each finalist:
- estimate the size of the chosen training subset, input resolution or sequence length, batch size range, parameter scale where knowable, approximate GPU memory, training duration, and number of experiments needed;
- identify whether training fits a commonly available Colab GPU tier when provided, and mark estimates versus measured facts;
- note whether pretrained weights, mixed precision, caching or smaller data subsets are useful, without using them to excuse a weak model;
- keep the first credible experiment bounded and finishable; make it possible to reproduce the experiment across sessions;
- identify likely Colab limits and one practical contingency if the GPU is unavailable or a session is interrupted.

Do not run expensive training during discovery. Lightweight metadata inspection and a small data sample or input-throughput smoke test is allowed if needed to validate the budget.

## Fresh research rules

- Do not begin from the old candidate lead list or treat those candidates as preferred. Search independently from current problem needs, recent research and authoritative public data sources. A previously mentioned dataset may reappear only if it genuinely ranks well under the new evaluation.
- Screen **at least 12 candidate problem/data pairs across at least five distinct domains**. Use current web research because dataset status, data access, terms and recent prior art can change.
- Use a mix of official dataset pages, peer-reviewed papers or data descriptors, maintained baseline code, license terms, and credible recent research. Record source URLs, publication date when available, and access date.
- Seek candidates where the labels, sampling process and intended evaluation unit are well understood. Distinguish independent sites, subjects, devices, objects, recordings, experiments or runs from correlated rows, crops, windows, segments or augmented examples.
- Look for realistic split strategies such as subject/site/device/group/time-held-out splits, when supported by the data. Do not assume random row splitting is valid.
- Search prior art by the exact problem framing and dataset, not only by dataset name. Include existing baseline implementations and common benchmark saturation. Check if the desired contribution has already been done.
- Assess whether labels represent the target claim. Do not call weak proxy labels ground truth, simulated events real failures, or random image splits independent generalization.
- For images, audio and other modalities, check for duplicate/source leakage, subject/site/device leakage, near-duplicate samples, and data-origin artifacts where relevant.
- Record the data license separately from the source code license and pretrained weight license.

## Mandatory three-stage decision process

These stages must remain separate. Do not skip ahead or merge them into one large task.

### Stage 1 — Candidate discovery, shortlist and winner recommendation
This current prompt covers Stage 1 only.
- Discover and screen at least 12 candidate problem/data pairs across five or more domains.
- Use evidence to narrow the list to two or three strong finalists.
- Compare the finalists and recommend one **shortlist winner** with a clear rationale, alternatives, risks and unresolved assumptions.
- The recommendation is not final approval. The user/technical decision-maker reviews the shortlist and explicitly selects which candidate advances.
- Stage 1 can include preliminary source, license and metadata checks sufficient to screen candidates, but it must not pretend these replace the full validation gate.
- Do not begin extensive data profiling, model experiments, architecture selection, final training, application implementation or the end-to-end execution plan. Only small inspections needed for trustworthy discovery are allowed.

### Stage 2 — Proper validation of the selected winner (separate future task)
Start this stage only after the user/technical decision-maker explicitly selects a candidate.
- Re-verify official data access and terms, labels, independent evaluation units, data quality, sample/compute requirements, prior art, realistic baselines, leakage-safe splits and a defensible ML/DL hypothesis.
- Inspect a representative data subset and run small, pre-registered feasibility experiments where needed. Compare strong-enough classical ML and DL candidates on fair splits; use Colab GPU when justified and available.
- Define objective pass/fail conditions before experiments. Record failures, uncertainties and results; do not tune only for good-looking results.
- Conclude with an explicit decision: pass, conditional pass with named limitations, or reject/return to discovery.
- Do not write the full implementation plan until the selected winner passes this validation gate.

### Stage 3 — End-to-end execution plan (separate future task)
Begin only after Stage 2 passes and the user/technical decision-maker approves the validated project definition.
- Prepare the full staged plan: data acquisition and governance, EDA, preprocessing, baseline experiments, ML/DL model development, ablations, evaluation, reproducibility, software architecture, testing, basic MLOps, demo/deployment, monitoring limits, documentation, milestones and acceptance criteria.
- Choose the final model family and a realistic Colab training plan from validation evidence, not from assumptions made during discovery.
- Do not start implementation until the user approves the execution plan.

Current task must stop after Stage 1 is documented, committed and verified.

## Required process

### Stage 1 — Broad screen

Build an inventory of at least 12 distinct candidate problem/data pairs covering five or more domains. For each record:
- stakeholder/problem and target;
- official data source and one credible prior-art source;
- modality, approximate volume and feasible subset;
- label provenance and independent evaluation units;
- explicit data-license evidence and any limits;
- current state of research and what might differentiate the framing;
- plausible simple, classical ML and DL baselines;
- Colab-GPU feasibility and estimated effort;
- key hard stop or uncertainty.

Reject obvious failures early. Do not fill the list with superficial variations of the same dataset or task.

### Stage 2 — Choose and deeply audit the best three

Choose the top three only after the breadth screen. Use official metadata, manifest/API, file headers, sample records or a small sample to verify structure where practical. Avoid unjustified full downloads. Keep downloaded data outside Git; log source, exact size and checksum if material is downloaded.

For each of the three finalists, verify:
- what the examples actually look like and the label schema;
- what counts as one independent evaluation unit and how many exist;
- whether groups, sites, devices, subjects, sessions or time periods allow a valid holdout;
- missingness, imbalance, duplicate or leakage risks where practical;
- data-use terms and separate code/pretrained-model licenses;
- feasibility of a fair simple baseline, meaningful classical ML and at least one capable DL family;
- whether a focused subset can preserve the question rather than make the task artificially easy;
- expected Colab training and data-loading constraints;
- what can legitimately be claimed from the data source.

If a sample cannot be accessed, record the actual blocker and lower confidence. A metadata-only audit is not a successful raw-data audit.

### Stage 3 — Formulate a defensible problem

For each finalist, propose no more than two precise, testable problem framings. Each framing must specify:
- primary user and decision that the output supports;
- prediction target and output form;
- real-world reason the decision matters;
- a specific differentiator backed by prior-art review;
- hypothesis for the ML/DL contribution;
- expected input and label requirements;
- one simple baseline, at least two relevant classical ML comparisons where appropriate, and two credible DL model families;
- valid train/validation/test design and independent unit;
- metrics suited to the decision and label distribution;
- ablations or stress tests that would genuinely test the hypothesis;
- main failure mode and evidence that would disprove the idea;
- likely technical-interview questions and what the user must understand or demonstrate to answer them.

Do not invent a new algorithm just to sound novel. A precise, useful and well-evaluated task can be distinctive; a generic benchmark rerun is not.

### Stage 4 — Scored decision matrix with hard stops

Score each finalist from 1 to 5, with evidence, confidence and one-line rationale for every score:
- real-world importance and clarity of the stakeholder decision;
- potential for a meaningful ML/DL contribution;
- quality and credibility of labels;
- sufficiency of independent evaluation units;
- problem-level differentiation and prior-art headroom;
- fair and informative classical ML comparisons;
- data access and license clarity;
- evaluation validity and leakage control;
- Colab-GPU feasibility and experiment budget;
- implementation effort (higher score means more manageable);
- interview explainability and defensibility;
- resume/demo value;
- useful software engineering/basic-MLOps fit without over-engineering.

Separate hard stops from scores. A high average cannot compensate for missing legal permission, inaccessible data, unusable labels, insufficient independent units for the proposed claim, invalid evaluation, no credible ML/DL role, or a requirement for paid resources the user did not approve.

For each finalist, include 8–10 likely interview questions covering data, labels, baselines, architecture, loss/objective, evaluation, leakage, ablations, failure cases, GPU/training choices and deployment. State what experiment, plot, code test or reasoning would support a strong answer.

### Stage 5 — No project implementation yet

Do not build the application, select the final architecture, train final models, or write the full end-to-end plan in this gate. A small data inspection or input-pipeline smoke test is allowed only when necessary; document precisely what it proves and does not prove. Stop once the research and ranked shortlist are published.

## Required deliverables

Create new files under validation and preserve the earlier FCU history:

1. research/fresh_candidate_discovery.md — broad screen of at least 12 candidates across five domains, rejection reasons and ranked top three.
2. research/fresh_candidate_data_audit.md — verified sources, licensing, sample structure, labels, independent units, leakage risks, size and Colab budget for the finalists.
3. research/fresh_candidate_related_work.md — precise prior-art comparison and novelty/saturation analysis for each proposed framing.
4. research/fresh_candidate_sources.md — source ledger with URLs, source type, publication/access dates and exact claims supported.
5. review/fresh_project_selection_gate.md — executive recommendation, detailed scored matrix, hard stops, open questions and next validation step.
6. review/fresh_candidate_shortlist.json — compact machine-readable shortlist with source, license state, domain, task, independent unit, data size, model families, GPU budget estimate, score, confidence, risk and decision status.
7. Append to research/agent_execution_log.md without deleting or rewriting earlier audit history.

Keep research concise, sourced and easy to review. Link to papers and official pages; do not copy long passages. State explicitly when a claim is not independently verified.

## Git and repository rules

Repository: nayanojwal0810/Yantra---Industrial-Anomaly-Detection-Monitoring  
Branch: validation/problem-feasibility-review  
Remote: https://github.com/nayanojwal0810/Yantra---Industrial-Anomaly-Detection-Monitoring.git

Before editing, verify the remote, current branch, status and recent commit. Work only on the required validation branch. Never change main, force-push, rewrite history, or delete prior FCU evidence. New research must stay under validation; a factual README update is allowed. Do not commit raw data, large binaries, caches, credentials, or model weights. Review staged diffs; run git diff --check; commit and push to the required branch; then verify remote commit SHA and all important file links.

## Acceptance criteria

The gate is complete only if:
- at least 12 distinct tasks across five or more domains were screened;
- the top three have detailed evidence and checked data metadata/samples where access allows;
- license terms are explicit and unclear licenses are handled as hard stops;
- independent units and leakage risks are addressed;
- each finalist has credible prior-art comparisons and a testable ML/DL hypothesis;
- model recommendations are appropriate to the task, not artificially constrained to CPU or tiny models;
- Colab GPU requirements, time and uncertainty are documented without assuming unlimited access;
- the user can reasonably learn and defend the project end to end;
- no NLP/LLM/RAG/GenAI task is proposed;
- previous FCU reports and the branch cleanup history are preserved;
- the new research is committed, pushed and verified on validation/problem-feasibility-review only.

The final response must provide the verified commit SHA, links to the six primary deliverables, the ranked top three with the strongest reason for each, any hard stops, and the single candidate recommended as shortlist winner. Clearly state that the user/technical decision-maker must choose the candidate that advances. Do not start Stage 2 validation until the user selects the candidate, and do not create the Stage 3 execution plan until validation passes and is approved. This is a shortlist recommendation, not final project approval.
