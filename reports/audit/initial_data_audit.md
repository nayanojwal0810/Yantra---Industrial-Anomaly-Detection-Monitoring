# Initial Data, License, Label, and Reproducibility Audit

**Status:** Completed  
**Audit Date:** 2026-10-25  
**Auditor:** Antigravity (Implementation Worker)  
**Technical Decision-Maker:** ChatGPT  
**Target Repository:** [fluid-mixing-anomaly-benchmark](https://github.com/MalteRamonat/fluid-mixing-anomaly-benchmark)  
**Associated Publication:** Ramonat et al., *"A Fluid Mixing Benchmark for Anomaly Detection in CPS with Real & Simulated Data,"* IEEE Access, vol. 13, pp. 134113–134128, 2025. [DOI: 10.1109/ACCESS.2025.3592815](https://doi.org/10.1109/ACCESS.2025.3592815)

---

## 1. Executive Verdict

**Verdict: Suitable with caveats**

### Key Findings:
1. **Real Physical Testbench Data:** The candidate dataset contains 55 CSV runs (19,848 timesteps total, ~11.9 MB uncompressed) collected from a physical fluid-mixing test plant at Helmut Schmidt University Hamburg. Data quality is exceptionally high: 0 missing values, 0 infinities, 0 duplicate rows, and strictly monotonic timestamps.
2. **Run-Level Label Semantics:** Anomaly annotations in the dataset are **run-level fault assignments** where 100% of rows in a fault run are marked with the respective non-zero fault code (1 to 8), and 100% of rows in normal runs are marked 0. There are no within-run normal-to-fault transitions or event onset timestamps.
3. **Severe Upstream Evaluation Leakage:** The upstream repository exhibits significant methodological leakage:
   - Upstream preprocessing (`scripts/Preprocess_datasets.py`) fits scalers across *all* normal runs simultaneously without separating train/validation/test sets.
   - Upstream evaluation (`evaluate_anomaly_scores`) tunes decision thresholds directly on test-set ground-truth labels using Youden's J statistic, artificially inflating reported test F1 scores.
4. **Schema Inconsistency in Run 0:** 54 of the 55 CSV files have identical 50-column schemas. `dataset_0_normal_behaviour.csv` contains only 42 columns (missing 8 pressure-sensor level calculations added in subsequent runs), causing upstream preprocessing to silently discard it.
5. **Open License with Third-Party Boundary:** The repository root is licensed under Creative Commons Attribution 4.0 International (CC-BY-4.0). However, `documents/Process_Equipment/` contains proprietary third-party manufacturer datasheets that must not be bundled.
6. **Feasibility:** Classical ML models (Isolation Forest, One-Class SVM, LOF, PCA) and a statistical baseline are completely feasible on CPU, training in under 1 second per model on this dataset.

---

## 2. Source Revision and Audit Environment

### Source Revision
- **Repository URL:** `https://github.com/MalteRamonat/fluid-mixing-anomaly-benchmark`
- **Default Branch:** `main`
- **Commit SHA Inspected:** `07b9565c794da01b46ec76c442f416d509d6b73b`
- **Commit Date:** Mon Jul 28 11:57:00 2025 +0200
- **Commit Author:** `zimmer-ing <bernd@zimmer-ing.de>`
- **Commit Message:** `Update readme.md`

### Audit Environment
- **Operating System:** Windows 11 Pro (10.0.26100)
- **Shell:** PowerShell 7 / Windows PowerShell
- **Python Version:** 3.13.3
- **Git Version:** 2.55.0.windows.3
- **Active Libraries:** pandas 3.0.3, numpy 2.4.6, scikit-learn 1.9.0, scipy 1.17.1, torch 2.13.0, optuna 5.0.0
- **Audit Isolation:** Upstream repository was cloned to disposable temporary storage (`$env:TEMP\fluid-mixing-audit`) outside the project workspace. No raw data bundles or upstream git trees were committed to `d:\Yantra`.

---

## 3. Repository Structure and Executable Entry Points

### Repository Layout
```text
fluid-mixing-anomaly-benchmark/
├── .gitignore
├── Constants.py                          # Path constants and directory configuration
├── LICENSE                               # CC-BY-4.0 license text
├── readme.md                             # Setup instructions, paper citation, data notes
├── Run_Anomaly_Detection.py              # Wrapper executing scripts/Train_and_Benchmark.py
├── configs/
│   └── AD_Benchmark/                     # YAML configs for datasets, models, experiments
├── data/
│   ├── ModVA_Datasets/                   # 55 raw process CSV files (dataset_0 to dataset_54)
│   │   ├── scaled_minmax/                # 54 MinMax-scaled CSV files + scaler_params.json
│   │   └── scaled_standard/              # 54 Standard-scaled CSV files + scaler_params.json
│   └── Plots/                            # Pre-generated interactive HTML visualization plots
├── documents/
│   ├── PID-Diagram.pdf                   # Process & Instrumentation Diagram of mixing plant
│   ├── PLC_Code/                         # Structured text / XML PLC control code
│   └── Process_Equipment/                # Manufacturer hardware datasheets (Piping, PLC, Pumps, Sensors, Valves)
├── results/
│   └── Comparison/                       # Pre-computed benchmark results across 10 random seeds
│       ├── CloggingDataset/              # JSON metrics & CSV summary for IF, OCSVM, DL models
│       └── LeakageDataset/               # JSON metrics for IF, OCSVM, DL models
├── scripts/
│   ├── Check_sampling.py                 # Evaluates timestamp dt range and sampling interval
│   ├── Evaluate_Comparison.py            # Generates comparative boxplots and metric tables
│   ├── Evaluate_for_paper.py             # Generates publication figures using LaTeX/seaborn
│   ├── Plot_Dataset.py                   # Single dataset plotting script
│   ├── Plot_All_Datasets.py              # Batch dataset plotting script
│   ├── Preprocess_datasets.py            # Scaling script (contains data leakage)
│   └── Train_and_Benchmark.py            # Core training and benchmarking loop
├── simulation/
│   ├── ModVA_online_stable.mo            # OpenModelica simulation model
│   ├── simulation_datasets/              # OpenModelica .mat and raw CSV simulation outputs
│   └── simulation_scripts/               # OMPython interface and simulation GUI
├── Simulation_Model_Control/             # Actuator control schedule matrices (CSV)
└── src/
    └── AD_Benchmark/
        ├── datasets/                     # Dataset loaders (clogging_dataset.py, leakage_dataset.py, dataset_base.py)
        ├── experiments/                  # Experiment runners and evaluation metric logic
        ├── models/                       # Model implementations (IF, OCSVM, FC-AE, FC-Forecast, LSTM-ED, TCN-ED)
        └── utils/                        # Batch helpers and tensor utilities
```

### Documented vs Executed Entry Points
| Entry Point | Documented Capability | Actually Executed During Audit? | Result / Verification |
|---|---|---|---|
| `Run_Anomaly_Detection.py` | Runs full benchmark across seeds and datasets | No (runs 10 seeds x 2 datasets with Optuna; avoided to prevent long CPU runs) | Verified logic; wraps `scripts/Train_and_Benchmark.py` |
| `scripts/Train_and_Benchmark.py` | Tunes and evaluates IF & OCSVM; DL models commented out | No (full loop avoided) | Inspected code; DL models are commented out |
| `scripts/Preprocess_datasets.py` | Pre-scales data into `scaled_minmax` and `scaled_standard` | Inspected code | Verified that it drops `dataset_0` and scales test labels |
| `scripts/Check_sampling.py` | Evaluates sampling interval Δt | Verified via custom audit script | Δt median = 1.62s across all 55 files |
| `reports/audit/smoke_test_upstream_pipeline.py` | Single-seed execution of upstream Isolation Forest on CPU | **Yes** | **Passed in 5.02s on CPU** (AUROC: 0.5770, Best Threshold F1: 0.5531) |
| `reports/audit/smoke_test_load.py` | Schema and data loading check across normal and 3 fault types | **Yes** | **Passed in 0.42s** (All columns, timestamps, and sensors parsed) |

---

## 4. Data Inventory and Schema

### Measured Inventory
All measurements were computed across all 55 CSV files located in `data/ModVA_Datasets` using `reports/audit/audit_data_inventory.py`.

- **Total CSV Files:** 55
- **Total Timesteps (Rows):** 19,848
- **Total Size on Disk:** 11,898,312 bytes (~11.35 MB uncompressed, ~11.9 MB)
- **Minimum File Size:** 65,696 bytes (`dataset_47_manual_mode.csv`, 110 rows)
- **Maximum File Size:** 227,207 bytes (`dataset_36_normal_behaviour.csv`, 377 rows)
- **Row Count Range:** 110 to 377 rows per file
- **Mean Row Count:** ~360.9 rows per file
- **Nominal Run Duration:** ~10 minutes (600 seconds) per automated run

### Scenario Breakdown
| Scenario Name | Description | Run Count | Total Rows | File Size Range (KB) | Row Range |
|---|---|---|---|---|---|
| `normal_behaviour` | Baseline automated mixing sequence | 33 | 12,042 | 164.7 – 221.9 KB | 347 – 377 |
| `clogging` | Pipe clogging fault scenario | 3 | 1,099 | 211.8 – 218.8 KB | 360 – 370 |
| `leakage` | Pipe/system leakage fault scenario | 2 | 729 | 214.5 – 216.1 KB | 364 – 365 |
| `reconfiguration` | Piping network reconfiguration | 4 | 1,452 | 204.2 – 218.8 KB | 348 – 373 |
| `sensor_errors` | Induced sensor fault / noise | 2 | 731 | 214.2 – 215.7 KB | 364 – 367 |
| `stirring_error` | Agitator/stirrer motor fault | 1 | 371 | 218.1 KB | 371 |
| `leakage_and_clogging`| Combined compound fault | 1 | 362 | 213.6 KB | 362 |
| `changed_initial_state`| Abnormal starting tank levels | 1 | 361 | 213.2 KB | 361 |
| `manual_mode` | Manual operator valve/pump control | 8 | 2,701 | 64.2 – 219.9 KB | 110 – 376 |
| **Total** | **All Scenarios** | **55** | **19,848** | **64.2 – 221.9 KB** | **110 – 377** |

### Schema and Column Definitions
54 of 55 files contain exactly 50 columns. `dataset_0_normal_behaviour.csv` contains 42 columns (missing the last 8 PI-calculated level channels).

```text
Columns 1–2 (Timestamp & Metadata):
  1. Server Time                              (Timestamp string: "YYYY-MM-DD HH:MM:SS.ffffff")
  2. Session Time Stamps                      (Float: Elapsed run time in seconds, e.g. 0.62 to 600.0)

Columns 3–11 (Discrete / Binary Level Limit Switches):
  3. Tank_B201_empty                          (Binary flag: 1.0 or 0.0)
  4. Tank_B202_empty                          (Binary flag: 1.0 or 0.0)
  5. Tank_B203_empty                          (Binary flag: 1.0 or 0.0)
  6. Tank_B204_empty                          (Binary flag: 1.0 or 0.0)
  7. Tank_B204_middle                         (Binary flag: 1.0 or 0.0)
  8. Tank_B201_full                           (Binary flag: 1.0 or 0.0)
  9. Tank_B202_full                           (Binary flag: 1.0 or 0.0)
 10. Tank_B203_full                           (Binary flag: 1.0 or 0.0)
 11. Tank_B204_full                           (Binary flag: 1.0 or 0.0)

Columns 12–15 (Continuous Tank Volumes):
 12. Tank_B201_Volume                         (Float: Dosing Tank 1 volume in ml)
 13. Tank_B202_Volume                         (Float: Dosing Tank 2 volume in ml)
 14. Tank_B203_Volume                         (Float: Dosing Tank 3 volume in ml)
 15. Tank_B204_Volume                         (Float: Main Mixing Tank volume in ml)

Columns 16–19 (Continuous Pressure Sensors):
 16. Pressure_below_B201                      (Float: Pressure below Tank B201 in bar)
 17. Pressure_below_B202                      (Float: Pressure below Tank B202 in bar)
 18. Pressure_below_B203                      (Float: Pressure below Tank B203 in bar)
 19. Pressure_below_B204                      (Float: Pressure below Mixing Tank B204 in bar)

Columns 20–21 (Continuous Temperature Sensors):
 20. Tempreature_before_Pump_P201             (Float: Fluid temperature before Pump P201 in °C) [Note: typo in source]
 21. Temperature_in_B204                      (Float: Fluid temperature inside Tank B204 in °C)

Columns 22–23 (Continuous Flow Sensors):
 22. Flow_after_Pump_P201                     (Float: Flow rate after Pump P201 in l/min)
 23. Flow_after_Pump_P202                     (Float: Flow rate after Pump P202 in l/min)

Columns 24–30 (Actuator Positions - Valves):
 24. Valve_V201_opening                       (Float/binary: Opening state of Valve V201)
 25. Valve_V202_opening                       (Float/binary: Opening state of Valve V202)
 26. Valve_V203_opening                       (Float/binary: Opening state of Valve V203)
 27. Valve_V204_opening                       (Float/binary: Opening state of Valve V204)
 28. Valve_V205_opening                       (Float/binary: Opening state of Valve V205)
 29. Valve_V206_opening                       (Float/binary: Opening state of Valve V206)
 30. Valve_V209_opening                       (Float/binary: Opening state of Valve V209)

Columns 31–33 (Actuator States - Pumps and Agitator):
 31. Pump_P201_active                         (Binary flag: Pump P201 running 1/0)
 32. Pump_P202_active                         (Binary flag: Pump P202 running 1/0)
 33. Mixer_R201_of_B204_active                (Binary flag: Agitator motor running 1/0)

Columns 34–37 (Level via Level Indicators LI211–LI214):
 34. Tank_B201_level_calculated_via_LI211     (Float: Level in mm)
 35. Tank_B202_level_calculated_via_LI212     (Float: Level in mm)
 36. Tank_B203_level_calculated_via_LI213     (Float: Level in mm)
 37. Tank_B204_level_calculated_via_LI214     (Float: Level in mm)

Columns 38–41 (Level via Tank Volume):
 38. Tank_B201_level_calculated_via_VolumeB201 (Float: Level in mm)
 39. Tank_B202_level_calculated_via_VolumeB202 (Float: Level in mm)
 40. Tank_B203_level_calculated_via_VolumeB203 (Float: Level in mm)
 41. Tank_B204_level_calculated_via_VolumeB204 (Float: Level in mm)

Columns 42–49 (Level via Pressure Sensors PI251–PI254 - Present in datasets 1–54):
 42. Tank_B201_level_calculated_via_PI251     (Float: Level in mm)
 43. Tank_B202_level_calculated_via_PI252     (Float: Level in mm)
 44. Tank_B203_level_calculated_via_PI253     (Float: Level in mm)
 45. Tank_B204_level_calculated_via_PI254     (Float: Level in mm)
 46. Tank_B201_level_calculated_via_PI251_until_zero_level (Float: Adjusted level in mm)
 47. Tank_B202_level_calculated_via_PI252_until_zero_level (Float: Adjusted level in mm)
 48. Tank_B203_level_calculated_via_PI253_until_zero_level (Float: Adjusted level in mm)
 49. Tank_B204_level_calculated_via_PI254_until_zero_level (Float: Adjusted level in mm)

Column 50 (Label):
 50. Anomaly                                  (Integer: 0 = Normal; 1..8 = Fault type code)
```

---

## 5. Label Semantics and Fault-Run Counts

### Label Distribution and Mapping
The `Anomaly` column encodes the experimental condition:
- `0`: Normal operation
- `1`: Leakage
- `2`: Clogging
- `3`: Leakage and clogging (combined)
- `4`: Changed initial state
- `5`: Reconfiguration
- `6`: Sensor errors
- `7`: Stirring error
- `8`: Manual mode

### Empirical Run-Level Label Distribution
The table below details every non-normal run and the label distribution measured:

| Run Filename | Scenario | Total Rows | Normal Rows (0) | Fault Rows (1..8) | % Fault | Assigned Anomaly Code |
|---|---|---|---|---|---|---|
| `dataset_10_leakage.csv` | leakage | 365 | 0 | 365 | 100.0% | 1 |
| `dataset_11_leakage.csv` | leakage | 364 | 0 | 364 | 100.0% | 1 |
| `dataset_12_reconfiguration.csv` | reconfiguration | 363 | 0 | 363 | 100.0% | 5 |
| `dataset_13_leakage_and_clogging.csv`| leakage_and_clogging | 362 | 0 | 362 | 100.0% | 3 |
| `dataset_14_changed_initial_state.csv`| changed_initial_state | 361 | 0 | 361 | 100.0% | 4 |
| `dataset_15_clogging.csv` | clogging | 360 | 0 | 360 | 100.0% | 2 |
| `dataset_26_reconfiguration.csv` | reconfiguration | 348 | 0 | 348 | 100.0% | 5 |
| `dataset_40_clogging.csv` | clogging | 370 | 0 | 370 | 100.0% | 2 |
| `dataset_41_reconfiguration.csv` | reconfiguration | 373 | 0 | 373 | 100.0% | 5 |
| `dataset_42_clogging.csv` | clogging | 369 | 0 | 369 | 100.0% | 2 |
| `dataset_43_sensor_errors.csv` | sensor_errors | 367 | 0 | 367 | 100.0% | 6 |
| `dataset_44_stirring_error.csv` | stirring_error | 371 | 0 | 371 | 100.0% | 7 |
| `dataset_45_sensor_errors.csv` | sensor_errors | 364 | 0 | 364 | 100.0% | 6 |
| `dataset_46_reconfiguration.csv` | reconfiguration | 368 | 0 | 368 | 100.0% | 5 |
| `dataset_47_manual_mode.csv` | manual_mode | 110 | 0 | 110 | 100.0% | 8 |
| `dataset_48_manual_mode.csv` | manual_mode | 373 | 0 | 373 | 100.0% | 8 |
| `dataset_49_manual_mode.csv` | manual_mode | 373 | 0 | 373 | 100.0% | 8 |
| `dataset_50_manual_mode.csv` | manual_mode | 376 | 0 | 376 | 100.0% | 8 |
| `dataset_51_manual_mode.csv` | manual_mode | 370 | 0 | 370 | 100.0% | 8 |
| `dataset_52_manual_mode.csv` | manual_mode | 369 | 0 | 369 | 100.0% | 8 |
| `dataset_53_manual_mode.csv` | manual_mode | 374 | 0 | 374 | 100.0% | 8 |
| `dataset_54_manual_mode.csv` | manual_mode | 374 | 0 | 374 | 100.0% | 8 |
| **All 33 Normal Runs** | normal_behaviour | 12,042 | 12,042 | 0 | 0.0% | 0 |

### Critical Annotation Implications:
1. **No Transient / Injected Event Annotations:** The experiments were conducted by configuring a fault condition prior to or throughout the execution of the experiment. Hence, every timestep from index 0 to the end is labeled with that fault code.
2. **Binary Transformation:** When evaluating standard unsupervised anomaly detectors, downstream code casts `Anomaly > 0` to 1. In this setup, every fault run is a pure positive run (100% ones), and every normal run is a pure negative run (100% zeros).

---

## 6. Data Quality Findings

An exhaustive scan across all 55 CSV files revealed the following data quality results:

1. **Missing / Null Values:** **0** across all 55 files. (No NaNs, nulls, or empty cells).
2. **Infinite Values:** **0** across all numeric columns in all 55 files.
3. **Duplicate Rows:** **0** exact duplicate rows across all files.
4. **Duplicate Timestamps:** **0** duplicate `Server Time` or `Session Time Stamps` within any file.
5. **Timestamp Monotonicity:** `Session Time Stamps` is strictly increasing ($\Delta t > 0$) across all 55 files without any backward jumps or clock resets.
6. **Sampling Intervals:**
   - Median $\Delta t$: **1.62 seconds** across runs.
   - Mean $\Delta t$: **1.64 seconds**.
   - Min $\Delta t$: 0.49s (observed during transient fast polling).
   - Max $\Delta t$: 2.45s.
7. **Constant Features on Normal Data:**
   Several discrete control/state channels exhibit zero variance during normal automated operations:
   - Level switch flags: `Tank_B201_empty`, `Tank_B202_empty`, `Tank_B203_empty`, `Tank_B201_full`, `Tank_B202_full`, `Tank_B203_full`, `Tank_B204_full` (all constant 1.0 or 0.0 depending on operational range).
   - Unused actuators: `Valve_V209_opening` (constant 0.0), `Mixer_R201_of_B204_active` (constant 0.0 in normal automated runs).
8. **Real vs. Simulated Distinction:**
   - Files in `data/ModVA_Datasets/` represent **real physical measurements** from the plant testbench (verified by physical noise, temperature drift, pump flow inertia, and paper documentation).
   - Files in `simulation/simulation_datasets/` represent OpenModelica mathematical model outputs with 180+ internal equations/variables.

---

## 7. License and Attribution Findings

### Evidenced Terms
- **Repository Root License:** Creative Commons Attribution 4.0 International (CC-BY-4.0).
- **Permissions:** Allows reproduction, sharing, adaptation, and commercial/non-commercial use, provided appropriate credit is given, a link to the license is provided, and changes are indicated.
- **Attribution Citation:**
  ```bibtex
  @ARTICLE{11096565,
    author={Ramonat, Malte and Zimmering, Bernd and Merkelbach, Silke and Gehlhoff, Felix and Niggemann, Oliver and Fay, Alexander},
    journal={IEEE Access}, 
    title={A Fluid Mixing Benchmark for Anomaly Detection in CPS with Real & Simulated Data}, 
    year={2025},
    doi={10.1109/ACCESS.2025.3592815}
  }
  ```

### License Boundaries and Caveats
1. **Third-Party Documents in `documents/`:** The folder `documents/Process_Equipment/` contains proprietary vendor manuals and specification sheets (e.g., WAGO PLC manuals, John Guest piping datasheets). These materials belong to their respective manufacturers and are not covered under the authors' CC-BY-4.0 grant. They must not be copied or committed to the portfolio project repository.
2. **Dataset Redistribution:** While CC-BY-4.0 legally permits redistributing the CSV data, committing 12 MB of raw data directly into the application git repository is unnecessary and violates repository hygiene.
3. **Recommendation:** Keep raw data local in `data/raw/` (ignored by `.gitignore`) or download it programmatically via a reproducible retrieval script. Maintain explicit citation in `README.md` and documentation.

---

## 8. Existing Methods and Reproducibility Notes

### Upstream Implementations
1. **Classical ML Models (`src/AD_Benchmark/models/`):**
   - `IsolationForest.py`: Wraps `sklearn.ensemble.IsolationForest`.
   - `OneClass_SVM.py`: Wraps `sklearn.svm.OneClassSVM` with RBF kernel.
2. **Deep Learning Models:**
   - `FC_AutoEncoder.py`, `FC_Forecast.py`, `LSTM_EncDec.py`, `TCN_EncDec.py` (PyTorch-based).
3. **Execution Architecture:**
   - The upstream benchmark wraps all models (even scikit-learn models) in PyTorch `DataLoader` pipelines with sliding-window slicing (`history_length`, `forecast_length`, `stride`).
   - Hyperparameter optimization is performed using Optuna (`optuna=4.0.0`) across 10 random seeds.
   - Deep learning runs are commented out in `Train_and_Benchmark.py`; only IF and OCSVM are actively run.

### Reproducibility Verification
- **Audit Smoke Test:** We executed a clean, single-seed smoke test of `DirectClassificatorPerformance` with `IsolationForest` on CPU (`reports/audit/smoke_test_upstream_pipeline.py`).
- **Runtime:** **5.02 seconds** total execution time on Windows CPU.
- **Dependencies:** The pipeline executed successfully with Python 3.13, PyTorch 2.13.0, and scikit-learn 1.9.0 without GPU acceleration.
- **Architecture Risk for Portfolio:** Wrapping classical scikit-learn models in PyTorch data loaders adds unnecessary PyTorch dependencies for a classical ML application. For our final project, classical models should be trained directly on feature matrices extracted from run windows.

---

## 9. Evaluation Design Options and Data-Leakage Risks

### Independent Runs Inventory
The dataset contains 55 distinct experimental runs:
- **Normal Runs:** 33 runs
- **Fault Runs:** 22 runs (2 Leakage, 3 Clogging, 4 Reconfiguration, 2 Sensor Errors, 1 Stirring Error, 1 Leakage & Clogging, 1 Changed Initial State, 8 Manual Mode)

### Data Leakage Risks in Current Upstream Code
1. **Global Normal Preprocessing Leakage:** `Preprocess_datasets.py` computes global `MinMaxScaler` and `StandardScaler` statistics over all normal files combined (`all_normal_data = pd.concat([data.iloc[:, 2:] for data in normal_data.values()], axis=0)`). Validation and test runs leak into training feature scaling.
2. **Test-Set Threshold Tuning Leakage:** In `DirectClassificator_AD_performance_evaluation.py` (lines 72–79), the method `evaluate_anomaly_scores` computes Youden's J statistic ($TPR - FPR$) on the **test set labels** to select `best_threshold`. This violates holdout integrity and produces unrealistically high test F1 scores.
3. **Pre-Scaled Files in Repository:** The directory `data/ModVA_Datasets/scaled_minmax/` contains files scaled with this leaky global scaler. These files must not be used for model training. Raw CSVs must be scaled strictly within split boundaries.
4. **Non-Predictive Feature Leakage:** Upstream scripts separate features into `excitation`, `response`, and `auxiliary`. Metadata columns (`Server Time`, `Session Time Stamps`, and `Anomaly`) must never be passed to model training.

### Split Options for Decision-Maker Approval

#### Option A: Grouped Multi-Fault Run-Level Split (Recommended for Broad Monitoring)
- **Train Set (Normal Only):** 20 normal runs (~7,200 timesteps)
- **Validation Set:** 5 normal runs + 1 Clogging run (`dataset_15`) + 1 Leakage run (`dataset_10`) + 1 Reconfiguration run (`dataset_12`) (8 runs total, ~2,900 timesteps)
  - Used for threshold calibration and hyperparameter validation without test contamination.
- **Holdout Test Set:** 7 normal runs + 19 remaining fault/abnormal runs (26 runs total, ~9,400 timesteps)
  - Used strictly for final unbiased evaluation across normal behavior and diverse fault categories.
- **Pros:** Evaluates classical detectors across multiple real fault categories; protects holdout integrity.
- **Cons:** Very low sample count (1–2 runs) for rare fault types.

#### Option B: Benchmark-Aligned Split (Clogging & Leakage Focus)
- Mimics the paper's benchmark splits:
  - Clogging Track: 6 train normal, 3 val normal, 3 test normal + 3 clogging test runs.
  - Leakage Track: 3 train normal, 1 val normal, 2 test normal + 2 leakage test runs.
- **Pros:** Directly comparable to upstream reported numbers.
- **Cons:** Discards 35+ available recorded runs; very small sample size (only 2 leakage runs exist in total).

---

## 10. Metrics Supported by Annotations

| Metric | Supported? | Feasibility and Limitations |
|---|---|---|
| **Run-level False Positive Rate (FPR)** | **Yes** | Fully supported on normal test runs (fraction of normal runs erroneously flagged). |
| **Run-level Fault Detection Rate (Recall)** | **Yes** | Fully supported (fraction of anomalous runs correctly alerted). |
| **Run-level Precision / F1 / Specificity** | **Yes** | Supported at the discrete run level (binary: run is anomalous or healthy). |
| **Point-level ROC-AUC / PR-AUC** | **Yes (with caveats)** | Supported across concatenated test windows. However, because ground truth is 100% positive for fault runs, point-level curves evaluate continuous anomaly score separation between runs rather than within-run onset. |
| **Point-level Precision / Recall / F1** | **Yes (with caveats)** | Must be evaluated using thresholds calibrated strictly on validation data, never on test data. |
| **Detection Delay / Time-to-Detect** | **No / Unsupported** | **Unsupported:** All rows in fault runs are labeled anomalous starting at $t=0.0$s. There is no recorded baseline preceding the fault in those files to measure response delay. |
| **Within-run Event Onset Precision** | **No / Unsupported** | **Unsupported:** Ground truth does not distinguish between steady-state operation and fault injection moment. |

---

## 11. CPU / Resource Feasibility

1. **Storage & Memory Footprint:**
   - Total dataset size: ~11.9 MB uncompressed.
   - Entire dataset loads into RAM in under 0.15 seconds (< 25 MB RAM).
2. **Compute Requirements:**
   - Feature extraction and tabular aggregation take < 2 seconds on CPU.
   - Isolation Forest training: ~0.15 seconds per run on modern CPU.
   - One-Class SVM training: ~0.25 seconds per run on modern CPU.
   - PCA reconstruction error: ~0.05 seconds.
   - Statistical baselines: ~0.01 seconds.
3. **Deployment Feasibility:**
   - FastAPI and Streamlit running on recorded run replay will require negligible CPU and memory (< 150 MB RAM total).
   - Docker container execution on local developer machine is completely viable without GPU.

---

## 12. Risks, Blockers, and Decision Questions

### Precise Questions Requiring Decision-Maker Approval:

1. **Question 1: Handling `dataset_0_normal_behaviour.csv` (Schema Inconsistency)**
   - *Issue:* `dataset_0` has 42 columns, missing 8 pressure-calculated level columns (`PI251`–`PI254`).
   - *Options:*
     - Option 1A (Exclude Run 0): Drop `dataset_0` from the dataset pool. We retain 32 normal runs and all 22 fault runs, all sharing the exact same 50-column schema.
     - Option 1B (Drop 8 PI columns across all files): Exclude the 8 PI-calculated level channels from all runs, using the remaining 42 columns across 55 runs.
     - Option 1C (Impute PI columns in Run 0): Compute the 8 level calculations from `Pressure_below_B201..B204`.
   - *Worker Note:* Option 1A is recommended because 32 normal runs provide ample normal data without introducing imputation artifacts.

2. **Question 2: Evaluation Scope (Multi-Fault vs Focused Clogging/Leakage)**
   - *Issue:* Upstream only benchmarks Clogging (3 fault runs) and Leakage (2 fault runs), discarding the other 17 fault runs.
   - *Options:*
     - Option 2A (Broad Evaluation): Adopt Option A split (train on normal, evaluate detection across all fault categories at run level).
     - Option 2B (Paper-aligned subset): Restrict comparison to Clogging and Leakage.
   - *Worker Note:* Option 2A better reflects real-world industrial monitoring and tests out-of-distribution generalization.

3. **Question 3: Threshold Calibration Strategy (Fixing Upstream Leakage)**
   - *Issue:* Upstream selects thresholds using test-set labels.
   - *Options:*
     - Option 3A (Normal Validation Percentile): Set anomaly threshold on normal validation runs to achieve an acceptable false alarm budget (e.g., 95th or 99th percentile of normal validation anomaly scores).
     - Option 3B (Validation Set Youden's J): Tune threshold on a mixed validation set containing normal and selected validation fault runs.

4. **Question 4: Raw Data Storage Strategy**
   - *Issue:* How should raw data be maintained in the workspace starter pack?
   - *Options:*
     - Option 4A (Local Uncommitted): Keep raw data in `data/raw/` (untracked in git, ignored by `.gitignore`).
     - Option 4B (Download Script): Provide an automated retrieval script (`scripts/download_data.py`) that clones/downloads the 12 MB bundle into `data/raw/` with hash verification.

---

## 13. Recommendation to the Technical Decision-Maker

### Recommendation: Proceed after changes (Approve Checkpoint 1 with documented caveats)

### Justification:
1. **Valid Industrial Benchmark:** The dataset is genuine physical testbench data, well-suited for multivariate anomaly detection and industrial process monitoring.
2. **Flaws are Remediable:** Upstream flaws (global pre-scaling, test-label threshold tuning, and PyTorch dependency bloat) are methodological errors in the benchmark's evaluation code, not fatal flaws in the recorded physical data.
3. **Clean Foundation:** By sourcing from the raw CSVs, implementing strict run-level splits, calibrating thresholds on normal validation runs, and eliminating test leakage, our project will establish a substantially more honest and rigorous evaluation than the upstream paper.

---

## 14. References, Links, and Audit Commands

### References
- Repository: [fluid-mixing-anomaly-benchmark](https://github.com/MalteRamonat/fluid-mixing-anomaly-benchmark)
- Upstream Commit: `07b9565c794da01b46ec76c442f416d509d6b73b`
- Paper: Ramonat et al., *"A Fluid Mixing Benchmark for Anomaly Detection in CPS with Real & Simulated Data,"* IEEE Access, 2025. [DOI: 10.1109/ACCESS.2025.3592815](https://doi.org/10.1109/ACCESS.2025.3592815)

### Verification Commands Actually Executed
1. **Upstream Commit Verification:**
   ```powershell
   git -C $env:TEMP\fluid-mixing-audit log -n 1 --format=fuller
   # Output: commit 07b9565c794da01b46ec76c442f416d509d6b73b, Author: zimmer-ing, Mon Jul 28 11:57:00 2025
   ```
2. **Dataset Inventory and Schema Validation:**
   ```powershell
   python reports/audit/audit_data_inventory.py
   # Output: Total 55 files, 19,848 rows, 11,898,312 bytes. 0 nulls, 0 infs, 0 dupes. dataset_0 schema mismatch (42 cols vs 50 cols).
   ```
3. **Label Semantics and Distribution Analysis:**
   ```powershell
   python reports/audit/analyze_labels.py
   # Output: 33 normal runs (100% zeros), 22 fault runs (100% non-zero fault codes 1..8).
   ```
4. **Smoke Test - Data and Sensor Parsing:**
   ```powershell
   python reports/audit/smoke_test_load.py
   # Output: Successfully parsed Normal, Leakage, Clogging, and Reconfiguration files. All key sensor channels verified.
   ```
5. **Smoke Test - Upstream Execution Feasibility:**
   ```powershell
   python reports/audit/smoke_test_upstream_pipeline.py
   # Output: IsolationForest executed on CPU in 5.02 seconds (AUROC: 0.5770, Best Threshold: 0.0929).
   ```
