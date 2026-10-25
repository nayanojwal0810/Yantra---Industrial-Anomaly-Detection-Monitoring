# Feasibility, Modeling Suitability, and Evaluation Protocol

This report defines the modeling suitability, evaluation protocols, anti-leakage safeguards, and end-to-end system engineering feasibility for Candidate B (LBNL / OpenEI FDD Benchmark, Fan Coil Unit), contrasting it against Candidates A (WDSEventDB) and C (HazardNet).

---

## 1. Modeling Suitability and Comparative Architectures

### 1.1 Structural Suitability for Deep Learning vs. Classical ML
A common trap in industrial time-series projects is forcing deep neural networks onto tabular snapshots where tree ensembles or threshold rules dominate. To justify deep learning, the data must contain **temporal dynamics, multi-sensor phase lags, and sequential feedback loops** that static point-in-time classifiers cannot capture.

- **Why Candidate B (LBNL FCU) Justifies Deep Learning:**
  - An HVAC Fan Coil Unit is a closed-loop thermodynamic control system governed by delayed thermal inertia (air thermal capacitance, chilled water transport delay, and PI/PID controller response times).
  - A stuck valve or leaking damper does not immediately cause a drastic temperature error; rather, the control loop attempts to compensate (e.g., increasing fan speed or adjusting the opposing heating/cooling coil) until compensation limits are reached.
  - Sequential deep architectures (such as 1D Temporal Convolutional Networks or Bidirectional LSTMs) can model the **dynamic lag between actuator commands and thermal responses**, capturing subtle phase-shift anomalies that point-in-time classifiers miss.
- **Why Classical ML Comparisons are Mandatory:**
  - In commercial building automation systems, interpretability, computational efficiency, and deterministic failure modes are paramount.
  - A rigorous project must benchmark DL against strong classical baselines. If a simpler model achieves comparable performance with 100x lower latency and zero GPU requirements, that is an essential operational finding, not a project failure.

---

### 1.2 Model Family Selection

#### 1. Baseline Rules & Physics Heuristics
- **ASHRAE Guideline 36 & APAR Logic:**
  - Operational rules based on first principles:
    - *Simultaneous Heating and Cooling Check:* If `FCU_CVLV_DM > 0.05` and `FCU_HVLV_DM > 0.05` for $>15$ continuous minutes, flag valve contention / control instability.
    - *Temperature Delta Invariant:* When cooling valve is open (`FCU_CVLV > 0.20`), discharge air temperature must be lower than mixed air temperature (`FCU_DAT < FCU_MAT - 2.0°F`). A violation flags cooling coil failure or valve stuck shut.
    - *Sensor Consistency:* Outdoor air damper position must correlate with outdoor air flow fraction ($OAF = \frac{MAT - RAT}{OAT - RAT}$). Deviations flag temperature sensor bias or stuck dampers.

#### 2. Classical Machine Learning Families
- **Family 1: Gradient Boosted Decision Trees (LightGBM / XGBoost)**
  - *Rationale:* Standard tabular champion on physical sensor features. Highly robust to non-linear sensor relationships and scale differences.
  - *Feature Engineering:* Explicit lag windows (e.g., $t-15\text{m}, t-30\text{m}, t-60\text{m}$), rolling statistics (mean, variance, min, max), and thermodynamic domain features ($\Delta T = FCU\_MAT - FCU\_DAT$, water enthalpy delta $Q = \dot{m} C_p \Delta T_{water}$).
- **Family 2: Semi-Supervised Reconstruction / Density Estimators (Isolation Forest & One-Class SVM with RBF Kernel)**
  - *Rationale:* Trained strictly on normal baseline operation (`Fault_free.csv`). Detects anomalies as out-of-distribution density outliers in high-dimensional sensor space.
- **Family 3: Linear State-Space / Mahalanobis Distance on Physics Residuals**
  - *Rationale:* Establishes a transparent linear benchmark computing the covariance distance of sensor residuals relative to nominal operating regimes.

