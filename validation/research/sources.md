# Validation Research Sources and Evidence Ledger

This document registers all canonical data sources, research papers, software repositories, and industry standards audited during the candidate validation process. Every claim in the validation deliverables is directly mapped to an entry below.

---

## 1. Primary Dataset Registries and Portals

| Source ID | Canonical Title & URL | Source Type | Publication Date | Access Date | Claims & Verified Findings Supported |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **SRC-DS-01** | [OpenEI Submission 5763: LBNL Fault Detection and Diagnostics Datasets](https://data.openei.org/submissions/5763) | Official Open Data Portal (DOE OEDI) | 2022-08-01 | 2026-10-26 | Canonical host of Candidate B; confirms DOI `10.25984/1881324`, CC BY 4.0 license, Fan Coil Unit scope, BRICK schema support. |
| **SRC-DS-02** | [LBNL Fault Detection and Diagnostics Data Portal](https://faultdetection.lbl.gov/data/) | National Laboratory Project Site | 2022-08-01 | 2026-10-26 | Confirms 7 HVAC subsystems, download routes on `fdddata.lbl.gov`, and official team affiliations (LBNL, Drexel, ORNL, NREL, PNNL). |
| **SRC-DS-03** | [LBNL FCU Inventory PDF Specification](https://data.openei.org/files/5763/Inventory%20of%20LBNL%20FDD%20Data%20Sets_FCU.pdf) | Technical Specification Document | 2022-08-01 | 2026-10-26 | Confirms 49 CSV files, 29 sensor/actuator points, 1-minute sampling, 48 fault modes, Des Moines TMY3 weather, and physical injection methods. |
| **SRC-DS-04** | [WDSEventDB GitHub Repository](https://github.com/Moazeni-s-Concise-Lab/WDSEventDB) | Public Code & Data Repository | 2025-05-10 | 2026-10-26 | Confirms Candidate A repository, CC0 1.0 license, physical testbed description at Lehigh University, and archive `WDSEventDB.zip`. |
| **SRC-DS-05** | [WDSEventDB Data Archive](https://raw.githubusercontent.com/Moazeni-s-Concise-Lab/WDSEventDB/main/WDSEventDB.zip) | Binary Data Archive | 2025-05-10 | 2026-10-26 | Verified download size 2.16 MB; confirmed exactly 9 Excel files, 25,165 total rows, and only 8 independent fault episodes. |
| **SRC-DS-06** | [HazardNet Dataset on Zenodo (Record 10050368)](https://doi.org/10.5281/zenodo.10050368) | Open Research Data Repository | 2023-10-27 | 2026-10-26 | Confirms Candidate C DOI `10.5281/zenodo.10050368`, CC BY 4.0 license, 3 `.csv.gz` files (1.02 GB total), and total absence of ground truth labels. |
| **SRC-DS-07** | [HazardNet GitHub Repository](https://github.com/MSKazemi/HazardNet) | Public Code Repository | 2023-11-01 | 2026-10-26 | Confirms Apache 2.0 license; verified that `HazardNet_DataGen.py` and `HazardNet_Models.py` are missing (HTTP 404), blocking reproduction. |

---

## 2. Peer-Reviewed Academic Literature

| Source ID | Full Citation & DOI | Publication Type | Verified Claims Supported |
| :--- | :--- | :--- | :--- |
| **SRC-LIT-01** | Granderson, J., Lin, G., Chen, Y., Casillas, A., Im, P., Jung, S., Benne, K., Ling, J., Gorthala, R., Wen, J., Chen, Z., Huang, S., & Vrabie, D. (2023). *A labeled dataset for building HVAC systems operating in faulted and fault-free states.* Nature Scientific Data, 10(1), 344. DOI: [10.1038/s41597-023-02206-8](https://doi.org/10.1038/s41597-023-02206-8). (PMC10235024). | Data Descriptor Journal Article (*Nature*) | Confirms Candidate B experimental design, annual simulation protocol, multi-institution peer-review, and establishment of national commercial FDD benchmark. |
| **SRC-LIT-02** | Ardebili, M. S., Acquaviva, A., Benini, L., & Bartolini, A. (2024). *HazardNet: A thermal hazard prediction framework for datacenters.* Future Generation Computer Systems, 155, 340–353. DOI: [10.1016/j.future.2024.01.031](https://doi.org/10.1016/j.future.2024.01.031). | Journal Research Article (*Elsevier*) | Confirms Candidate C modeling architecture (1D/2D/3D TCN, LSTM, SVM), Marconi A2 supercomputer testbed, and 6-hour prediction horizon formulation. |
| **SRC-LIT-03** | Raza, N., Iwakin, O., Villacres, D., Putri, S. A., & Moazeni, F. (2025/2026). *WDSEventDB: A real-time benchmark dataset for event diagnosis in water distribution networks.* World Environmental & Water Resources Congress (EWRI 2026). | Refereed Conference Paper (*ASCE*) | Confirms Candidate A origin at Lehigh University CONCISE lab, sensor instrumentation, and multi-class failure emulation objectives. |
| **SRC-LIT-04** | Granderson, J., Singla, R., Mayhorn, E., Ehrlich, P., Vrabie, D., & Frank, S. (2020). *Building fault detection and diagnostics: achieved performance, and national-scale energy savings.* Energy and Buildings, 221, 110022. DOI: [10.1016/j.enbuild.2020.110022](https://doi.org/10.1016/j.enbuild.2020.110022). | Journal Research Article (*Elsevier*) | Supports stakeholder impact claim: commercial building FDD achieves 9% median energy savings, but suffers from false alarm barriers. |
| **SRC-LIT-05** | Chen, Z., Wen, J., & Granderson, J. (2023). *Cross-building domain adaptation for HVAC fault detection and diagnosis based on contrastive learning and semantic graphs.* Building and Environment, 238, 110368. | Journal Research Article (*Elsevier*) | Supports SOTA modeling claim: demonstrates value of Brick Schema and domain adaptation for cross-building transfer in commercial HVAC. |
| **SRC-LIT-06** | Taormina, R., et al. (2018). *Battle of the Attack Detection Algorithms for Water Networks (BATADAL).* Journal of Water Resources Planning and Management, 144(8), 04018048. DOI: [10.1061/(ASCE)WR.1943-5452.0000969](https://doi.org/10.1061/(ASCE)WR.1943-5452.0000969). | Benchmark Journal Article (*ASCE*) | Supports Candidate A literature context: establishes prior art on cyber-physical anomaly detection benchmarks in water distribution systems. |
| **SRC-LIT-07** | Lin, G., Kramer, H., & Granderson, J. (2020). *Assessment of fully automated HVAC fault detection and diagnostic tools in commercial buildings.* Energy and Buildings, 218, 109995. DOI: [10.1016/j.enbuild.2020.109995](https://doi.org/10.1016/j.enbuild.2020.109995). | Journal Research Article (*Elsevier*) | Confirms baseline limitations: rule-based FDD tools struggle with minor fouling, valve leaks $<20\%$, and transient operational shifts. |
| **SRC-LIT-08** | Bartolini, A., et al. (2018). *ExaMon: A Scalable Telemetry and Monitoring Framework for Exascale Supercomputers.* IEEE Transactions on Parallel and Distributed Systems. | Journal Research Article (*IEEE*) | Confirms telemetry provenance of Candidate C (Marconi A2 data collected via MQTT/InfluxDB infrastructure). |

---

## 3. Industrial Standards and Software Specifications

| Source ID | Standard / Artifact | Sponsoring Organization | Verified Claims Supported |
| :--- | :--- | :--- | :--- |
| **SRC-STD-01** | [ASHRAE Guideline 36-2021: High-Performance Sequences of Operation for HVAC Systems](https://www.ashrae.org/) | ASHRAE | Defines standard baseline sequence logic, trim-and-respond setpoint resets, and operational rules for commercial air systems. |
| **SRC-STD-02** | [Brick Schema Specification v1.2](https://brickschema.org/) | Brick Consortium | Confirms standardized metadata ontology mapping telemetry points (`RM_TEMP`, `FCU_DAT`, `FCU_CVLV`) across commercial equipment. |
| **SRC-STD-03** | [NIST 10D243 / NIST Tools for Evaluating FDD Methods](https://www.nist.gov/) | National Institute of Standards and Technology | Confirms HVACSIM+ simulation physics models and baseline commercial building operational sequences. |
