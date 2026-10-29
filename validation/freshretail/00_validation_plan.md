# FreshRetailNet-50K — Candidate Validation Plan

## Purpose
Decide whether FreshRetailNet-50K is sufficiently feasible, reproducible, and worthwhile for Project 1. This is a candidate validation exercise, not the final portfolio implementation.

## Validation policy
- We will complete one task at a time and review all artifacts before authorizing the next task.
- Do not use or inspect any pre-existing repository files outside `validation/freshretail/`.
- Do not add the dataset files to Git.
- Do not claim successful reproduction unless a command was actually run and its output retained.
- Antigravity executes the task exactly as described; it must not choose new scope, select a project, or invent improvements.

## Candidate
FreshRetailNet-50K, the stockout-annotated fresh-retail demand dataset. Candidate only; not approved yet.

## Validation gates

### Gate 1 — Local dataset integrity and schema census
**Objective:** Verify that the user downloaded the official train and evaluation Parquet files and determine what they contain before installing a large stack or modeling anything.

Required evidence:
- Exact file paths, byte sizes, and SHA-256 checksums.
- Confirmation that both files can be read as Parquet.
- Row/column counts, column names, inferred dtypes, and a small safe preview.
- Null counts, duplicate counts at the documented row grain, date/time coverage, distinct entity counts, numeric ranges, and train/evaluation date overlap.
- Verify stock-status field representation and whether the expected fields are present.
- Compare observed values to the dataset card and official documentation; clearly distinguish checked facts from hypotheses.
- Reproducible script, deterministic report (JSON + Markdown), captured logs, requirements, and a concise run guide.

Pass if both files are readable and structurally consistent with the official schema, essential identifiers/targets/time fields exist, and there are no unexplained integrity failures. Conditional if a mismatch is explainable and fixable without altering raw data. Fail if files are corrupt, wrong-version, unlicensed, or the needed fields are absent.

### Gate 2 — Evaluation protocol and leakage audit
Only after Gate 1 passes. Derive the correct forecasting task, prediction unit, time cutoff, target definition, eligible features, and metrics from the original paper / official implementation. Map every feature to when it is known. Identify train/evaluation split boundaries and potential leakage. No modeling claims yet.

### Gate 3 — Minimal baseline feasibility
Only after Gate 2 passes. Implement and run the smallest credible baseline on a documented subset first, then a small full-data slice if resource use permits. Include a naive baseline and a simple statistical or tree-based baseline where justified. Record runtime, peak memory if available, metric definitions, seeds, and outputs. Do not tune excessively or claim state-of-the-art performance.

### Gate 4 — Reproduction and differentiation audit
Compare the exact candidate project against the original paper, official baseline, and relevant public implementation(s). Decide among (a) faithful reproduction, (b) reproduction plus one tested, worthwhile improvement, (c) conditional redesign within the same domain, or (d) reject candidate. Do not invent novelty.

### Gate 5 — Final go/no-go decision
Combine the evidence. Approval requires accessible/licensed data, successful pipeline, defensible evaluation, manageable compute, interview explainability, and an honest project narrative. Any critical unresolved defect blocks approval.

## Current status
- Candidate discovery: completed as desk research.
- Gate 1: not yet run.
- Gates 2–5: not started.
- Final project selection: pending.
