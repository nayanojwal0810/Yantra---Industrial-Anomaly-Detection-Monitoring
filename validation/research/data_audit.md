# Candidate Data Audit

This audit evaluates the physical structure, data-generating process, licensing, label integrity, and computational feasibility of the three primary candidate datasets:
1. **Candidate A:** WDSEventDB (Water Distribution System Event Diagnosis Benchmark)
2. **Candidate B:** LBNL / OpenEI Fault Detection and Diagnostics Datasets (Submission 5763 / Fan Coil Unit & SDAHU)
3. **Candidate C:** HazardNet (HPC Thermal Hazard Prediction / Marconi A2)

---

## 1. Candidate A: WDSEventDB

### 1.1 Canonical Source, Documentation, and Access
- **Canonical Repository:** [Moazeni-s-Concise-Lab/WDSEventDB](https://github.com/Moazeni-s-Concise-Lab/WDSEventDB)
- **Lab / Institution:** CONCISE Research Lab (InterCONnected Critical Infrastructure Systems Engineering), Lehigh University (PI: Dr. Faegheh Moazeni; Lead Author: Nazia Raza).
- **Conference Citation / Documentation:** Raza, N., Iwakin, O., Villacres, D., Putri, S. A., & Moazeni, F. (2025). *WDSEventDB: A real-time benchmark dataset for event diagnosis in water distribution networks*. World Environmental & Water Resources Congress 2026 (EWRI 2026), Mobile, Alabama.
- **Repository Archive Link:** [WDSEventDB.zip on GitHub](https://github.com/Moazeni-s-Concise-Lab/WDSEventDB/blob/main/WDSEventDB.zip)
- **Direct Raw Download Route:** `https://raw.githubusercontent.com/Moazeni-s-Concise-Lab/WDSEventDB/main/WDSEventDB.zip` (Verified working: HTTP 200).
- **Access Date:** 2026-10-26.

### 1.2 Licensing Terms
- **Dataset and Repository License:** Creative Commons CC0 1.0 Universal (Public Domain Dedication). Verified from root `LICENSE` file on the repository.
- **Paper Terms:** EWRI conference proceedings (ASCE copyright on published paper text; data released into public domain).
- **Commercial & Academic Reuse:** Permitted without restriction under CC0 1.0.

### 1.3 Physical Storage and Data Layout
- **Download Size:** 2,265,766 bytes (~2.16 MB compressed zip).
- **Extracted Size:** 1,309,619 bytes (~1.25 MB uncompressed Excel files).
- **File Format:** Microsoft Excel (`.xlsx`) files across 4 subdirectories.
- **Directory Structure:**
  - `Clean/CleanData.xlsx` (1 sheet: `NormalOperation`)
  - `Cyberattack/CyberEvent1-4.xlsx` (1 sheet: `TestSet_4Resets`)
  - `Leakage/` (3 files: `LeakEvent1.xlsx`, `LeakEvent2.xlsx`, `LeakEvent3.xlsx`)
  - `Sensor Failure/` (4 files: `SensorEvent1.xlsx`, `SensorEvent23.xlsx`, `SensorEvent45.xlsx`, `SensorEvent67.xlsx`)
- **Total Files:** Exactly 9 meaningful `.xlsx` files (plus macOS `__MACOSX` metadata artifacts).

### 1.4 Structural Counts and Granularity
- **Total Rows Across Entire Dataset:** Exactly 25,165 rows.
- **Breakdown by File and Class Distribution:**
  | Subfolder | File Name | Sheet Name | Row Count | Class 0 (Normal) | Class 1 (Fault) | Nulls |
  | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
  | `Clean/` | `CleanData.xlsx` | `NormalOperation` | 9,743 | 9,743 (100.0%) | 0 (0.0%) | 0 |
  | `Cyberattack/` | `CyberEvent1-4.xlsx` | `TestSet_4Resets` | 5,869 | 5,154 (87.8%) | 715 (12.2%) | 0 |
  | `Leakage/` | `LeakEvent1.xlsx` | `9-6-2024 7-54-01 PM` | 1,368 | 540 (39.5%) | 828 (60.5%) | 0 |
  | `Leakage/` | `LeakEvent2.xlsx` | `9-28-2025 12-43-22 PM` | 1,385 | 771 (55.7%) | 614 (44.3%) | 0 |
  | `Leakage/` | `LeakEvent3.xlsx` | `10-21-2025 3-08-38 PM` | 1,355 | 659 (48.6%) | 696 (51.4%) | 0 |
  | `Sensor Failure/` | `SensorEvent1.xlsx` | `10-21-2025 2-09-59 PM` | 1,360 | 1,183 (87.0%) | 177 (13.0%) | 0 |
  | `Sensor Failure/` | `SensorEvent23.xlsx` | `10-21-2025 1-41-52 PM` | 1,362 | 1,210 (88.8%) | 152 (11.2%) | 0 |
  | `Sensor Failure/` | `SensorEvent45.xlsx` | `10-21-2025 11-27-13 AM` | 1,361 | 1,202 (88.3%) | 159 (11.7%) | 0 |
  | `Sensor Failure/` | `SensorEvent67.xlsx` | `10-21-2025 9-45-08 AM` | 1,362 | 1,240 (91.0%) | 122 (9.0%) | 0 |
  | **Total** | **9 Files** | **9 Sheets** | **25,165** | **21,862 (86.9%)** | **3,303 (13.1%)** | **0** |

- **Independent Sample / Run Count:**
  - *Clean Runs:* Exactly 1 run (9,743 steps).
  - *Cyberattack Runs:* Exactly 1 file containing 4 attack resets (715 attack steps total).
  - *Leakage Runs:* Exactly 3 runs (`LeakEvent1`, `LeakEvent2`, `LeakEvent3`).
  - *Sensor Failure Runs:* Exactly 4 runs (`SensorEvent1`, `SensorEvent23`, `SensorEvent45`, `SensorEvent67`).
  - **Total Independent Fault Episodes:** Exactly 8 fault runs.
- **Independent Systems / Devices:** Exactly 1 physical lab testbed loop.

### 1.5 Features, Schema, and Label Provenance
- **Feature Channels (15 numeric features):**
  - Pressure sensors: `Pressure 1 Out`, `Pressure 2 Out`, `Pressure 3 In`, `Pressure 4 In` (psi).
  - Flow meters: `Water Flow 1`, `Water Flow 2`, `Water Flow 3`, `Water Flow 4` (gpm / L/s).
  - Variable Frequency Drives (Pumps): `VFD 1`, `VFD 2`, `VFD 3`, `VFD 4-1`, `VFD 4-2` (% or Hz).
  - Actuated Valves: `Analog Valve 1`, `Analog Valve 2` (% open).
  - Target: `Labels` (Binary float: `0.0` = Normal, `1.0` = Event).
- **Timestamps:** No timestamp column exists within any sheet. The timestamps exist only in the sheet title (e.g., `9-6-2024 7-54-01 PM`). Sampling appears to be 1 sample per second (~1,360 rows = ~22.6 minutes per run).
- **Missing Data and Quality:** 0 missing values. However, sensor failure runs contain non-physical readings (e.g. `Pressure 2 Out = -12.72`) indicating that sensor faults were injected as hard electrical disconnects or fixed numerical offsets.

### 1.6 Data-Generating Process and Evaluation Risks
- **DGP:** Physical, sensor-instrumented water distribution testbed at Lehigh University. Faults were deliberately injected by lab operators (manually cracking valves for leaks, sending cyber-override commands to VFDs, and disconnecting sensor pins).
- **Critical Methodological Flaw:**
  - The dataset has only **8 independent fault episodes**.
  - If rows are randomly split (train/test), adjacent time points leak 100% of the dynamics, yielding inflated >99% F1 scores that do not reflect operational generalization.
  - If split by run (Group-K-Fold by file), the Cyberattack class has **only 1 run**, making cross-run validation mathematically impossible for cyberattacks without training and testing on the identical run.
  - Deep sequence models (LSTM/TCN) cannot learn generalizable hydrodynamics from 8 short runs on 1 static testbed; they will simply memorize the background setpoints of those 8 sessions.

### 1.7 Compute and Resource Requirements
- Extremely lightweight. Entire dataset fits in ~5 MB of RAM. Can be processed and modeled in <30 seconds on any 2-core CPU.

---

## 2. Candidate B: LBNL / OpenEI Fault Detection and Diagnostics Datasets

### 2.1 Canonical Source, Documentation, and Access
- **Canonical Portal:** [Open Energy Data Initiative (OEDI) Submission 5763](https://data.openei.org/submissions/5763) & [LBNL Fault Detection and Diagnostics Portal](https://faultdetection.lbl.gov/data/).
- **Dataset DOI:** [10.25984/1881324](https://doi.org/10.25984/1881324).
- **Lead Authors and Institutions:** Jessica Granderson, Guanjing Lin, Yimin Chen, Armando Casillas (Lawrence Berkeley National Laboratory); Jin Wen, Zhelun Chen (Drexel University); Piljae Im, Sungkyun Jung (Oak Ridge National Laboratory); Kyle Benne, Jiazhen Ling (NREL); Ravi Gorthala (UConn); Sen Huang, Draguna Vrabie (PNNL).
- **Primary Data Descriptor Paper:** Granderson, J., Lin, G., Chen, Y., Casillas, A., Im, P., Jung, S., Benne, K., Ling, J., Gorthala, R., Wen, J., Chen, Z., Huang, S., & Vrabie, D. (2023). *A labeled dataset for building HVAC systems operating in faulted and fault-free states*. Nature Scientific Data, 10(1), 344. DOI: [10.1038/s41597-023-02206-8](https://doi.org/10.1038/s41597-023-02206-8). (PMC10235024).
- **Direct Download Routes (Verified working: HTTP 200):**
  - FCU Zip (OpenEI 5763): `https://fdddata.lbl.gov/data/Simulated_LBNL_FDD_Data_Sets_FCU/LBNL_FDD_Data_Sets_FCU.zip` (506.1 MB).
  - FCU Inventory PDF: `https://data.openei.org/files/5763/Inventory of LBNL FDD Data Sets_FCU.pdf` (763 KB).
  - FCU Semantic Model: `https://data.openei.org/files/5763/LBNL_FDD_Data_Sets_FCU_ttl.ttl` (Brick Schema v1.2).
  - SDAHU Zip: `https://fdddata.lbl.gov/data/Simulated_LBNL_FDD_Data_Sets_SDAHU/LBNL_FDD_Data_Sets_SDAHU.zip` (579.5 MB).
- **Access Date:** 2026-10-26.

### 2.2 Licensing Terms
- **Dataset License:** Creative Commons Attribution 4.0 International (**CC BY 4.0**). Confirmed on OpenEI submission metadata and LBNL data portals.
- **Code & Metadata:** CC BY 4.0 / Public domain US Government work (DOE Contract DE-AC02-05CH11231).
- **Commercial & Academic Reuse:** Permitted without royalty, requiring only formal attribution.

### 2.3 Physical Storage and Data Layout
- **Subsystem Scope:** The complete LBNL collection covers 7 HVAC equipment categories: Fan Coil Units (FCU), Single-Duct AHU (SDAHU), Dual-Duct AHU (DDAHU), Rooftop Units (RTU), Fan-Powered VAV Terminal Units (FPU), Chiller Plants, and Boiler Plants.
- **OpenEI Submission 5763 Focus:** Focuses on the Fan Coil Unit (FCU) benchmark.
- **Compressed Download Size:** 530,633,129 bytes (506.1 MB).
- **Extracted Contents:** 49 separate `.csv` files + 1 Brick schema `.ttl` semantic graph + 1 comprehensive inventory document.
- **File Organization:** 48 individual fault scenario files (e.g. `FCU_OADMPRLeak_20.csv`, `FCU_VLVStuck_Cooling_50.csv`) + 1 baseline file (`Fault_free.csv`).

### 2.4 Structural Counts and Granularity
- **Temporal Resolution:** Exactly 1-minute sampling interval across an entire continuous calendar year (365 days * 24 hours * 60 minutes = 525,600 rows per file).
- **Total Rows (Full Resolution):** 49 files * 525,600 rows = **25,754,400 rows**.
- **Downsampled Resolution (Industry Standard BAS Rate):**
  - At 5-minute sampling: 105,120 rows per file = ~5.15 million rows total.
  - At 15-minute sampling: 35,040 rows per file = ~1.72 million rows total (~85 MB uncompressed parquet).
- **Independent Equipment / Fault Runs:**
  - 48 independent fault modes (encompassing 17 distinct physical fault types across minor, moderate, and severe intensities) plus 1 full-year fault-free baseline.
  - Full seasonal cycle: Each fault file spans Winter, Spring, Summer, and Fall under variable commercial occupancy schedules and TMY3 ambient weather.
- **Fault Types Covered (17 Classes):**
  1. Outdoor air damper leaking (20%, 50%, 80%)
  2. Outdoor air damper stuck (0%, 30%, 50%, 80%, 100%)
  3. Heating coil valve leaking (20%, 50%, 80%)
  4. Heating coil valve stuck (0%, 20%, 50%, 80%, 100%)
  5. Cooling coil valve leaking (20%, 50%, 80%)
  6. Cooling coil valve stuck (0%, 20%, 50%, 80%, 100%)
  7. Room temperature sensor bias (-4°C, -2°C, +2°C, +4°C)
  8. Cooling coil fouling air-side (Minor, Moderate, Severe)
  9. Cooling coil fouling water-side (Minor, Moderate, Severe)
  10. Heating coil fouling air-side (Minor, Moderate, Severe)
  11. Heating coil fouling water-side (Minor, Moderate, Severe)
  12. Filter restriction (10%, 15%, 50% flow reduction)
  13. Outdoor air inlet blockage
  14. Fan outlet blockage
  15. FCU unstable control loop
  16. Cooling control reverse acting
  17. Heating control reverse acting
  18. Normal fault-free operation

### 2.5 Features, Schema, and Label Provenance
- **Telemetry Channels (29 variables):**
  - Control modes: `FCU_CTRL` (0=Shutdown, 1=Operate, 2=Setback), `FAN_CTRL` (1=Auto, 2=Off).
  - Temperatures: `RM_TEMP` (Room °F), `RMCLGSPT` (Cooling setpoint °F), `RMHTGSPT` (Heating setpoint °F), `FCU_MAT` (Mixed air °F), `FCU_DAT` (Discharge air °F), `FCU_RAT` (Return air °F), `FCU_OAT` (Outdoor air °F), `FCU_CLG_EWT` / `RWT` (Chilled water entering/return °F), `FCU_HTG_EWT` / `RWT` (Hot water entering/return °F).
  - Actuators & Commands: `FCU_CVLV` (Cooling valve position), `FCU_CVLV_DM` (Cooling valve command), `FCU_HVLV` (Heating valve position), `FCU_HVLV_DM` (Heating valve command), `FCU_DMPR` (Damper position), `FCU_DMPR_DM` (Damper command).
  - Flows, Fan & Power: `FCU_CLG_GPM` (Cooling GPM), `FCU_HTG_GPM` (Heating GPM), `FCU_DA_CFM` (Discharge CFM), `FCU_OA_CFM` (Outdoor air CFM), `FCU_SPD` (Fan rev/s), `FCU_WAT` (Fan power Watts).
  - Humidity: `FCU_MA_HUMD`, `FCU_OA_HUMD`, `FCU_DA_HUMD`, `FCU_RA_HUMD` (%RH).
- **Semantic Metadata:** Accompanying Brick Schema (`.ttl`) maps points to standard ontologies.
- **Label Provenance:** Unambiguous ground truth established by physical simulation injection. Each CSV corresponds to a controlled operating scenario.

### 2.6 Data-Generating Process and Evaluation Risks
- **DGP:** Highly calibrated physics-based simulation developed in HVACSIM+ (NIST) using DOE prototype commercial building models and Des Moines, IA TMY meteorological data.
- **Evaluation Leakage Risks:**
  - Because each file represents a continuous fault scenario across a year, a naive random train/test split of rows will leak temporal weather dynamics (e.g. ambient temperature).
  - **Correct Evaluation Protocol:** Split strictly by **season** (e.g., train on Spring/Autumn, evaluate on Summer/Winter) or split by **severity** (train on moderate/severe faults, evaluate zero-shot detection on minor/nascent faults).
- **Representativeness:** Calibrated on physics, but lacks stochastic human operational overrides present in field buildings.

### 2.7 Compute and Resource Requirements
- Raw download is 506 MB.
- Downsampling to 15-minute intervals produces a clean ~85 MB Parquet dataset (1.72M rows * 29 columns).
- Can be processed completely in pandas/polars within 2 GB of RAM.
- Classical ML (LightGBM/XGBoost) trains in <2 minutes on a standard 4-core CPU. Deep learning models (1D-CNN, TCN, LSTM) train in 10–25 minutes on a free Google Colab / Kaggle T4 GPU.

---

## 3. Candidate C: HazardNet (HPC Thermal Hazard Prediction)

### 3.1 Canonical Source, Documentation, and Access
- **Canonical Dataset DOI:** [10.5281/zenodo.10050368](https://doi.org/10.5281/zenodo.10050368).
- **Code Repository:** [MSKazemi/HazardNet](https://github.com/MSKazemi/HazardNet).
- **Authors and Institution:** Mohsen Seyedkazemi Ardebili, Andrea Acquaviva, Luca Benini, Andrea Bartolini (University of Bologna & CINECA).
- **Peer-Reviewed Journal Publication:** Ardebili, M. S., Acquaviva, A., Benini, L., & Bartolini, A. (2024). *HazardNet: A thermal hazard prediction framework for datacenters*. Future Generation Computer Systems, 155, 340–353. DOI: [10.1016/j.future.2024.01.031](https://doi.org/10.1016/j.future.2024.01.031).
- **Direct Download Routes (Verified working: HTTP 200/206):**
  - `https://zenodo.org/records/10050368/files/Marconi_A2_Power_Consumption.csv.gz` (469.5 MB).
  - `https://zenodo.org/records/10050368/files/Marconi_A2_Inlet_Air_Temp.csv.gz` (216.3 MB).
  - `https://zenodo.org/records/10050368/files/Marconi_A2_Outlet_Air_Temp.csv.gz` (287.8 MB).
- **Access Date:** 2026-10-26.

### 3.2 Licensing Terms
- **Dataset License:** Creative Commons Attribution 4.0 International (**CC BY 4.0**).
- **Codebase License:** Apache License 2.0 (Verified in root `LICENSE` on GitHub).
- **Commercial & Academic Reuse:** Permitted with attribution under CC BY 4.0 and Apache 2.0.

### 3.3 Physical Storage and Data Layout
- **Download Size:** 1,020,892,729 bytes (~973.6 MB compressed, ~1.02 GB).
- **Extracted Size:** Estimated 6.5 to 8.5 GB uncompressed text CSV.
- **File Organization:** Exactly 3 large compressed CSV files containing telemetry matrices.

### 3.4 Structural Counts and Granularity
- **Temporal Resolution:** Exactly 10-minute intervals (600 seconds) spanning January 14, 2019, 18:10:00 to December 31, 2019, 23:50:00 (~351 days).
- **Row Count:** Approximately 50,544 rows per file.
- **Dimensionality / Width:** Exactly 3,313 columns (1 timestamp index + 3,312 compute nodes: `r065c01s01` through `r110c18s04`).
- **Total Numerical Matrix Entries:** 50,544 timestamps * 3,312 nodes = **167,401,728 data points per file** (~502 million observations across the 3 files).
- **System Scope:** Marconi A2 Tier-0 Supercomputer at CINECA (Lenovo NeXtScale, Intel Xeon Phi 7250 Knights Landing). Exactly 1 physical datacenter site.

### 3.5 Features, Schema, and Label Provenance
- **Raw Telemetry Metrics:**
  1. `Marconi_A2_Inlet_Air_Temp`: Node intake air temperature (°C).
  2. `Marconi_A2_Outlet_Air_Temp`: Node exhaust air temperature (°C).
  3. `Marconi_A2_Power_Consumption`: Node electrical power (Watts).
- **FATAL FLAW — Label Absence and Provenance:**
  - The Zenodo dataset contains **NO ground-truth target labels**. It is purely raw operational telemetry.
  - In the published paper, target labels ("thermal hazard likely within next 6 hours") were generated via a private, rule-based statistical threshold applied to the exhaust temperatures.
  - The authors' preprocessing, data generation, and labeling module (`HazardNet_DataGen.py`) and model definitions (`HazardNet_Models.py`) are **MISSING from the public GitHub repository** (HTTP 404).
  - In `src/HazardNet_Utils.py`, the code contains unresolvable local system paths (`sys.path.append("/home/seyedkazemi/codes/HPCRoomModel/mskhelper/")`).
  - Consequently, any user working with this dataset must invent their own label definitions, rendering experimental results arbitrary and unreproducible against the published benchmark.

### 3.6 Data-Generating Process and Evaluation Risks
- **DGP:** Real production telemetry collected via the *ExaMon* scalable monitoring infrastructure on a live supercomputer.
- **Spatiotemporal Structure:** Extremely high-dimensional (3,312 spatial sensor nodes arranged across racks and chassis).
- **Evaluation Risks:**
  - High risk of temporal auto-correlation. Supercomputers run batch workloads (SLURM jobs) that create localized thermal spikes lasting hours.
  - Because labels are generated by thresholding future temperature values of the same sensors, the ML model is merely predicting its own thresholded input smoothed over time.

### 3.7 Compute and Resource Requirements
- Requires >16 GB RAM just to load the uncompressed matrices.
- Processing 3,312 channels through 2D/3D TCNs or LSTMs requires dedicated high-end GPU hardware (>16 GB VRAM, e.g. A100/V100) and hours of training. It cannot run on a free 2-core CPU or basic local environment.

---

## 4. Cross-Candidate Data Comparison Table

| Audit Criterion | Candidate A: WDSEventDB | Candidate B: LBNL / OpenEI 5763 (FCU) | Candidate C: HazardNet (Marconi A2) |
| :--- | :--- | :--- | :--- |
| **Canonical Source** | GitHub (Moazeni Lab) | OpenEI / LBNL FDD Portal | Zenodo / GitHub (MSKazemi) |
| **Peer-Reviewed Reference** | EWRI 2026 Conference | Nature Scientific Data 10, 344 (2023) | Future Gen. Comp. Sys. 155 (2024) |
| **License (Data / Code)** | CC0 1.0 (Public Domain) | CC BY 4.0 / Open Government | CC BY 4.0 / Apache 2.0 |
| **Download Size** | 2.16 MB (Zip) | 506.1 MB (Zip) | 973.6 MB (Gz) |
| **Extracted Size** | 1.25 MB (.xlsx) | ~2.5 GB (.csv) / ~85 MB (downsampled) | ~7.5 GB (.csv) |
| **Total Rows** | 25,165 | 25,754,400 (raw) / 1,720,000 (15-min) | 50,544 rows * 3,313 cols |
| **Sensor / Feature Channels** | 15 sensor/actuator features | 29 physical sensor/control features | 3,312 node channels across 3 files |
| **Independent Runs / Units** | **Only 8 fault runs** (1 cyber, 3 leak, 4 sensor) | **48 fault scenarios** + 1 baseline (full year) | 1 live supercomputer cluster (351 days) |
| **Target Labels Present?** | Yes (`Labels` 0.0 or 1.0 in sheets) | Yes (Defined by file/scenario & injection) | **NO** (Requires missing private generator) |
| **Label Provenance** | Testbed injection (known runs) | Physics simulation (NIST HVACSIM+) | Threshold pseudo-labels (unreleased code) |
| **Data Generating Process** | 1 Lab-scale physical water loop | Physics simulation (calibrated commercial zone)| Production Tier-0 HPC telemetry |
| **Compute Feasibility (CPU)** | <1 minute on 2-core CPU | 2–5 min on CPU (downsampled 15-min) | Infeasible on CPU (requires GPU cluster) |
| **Primary Blocker / Hard Stop** | Sample size fatal flaw (8 runs; 1 cyber run) | Requires downsampling & seasonal isolation | Missing labels & missing GitHub scripts |

---

## 5. Audit Conclusion

1. **Candidate A (WDSEventDB):** Disqualified for deep learning. While legally unencumbered (CC0) and small, having only 8 total fault episodes (with only 1 cyberattack run) makes statistically valid, leakage-free sequence modeling impossible.
2. **Candidate C (HazardNet):** Disqualified due to non-reproducibility and missing artifacts. The Zenodo data lacks target labels, and the author's code repository lacks the essential label generation and model scripts. High dimensionality also imposes excessive compute burdens.
3. **Candidate B (LBNL / OpenEI 5763):** Qualified. It possesses official CC BY 4.0 licensing, verified Nature documentation, rich 29-channel physical telemetry, 48 diverse fault modes spanning an entire meteorological year, clean Brick Schema alignment, and manageable downsampled compute requirements.
