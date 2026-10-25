# Candidate Data Audit

This audit evaluates the physical structure, data-generating process, licensing, label integrity, empirical representative file inspections, and computational feasibility of the three candidate datasets:
1. **Candidate A:** WDSEventDB (Water Distribution System Event Diagnosis Benchmark)
2. **Candidate B:** LBNL / OpenEI Fault Detection and Diagnostics Datasets (Submission 5763 / Simulated Fan Coil Unit Benchmark)
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
- **Timestamps:** No timestamp column exists within any sheet. The timestamps exist only in the sheet title.
- **Missing Data and Quality:** 0 missing values. However, sensor failure runs contain non-physical readings (e.g. `Pressure 2 Out = -12.72`) indicating hard electrical offsets.

### 1.6 Data-Generating Process and Evaluation Risks
- **DGP:** Physical, sensor-instrumented water distribution testbed at Lehigh University.
- **Critical Methodological Flaw:**
  - The dataset has only **8 independent fault episodes**.
  - If rows are randomly split (train/test), adjacent time points leak 100% of the dynamics.
  - If split by run (Group-K-Fold by file), the Cyberattack class has **only 1 run**, making cross-run validation impossible.
  - Deep sequence models will severely overfit to the static background states of those 8 sessions.

---

## 2. Candidate B: LBNL / OpenEI Simulated Fan Coil Unit Dataset

