# Data Contract: Fluid-Mixing Industrial Process Recordings

**Status:** Approved Specification (Checkpoint 2)  
**Target Repository:** [Yantra (Industrial Anomaly Detection & Monitoring)](https://github.com/nayanojwal0810/Yantra---Industrial-Anomaly-Detection-Monitoring.git)  
**Upstream Source Repository:** [MalteRamonat/fluid-mixing-anomaly-benchmark](https://github.com/MalteRamonat/fluid-mixing-anomaly-benchmark)  
**Audited Upstream Commit:** `07b9565c794da01b46ec76c442f416d509d6b73b` (Mon Jul 28 11:57:00 2025 +0200)  
**Publication Citation:** Ramonat et al., *"A Fluid Mixing Benchmark for Anomaly Detection in CPS with Real & Simulated Data,"* IEEE Access, vol. 13, pp. 134113–134128, 2025. [DOI: 10.1109/ACCESS.2025.3592815](https://doi.org/10.1109/ACCESS.2025.3592815)

---

## 1. Dataset Provenance and Licensing Boundaries

### 1.1 Provenance
The dataset comprises recorded time-series sensor and actuator telemetry from a physical laboratory-scale fluid-mixing plant ("ModVA" plant) operated at Helmut Schmidt University Hamburg, Germany. The plant consists of two rotational dosing pumps, four fluid reservoirs (three 3-liter dosing tanks B201, B202, B203 and one 10-liter stirred mixing tank B204), eleven controllable valves, pressure transducers, level indicators, temperature sensors, and magnetic flow meters controlled by a WAGO PLC.

The project utilizes only the **real physical process recordings** (`data/ModVA_Datasets/`), not the mathematical simulation outputs (`simulation/simulation_datasets/`).

### 1.2 License and Attribution
- **Source License:** Creative Commons Attribution 4.0 International (CC-BY-4.0).
- **Attribution Obligation:** Any distribution, presentation, or documentation deriving from this data must attribute the authors (Ramonat, Zimmering, Merkelbach, Gehlhoff, Niggemann, Fay) and cite the IEEE Access 2025 publication.
- **Third-Party Exclusions:** Upstream `documents/Process_Equipment/` contains proprietary manufacturer hardware datasheets (WAGO PLC specifications, John Guest piping manuals, etc.). These materials are owned by their respective third-party manufacturers, are outside the CC-BY-4.0 license, and **must never be committed to or redistributed by this repository**.
- **Data Storage Policy:** In compliance with Decision D-010, raw CSV files are kept locally in `data/raw/` and excluded from Git tracking via `.gitignore`. The dataset is retrieved locally or downloaded on-demand with hash verification.

---

## 2. Schema Specification (50-Column Standard)

### 2.1 Scope and Exclusions
Across the 55 audited raw CSV files:
- **Included Dataset Pool (54 files):** Runs 1 through 54 share an identical 50-column schema.
- **Excluded Run (`dataset_0_normal_behaviour.csv`):** Contains only 42 columns, lacking 8 pressure-sensor-derived level channels (`Tank_B201_level_calculated_via_PI251` through `Tank_B204_level_calculated_via_PI254_until_zero_level`). Per approved Decision D-013, `dataset_0` is excluded from the project pipeline without channel imputation.

### 2.2 Column Catalog and Data Types

| Col # | Column Name | Physical / Logical Meaning | Data Type | Permitted Values / Units | Role |
|---|---|---|---|---|---|
| 1 | `Server Time` | Wall-clock recording timestamp | String (ISO-like) | `YYYY-MM-DD HH:MM:SS.ffffff` | **Metadata (Excluded from Features)** |
| 2 | `Session Time Stamps` | Elapsed run duration | Float64 | $\ge 0.0$ seconds | **Metadata (Excluded from Features)** |
| 3 | `Tank_B201_empty` | Tank B201 empty limit switch | Float64 / Int | $\{0.0, 1.0\}$ | Plant State Flag |
| 4 | `Tank_B202_empty` | Tank B202 empty limit switch | Float64 / Int | $\{0.0, 1.0\}$ | Plant State Flag |
| 5 | `Tank_B203_empty` | Tank B203 empty limit switch | Float64 / Int | $\{0.0, 1.0\}$ | Plant State Flag |
| 6 | `Tank_B204_empty` | Tank B204 empty limit switch | Float64 / Int | $\{0.0, 1.0\}$ | Plant State Flag |
| 7 | `Tank_B204_middle` | Tank B204 mid-level switch | Float64 / Int | $\{0.0, 1.0\}$ | Plant State Flag |
| 8 | `Tank_B201_full` | Tank B201 full limit switch | Float64 / Int | $\{0.0, 1.0\}$ | Plant State Flag |
| 9 | `Tank_B202_full` | Tank B202 full limit switch | Float64 / Int | $\{0.0, 1.0\}$ | Plant State Flag |
| 10 | `Tank_B203_full` | Tank B203 full limit switch | Float64 / Int | $\{0.0, 1.0\}$ | Plant State Flag |
| 11 | `Tank_B204_full` | Tank B204 full limit switch | Float64 / Int | $\{0.0, 1.0\}$ | Plant State Flag |
| 12 | `Tank_B201_Volume` | Fluid volume in Tank B201 | Float64 | $\approx 0 - 2500$ ml | Sensor Measurement |
| 13 | `Tank_B202_Volume` | Fluid volume in Tank B202 | Float64 | $\approx 0 - 2500$ ml | Sensor Measurement |
| 14 | `Tank_B203_Volume` | Fluid volume in Tank B203 | Float64 | $\approx 0 - 2500$ ml | Sensor Measurement |
| 15 | `Tank_B204_Volume` | Fluid volume in Tank B204 | Float64 | $\approx 0 - 8000$ ml | Sensor Measurement |
| 16 | `Pressure_below_B201` | Hydrostatic pressure at B201 base | Float64 | $\approx -0.5 - 5.0$ bar | Sensor Measurement |
| 17 | `Pressure_below_B202` | Hydrostatic pressure at B202 base | Float64 | $\approx -0.5 - 5.0$ bar | Sensor Measurement |
| 18 | `Pressure_below_B203` | Hydrostatic pressure at B203 base | Float64 | $\approx -0.5 - 5.0$ bar | Sensor Measurement |
| 19 | `Pressure_below_B204` | Hydrostatic pressure at B204 base | Float64 | $\approx -0.5 - 5.0$ bar | Sensor Measurement |
| 20 | `Tempreature_before_Pump_P201` | Fluid temp before Pump P201 *(source typo)* | Float64 | $\approx 10 - 45$ °C | Sensor Measurement |
| 21 | `Temperature_in_B204` | Fluid temp inside Tank B204 | Float64 | $\approx 10 - 45$ °C | Sensor Measurement |
| 22 | `Flow_after_Pump_P201` | Discharge flow rate from Pump P201 | Float64 | $\approx -0.5 - 15.0$ l/min | Sensor Measurement |
| 23 | `Flow_after_Pump_P202` | Discharge flow rate from Pump P202 | Float64 | $\approx -0.5 - 15.0$ l/min | Sensor Measurement |
| 24 | `Valve_V201_opening` | Valve V201 commanded opening | Float64 | $\{0.0, 1.0\}$ (binary/proportional) | Actuator State |
| 25 | `Valve_V202_opening` | Valve V202 commanded opening | Float64 | $\{0.0, 1.0\}$ (binary/proportional) | Actuator State |
| 26 | `Valve_V203_opening` | Valve V203 commanded opening | Float64 | $\{0.0, 1.0\}$ (binary/proportional) | Actuator State |
| 27 | `Valve_V204_opening` | Valve V204 commanded opening | Float64 | $\{0.0, 1.0\}$ (binary/proportional) | Actuator State |
| 28 | `Valve_V205_opening` | Valve V205 commanded opening | Float64 | $\{0.0, 1.0\}$ (binary/proportional) | Actuator State |
| 29 | `Valve_V206_opening` | Valve V206 commanded opening | Float64 | $\{0.0, 1.0\}$ (binary/proportional) | Actuator State |
| 30 | `Valve_V209_opening` | Valve V209 commanded opening | Float64 | $\{0.0, 1.0\}$ (binary/proportional) | Actuator State |
| 31 | `Pump_P201_active` | Pump P201 run status | Float64 / Int | $\{0.0, 1.0\}$ | Actuator State |
| 32 | `Pump_P202_active` | Pump P202 run status | Float64 / Int | $\{0.0, 1.0\}$ | Actuator State |
| 33 | `Mixer_R201_of_B204_active` | Agitator stirrer motor status | Float64 / Int | $\{0.0, 1.0\}$ | Actuator State |
| 34 | `Tank_B201_level_calculated_via_LI211` | Level in B201 from LI211 probe | Float64 | $\ge 0.0$ mm | Calculated Derived Channel |
| 35 | `Tank_B202_level_calculated_via_LI212` | Level in B202 from LI212 probe | Float64 | $\ge 0.0$ mm | Calculated Derived Channel |
| 36 | `Tank_B203_level_calculated_via_LI213` | Level in B203 from LI213 probe | Float64 | $\ge 0.0$ mm | Calculated Derived Channel |
| 37 | `Tank_B204_level_calculated_via_LI214` | Level in B204 from LI214 probe | Float64 | $\ge 0.0$ mm | Calculated Derived Channel |
| 38 | `Tank_B201_level_calculated_via_VolumeB201` | Level in B201 from volume | Float64 | $\ge 0.0$ mm | Calculated Derived Channel |
| 39 | `Tank_B202_level_calculated_via_VolumeB202` | Level in B202 from volume | Float64 | $\ge 0.0$ mm | Calculated Derived Channel |
| 40 | `Tank_B203_level_calculated_via_VolumeB203` | Level in B203 from volume | Float64 | $\ge 0.0$ mm | Calculated Derived Channel |
| 41 | `Tank_B204_level_calculated_via_VolumeB204` | Level in B204 from volume | Float64 | $\ge 0.0$ mm | Calculated Derived Channel |
| 42 | `Tank_B201_level_calculated_via_PI251` | Level in B201 from PI251 pressure | Float64 | $\ge 0.0$ mm | Calculated Derived Channel |
| 43 | `Tank_B202_level_calculated_via_PI252` | Level in B202 from PI252 pressure | Float64 | $\ge 0.0$ mm | Calculated Derived Channel |
| 44 | `Tank_B203_level_calculated_via_PI253` | Level in B203 from PI253 pressure | Float64 | $\ge 0.0$ mm | Calculated Derived Channel |
| 45 | `Tank_B204_level_calculated_via_PI254` | Level in B204 from PI254 pressure | Float64 | $\ge 0.0$ mm | Calculated Derived Channel |
| 46 | `Tank_B201_level_calculated_via_PI251_until_zero_level` | Zero-calibrated level B201 | Float64 | $\ge 0.0$ mm | Calculated Derived Channel |
| 47 | `Tank_B202_level_calculated_via_PI252_until_zero_level` | Zero-calibrated level B202 | Float64 | $\ge 0.0$ mm | Calculated Derived Channel |
| 48 | `Tank_B203_level_calculated_via_PI253_until_zero_level` | Zero-calibrated level B203 | Float64 | $\ge 0.0$ mm | Calculated Derived Channel |
| 49 | `Tank_B204_level_calculated_via_PI254_until_zero_level` | Zero-calibrated level B204 | Float64 | $\ge 0.0$ mm | Calculated Derived Channel |
| 50 | `Anomaly` | Experimental condition code | Int64 | $\{0, 1, 2, 3, 4, 5, 6, 7, 8\}$ | **Ground-Truth Label (Excluded from Features)** |

---

## 3. Non-Predictive Features and Exclusion Rules

### 3.1 Strictly Excluded Columns
The following fields **must never be passed as feature inputs** to any preprocessing scaler, feature selector, or anomaly detection model:
1. `Server Time` (recording timestamp string).
2. `Session Time Stamps` (run elapsed time).
3. `Anomaly` (target label).
4. `filename` or `run_id` (identifiers).
5. Scenario descriptions or manifest metadata.

**Safeguard:** Any modeling pipeline must explicitly drop columns 1, 2, and 50 (and any string/ID columns) prior to feature matrix construction. Feature selection or extraction must operate exclusively on the 47 physical sensor, actuator, and derived state channels (Columns 3 through 49).

---

## 4. Label Semantics and Scope Boundaries

### 4.1 Label Map
The `Anomaly` column encodes experimental runs as follows:

| Code | Scenario Identifier | Description | Total Runs in Source | Included Runs |
|---|---|---|---|---|
| `0` | `normal_behaviour` | Healthy automated batch mixing cycle | 33 | **32** *(Run 0 excluded)* |
| `1` | `leakage` | Pipe/system leakage fault | 2 | **2** |
| `2` | `clogging` | Pipe clogging / restricted flow fault | 3 | **3** |
| `3` | `leakage_and_clogging` | Compound fault: concurrent leakage & clogging | 1 | **1** |
| `4` | `changed_initial_state`| Abnormal starting volume / tank states | 1 | **1** |
| `5` | `reconfiguration` | Altered piping valve configuration | 4 | **4** |
| `6` | `sensor_errors` | Induced measurement errors / sensor noise | 2 | **2** |
| `7` | `stirring_error` | Agitator/stirrer failure | 1 | **1** |
| `8` | `manual_mode` | Manual human operator process control | 8 | **8** |

### 4.2 Manifest Target and Observed Code Representation
- **`scenario`:** The scenario category recorded directly from the run's filename (e.g. `normal_behaviour`, `leakage`, `reconfiguration`, `clogging`, etc.). This represents the definitive experimental scenario.
- **`binary_label`:** The run-level screening target: $0$ for normal operation (`normal_behaviour`), and $1$ for non-normal operation (all other scenarios).
- **`observed_anomaly_codes`:** Explicitly records the set of observed raw integer anomaly codes from the run's data (e.g. `'0'`, `'1'`, `'5'`). A single integer `anomaly_code` is not treated as a definitive scenario label, and scenario categories are never inferred from the order of observed raw values.

### 4.3 Evaluation Scope Boundary
1. **Whole-Run Level Evaluation:** Ground truth is established at the **complete run level**. In all 22 non-normal runs, 100% of rows are marked with the respective non-zero anomaly code; in all normal runs, 100% of rows are marked 0.
2. **Unsupported Metrics:**
   - **Fault-onset timing and Detection Delay (Time-to-Detect) are strictly unsupported** because the datasets do not record normal-to-fault transitions within a single run.
   - **Point-level event onset precision is unsupported**.
   - Claims that models detect "incipient fault development in real time" are prohibited. The project evaluates whether models successfully flag an entire anomalous run as divergent from normal reference operations.
3. **Exploratory Scenarios:** Categories represented by only 1 or 2 runs (e.g. `leakage`, `stirring_error`, `changed_initial_state`, `leakage_and_clogging`, `sensor_errors`) must be explicitly presented as **exploratory evaluations**, not as generalizable estimates of real-world sensitivity.

---

## 5. Data Validation Rules

Any ingested run file must satisfy the following validation contract before processing:

1. **Schema Check:** Exactly 50 columns with identical naming, order, and casing as defined in Section 2.
2. **Completeness:** 0 null, NaN, or empty values across all rows and columns.
3. **Finiteness:** 0 infinite values (`+inf`, `-inf`) in any numeric channel.
4. **Row Uniqueness:** 0 exact duplicate rows within any file.
5. **Timestamp Monotonicity:** `Session Time Stamps` must be strictly increasing ($\Delta t = t_i - t_{i-1} > 0$).
6. **Sampling Interval Validity:** Sampling interval must fall within valid bounds ($0.1\text{s} \le \Delta t \le 5.0\text{s}$; nominal median $\approx 1.62\text{s}$).
7. **Label Uniformity:** `Anomaly` values within a single run must be constant (100% rows equal to the assigned run-level anomaly code).
8. **Binary Label Consistency:** `binary_label` must be 0 if `Anomaly == 0`, and 1 if `Anomaly > 0`.

---

## 6. Preprocessing and Zero-Variance Handling

### 6.1 Preprocessing Leakage Prevention Rule
- **No Global Scaling:** All scalers (StandardScaler, MinMaxScaler, or RobustScaler) and transformers must be **fit strictly on training data** (which contains normal runs only).
- Scaler parameters (`mean_`, `scale_`, etc.) must be persisted as part of the model/preprocessing pipeline artifact.
- Validation and test runs must only be transformed using scalers fit on the training split.

### 6.2 Constant / Zero-Variance Features Rule
- Audited data shows that several discrete channels (e.g. `Tank_B201_empty`, `Tank_B201_full`, `Valve_V209_opening`, `Mixer_R201_of_B204_active`) exhibit zero variance across normal automated runs.
- **Rule:** Feature variance must be computed **strictly on the training normal split**. Features with zero variance in the training normal split will be flagged.
- **Feature Pruning Policy:** Dropping or retaining constant channels is a modeling decision to be approved in Checkpoint 3/4. Features must **never** be dropped globally based on full-dataset or validation/test statistics.

---

## 7. Threshold Calibration Safeguard

- **Normal-Only Validation Calibration:** Decision thresholds for anomaly alerting must be calibrated **strictly on normal validation data** (e.g. 95th, 99th, or 99.5th percentile score budget corresponding to an operational false-alarm tolerance).
- **Validation Fault Runs Policy:** The three validation non-normal runs (`dataset_15_clogging.csv`, `dataset_10_leakage.csv`, `dataset_12_reconfiguration.csv`) may be used to observe detection behavior and select model architectures/hyperparameters, but **must never be used to tune or select the decision threshold**.
- **Test Set Isolation:** Test run scores and labels must remain completely untouched until the final unbiased evaluation stage. Test labels must never be accessed to select thresholds (reversing the upstream Youden's J test leakage).