#### 3. Deep Learning Families
- **Family 1: Temporal Convolutional Network (TCN) / 1D-CNN Autoencoder**
  - *Architecture:* Dilated causal 1D convolutions with residual blocks.
  - *Hypothesis:* Captures long-range multi-sensor temporal dependencies across 60–120 minute sliding windows with stable gradient propagation and faster parallel training than recurrent networks.
- **Family 2: Recurrent Encoder-Decoder (Bi-LSTM / GRU Autoencoder)**
  - *Architecture:* Multi-layer LSTM reconstructing 29-channel sensor sequences.
  - *Hypothesis:* Models temporal sequences and outputs reconstruction error vectors ($\mathbf{e}_t = |\mathbf{x}_t - \mathbf{\hat{x}}_t|$). High residual errors localized to specific channels (e.g., discharge temp or valve position) provide direct root-cause diagnostic attribution.
- **Evidence Required to Justify DL:**
  - DL must either: (1) achieve higher precision/recall on **minor nascent faults** (e.g. 20% leaks, minor fouling) where static trees fail, or (2) demonstrate superior **cross-season generalization** when trained on Spring/Fall and tested on Summer/Winter.

#### 4. The Fallback Position: What if Classical ML Beats Deep Learning?
- If LightGBM or physics rules match or outperform DL, **the project is still a major success**.
- In an industrial engineering context, demonstrating that a well-engineered classical pipeline with domain-specific thermodynamic features outperforms a heavy deep neural network—while consuming 95% less compute and providing full explainability—is a highly defensible, senior-level engineering finding.
- The project's value will reside in the rigorous comparative benchmark, the leak-free evaluation protocol, and the production-grade data/inference pipeline.

---

## 2. Evaluation Protocol and Anti-Leakage Safeguards

### 2.1 The Correct Evaluation Unit
In industrial time-series, **rows are not independent samples**. Randomly splitting rows ($80/20$ train/test) on continuous time-series data is an elementary methodological error that guarantees data leakage due to high auto-correlation between adjacent timestamps ($t$ and $t+1$).

- **Evaluation Units for Candidate B:**
  1. **Seasons (Meteorological Regimes):** Winter (heating-dominated), Summer (cooling-dominated), Spring/Fall (transitional/economizer).
  2. **Fault Severity Levels:** Minor (nascent, 10–20%), Moderate (30–50%), Severe (80–100%).
  3. **Equipment Run Scenarios:** Distinct annual scenario files.

---

### 2.2 Leakage-Safe Split Strategies

#### Protocol 1: Cross-Season Temporal Holdout (Regime Generalization)
```
┌─────────────────────────────────────────────────────────────┐
│ Training Split (Transitional / Moderate Weather)            │
│ Months: March – May (Spring) + September – November (Fall)  │
│ 183 days of operational data across fault & normal modes    │
└──────────────────────────────┬──────────────────────────────┘
                               │
            Evaluated Zero-Shot on Unseen Extremes
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ Test Split 1: Summer Peak Cooling (June – August)           │
│ High ambient OAT, chilled water cooling at maximum capacity │
├─────────────────────────────────────────────────────────────┤
│ Test Split 2: Winter Peak Heating (December – February)     │
│ Low ambient OAT, hot water heating & freeze-protection mode │
└─────────────────────────────────────────────────────────────┘
```
- **Validation Objective:** Proves that the model has learned intrinsic thermodynamic failure mechanisms rather than memorizing outdoor weather correlations.

#### Protocol 2: Cross-Severity Incipient Fault Generalization (Zero-Shot Detection)
- **Train Set:** Fault-free data + Moderate and Severe fault scenarios (e.g., 50% and 80% valve leaks, severe coil fouling).
- **Test Set:** Minor / Nascent fault scenarios (e.g., 20% valve leaks, minor coil fouling, 10% filter restriction).
- **Validation Objective:** Evaluates whether models can detect incipient machine degradation early, before it escalates to severe failures.

---

### 2.3 Explicit Safeguards Against Shortcuts and Artifacts
1. **Filename / Scenario Identifier Leakage:**
   - Raw scenario files contain fault names in their filenames (e.g., `FCU_OADMPRLeak_20.csv`).
   - *Safeguard:* Ingestion pipelines must strip all metadata, file origins, and scenario tags. Data frames are merged into an anonymous continuous stream with only physical telemetry and separate ground-truth label tables.
