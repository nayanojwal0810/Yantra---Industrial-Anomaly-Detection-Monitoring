# USAspending Downloaded Sample Audit and Transaction Coverage Report

## Executive Summary
This report audits the real USAspending ZIP export downloaded from the official website UI and placed in the project repository. It evaluates file integrity, schema consistency, award-to-transaction linkage, date coverage, and count reconciliation against the website download dialog.

- **ZIP Archive**: `PrimeAwardSummariesAndTransactions_2026-10-27_H21M56S49644703.zip`
- **Archive Size**: 122,643 bytes
- **SHA-256**: `9b4abc45db0e617b0ee1aea80e74ff0e88da86beac3666c2bbe5c4a6096d39cd`
- **Award Summaries Count**: 221 data rows (286 columns)
- **Prime Transactions Count**: 390 data rows (297 columns)
- **Referential Integrity**: 100.0% of transactions link to award summaries via `contract_award_unique_key` with 0 unmatched keys.
- **Count Discrepancy Status**: **UNRESOLVED** (Website displayed 1,384 transactions vs. 390 rows in downloaded CSV).

---

## 1. Archive Inventory and File Dimensions

| Member Name | Type | Compressed Size | Uncompressed Size | Data Rows | Columns |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Contracts_PrimeAwardSummaries_2026-10-27_H21M56S50_1.csv` | Award Summaries CSV | 51,553 bytes | 508,715 bytes | 221 | 286 |
| `Contracts_PrimeTransactions_2026-10-27_H21M56S56_1.csv` | Prime Transactions CSV | 70,696 bytes | 1,003,722 bytes | 390 | 297 |

---

## 2. Identifier Uniqueness and Linkage

### Primary Identifiers
- **Award Unique Key (`contract_award_unique_key`)**:
  - Total records: 221
  - Unique keys: 221 (100.0% unique)
  - Missing values: 0
- **Award PIID (`award_id_piid`)**:
  - Unique PIIDs: 221 (100.0% unique in this sample)
  - Missing values: 0
- **Transaction Unique Key (`contract_transaction_unique_key`)**:
  - Total records: 390
  - Unique keys: 390 (100.0% unique)
  - Missing values: 0

### Award-to-Transaction Linkage
- **Join Key**: `contract_award_unique_key`
- **Unmatched Transaction Keys**: 0 (0.0% unmatched)
- **Awards with Zero Transactions**: 0 (0.0% unlinked; all 221 awards have at least one transaction row)
- **Transactions Per Award**: Min = 1, Median = 1, Max = 21

#### Transactions per Award Distribution
| Transactions per Award | Number of Awards |
| :--- | :--- |
| 1 | 150 |
| 2 | 43 |
| 3 | 8 |
| 4 | 9 |
| 5 | 3 |
| 6 | 1 |
| 7 | 3 |
| 8 | 1 |
| 10 | 1 |
| 13 | 1 |
| 21 | 1 |

---

## 3. Date Coverage and Fiscal Year Analysis

### Award Base Action Dates
- **Min Base Action Date**: `2019-10-08`
- **Max Base Action Date**: `2020-09-30`
- **Fiscal Year Distribution**: 100.0% FY2020 (221 / 221).

### Award Latest Action Dates
- **Min Latest Action Date**: `2019-10-15`
- **Max Latest Action Date**: `2026-10-06`
- **Fiscal Year Distribution**:
| Fiscal Year | Awards Count |
| :--- | :--- |
| FY2020 | 82 (37.1%) |
| FY2021 | 42 (19.0%) |
| FY2022 | 42 (19.0%) |
| FY2023 | 23 (10.4%) |
| FY2024 | 12 (5.4%) |
| FY2025 | 7 (3.2%) |
| FY2026 | 12 (5.4%) |
| FY2027 | 1 (0.5%) |

> **Observation**: 139 out of 221 awards (62.9%) experienced subsequent modifications or actions in FY2021 through FY2027, with the latest action recorded on `2026-10-06`.

### Transaction Action Dates
- **Min Action Date**: `2019-10-08`
- **Max Action Date**: `2020-09-30`
- **Fiscal Year Distribution**: 100.0% FY2020 (390 / 390).
- **Post-FY2020 Transactions Present**: **0**
- **Pre-FY2020 Transactions Present**: **0**

> **Finding**: While the award summaries demonstrate that the awards had active modifications well into FY2026/FY2027, the transaction file contains **only FY2020 transactions**. It does **not** contain the later-year transactions corresponding to `award_latest_action_date`.

---

## 4. Filter Compliance Verification

| Dimension | Filter Requirement | Award Summary Conformance | Transaction Conformance | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Awarding Agency** | NASA | 221/221 (100.0%) | 390/390 (100.0%) | FULL COMPLIANCE |
| **NAICS** | 541330 (Engineering Services) | 221/221 (100.0%) | 390/390 (100.0%) | FULL COMPLIANCE |
| **Time Period** | FY2020 New Awards | 221 Base Action Dates in FY2020 | 390 Action Dates in FY2020 | FULL COMPLIANCE |

---

## 5. Amount Fields and Statistics

Cumulative award totals must not be conflated with discrete transaction obligations.

### Award Summary Dollar Fields
| Metric | `total_obligated_amount` | `current_total_value_of_award` | `potential_total_value_of_award` |
| :--- | :--- | :--- | :--- |
| **Total Populated** | 221 | 221 | 221 |
| **Missing** | 0 | 0 | 0 |
| **Zero Values** | 5 | 5 | 5 |
| **Negative Values** | 0 | 0 | 0 |
| **Minimum** | $0.00 | $0.00 | $0.00 |
| **Median** | $175,531.26 | $175,531.26 | $175,531.26 |
| **Maximum** | $104,034,311.50 | $104,304,311.50 | $104,304,311.50 |

### Transaction Dollar Fields
| Metric | `federal_action_obligation` |
| :--- | :--- |
| **Total Populated** | 390 |
| **Missing** | 0 |
| **Zero Values** | 58 (Administrative / no-cost actions) |
| **Negative Values** | 13 (Deobligations) |
| **Positive Values** | 319 |
| **Minimum** | -$1,265,976.15 |
| **Median** | $93,441.50 |
| **Maximum** | $11,257,021.81 |

---

## 6. Discrepancy Reconciliation (Website Declared vs. Downloaded CSV)

| Entity | Website Dialog Declared | Actual Downloaded CSV | Discrepancy | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Awards** | 221 | 221 | 0 | MATCHED (Exact) |
| **Transactions** | 1384 | 390 | -994 | **UNRESOLVED** |

### Evidence-Based Assessment
1. The website download dialog displayed `Awards: 221 records` and `Transactions: 1,384 records`.
2. The downloaded award summary CSV contains exactly 221 records, matching the displayed count.
3. The downloaded transaction CSV contains 390 records. All 390 records have action dates strictly within FY2020.
4. Award summary records show that 139 awards had subsequent actions through FY2027.
5. **Conclusion**: The reason why the website dialog showed 1,384 transactions while the downloaded CSV contains 390 transactions is **UNRESOLVED**. Plausible explanations include (a) the website dialog estimated all historical transactions for the 221 awards while the download endpoint applied the FY2020 action date filter, or (b) another backend counting distinction. In accordance with safety rules, no conclusion is assumed without direct API documentation or server confirmation.

---

## 7. Top Missing Schema Columns

### Award Summaries (Top Missing Fields)
| Column | Missing Count | Missing Pct |
| :--- | :--- | :--- |
| `outlayed_amount_from_IIJA_supplemental` | 221 | 100.0% |
| `obligated_amount_from_IIJA_supplemental` | 221 | 100.0% |
| `ordering_period_end_date` | 221 | 100.0% |
| `sam_exception` | 221 | 100.0% |
| `sam_exception_description` | 221 | 100.0% |
| `idv_type_code` | 221 | 100.0% |
| `idv_type` | 221 | 100.0% |
| `multiple_or_single_award_idv_code` | 221 | 100.0% |
| `multiple_or_single_award_idv` | 221 | 100.0% |
| `type_of_idc_code` | 221 | 100.0% |

### Prime Transactions (Top Missing Fields)
| Column | Missing Count | Missing Pct |
| :--- | :--- | :--- |
| `outlayed_amount_from_IIJA_supplemental_for_overall_award` | 390 | 100.0% |
| `obligated_amount_from_IIJA_supplemental_for_overall_award` | 390 | 100.0% |
| `ordering_period_end_date` | 390 | 100.0% |
| `sam_exception` | 390 | 100.0% |
| `sam_exception_description` | 390 | 100.0% |
| `idv_type_code` | 390 | 100.0% |
| `idv_type` | 390 | 100.0% |
| `multiple_or_single_award_idv_code` | 390 | 100.0% |
| `multiple_or_single_award_idv` | 390 | 100.0% |
| `type_of_idc_code` | 390 | 100.0% |

---

## 8. Data Feasibility Assessment

### Schema Validation: **SUFFICIENT**
The downloaded data successfully verifies the official USAspending file structure:
- Consistent multi-column schemas (286 columns for award summaries, 297 columns for prime transactions).
- Reliable join key (`contract_award_unique_key`) providing 100% referential linkage between transactions and award summaries.
- Valid representation of core recompete metadata: agency codes, NAICS codes, action dates, performance periods, and monetary amounts.

### Successor Matching / Recompete Feasibility: **INSUFFICIENT**
This dataset is **strictly insufficient** to establish feasibility of recompete successor matching:
- **Scope Limitation**: Limited to a single awarding agency (NASA), a single NAICS code (541330), and awards initiated in FY2020.
- **Truncated Transaction History**: Transactions are strictly restricted to FY2020 actions. Post-FY2020 modifications and follow-on awards are absent from this export.
- **Cohort Representation**: The eventual Sanket cohort requires combining multiple NAICS families, IT PSCs, and PSC R families with historical dollar thresholds. This pilot does not represent that full population.
