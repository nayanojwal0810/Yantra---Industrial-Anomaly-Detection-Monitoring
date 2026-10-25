# Technical Decision Log

This file records decisions after they are explicitly approved. Entries marked **Provisional** are not final.

| ID | Topic | Current position | Status | Evidence / next action |
|---|---|---|---|---|
| ID | Topic | Current position | Status | Evidence / next action |
|---|---|---|---|---|
| D-001 | Project problem | Industrial process health monitoring and fault alerting using recorded fluid-mixing sensor data | Approved | Evaluated at whole-run level; fault-onset/delay unsupported |
| D-002 | Source dataset | `MalteRamonat/fluid-mixing-anomaly-benchmark`, commit `07b9565c794da01b46ec76c442f416d509d6b73b` | Approved | Real physical ModVA testbench recordings approved; simulation data excluded |
| D-003 | Learning scope | Classical ML only; deep learning excluded | Approved | Keep CPU-friendly end product |
| D-004 | Model comparison | Statistical baseline plus four candidates: Isolation Forest, One-Class SVM, LOF novelty mode, PCA reconstruction error | Provisional | Confirm data/split feasibility; evaluate candidates in Checkpoint 4 |
| D-005 | Evaluation unit | Split strictly by complete CSV run; zero row-wise leakage; calibrate threshold on normal validation data | Approved | Run manifest created with 20 train, 8 val, 26 test |
| D-006 | Application | FastAPI inference API + Streamlit dashboard for recorded runs | Provisional | Build only after model evaluation is credible |
| D-007 | MLOps | MLflow experiment tracking, automated tests, CI, pinned environment, Docker local packaging and model provenance | Provisional | Implement proportionately in Checkpoint 7 |
| D-008 | Compute | CPU is the required deployment baseline; Colab is optional for experiments | Approved | Verified Isolation Forest CPU execution in 5.02s |
| D-009 | Results claims | Report only metrics actually measured on documented splits | Approved guardrail | Applies throughout project |
| D-010 | Data in Git | Do not commit raw data; keep data/raw/ ignored; exclude manufacturer datasheets | Approved guardrail | CC BY 4.0 attribution documented in docs/DATA_CONTRACT.md |
| D-011 | Project scope & label limits | Whole-run process health screening; no claims of onset detection or time-to-detect | Approved | Labels are block-annotated across 100% of rows per fault run |
| D-012 | Source data selection | Real physical process recordings in `ModVA_Datasets/`; OpenModelica simulation outputs excluded | Approved | Verified physical testbench noise and characteristics |
| D-013 | Schema standardization | Exclude `dataset_0_normal_behaviour.csv` (42 cols); retain 54 runs at 50 cols; no imputation | Approved | 54 included runs share identical schema without imputation |
| D-014 | Evaluation scope | Broad multi-fault evaluation across all 8 abnormal categories; 1-2 run categories marked exploratory | Approved | Evaluates generalizability beyond paper's clogging/leakage focus |
| D-015 | Fixed run manifest | Split 54 included runs: 20 train (normal), 8 val (5 normal + 3 fault), 26 test (7 normal + 19 fault) | Approved | Seed 42 for normal runs; uses scenario and binary_label with observed_anomaly_codes |
| D-016 | Threshold calibration safeguard | Thresholds calibrated strictly on normal validation data; zero test-label access | Approved | Prevents upstream Youden's J test leakage |
| D-017 | Validation fault runs role | Validation fault runs (15, 10, 12) used for model/config selection only, never thresholding | Approved | Strict boundary between threshold budget and model tuning |
| D-018 | Licensing and third-party boundary | CC BY 4.0 attribution maintained; vendor datasheets in upstream `documents/` excluded from repo | Approved | Clean IP boundary established in docs/DATA_CONTRACT.md |

## Decision Detail Records

### D-011 to D-018 (Approved 2026-10-25 by ChatGPT)
- **Scope:** Yantra evaluates process health at the whole-run level. Onset delay metrics are excluded due to block labeling.
- **Schema:** Run 0 dropped due to missing PI channels; remaining 54 runs form the standardized 50-column pool.
- **Split Sizes:** Fixed 20 normal train, 8 validation (5 normal + 3 fault), 26 test (7 normal + 19 fault). Manifest is source of truth.
- **Manifest Semantics:** `scenario` is recorded from filename; `binary_label` is 0 (normal) and 1 (non-normal); raw observed codes are stored in `observed_anomaly_codes` without inferring scenario from code order.
- **Safeguards:** Thresholds set strictly on normal validation quantile/budget. Pre-scaled upstream files and test labels prohibited during training/tuning.