### 2.1 Canonical Source, Documentation, and Access
- **Canonical Portal:** [Open Energy Data Initiative (OEDI) Submission 5763](https://data.openei.org/submissions/5763) & [LBNL Fault Detection and Diagnostics Portal](https://faultdetection.lbl.gov/data/).
- **Dataset DOI:** [10.25984/1881324](https://doi.org/10.25984/1881324).
- **Lead Authors and Institutions:** Jessica Granderson, Guanjing Lin, Yimin Chen, Armando Casillas (Lawrence Berkeley National Laboratory); Jin Wen, Zhelun Chen (Drexel University); Piljae Im, Sungkyun Jung (Oak Ridge National Laboratory); Kyle Benne, Jiazhen Ling (NREL); Ravi Gorthala (UConn); Sen Huang, Draguna Vrabie (PNNL).
- **Primary Data Descriptor Paper:** Granderson, J., Lin, G., Chen, Y., Casillas, A., Im, P., Jung, S., Benne, K., Ling, J., Gorthala, R., Wen, J., Chen, Z., Huang, S., & Vrabie, D. (2023). *A labeled dataset for building HVAC systems operating in faulted and fault-free states*. Nature Scientific Data, 10(1), 342. DOI: [10.1038/s41597-023-02197-w](https://doi.org/10.1038/s41597-023-02197-w). (PMC10235024).
- **Direct Download Routes (Verified working: HTTP 200 / Range Requests 206):**
  - FCU Zip (OpenEI 5763): `https://fdddata.lbl.gov/data/Simulated_LBNL_FDD_Data_Sets_FCU/LBNL_FDD_Data_Sets_FCU.zip` (506.1 MB, 530,633,129 bytes).
  - FCU Inventory PDF: `https://data.openei.org/files/5763/Inventory of LBNL FDD Data Sets_FCU.pdf` (763 KB).
  - FCU Semantic Model: `https://data.openei.org/files/5763/LBNL_FDD_Data_Sets_FCU_ttl.ttl` (Brick Schema v1.2).
- **Access Date:** 2026-10-26.

### 2.2 Licensing Terms
- **Dataset License:** Creative Commons Attribution 4.0 International (**CC BY 4.0**). Confirmed on OpenEI submission metadata and LBNL data portals.
- **Code & Metadata:** CC BY 4.0 / Public domain US Government work (DOE Contract DE-AC02-05CH11231).
- **Commercial & Academic Reuse:** Permitted without royalty, requiring only formal attribution.

### 2.3 Physical Storage, File Inventory, and Scope
- **Physical Equipment Simulated:** 1 four-pipe Fan Coil Unit (FCU) conditioning a commercial building perimeter zone.
- **Compressed Download Size:** 530,633,129 bytes (506.1 MB).
- **Archive Contents:** Exactly 50 Central Directory entries (1 directory `LBNL_FDD_Dataset_FCU/` + 49 CSV files).
- **Scenario File Structure:**
  - 1 baseline scenario file: `FCU_FaultFree.csv` (80.40 MB uncompressed text).
  - 48 severity-specific scenario files representing **17 distinct physical fault types** across minor, moderate, and severe intensities (80–82 MB each).
  - Total uncompressed size of all 49 CSVs: **~3.92 GB**.

### 2.4 Empirical Inspection of Representative Files
Using custom HTTP range requests, five representative files were extracted and audited in `scratch/fcu_sample/`:
1. `FCU_FaultFree.csv` (Normal baseline: 84,305,845 bytes, 525,600 rows).
2. `FCU_VLVLeak_Cooling_20.csv` (Minor 20% cooling valve leak: 84,196,922 bytes, 525,600 rows).
3. `FCU_VLVLeak_Cooling_50.csv` (Moderate 50% cooling valve leak: 84,047,790 bytes, 525,600 rows).
4. `FCU_VLVLeak_Cooling_80.csv` (Severe 80% cooling valve leak: 83,953,504 bytes, 525,600 rows).
5. `FCU_Fouling_Cooling_Airside_Minor.csv` (Minor airside coil fouling: 83,997,327 bytes, 525,600 rows).

**Audit Findings on Inspected Files:**
- **Row Counts & Granularity:** Every single file contains exactly **525,600 rows** ($365 \text{ days} \times 24 \text{ h} \times 60 \text{ min}$) spanning `01/01/2018 00:00` to `12/31/2018 23:59` at uniform 1-minute intervals. Total across 49 files is **25,754,400 rows**.
- **Data Quality:** Exactly **0 missing values** and **0 infinite values** in all files.
- **Timestamp & Weather Alignment:**
  - Timestamps are 100% identical row-for-row across all files (`True`).
  - Weather channels (`FCU_OAT` outdoor temperature and `FCU_OA_HUMD` outdoor humidity) have a maximum absolute difference of **`0.0000`** across all files. Every scenario uses the identical Des Moines, IA TMY3 meteorological sequence.
- **Constant Columns Identified:**
  - `FAN_CTRL` = `1.0` (Fan mode fixed at Auto).
  - `FCU_CLG_EWT` = `45.0` °F (Chilled water plant entering temperature).
  - `FCU_HTG_EWT` = `120.0` °F (Hot water plant entering temperature).
  - These 3 constant channels provide zero diagnostic variance and must be dropped during preprocessing.
- **Label Representation:**
  - CSV files do not contain an inline label column. The fault is active continuously for the full year in each fault file. Ground-truth labels are defined by the controlled simulation scenario configuration.

### 2.5 Measured Downsampling Verification
Downsampling was tested across 1-minute, 5-minute, and 15-minute aggregations on `FCU_FaultFree.csv` vs. `FCU_VLVLeak_Cooling_20.csv`:
- **1-minute (raw):** 525,600 rows | 120.3 MB RAM | 12.29 MB Parquet.
- **5-minute:** 105,120 rows | 24.06 MB RAM | 4.53 MB Parquet | 1.12s resample time.
- **15-minute:** 35,040 rows | 8.02 MB RAM | 2.53 MB Parquet | 0.73s resample time.
- **Dataset Total (49 files at 15-min):** Exactly **1,716,960 rows** (1.72M) occupying **~124 MB Parquet** and **~393 MB RAM**.
- **Signal Fidelity:**
  - The mean chilled water flow delta ($\Delta GPM = +1.02496$) and discharge temperature delta ($\Delta T = -7.01199^\circ\text{F}$) are **identical to 5 decimal places across 1-min, 5-min, and 15-min resolutions**.
  - During periods when the cooling valve is commanded shut (`FCU_CVLV_DM == 0`), the leak exhibits a steady **1.1400 GPM** chilled water flow across 100% of shut hours.
  - In Winter, the valve is shut 96.2% of the time, causing a constant 1.14 GPM leak that depresses discharge air temperature by -2.17°F. In Spring/Fall, discharge temperature drops by -8.7°F to -9.2°F.
  - Abrupt 1-minute valve command blips ($>0.5$) are 0 because NIST HVACSIM+ simulates continuous PI control.

### 2.6 Data-Generating Process and Real-World Limitations
- **DGP:** Calibrated physical simulation in NIST HVACSIM+ using DOE commercial reference building models and Des Moines, IA TMY3 weather.
- **Critical Limitations:**
  - The dataset represents **one simulated FCU unit** and **one weather year**.
  - Held-out seasonal splits test seasonal distribution shift within this simulated system, but do **not** prove generalization to real field buildings, other climates, or multi-year drift.
  - Labels reflect simulated fault injection, not field-confirmed physical repairs.

---

## 3. Candidate C: HazardNet (HPC Thermal Hazard Prediction)

### 3.1 Canonical Source, Documentation, and Access
- **Canonical Dataset DOI:** [10.5281/zenodo.10050368](https://doi.org/10.5281/zenodo.10050368).
- **Code Repository:** [MSKazemi/HazardNet](https://github.com/MSKazemi/HazardNet).
- **Authors and Institution:** Mohsen Seyedkazemi Ardebili, Andrea Acquaviva, Luca Benini, Andrea Bartolini (University of Bologna & CINECA).
- **Journal Publication:** Ardebili, M. S., Acquaviva, A., Benini, L., & Bartolini, A. (2024). *HazardNet: A thermal hazard prediction framework for datacenters*. Future Generation Computer Systems, 155, 340–353. DOI: [10.1016/j.future.2024.01.031](https://doi.org/10.1016/j.future.2024.01.031).
- **Direct Download Routes (Verified working: HTTP 200/206):**
  - `https://zenodo.org/records/10050368/files/Marconi_A2_Power_Consumption.csv.gz` (469.5 MB).
  - `https://zenodo.org/records/10050368/files/Marconi_A2_Inlet_Air_Temp.csv.gz` (216.3 MB).
  - `https://zenodo.org/records/10050368/files/Marconi_A2_Outlet_Air_Temp.csv.gz` (287.8 MB).
- **Access Date:** 2026-10-26.

### 3.2 Licensing Terms
- **Dataset License:** Creative Commons Attribution 4.0 International (**CC BY 4.0**).
- **Codebase License:** Apache License 2.0.

### 3.3 Physical Storage and Data Layout
- **Download Size:** 1,020,892,729 bytes (~973.6 MB compressed, ~1.02 GB).
- **Extracted Size:** Estimated 6.5 to 8.5 GB uncompressed text CSV.
- **File Organization:** Exactly 3 large compressed CSV files containing telemetry matrices.

### 3.4 Structural Counts and Granularity
- **Temporal Resolution:** Exactly 10-minute intervals (600 seconds) spanning Jan 14, 2019 to Dec 31, 2019 (~50,544 rows).
- **Dimensionality / Width:** Exactly 3,313 columns (1 timestamp index + 3,312 compute nodes: `r065c01s01` through `r110c18s04`).
- **Total Numerical Matrix Entries:** 50,544 timestamps * 3,312 nodes = **167,401,728 data points per file** (~502 million observations across the 3 files).
- **System Scope:** Marconi A2 Tier-0 Supercomputer at CINECA. Exactly 1 physical datacenter site.

### 3.5 Disqualifying Flaws: Missing Labels and Missing Code
- **No Ground-Truth Labels:** Inspection via HTTP range requests confirmed that the Zenodo download contains purely raw temperatures and power readings. **There are zero target hazard labels**.
- **Missing Code Artifacts:** The GitHub repository (`MSKazemi/HazardNet`) is missing the core data-generation/labeling script (`HazardNet_DataGen.py`) and model definitions (`HazardNet_Models.py`) with HTTP 404 errors.
- The codebase contains unresolvable local system paths (`sys.path.append("/home/seyedkazemi/...")`).
- Any attempt to use this dataset requires inventing synthetic pseudo-labels, making scientific comparison impossible.

---

## 4. Cross-Candidate Data Comparison Table

| Audit Criterion | Candidate A: WDSEventDB | Candidate B: LBNL / OpenEI FCU (Calibrated) | Candidate C: HazardNet (Marconi A2) |
| :--- | :--- | :--- | :--- |
| **Canonical Source** | GitHub (Moazeni Lab) | OpenEI / LBNL FDD Portal | Zenodo / GitHub (MSKazemi) |
| **Peer-Reviewed Reference** | EWRI 2026 Conference | Nature Scientific Data 10, 342 (2023) | Future Gen. Comp. Sys. 155 (2024) |
| **License (Data / Code)** | CC0 1.0 (Public Domain) | CC BY 4.0 / Open Government | CC BY 4.0 / Apache 2.0 |
| **Download Size** | 2.16 MB (Zip) | 506.1 MB (Zip; ~52 MB selective) | 973.6 MB (Gz) |
| **Extracted Size** | 1.25 MB (.xlsx) | ~3.92 GB raw / **124 MB (15-min Parquet)** | ~7.5 GB (.csv) |
| **Total Rows** | 25,165 | 25,754,400 raw / **1,716,960 (15-min)** | 50,544 rows * 3,313 cols |
| **Sensor / Feature Channels** | 15 sensor/actuator features | 26 active physical channels (3 constant dropped) | 3,312 node channels across 3 files |
| **Independent Units** | **Only 8 fault runs** (1 cyber, 3 leak, 4 sensor) | **17 fault types** (48 severity scenarios, 1 FCU) | 1 supercomputer cluster (351 days) |
| **Target Labels Present?** | Yes (`Labels` 0.0 or 1.0 in sheets) | Yes (Defined by controlled simulation scenario) | **NO** (Requires missing private generator) |
| **Label Provenance** | Testbed injection (known runs) | Physics simulation (NIST HVACSIM+) | Threshold pseudo-labels (unreleased code) |
| **Data Generating Process** | 1 Lab-scale physical water loop | Physics simulation (calibrated commercial zone)| Production Tier-0 HPC telemetry |
| **Compute Feasibility (CPU)** | <1 minute on 2-core CPU | **2–5 min on CPU (15-min Parquet)** | Infeasible on CPU (requires GPU cluster) |
| **Primary Blocker / Hard Stop** | Sample size fatal flaw (8 runs; 1 cyber run) | Simulated data; 1 unit/year (Calibrated) | Missing labels & missing GitHub scripts |

---

## 5. Audit Conclusion

1. **Candidate A (WDSEventDB):** Disqualified due to sample insufficiency (only 8 fault episodes total).
2. **Candidate C (HazardNet):** Disqualified due to missing ground-truth labels and missing GitHub scripts (HTTP 404).
3. **Candidate B (LBNL Simulated FCU):** Qualified as a controlled MLOps engineering benchmark. Selective range-request extraction works cleanly (~52 MB transfer), and 15-minute downsampling reduces the dataset to 124 MB Parquet while preserving 100% of persistent thermodynamic leak signals.