2. **Timestamp Memorization:**
   - Datasets with continuous timestamps allow trees to split on specific dates or calendar weeks.
   - *Safeguard:* Absolute calendar timestamps (`datetime`) must be transformed into strictly cyclical relative features (hour-of-day sine/cosine, day-of-week) or omitted from model inputs entirely.
3. **Static Sensor Channels:**
   - Channels that remain constant in simulation (e.g., fan mode fixed at `1-Auto`) provide zero variance and must be automatically detected and pruned during pipeline validation.
4. **Sensor Fault Inversion / Direct Leakage:**
   - In sensor bias faults, the recorded channel is corrupted by design. Evaluating on the corrupted channel directly can allow models to detect bias trivially if the reading is non-physical. Models must evaluate physical consistency against adjacent coupled channels (e.g., comparing `RM_TEMP` against `FCU_RAT`).

---

### 2.4 Metrics Aligned with Industrial Decision-Making
Accuracy is completely meaningless on imbalanced operational anomaly data. The evaluation must report:

1. **False Alarm Rate (FAR) per 1,000 Operational Hours:**
   $$\text{FAR} = \frac{\text{False Positives}}{\text{Total Normal Operating Hours}} \times 1,000$$
   *Industrial threshold:* Facility operators ignore systems with $>5$ false alarms per week. A model with 99% accuracy but 20 false alarms a day is operationally unusable.
2. **Time-to-Detect (TTD):**
   - The elapsed operating time (in minutes or hours) from fault inception to the first sustained alarm (defined as $>3$ consecutive alarm windows to prevent transient false triggers).
3. **Area Under the Precision-Recall Curve (AUPRC):**
   - Evaluates performance across varying decision thresholds under severe class imbalance.
4. **Multiclass Diagnostic Confusion Matrix:**
   - Normal vs. Valve Leak vs. Valve Stuck vs. Damper Stuck vs. Sensor Bias vs. Fouling vs. Control Instability.

---

## 3. Product and System Engineering Feasibility

