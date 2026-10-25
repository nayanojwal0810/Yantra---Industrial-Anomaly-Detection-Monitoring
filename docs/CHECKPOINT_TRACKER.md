# Checkpoint Tracker

Update after each reviewed stage. Do not mark a checkpoint complete based only on an agent's assertion; inspect the artifacts and evidence.

| Checkpoint | Status | Required evidence | Reviewer notes |
|---|---|---|---|
| 0. Workspace/repository setup | Not started | Clean Git repo, starter docs committed, no secrets/raw data accidentally tracked | |
| 1. Dataset/license/reproducibility audit | Accepted with caveats | `reports/audit/initial_data_audit.md`, counts/schema/label summary, source revision, license evidence, split feasibility | Reviewed and accepted by technical decision-maker. Scope bounded to run-level evaluation; schema standardized by excluding run 0. |
| 2. Data contract and run manifest | **Current / In review** | `docs/DATA_CONTRACT.md`, `data/run_manifest.csv`, `reports/audit/validate_run_manifest.py` | Run manifest generated (20 train, 8 val, 26 test, 1 excluded); validation script passing; data contract drafted. Pending review. |
| 3. Split protocol and baseline | Blocked by CP2 | Approved split manifest, baseline metrics, leakage checks | |
| 4. Four-model comparison | Blocked by CP3 | Comparable metrics, tracked experiments, error analysis | |
| 5. Inference API | Blocked by CP4 | API tests, model reload consistency check | |
| 6. Dashboard | Blocked by CP5 | Demo on normal and fault runs; API agreement | |
| 7. MLOps and hardening | Blocked by CP6 | MLflow artifacts, CI results, clean local run and documented provenance | |
| 8. Final docs and verification | Blocked by CP7 | Clean environment verification, final limitations/results report and README | |
