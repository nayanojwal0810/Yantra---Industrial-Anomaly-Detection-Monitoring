# Related Work, Novelty, and Problem Framing Audit

This report audits the academic literature, industrial state-of-the-art, stakeholder economics, and viable problem framings for:
1. **Candidate A:** Water Distribution System Event Diagnosis (WDSEventDB)
2. **Candidate B:** Commercial HVAC Fault Detection and Diagnostics (LBNL / OpenEI Simulated FCU Dataset)
3. **Candidate C:** High-Performance Computing Datacenter Thermal Hazard Prediction (HazardNet)

---

## 1. Candidate A: Water Distribution Network Event Diagnosis

### 1.1 Stakeholder, Operational Decisions, and Economic Costs
- **Primary Stakeholder:** Municipal water utility operations engineer and SCADA monitoring operator.
- **Operational Decision:** Distinguishing whether an abrupt hydraulic deviation is caused by a physical pipe burst, an instrumentation failure, or a malicious cyber-attack.
- **Economic & Operational Costs:** Missed pipe bursts cause millions of gallons of water loss and street damage ($50,000–$500,000 per major event). Misdiagnosing sensor drift as a pipe burst wastes physical repair crew overtime.

### 1.2 Academic Literature and SOTA Implementations
1. **Raza, N., Iwakin, O., Villacres, D., Putri, S. A., & Moazeni, F. (2025/2026).** *WDSEventDB: A real-time benchmark dataset for event diagnosis in water distribution networks.* World Environmental & Water Resources Congress (EWRI 2026).
2. **Taormina, R., et al. (2018).** *Battle of the Attack Detection Algorithms for Water Networks (BATADAL).* Journal of Water Resources Planning and Management, 144(8), 04018048. DOI: [10.1061/(ASCE)WR.1943-5452.0000969](https://doi.org/10.1061/(ASCE)WR.1943-5452.0000969).
3. **Inoue, J., et al. (2017).** *Anomaly Detection for a Water Treatment System Using Unsupervised Machine Learning.* IEEE ICDMW, pp. 1058–1065. (WADI / SWaT Testbeds by iTrust).
4. **Moazeni, F., & Khazaei, J. (2020).** *Cyber-Physical Security of Water Distribution Networks: A Survey.* Water Research, 185, 116240.
5. **Ferrante, M., et al. (2022).** *Leak detection in water distribution networks: A review of hydraulic and machine learning approaches.* Mechanical Systems and Signal Processing, 172, 108967.

### 1.3 Audit Verdict on Candidate A
- **Verdict: Disqualified.** The dataset has only 8 independent fault episodes (1 cyberattack run, 3 leak runs, 4 sensor fault runs). Any cross-run evaluation of cyberattacks is impossible, and deep learning sequence models will simply memorize the static testbed background state.

---

## 2. Candidate B: Commercial HVAC Fault Detection and Diagnostics

### 2.1 Stakeholder, Operational Decisions, and Economic Costs
- **Primary Stakeholder:** Commercial building automation system (BAS) facility managers, HVAC service contractors, and Energy Service Companies (ESCOs).
- **Operational Decision:** Identifying mechanical degradation (leaking cooling/heating valves, stuck dampers, coil fouling, sensor bias) early before occupant comfort is compromised or major energy waste occurs.
- **Economic & Operational Costs:**
  - HVAC systems account for ~40% of commercial building energy consumption in the US (~$150B annually).
  - Unrepaired operational faults (e.g. leaking cooling valves causing simultaneous heating and cooling) increase annual energy use by **15% to 30%** (DOE / LBNL estimates).
  - Alarm fatigue: Operators routinely disable FDD tools if false positive rates exceed 5 alarms per week.

### 2.2 Academic Literature and Current Prior Art (6 Sources)
1. **Granderson, J., Lin, G., Chen, Y., Casillas, A., Im, P., Jung, S., Benne, K., Ling, J., Gorthala, R., Wen, J., Chen, Z., Huang, S., & Vrabie, D. (2023).** *A labeled dataset for building HVAC systems operating in faulted and fault-free states.* Nature Scientific Data, 10(1), article 342. DOI: [10.1038/s41597-023-02197-w](https://doi.org/10.1038/s41597-023-02197-w). (PMC10235024).
   - *Key Findings:* National laboratory benchmark covering 7 HVAC subsystems, 1-minute continuous operational time series for full annual cycles, 48+ fault intensities, and Brick Schema v1.2 models.
2. **Zhong, F., Calautit, J. K., & Wu, Y. (2023).** *Fault data seasonal imbalance and insufficiency impacts on data-driven heating, ventilation and air-conditioning fault detection and diagnosis performances for energy-efficient building operations.* Energy, 282, 128180. DOI: [10.1016/j.energy.2023.128180](https://doi.org/10.1016/j.energy.2023.128180).
   - *Key Findings:* Directly investigates the impact of seasonal data insufficiency on supervised HVAC classifiers. Demonstrates that models trained on single-season data suffer drastic diagnostic accuracy drops when tested on unseen seasons due to weather regime shifts.
3. **Babakhani, P., Völkerling, D., Tawackolian, K., Neubauer, A., Fuerst, Y., & Kriegel, M. (2026).** *Explainable Robustness Assessment of Data-Driven HVAC Fault Detection under Noise, Drift, Bias, Missingness, and Downsampling.* SSRN Preprint 7438633. Available at: [SSRN 7438633](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7438633).
   - *Key Findings:* Evaluates classical ML (SVM, RF, XGBoost) and deep learning (LSTM, CNN-LSTM) on LBNL DataFDD and real AHU datasets under simulated downsampling, noise, drift, and missingness. (Treat as preprint, not peer-reviewed proof).
4. **Granderson, J., Singla, R., Mayhorn, E., Ehrlich, P., Vrabie, D., & Frank, S. (2020).** *Building fault detection and diagnostics: achieved performance, and national-scale energy savings.* Energy and Buildings, 221, 110022. DOI: [10.1016/j.enbuild.2020.110022](https://doi.org/10.1016/j.enbuild.2020.110022).
   - *Key Findings:* Large-scale field study showing 9% median whole-building energy savings with automated FDD, but identifying false alarm fatigue as the primary industry barrier.
5. **Chen, Z., Wen, J., & Granderson, J. (2023).** *Cross-building domain adaptation for HVAC fault detection and diagnosis based on contrastive learning and semantic graphs.* Building and Environment, 238, 110368.
   - *Key Findings:* Evaluates deep contrastive networks and Brick Schema graphs for cross-building transfer.
6. **Lin, G., Kramer, H., & Granderson, J. (2020).** *Assessment of fully automated HVAC fault detection and diagnostic tools in commercial buildings.* Energy and Buildings, 218, 109995. DOI: [10.1016/j.enbuild.2020.109995](https://doi.org/10.1016/j.enbuild.2020.109995).
   - *Key Findings:* Commercial rule-based systems struggle with low-severity faults (<20% valve leaks and coil fouling) and transient load shifts.

### 2.3 Critical Novelty Reassessment: Correcting Overstated Claims
- **Seasonal Generalization is Not an Open Void:** Zhong et al. (2023) has already analyzed seasonal imbalance and unseen-season performance drops. A held-out seasonal split on this dataset is simply a **controlled within-year seasonal stress test**, not a broad claim of generalizable multi-climate deployment transfer.
- **Downsampling is Actively Studied:** Babakhani et al. (2026) already benchmarks downsampled LBNL data.
- **Separating Detection from Diagnosis:** A normal-only baseline model detects anomalies; it cannot provide root-cause fault diagnosis without secondary attribution rules. Training on moderate/severe faults and testing on minor faults measures severity transfer, not zero-shot unseen fault discovery.
- **Calibrated Project Positioning:** This project should **not** claim novel theoretical ML discovery. Its defensible value lies in being a **rigorous industrial MLOps system and comparative engineering benchmark** testing physics-residual heuristics against classical ML and deep sequence models under strict anti-leakage constraints.

---

## 3. Candidate C: HPC Thermal Hazard Prediction (HazardNet)

### 3.1 Literature and SOTA
1. **Ardebili, M. S., Acquaviva, A., Benini, L., & Bartolini, A. (2024).** *HazardNet: A thermal hazard prediction framework for datacenters.* Future Generation Computer Systems, 155, 340–353. DOI: [10.1016/j.future.2024.01.031](https://doi.org/10.1016/j.future.2024.01.031).
2. **Bartolini, A., et al. (2018).** *ExaMon: A Scalable Telemetry and Monitoring Framework for Exascale Supercomputers.* IEEE Transactions on Parallel and Distributed Systems.
3. **Evans, R., & Gao, J. (2016).** *DeepMind AI Reduces Google Data Centre Cooling Bill by 40%.* DeepMind Research Blog.

### 3.2 Audit Verdict on Candidate C
- **Verdict: Disqualified.** The Zenodo dataset lacks target labels, and the author's GitHub repository is missing the core data-generation and modeling code (`HazardNet_DataGen.py`, `HazardNet_Models.py` return HTTP 404).

---

## 4. Comparison of Three Viable Problem Definitions for Candidate B

To ensure the final project is grounded in verified data and distinct from prior work, we evaluate three viable task formulations:

### Problem Definition 1 (Recommended): Semi-Supervised Anomaly Scoring with Physics-Residual Diagnostic Attribution
- **Operational Decision:** Facility manager needs to know if an air unit is degrading and which subsystem (cooling coil, heating coil, damper, sensor) requires physical inspection, without having labeled historical fault data.
- **Task Structure:**
  - *Stage 1 (Detection):* An unsupervised temporal model trained 100% on normal baseline data (`FCU_FaultFree.csv`) outputs a continuous anomaly score $S_t \in [0, 1]$.
  - *Stage 2 (Diagnostic Attribution):* Channel-wise physical residuals ($\Delta T$, $\Delta GPM$, actuator command-response deviations) localize the failure to the cooling coil, heating coil, or damper.
- **Data & Resolution:** 15-minute downsampled Parquet (124 MB across 49 files).
- **Independent Evaluation Unit:** 48 unseen fault scenario files across 17 fault types and 4 seasons.
- **Primary Metrics:** False Alarm Rate (FAR) per 1,000 normal hours; Time-to-Detect (TTD) on nascent fault onset; Area Under Precision-Recall Curve (AUPRC).
- **Realistic Baselines:**
  1. *Physics Rules:* Thermodynamic enthalpy and temperature delta rules.
  2. *Classical ML:* Isolation Forest and One-Class SVM on nominal sensor features.
- **Differentiation:** Refuses the unrealistic assumption that building operators have labeled fault datasets. Provides actionable physical attribution without black-box classification.
- **Primary Failure Mode:** If transitional weather (Spring/Fall) creates normal operational transients that trigger false alarms under nominal conditions.

---

### Problem Definition 2: Supervised Nascent Severity Generalization (Severity Transfer)
- **Operational Decision:** Maintenance contractor prioritizing repair dispatches based on early mechanical wear.
- **Task Structure:** Multiclass classification trained on Moderate/Severe scenarios (50% and 80% valve leaks, severe fouling) and evaluated zero-shot on Minor (20%) nascent scenarios.
- **Target:** Classify failure category (Valve Leak vs. Stuck Damper vs. Sensor Bias vs. Fouling).
- **Differentiation:** Evaluates whether models learn scale-invariant failure mechanisms rather than memorizing magnitude thresholds.
- **Limitation:** Requires training on at least some severity levels of known faults.

---

### Problem Definition 3: Comparative Industrial Engineering Benchmark & Telemetry Service
- **Operational Decision:** ML engineering team evaluating whether deep sequential models justify their compute overhead over classical gradient boosting in edge BMS controllers.
- **Task Structure:** Rigorous benchmarking of Physics Rules vs. LightGBM vs. 1D-CNN/TCN across 1-minute, 5-minute, and 15-minute telemetry.
- **Differentiation:** High software engineering rigor: complete FastAPI service, Pandera data contracts, Pytest test suite, and local MLflow tracking.
- **Limitation:** Positioned as an engineering system and benchmark, not an academic ML discovery.

---

## 5. Audit Summary Matrix

| Dimension | Candidate A: WDSEventDB | Candidate B: LBNL FCU (Calibrated) | Candidate C: HazardNet |
| :--- | :--- | :--- | :--- |
| **Stakeholder Specificity** | Water utility SCADA engineer | Commercial BAS facility manager & ESCO | HPC supercomputer sysadmin |
| **Available Literature** | Sparse (<5 papers on exact dataset) | Abundant (>50 papers, ASHRAE, Nature) | Published (FGCS 2024), but code unreleased |
| **Prior Art Overlap** | High (synthetic testbed anomaly detection) | High (Zhong 2023 seasonal paper; Babakhani 2026 preprint) | Unreproducible |
| **Viable Problem Framing** | None (sample size too small) | **Semi-Supervised Anomaly Scoring with Physics-Residual Attribution** | None (missing label generator & scripts) |
| **Differentiation Grounding** | N/A (Disqualified on data size) | MLOps rigor & physics-residual attribution | N/A (Disqualified on reproducibility) |