The project is structured to demonstrate rigorous software engineering, data engineering, and proportionate MLOps without relying on expensive cloud subscriptions.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        DATA PIPELINE ARCHITECTURE                      │
├─────────────────┬────────────────────┬─────────────────────────────────┤
│ Ingestion Layer │ Preprocessing      │ Storage & Feature Store         │
│ Raw CSVs        │ Pandera Validation │ Parquet Cache (15-min downsample│
│ (fdddata.lbl.gov│ Resampling (15m)   │ Fast streaming, schema-enforced │
└────────┬────────┴─────────┬──────────┴────────────────┬────────────────┘
         │                  │                           │
         ▼                  ▼                           ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        MODELING & EVALUATION CORE                      │
├─────────────────┬────────────────────┬─────────────────────────────────┤
│ Baselines       │ Classical ML       │ Deep Learning Sequences         │
│ ASHRAE-36 Rules │ LightGBM / XGBoost │ 1D-CNN / Bi-LSTM Autoencoder    │
│ APAR Heuristics │ Isolation Forest   │ Temporal ConvNet (TCN)          │
└────────┬────────┴─────────┬──────────┴────────────────┬────────────────┘
         │                  │                           │
         ▼                  ▼                           ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        OPERATOR & DEPLOYMENT LAYER                     │
├─────────────────┬────────────────────┬─────────────────────────────────┤
│ Fast API        │ Interactive CLI    │ Testing & CI/CD                 │
│ Telemetry stream│ Operator alerts    │ Pytest (unit & integration)     │
│ Diagnostic JSON │ Root-cause expl.   │ GitHub Actions automated checks │
└─────────────────┴────────────────────┴─────────────────────────────────┘
```

### 3.1 Data Pipeline and Ingestion
- **Automated Fetch Script:** Python script fetching official LBNL FCU zip archive from `fdddata.lbl.gov`, validating SHA-256 checksums, and verifying extraction integrity.
- **Data Validation Layer (Pandera / Pydantic):**
  - Strict schema enforcement checking physical bounds on all 29 channels (e.g. temperatures between $30^\circ\text{F}$ and $130^\circ\text{F}$, valve commands $\in [0.0, 1.0]$, flow rates $\ge 0.0$).
  - Automated detection of missing rows, stuck values, or out-of-order timestamps.
- **Downsampling & Feature Store:**
  - Automated aggregation from 1-minute to 15-minute intervals (mean of continuous temperatures, max of actuator commands) reducing 25M rows to a compact, lightning-fast 1.7M-row Parquet format (~85 MB).

### 3.2 Experimentation, Tracking, and Reproducibility
- **Configuration Management:** All hyperparameters, feature sets, downsampling rates, and split definitions stored in YAML configs (`configs/fcu_baseline.yaml`, `configs/fcu_deep_learning.yaml`).
- **Reproducible Pipeline:** Deterministic seeds across Python, NumPy, PyTorch, and LightGBM.
- **Lightweight Experiment Tracking:** Local MLflow tracking server or structured JSON/SQLite experiment logs recording training loss curves, ROC/PR curves, confusion matrices, and inference latency benchmarks.

### 3.3 Inference API and Operator Diagnostic Interface
- **FastAPI Telemetry Ingestion Service:**
  - Endpoint `/api/v1/diagnose` accepting 15-minute sliding windows of 29 sensor points.
  - Returns structured diagnostic JSON:
    ```json
    {
      "timestamp": "2026-10-26T12:00:00Z",
      "anomaly_score": 0.87,
      "alarm_state": "ALARM",
      "fault_category": "Cooling Valve Leaking",
      "confidence": 0.92,
      "severity": "Minor (20% leakage)",
      "estimated_energy_penalty_kw": 2.4,
      "top_contributing_sensors": ["FCU_DAT", "FCU_CLG_RWT", "FCU_CVLV"]
    }
    ```
- **Operator Workflow Demonstration:**
  - Lightweight web dashboard (Streamlit or Vanilla JS/HTML) or interactive terminal dashboard displaying live sensor trends, alarm status, and root-cause feature attributions.

### 3.4 Testing and CI/CD Quality Gates
- **Unit Tests (`tests/unit/`):**
  - Schema validation rules and out-of-bounds rejection.
  - Correct windowing and rolling-feature transformations.
  - Physics consistency checks (verifying temperature drop across cooling coil).
- **Integration Tests (`tests/integration/`):**
  - End-to-end data ingestion, downsampling, model inference, and output formatting.
  - Verification that the API returns responses in $<50\text{ms}$ on CPU.
- **CI Workflow (`.github/workflows/ci.yml`):**
  - Automated linting (`ruff` / `flake8`), formatting, and test execution (`pytest`) on every commit and pull request.

---

## 4. Feasibility Summary Across Candidates

| Dimension | Candidate A: WDSEventDB | Candidate B: LBNL / OpenEI FDD | Candidate C: HazardNet |
| :--- | :--- | :--- | :--- |
| **DL Justification** | Infeasible (overfits to 8 runs) | Strong (closed-loop thermal dynamics) | Moderate (spatiotemporal 3,312 nodes) |
| **Classical ML Baseline** | Simple threshold matches ML | Rich comparison (LightGBM vs. ASHRAE) | SVM baselines exist in literature |
| **Split Feasibility** | Broken (only 1 cyber run) | Clean (Cross-season & cross-severity) | Unclear (batch job noise dominates) |
| **Shortcut Risks** | Severe (negative sensor codes) | Manageable (controlled by seasonal split)| Severe (predicting self-thresholds) |
| **Local Compute (CPU)** | <1 minute | 2–5 minutes (downsampled Parquet) | Infeasible (>16 GB RAM & heavy GPU) |
| **Software Eng. Scope** | Minimal (small 1MB table) | Comprehensive (FastAPI, Pandera, CI) | Blocked by missing code modules |
| **Defensibility** | Low (toy testbed scale) | High (DOE / Nature landmark benchmark) | Low (unreproducible benchmark) |
