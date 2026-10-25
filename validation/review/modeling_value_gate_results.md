# Modeling Value and Reproducibility Gate Results

**Evaluation Date:** 2026-10-26<br>
**Auditor:** Implementation Worker<br>
**Decision Authority:** Technical Decision-Maker (ChatGPT)<br>
**Review Target:** Candidate B — LBNL / OpenEI Simulated Fan Coil Unit (FCU) Fault Detection and Diagnostics Dataset ([Submission 5763](https://data.openei.org/submissions/5763), [DOI 10.25984/1881324](https://doi.org/10.25984/1881324))<br>
**Official Dataset Reference:** Granderson et al., *Scientific Data* 10, article 342 (2023), DOI: [10.1038/s41597-023-02197-w](https://doi.org/10.1038/s41597-023-02197-w).

---

## 1. Executive Summary & Provisional Recommendation

### Core Empirical Findings:
1. **Full Reproducibility Achieved (Part A):**
   - Developed and committed four self-contained, reproducible scripts under [`validation/scripts/`](file:///d:/Yantra/validation/scripts/): `extract_fcu_subset.py`, `audit_fcu_subset.py`, `resample_fcu_subset.py`, and `run_pilot_experiment.py`.
   - Committed small, machine-readable JSON summaries under [`validation/review/evidence/`](file:///d:/Yantra/validation/review/evidence/): `audit_summary.json`, `aggregation_summary.json`, and `pilot_evaluation_summary.json`.
   - All scratch scripts were refactored into CLI-driven, repository-native workflows without user-specific paths or raw data commits.
2. **Methodological Corrections Applied (Part B):**
   - Replaced numeric `max` aggregation for discrete operating mode `FCU_CTRL` (0=shutdown, 1=operate, 2=setback) with fast vectorized categorical majority mode, transition indicators, and operating duration shares.
   - Evaluated peak and distribution attenuation across 1-min, 5-min, and 15-min sampling rates (e.g., peak discharge air temperature attenuates by 21.2% at 5-min and 22.1% at 15-min).
   - Completely removed Time-to-Detect (TTD) from metrics because the 48 simulated scenarios run continuously for an entire year without labeled fault onsets.
   - Enforced a contiguous 60% Train / 15% Calibration / 25% Untouched Test split on the fault-free baseline with a 60-minute boundary embargo, deriving anomaly thresholds strictly from normal calibration data at the 99.5th percentile.
3. **Modeling-Value Pilot Outcome (Part C):**
   - Conducted an empirical evaluation across 6 scenarios (1 baseline normal + 5 distinct low-severity physical fault mechanisms) comparing Domain Physical Rules, Classical Unsupervised ML (Isolation Forest), and a Temporal DL Probe (1D-CNN Autoencoder) across 1-min, 5-min, and 15-min rates.
   - **Physical Rules:** Achieved 100.0% detection on cooling valve leakage, 35.6% on coil fouling, and 35.3% on filter restriction, with a False Alarm Rate (FAR) of 1.05%–1.37% and compute latency of ~0.07s.
   - **Classical ML (Isolation Forest):** Macro-average detection rate of only 2.98%–3.48% (at or below its 3.1% false alarm rate), failing to distinguish low-severity industrial faults from normal operational weather/seasonal swings.
   - **Temporal DL Probe (1D-CNN Autoencoder):** Achieved 97.4%–100.0% detection on cooling valve leakage, but failed completely on the other 4 fault mechanisms (0.09%–0.64% detection rate), resulting in a macro-average detection of 19.6%–20.4%.
   - **Crucial Modeling Insight:** Temporal DL succeeded *only* on the valve leak scenario—which is the exact scenario that a 2-line physical rule already solves trivially at 100% with 0.08s of compute. On multi-channel subtle degradations, physical rules outperformed DL (34.5% vs. 20.4% macro-average).

### Final Recommendation:
**Keep FCU as an Engineering Benchmark only, or Reject it if the portfolio requires a DL-centered novelty contribution.**
- **If the project requires deep learning to provide measurable, non-trivial advantage over domain rules:** **REJECT FCU.** Deep learning does not justify its computational complexity over thermodynamic physics rules on this dataset.
- **If the project scope is calibrated as an Industrial MLOps Telemetry & Hybrid Benchmark:** Keep FCU strictly as an engineering system demonstrating end-to-end telemetry ingestion, hybrid physics-rule and statistical residual monitoring, reproducible evaluation pipelines, and telemetry-loss resilience.

---

## 2. Reproducibility & Committed Code (Part A)

All claims are supported by committed scripts and machine-readable evidence:

| Script / Artifact | Description | CLI Execution Command |
| :--- | :--- | :--- |
| [`validation/scripts/extract_fcu_subset.py`](file:///d:/Yantra/validation/scripts/extract_fcu_subset.py) | Selective HTTP 206 Range extraction of ZIP central directory and individual CSV members. | `python validation/scripts/extract_fcu_subset.py --files FCU_FaultFree.csv,FCU_VLVLeak_Cooling_20.csv --out-dir tmp/fcu_data` |
| [`validation/scripts/audit_fcu_subset.py`](file:///d:/Yantra/validation/scripts/audit_fcu_subset.py) | Audits schema, timestamps, nulls, infinities, constant sensors, and counterfactual weather sync. | `python validation/scripts/audit_fcu_subset.py --data-dir tmp/fcu_data --out-json validation/review/evidence/audit_summary.json` |
| [`validation/scripts/resample_fcu_subset.py`](file:///d:/Yantra/validation/scripts/resample_fcu_subset.py) | Semantically valid multi-rate downsampling evaluation with distribution and peak retention metrics. | `python validation/scripts/resample_fcu_subset.py --data-dir tmp/fcu_data --out-json validation/review/evidence/aggregation_summary.json` |
| [`validation/scripts/run_pilot_experiment.py`](file:///d:/Yantra/validation/scripts/run_pilot_experiment.py) | Executes the 3-model feasibility pilot across 1m, 5m, 15m rates with strict train/calib/test split. | `python validation/scripts/run_pilot_experiment.py --data-dir tmp/fcu_data --out-json validation/review/evidence/pilot_evaluation_summary.json` |
| [`validation/review/evidence/audit_summary.json`](file:///d:/Yantra/validation/review/evidence/audit_summary.json) | Committed machine-readable structural metrics across all 6 inspected CSVs. | N/A (Machine-readable evidence) |
| [`validation/review/evidence/aggregation_summary.json`](file:///d:/Yantra/validation/review/evidence/aggregation_summary.json) | Committed machine-readable multi-rate distribution, peak retention, and memory metrics. | N/A (Machine-readable evidence) |
| [`validation/review/evidence/pilot_evaluation_summary.json`](file:///d:/Yantra/validation/review/evidence/pilot_evaluation_summary.json) | Committed machine-readable pilot experiment results across all models and sampling rates. | N/A (Machine-readable evidence) |

### Evidence Status:
- **Measured & Reproduced:** Row counts (525,600/file), column counts (30), zero nulls, zero infs, constant columns (`FAN_CTRL`=1.0, `FCU_CLG_EWT`=45.0, `FCU_HTG_EWT`=120.0), downsampling peak attenuation, pilot FAR and scenario detection rates.
- **Estimated:** Total 49-file uncompressed storage (~3.93 GB uncompressed CSV, estimated ~124 MB Parquet across 49 files based on 5 audited Parquet conversions).
- **Unverified:** Performance on physical commercial buildings with unmodeled occupant behavior overrides (dataset is NIST HVACSIM+ simulation).

---

## 3. Methodological Corrections (Part B)

The following corrections have been resolved in the codebase and research documentation:

1. **Semantic Aggregation of `FCU_CTRL`:**
   - Prior report used numeric `max` on `FCU_CTRL`, which is semantically invalid for categorical states (0=shutdown, 1=operate, 2=setback).
   - Corrected in `resample_fcu_subset.py` using vectorized one-hot shares: calculates categorical majority mode via `argmax`, mode transition flag (`transition = 1` if mode switched in window), and operating duration shares (`share_shutdown`, `share_operate`, `share_setback`).
2. **Distribution & Peak Retention Analysis:**
   - Evaluated beyond full-year means. Peak discharge air temperature (`FCU_DAT`) falls from 115.22°F at 1-min to 90.79°F at 5-min (21.2% attenuation) and 89.71°F at 15-min (22.1% attenuation).
   - Cooling valve leak flow (`FCU_CLG_GPM`) maintains its 1.14 GPM lower bound and 3.19 GPM peak at 100% retention ratio across all rates.
3. **Removal of Time-to-Detect (TTD):**
   - The 48 fault scenario files represent continuous, year-long simulated faults without real physical onset timestamps.
   - TTD has been completely removed from the evaluation criteria and metrics.
4. **Contiguous Split & Window Embargo:**
   - Single annual normal trajectory partitioned into contiguous blocks:
     - **Normal Training:** First 60% of year (5,256 1-hour windows, Jan 1 to Aug 7).
     - **Normal Calibration:** Next 15% of year (1,314 1-hour windows, Aug 8 to Oct 1).
     - **Untouched Normal Test:** Final 25% of year (2,190 1-hour windows, Oct 2 to Dec 31).
   - A 60-minute embargo is enforced between blocks. Thresholds are derived strictly from normal calibration windows at the 99.5th percentile score. False alarm rates are reported strictly on untouched normal test windows.
5. **Controlled Paired-Simulation Scope:**
   - Scenarios share identical outdoor weather trajectories (`FCU_OAT`, `FCU_OA_HUMD`, max delta = 0.0000) and timestamps.
   - Evaluated strictly as a controlled counterfactual simulation, not independent field validation.
6. **Scenario Unit Clarification:**
   - Documented that the 48 fault files represent severity-specific simulated runs on one FCU design, not 48 independent real-world facilities.
7. **Sensor-Level Attribution:**
   - Re-scoped "root-cause diagnosis" to "sensor-level anomaly attribution" based on observable channel residuals.
8. **Unsupported Claims Removed:**
   - Removed unsourced operational limits ("5 alarms per week"), unsourced financial cost figures, and unmeasured training runtimes. Corrected primary paper citation to Granderson et al. (2023) across all documents.

---

## 4. Modeling-Value Feasibility Pilot Results (Part C)

### Scenarios Evaluated:
1. `FCU_FaultFree.csv`: Normal baseline
2. `FCU_VLVLeak_Cooling_20.csv`: Valve leak (20% cooling valve leakage)
3. `FCU_Fouling_Cooling_Airside_Minor.csv`: Heat transfer degradation (minor airside coil fouling)
4. `FCU_FilterRestriction_10%.csv`: Airflow resistance (10% filter restriction)
5. `FCU_SensorBias_RMTemp_+2C.csv`: Sensor calibration drift (+2°C room temperature offset)
6. `FCU_OADMPRLeak_20.csv`: Damper leakage (20% outdoor air damper leak)

### Quantitative Performance Matrix:

| Sampling Rate | Metric / Scenario | Physical Domain Rules | Classical ML (Isolation Forest) | Temporal DL Probe (1D-CNN AE) |
| :--- | :--- | :---: | :---: | :---: |
| **15-Minute** | **False Alarm Rate (Untouched Test)** | **1.37%** (13.7 / 1,000h) | **3.06%** (30.6 / 1,000h) | **0.55%** (5.5 / 1,000h) |
| | Valve Leak (Cooling 20%) | **100.00%** | 3.79% | **100.00%** |
| | Coil Fouling (Airside Minor) | **35.57%** | 2.88% | 0.55% |
| | Filter Restriction (10%) | **35.30%** | 3.06% | 0.64% |
| | Sensor Bias (Room Temp +2C) | 1.00% | 2.33% | 0.18% |
| | Damper Leak (OA 20%) | 0.37% | 2.83% | 0.64% |
| | **Macro-Average Detection Rate** | **34.45%** | **2.98%** | **20.40%** |
| | Compute Latency (Fit + Eval) | **0.087 s** | 0.252 s | 6.301 s |
| **5-Minute** | **False Alarm Rate (Untouched Test)** | **1.23%** (12.3 / 1,000h) | **3.20%** (32.0 / 1,000h) | **0.09%** (0.9 / 1,000h) |
| | Valve Leak (Cooling 20%) | **100.00%** | 4.89% | **97.40%** |
| | Coil Fouling (Airside Minor) | **35.75%** | 3.15% | 0.09% |
| | Filter Restriction (10%) | **35.43%** | 3.42% | 0.09% |
| | Sensor Bias (Room Temp +2C) | 0.96% | 2.65% | 0.09% |
| | Damper Leak (OA 20%) | 0.37% | 3.29% | 0.27% |
| | **Macro-Average Detection Rate** | **34.50%** | **3.48%** | **19.59%** |
| | Compute Latency (Fit + Eval) | **0.076 s** | 0.257 s | 2.454 s |
| **1-Minute** | **False Alarm Rate (Untouched Test)** | **1.05%** (10.5 / 1,000h) | **3.11%** (31.1 / 1,000h) | **0.18%** (1.8 / 1,000h) |
| | Valve Leak (Cooling 20%) | **100.00%** | 5.80% | **100.00%** |
| | Coil Fouling (Airside Minor) | **37.99%** | 2.88% | 0.18% |
| | Filter Restriction (10%) | **37.63%** | 3.11% | 0.18% |
| | Sensor Bias (Room Temp +2C) | 0.59% | 2.19% | 0.14% |
| | Damper Leak (OA 20%) | 0.41% | 3.20% | 0.41% |
| | **Macro-Average Detection Rate** | **35.32%** | **3.44%** | **20.18%** |
| | Compute Latency (Fit + Eval) | **0.066 s** | 0.287 s | 3.243 s |

### Key Pilot Observations:
1. **Physical Rules trivially solve the cooling valve leak:**
   Whenever `FCU_CVLV < 0.01`, the cooling water flow `FCU_CLG_GPM` remains at 1.14 GPM (vs normal baseline 0.0 GPM). A simple rule triggers with 100% precision and recall without needing any neural network.
2. **Classical ML completely fails to detect low-severity faults:**
   Isolation Forest achieved only 2.98%–3.48% detection across scenarios, which is virtually indistinguishable from its normal false alarm rate (3.06%–3.20%). Normal annual weather and operational variance overwhelm the subtle multi-dimensional signals in tabular feature space.
3. **Temporal DL Autoencoder fails on subtle multi-variable faults:**
   The 1D-CNN autoencoder scored 97.4%–100% on the valve leak, but collapsed to 0.09%–0.64% detection on coil fouling, filter restriction, sensor bias, and damper leak.
   The model learns to reconstruct the dominant normal annual cycles (seasonal heating/cooling loads) and absorbs minor physical degradations into its reconstruction tolerance.
4. **Sampling Rate Invariance:**
   Downsampling from 1-min to 15-min had virtually zero impact on detection capability (Physical rules: 35.3% at 1-min vs 34.5% at 15-min; DL: 20.2% at 1-min vs 20.4% at 15-min), while reducing memory and processing overhead by 93.3%.

---

## 5. Pass/Fail Decision and Trade-off Analysis

### Assessment Against Gate Pass/Fail Criteria:
- **Reproducibility criteria:** **PASS.** All scripts committed, runnable via standard CLI, machine-readable JSON artifacts committed.
- **Signal diversity criteria:** **PASS.** Evaluated 5 distinct physical fault mechanisms.
- **Rule triviality criteria:** **FAIL.** Simple physical domain rules detect the primary fault (cooling valve leak) at 100% and outperform DL across the remaining fault families (34.5% vs 20.4% macro-average).
- **ML/DL value-add criteria:** **FAIL.** Temporal DL does not demonstrate a distinct, measurable advantage over domain physical rules on this dataset.
- **Novelty criteria:** **FAIL.** Prior art (Zhong et al. 2023, Babakhani et al. 2026) already covers seasonal domain shifts and downsampling robustness on this exact dataset.

### Provisional Recommendation:
We recommend **Rejecting the FCU dataset if the mandate is a DL-centered novelty project**, OR **Keeping FCU strictly as an Engineering / MLOps Benchmark** if the goal is an industrial monitoring telemetry system.

| Decision Path | Justification | Trade-offs & Next Steps |
| :--- | :--- | :--- |
| **Path 1: Keep FCU as an Engineering Benchmark Only** *(Conditional)* | Accept that ML/DL does not outperform physics rules. Re-scope the project as an end-to-end telemetry system comparing physics-first vs statistical vs ML detection, focusing on real-time streaming, telemetry loss, and MLOps reliability. | Requires technical decision-maker sign-off to drop claims of ML algorithmic superiority and reposition as a software engineering / MLOps portfolio showcase. |
| **Path 2: Reject FCU for DL Goals** *(Recommended if DL mandate holds)* | The data does not provide a defensible niche where DL provides unique value over simple physics rules. | Pivot to another industrial dataset (e.g., vibration-based rotating machinery or multi-sensor process telemetry) where non-linear spatio-temporal ML is strictly necessary. |

---

## 6. Artifact & File Traceability

- Scripts committed:
  - [`validation/scripts/extract_fcu_subset.py`](file:///d:/Yantra/validation/scripts/extract_fcu_subset.py)
  - [`validation/scripts/audit_fcu_subset.py`](file:///d:/Yantra/validation/scripts/audit_fcu_subset.py)
  - [`validation/scripts/resample_fcu_subset.py`](file:///d:/Yantra/validation/scripts/resample_fcu_subset.py)
  - [`validation/scripts/run_pilot_experiment.py`](file:///d:/Yantra/validation/scripts/run_pilot_experiment.py)
- Evidence committed:
  - [`validation/review/evidence/audit_summary.json`](file:///d:/Yantra/validation/review/evidence/audit_summary.json)
  - [`validation/review/evidence/aggregation_summary.json`](file:///d:/Yantra/validation/review/evidence/aggregation_summary.json)
  - [`validation/review/evidence/pilot_evaluation_summary.json`](file:///d:/Yantra/validation/review/evidence/pilot_evaluation_summary.json)
