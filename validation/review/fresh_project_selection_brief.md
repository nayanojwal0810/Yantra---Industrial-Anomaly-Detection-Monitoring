# Fresh Project Selection Brief

**Status:** Active selection brief  
**Purpose:** Define the user's requirements before choosing a new ML/DL portfolio project.

## What the user wants

Build a standout resume project where **machine learning and deep learning are the core technical contribution**. Software engineering and basic MLOps should make the work reproducible and usable, but must not replace substantive modeling work.

The user is willing to train on a GPU through Google Colab. Candidate selection must therefore **not reject a project simply because the strongest justified model needs GPU compute** or prematurely force every candidate into the smallest possible architecture. Choose a capable, technically appropriate model for the problem, while keeping the project achievable and the design explainable.

## Non-negotiable goals

1. **Strong ML/DL core:** A meaningful target, enough data and label quality, and a defensible hypothesis for why learned representations or temporal/spatial patterns matter.
2. **Real differentiation:** A specific user problem, operational constraint, generalization challenge, failure mode or evaluation design that is not merely “apply a standard model to a dataset.” Verify prior work before claiming a gap.
3. **Efficient, bounded execution:** A project can be completed through well-scoped experiments and a manageable data pipeline. Colab GPU is an intended resource, but exact GPU availability and quotas must not be assumed.
4. **Interview-level understanding:** The user should be able to explain the data, labels, splitting strategy, leakage risks, model and loss choices, baselines, metrics, ablations, errors, limitations and deployment choices.
5. **Useful model comparisons:** Include a simple baseline, one or more meaningful classical ML comparisons, and credible DL model families. The final model is chosen only after the data/task is validated and a fair experiment supports it.
6. **Professional supporting engineering:** Reproducible training/inference, configuration, tests, experiment tracking, a useful interface or demo, packaging and CI where appropriate. Keep MLOps proportional; it is not the claimed novelty.
7. **Feasible public data and usage:** Check authoritative access and data-license terms. Do not assume that a downloadable file is legally reusable. Unclear or restrictive terms are explicit risks or hard stops.
8. **No NLP/LLM/GenAI:** This is the ML/DL project, separate from the user's planned AI/GenAI project.

## Model-complexity principle

Do not optimize first for the smallest model. Optimize for a **strong, proportionate model that addresses the problem**. Depending on the task, options may include a well-chosen CNN or residual network, temporal CNN/TCN, recurrent model, transformer, segmentation/detection model, or a pretrained vision/audio backbone fine-tuned appropriately. These are examples, not a predetermined architecture.

Avoid two opposite mistakes:
- **Under-modeling:** selecting a weak model only to make the task easy, even though the data/problem has meaningful structure that a better DL model can exploit.
- **Over-engineering:** selecting a large or complicated architecture merely to sound advanced, without a clear hypothesis, adequate data, fair baseline or achievable training plan.

Use Colab GPU realistically. Estimate memory, input pipeline, training duration and number of experiments from authoritative evidence, small measurements or clearly marked assumptions. Keep a practical fallback, but do not downgrade the project automatically to CPU-only because local GPU resources are limited.

## Selection process

This is a fresh selection. The prior HVAC/FCU candidate is rejected for this project, and its work is retained only as an audit trail. Do not anchor the new search to the previous shortlist or treat old leads as preferred candidates. Search broadly across multiple domains and modalities, with no NLP or GenAI. Bring the evidence for the best two or three candidates back for a decision; do not start implementation or approve a final architecture yet.

## Repository and branch safety

Continue in this repository on branch `validation/problem-feasibility-review`. Keep new research under `validation/` except for a factual README update. Do not modify `main`, delete the prior FCU validation record, commit raw datasets, or rewrite history.
