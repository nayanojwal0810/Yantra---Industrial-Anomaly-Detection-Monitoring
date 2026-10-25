# Feasibility, Modeling Suitability, and Evaluation Protocol

This report defines the modeling suitability, evaluation protocols, anti-leakage safeguards, and end-to-end system engineering feasibility for Candidate B (LBNL / OpenEI Simulated FCU Dataset, [Submission 5763](https://data.openei.org/submissions/5763), DOI: [10.25984/1881324](https://doi.org/10.25984/1881324)), incorporating the empirical findings from the feasibility and novelty gate.

---

## 1. Modeling Suitability and Comparative Architectures

### 1.1 Structural Suitability for Deep Learning vs. Classical ML
A recurring error in industrial time-series projects is forcing deep neural networks onto tabular sensor snapshots where tree ensembles or simple threshold rules dominate. To justify deep learning, the data must contain **temporal dynamics, multi-sensor phase lags, and sequential feedback loops** that static point-in-time classifiers cannot capture.

- **Why Candidate B (LBNL FCU) Justifies Sequential Modeling:**
  - An HVAC Fan Coil Unit is a closed-loop thermodynamic control system governed by delayed thermal inertia (air thermal capacitance, chilled water transport delay, and PI/PID controller response times).
  - A leaking valve or fouling coil does not immediately create an obvious static temperature threshold violation; the control loop attempts to compensate (e.g., increasing fan speed or opening opposing heating/cooling valves) until physical limits are reached.
  - Sequential architectures (such as 1D Temporal Convolutional Networks or Bidirectional LSTMs) can model the **dynamic lag between actuator commands and thermal responses**, capturing phase-shift anomalies that point-in-time classifiers miss.
- **Why Classical ML and Rule Baselines are Mandatory:**
  - In commercial building automation systems, interpretability, computational efficiency, and deterministic failure modes are paramount.
  - A rigorous project must benchmark DL against strong classical baselines. If a simpler model achieves comparable performance with 100x lower latency and zero GPU requirements, that is an essential operational finding, not a project failure.

---

### 1.2 Model Family Selection

#### 1. Baseline Physics Heuristics
- **Thermodynamic Residual Rules (ASHRAE Guideline 36 & APAR Logic):**
  - Rather than treating ASHRAE Guideline 36 as an off-the-shelf classifier, specific physical invariant rules are mapped directly to the FCU telemetry points:
    - *Simultaneous Heating and Cooling:* If `FCU_CVLV_DM > 0.05` and `FCU_HVLV_DM > 0.05` for $>15$ continuous minutes, flag valve contention / control instability.
    - *Closed-Valve Temperature Delta Invariant:* When cooling valve is commanded shut (`FCU_CVLV_DM == 0.0`), discharge air temperature must not drop significantly below mixed air temperature ($\Delta T = FCU\_MAT - FCU\_DAT > 2.0^\circ\text{F}$). A violation indicates cooling coil valve leakage.
    - *Airside Heat Transfer Invariant:* Coil fouling increases airside pressure drop and reduces heat transfer rate per unit airflow ($Q = \dot{m} C_p \Delta T$).

#### 2. Classical Machine Learning Families
- **Family 1: Semi-Supervised Reconstruction & Density Estimators (Isolation Forest & One-Class SVM with RBF Kernel)**
  - *Rationale:* Trained strictly on normal baseline operation (`FCU_FaultFree.csv`). Detects anomalies as out-of-distribution density outliers in high-dimensional sensor space without requiring labeled fault data.
- **Family 2: Supervised Gradient Boosted Trees (LightGBM / XGBoost)**
  - *Rationale:* Benchmark for severity classification. Employs lag windows (e.g., $t-15\text{m}, t-30\text{m}, t-60\text{m}$) and rolling statistics (mean, variance, min, max) on thermodynamic domain features.

#### 3. Deep Learning Families
- **Family 1: Temporal Convolutional Network (TCN) Autoencoder**
  - *Architecture:* Dilated causal 1D convolutions with residual blocks.
  - *Hypothesis:* Captures multi-sensor temporal dependencies across 60–120 minute sliding windows with stable gradient propagation and parallel training.
- **Family 2: Recurrent Encoder-Decoder (Bi-LSTM / GRU Autoencoder)**
  - *Architecture:* Multi-layer LSTM reconstructing 26-channel sensor sequences.
  - *Hypothesis:* Generates channel-wise reconstruction error vectors ($\mathbf{e}_t = |\mathbf{x}_t - \mathbf{\hat{x}}_t|$) that provide localized root-cause diagnostic attribution.

---

## 2. Evaluation Protocol and Anti-Leakage Safeguards

### 2.1 The Correct Evaluation Unit
In industrial time-series, **rows are not independent samples**. Randomly splitting rows ($80/20$ train/test) on continuous time-series data is an elementary methodological error that guarantees data leakage due to high auto-correlation between adjacent timestamps ($t$ and $t+1$).

- **Evaluation Units for Candidate B:**
  1. **Controlled Seasonal Stress Regimes:** Winter (heating-dominated), Summer (cooling-dominated), Spring/Fall (transitional/economizer).
  2. **Fault Severity Scenarios:** Minor (nascent, 20% leak, minor fouling), Moderate (50%), Severe (80%).
  3. **Distinct Scenario Files:** 49 separate annual simulation runs.

---
### 2.2 Leakage-Safe Evaluation Split Strategy

#### Corrected Protocol: Contiguous Split with Window Embargo
```
┌────────────────────────────────────────────────────────────────────────┐
│ Full Fault-Free Normal Baseline (FCU_FaultFree.csv, 1 Year)            │
├─────────────────────────┬──────────────────────┬───────────────────────┤
│ Normal Training Block   │ Normal Calibration   │ Untouched Normal Test │
│ First 60% of Year       │ Next 15% of Year     │ Remaining 25% of Year │
│ (5,256 1-Hour Windows)  │ (1,314 1-Hour Windows│ (2,190 1-Hour Windows)│
│ Jan 1 to Aug 7          │ Aug 8 to Oct 1       │ Oct 2 to Dec 31       │
│ Model parameter fitting │ Threshold derivation │ False Alarm Rate (FAR)│
│ strictly normal only    │ (99.5th percentile)  │ strictly untouched    │
└─────────────────────────┴──────────────────────┴───────────────────────┘
  [Embargo: 60-min buffer between splits to prevent window overlap leakage]

                                     │
          Evaluated Across Matching Counterfactual Test Period (Oct 2 to Dec 31)
                                     ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Scenario Test Evaluation (2,190 Windows per Fault Scenario):           │
│ - FCU_VLVLeak_Cooling_20.csv (20% Cooling Valve Leakage)               │
│ - FCU_Fouling_Cooling_Airside_Minor.csv (Minor Airside Coil Fouling)   │
│ - FCU_FilterRestriction_10%.csv (10% Airflow / Filter Restriction)     │
│ - FCU_SensorBias_RMTemp_+2C.csv (Room Temperature Sensor Bias +2°C)    │
│ - FCU_OADMPRLeak_20.csv (Outdoor Air Damper Leakage 20%)               │
└────────────────────────────────────────────────────────────────────────┘
```
- **Validation Objective:** Tests whether a model fitted strictly on normal training data and calibrated on held-out normal calibration data can flag distinct mechanical degradations while controlling false alarms on untouched normal test data.
- **Calibrated Real-World Boundary:** Evaluated as a controlled paired-simulation test under identical Des Moines, IA TMY3 weather and timestamps. It does **not** prove generalizability to unmodeled field buildings, other climate zones, or multi-year physical sensor drift.

---

### 2.3 Explicit Safeguards Against Shortcuts and Artifacts
1. **Scenario Identifier Leakage:**
   - Raw scenario files contain fault names in their filenames (e.g., `FCU_VLVLeak_Cooling_20.csv`).
   - *Safeguard:* Ingestion pipelines must strip all metadata and file origins. Data frames are merged into an anonymous continuous stream with only physical telemetry and separate ground-truth scenario labels.
2. **Timestamp Memorization:**
   - Datasets with continuous timestamps allow trees to split on specific dates.
   - *Safeguard:* Absolute calendar timestamps are transformed into cyclical relative features (hour-of-day sine/cosine) or omitted from model inputs entirely.
3. **Constant Sensor Channels:**
   - Empirical inspection confirmed that `FAN_CTRL`, `FCU_CLG_EWT`, and `FCU_HTG_EWT` are 100% constant across all files.
   - *Safeguard:* Ingestion schema automatically drops zero-variance columns.

---

### 2.4 Metrics Aligned with Industrial Decision-Making
The evaluation protocol reports:

1. **False Alarm Rate (FAR) on Untouched Normal Test Windows:**
   $$\text{FAR} = \frac{\text{False Positive Windows}}{\text{Total Untouched Normal Test Windows}} \times 100\%$$
   Also expressed as alarms per 1,000 operational hours ($\text{FAR} \times 10$).
   - Measured FAR in Gate 02 Pilot:
     - Physical Rules: 1.05%–1.37% (10.5–13.7 alarms / 1,000h)
     - Classical ML (Isolation Forest): 3.06%–3.20% (30.6–32.0 alarms / 1,000h)
     - Temporal DL Probe (1D-CNN AE): 0.09%–0.55% (0.9–5.5 alarms / 1,000h)
2. **Scenario Detection Rate (%):**
   - Percentage of 1-hour test windows flagged as anomalous during the active fault regime.
3. **Macro-Average Detection Rate (%):**
   - Unweighted average detection rate across all evaluated fault scenario mechanisms.
4. **Sensor-Level Anomaly Attribution:**
   - Channel-wise reconstruction error ranking or rule trigger mapping identifying which sensor channel or physical relationship deviates most strongly from baseline expectation.

*(Note: Time-to-Detect has been removed because the simulated scenario files represent full-year continuous faults without verified physical onset timestamps).*

---


## 3. Product and System Engineering Feasibility

The project is structured to demonstrate rigorous software engineering, data engineering, and proportionate MLOps without relying on expensive cloud subscriptions.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        DATA PIPELINE ARCHITECTURE                      │
├─────────────────┬────────────────────┬─────────────────────────────────┤
│ Ingestion Layer │ Preprocessing      │ Storage & Feature Store         │
│ Selective Range │ Pandera Validation │ Parquet Cache (15-min downsample│
│ Requests on Zip │ Resampling (15m)   │ 124 MB across 49 files          │
└────────┬────────┴─────────┬──────────┴────────────────┬────────────────┘
         │                  │                           │
         ▼                  ▼                           ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        MODELING & EVALUATION CORE                      │
├─────────────────┬────────────────────┬─────────────────────────────────┤
│ Baselines       │ Classical ML       │ Deep Learning Sequences         │
│ Thermodynamic   │ Isolation Forest   │ 1D-CNN Autoencoder              │
│ Residual Rules  │ One-Class SVM      │ Bi-LSTM Autoencoder             │
└────────┬────────┴─────────┬──────────┴────────────────┬────────────────┘
         │                  │                           │
         ▼                  ▼                           ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        OPERATOR & DEPLOYMENT LAYER                     │
├─────────────────┬────────────────────┬─────────────────────────────────┤
│ FastAPI Service │ Diagnostic Alert   │ Testing & CI/CD                 │
│ /api/v1/diagnose│ JSON with physical │ Pytest (unit & integration)     │
│ telemetry stream│ attribution vector │ GitHub Actions automated checks │
└─────────────────┴────────────────────┴─────────────────────────────────┘
```

### 3.1 Data Pipeline and Ingestion
- **Selective Range Ingestion:** Python script streaming ZIP Central Directory and individual scenario CSVs via HTTP range requests without downloading the 506 MB archive.
- **Data Validation Layer (Pandera):** Strict schema enforcement checking physical bounds on all 26 active channels (e.g. temperatures between $30^\circ\text{F}$ and $130^\circ\text{F}$, valve commands $\in [0.0, 1.0]$, flow rates $\ge 0.0$).
- **Measured Downsampling Pipeline:** Aggregation from 1-minute to 15-minute intervals reducing 25.75M rows to a compact 1.72M-row Parquet store (~124 MB across all 49 files, ~8 MB per file).

### 3.2 Experimentation and Tracking
- **Configuration Management:** All hyperparameters, feature sets, and split definitions stored in YAML configs (`configs/fcu_baseline.yaml`, `configs/fcu_deep_learning.yaml`).
- **Reproducible Pipeline:** Deterministic seeds across Python, NumPy, PyTorch, and scikit-learn.
- **Local Experiment Tracking:** Structured JSON/SQLite experiment logs recording loss curves, ROC/PR curves, confusion matrices, and inference latency.

### 3.3 Inference API and Operator Diagnostic Interface
- **FastAPI Telemetry Service:**
  - Endpoint `/api/v1/diagnose` accepting 15-minute sliding windows of 26 sensor points.
  - Returns structured diagnostic JSON:
    ```json
    {
      "timestamp": "2026-10-26T12:00:00Z",
      "anomaly_score": 0.84,
      "alarm_state": "ALARM",
      "fault_category": "Cooling Valve Leaking",
      "confidence": 0.91,
      "severity": "Minor (20% leakage)",
      "top_contributing_sensors": ["FCU_CLG_GPM", "FCU_DAT", "FCU_CLG_RWT"]
    }
    ```

### 3.4 Testing and CI/CD Quality Gates
- **Unit Tests (`tests/unit/`):**
  - Schema validation rules and out-of-bounds rejection.
  - Correct windowing and rolling-feature transformations.
  - Physics consistency checks (verifying temperature drop across cooling coil).
- **Integration Tests (`tests/integration/`):**
  - End-to-end data ingestion, downsampling, model inference, and output formatting.
  - Verification that the API returns responses in $<50\text{ms}$ on CPU.
