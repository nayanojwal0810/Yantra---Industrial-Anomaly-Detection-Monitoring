# Task 2 — Operational Forecast Availability and Data-Leakage Feasibility Audit
## Liander 2024 Energy Forecasting Benchmark (MV Feeder Asset Group)

**Audit Execution Timestamp (UTC):** 2026-10-31 17:49:16 UTC  
**Target Asset Group:** Medium Voltage Feeders (`mv_feeder`, 15 feeders)  
**Evaluation Period:** 2024-01-01 through 2024-12-31 (366 days, 5,490 feeder-days evaluated)  

---

### 1. Objective

The objective of Task 2 is to test whether the Liander 2024 dataset can support a realistic next-day operational electricity load forecast using **strictly information available by the forecast issue time**. Unlike raw file-level coverage audited in Task 1, this audit enforces operational time-travel boundaries, evaluates time-versioned weather forecast vintages, tests historical load lag availability, checks evaluation target labels, and rigorously validates that zero data leakage occurs.

---

### 2. Operational Forecast Protocol

Throughout this audit, the following fixed operational protocol is applied:
- **Target Day D:** Every calendar day in 2024 (`2024-01-01` to `2024-12-31`, 366 days).
- **Issue Time:** `D - 1 calendar day + 06:00:00 UTC`.
- **Target Period:** `D 00:00:00 UTC <= timestamp <= D 23:45:00 UTC` (96 intervals of 15 minutes each).
- **Forecast Horizon:**
  - Earliest target interval ($D\text{ 00:00 UTC}$): **18.0 hours** lead time from issue time.
  - Latest target interval ($D\text{ 23:45 UTC}$): **41.75 hours** (41h 45m) lead time from issue time.
- **Availability Filter:**
  - For weather forecasts: `available_at <= issue_time`.
  - For historical load inputs: `timestamp <= issue_time` AND `available_at <= issue_time`.
- **Target Labels:** Actual load values for day $D$ are evaluation targets only and are never permitted in the input feature space.

---

### 3. How As-Of Weather Selection Was Performed

1. For each feeder and each target day $D$, the 96 expected target timestamps are constructed.
2. All weather records corresponding to those 96 timestamps are extracted from the feeder's versioned weather Parquet file.
3. Every record where `available_at > issue_time` is strictly filtered out.
4. For each target timestamp, the record with the maximum `available_at` $\le \text{issue\_time}$ is selected (the most recent forecast published prior to the 06:00 UTC cutoff).
5. The selection is explicitly verified to ensure: (a) zero future leakage (`available_at <= issue_time`), (b) latest eligible version selected, and (c) exactly one version per target interval.

---

### 4. Operational Weather Availability Findings

| Metric | Total Count / Intervals | Percentage | Operational Meaning |
|:---|:---:|:---:|:---|
| Evaluated Feeder-Days | 5490 | 100.0% | 15 feeders $\times$ 366 target days in 2024 |
| Weather Core Complete Days (10 vars) | 5190 | 94.54% | All 96 intervals have eligible forecast with 10 core vars |
| Weather All-11 Complete Days (incl. ws80m) | 4785 | 87.16% | All 96 intervals have eligible forecast with all 11 vars |
| Weather Target Interval Coverage (10 vars) | 499335 / 527040 | 94.74% | Percentage of 15-minute target intervals with valid core forecast |

#### Key Findings on Weather Vintages:
1. **Initial Warm-up Gap (Jan 1 – Jan 19, 2024):**
   For target days between `2024-01-01` and `2024-01-19` (19 days), **zero eligible advance forecasts exist** at $D-1\text{ 06:00 UTC}$. In the raw dataset, weather records for these early dates have `available_at == timestamp` (0-hour advance notice, published post-facto or simultaneously with the event). Because their `available_at` is after the $D-1\text{ 06:00 UTC}$ cutoff, they cannot be used operationally.
2. **Partial Transition Day (Jan 20, 2024):**
   On `2024-01-20`, exactly 73 of 96 intervals (after 12:00 UTC) possess an eligible advance forecast. Intervals between 06:15 and 11:45 UTC (23 intervals) are unavailable.
3. **Complete Continuous Availability (Jan 21 – Dec 31, 2024):**
   From `2024-01-21` through `2024-12-31` (346 consecutive calendar days), **100.0% of target days and 100.0% of 15-minute intervals (33,216 intervals per feeder)** have an eligible, complete advance forecast for all 10 core weather variables.
4. **Impact of `wind_speed_80m` Missing Window:**
   Between `2024-01-20` and `2024-02-20` (27 days after advance forecasts began), `wind_speed_80m` is null across all lead times. As a result, complete all-11-variable days total 319 days (87.16%) compared to 346 core-complete days (94.54%).

---

### 5. Historical Load Availability Findings

| Lag Feature | Complete Days (96/96) | Percentage | Usability and Diagnostic Observations |
|:---|:---:|:---:|:---|
| Seven-day lag ($t - 7\text{d}$) | 5370 / 5490 | 97.81% | 358 complete days per feeder. 7 initial warm-up days (Jan 1-7) missing because 2023 data is absent. 1 day (Nov 3) partial due to Oct 27 DST nulls. |
| Fourteen-day lag ($t - 14\text{d}$) | 5265 / 5490 | 95.90% | 351 complete days per feeder. 14 initial warm-up days missing. 1 day (Nov 10) partial. |
| One-day lag ($t - 1\text{d}$, Diagnostic) | 0 / 5490 | 0.00% | **0 full days possible.** At $D-1\text{ 06:00 UTC}$, only 25 intervals (00:00 to 06:00 UTC) have occurred; the remaining 71 intervals are future unobserved data. |

#### Most Recent Historical Load Observation:
- Across all feeders and days, the most recent available load measurement at $D-1\text{ 06:00:00 UTC}$ is the measurement at $D-1\text{ 06:00:00 UTC}$.
- **Age of observation at issue time:** **0.0 minutes** (median across all days).
- This confirms that the most recently logged load value at issue time is current and aligned with the 15-minute telemetry interval.

---

### 6. Target Label Quality Findings

- **Fully Complete Actual Target Days:** **5475 of 5490 feeder-days (99.73%)**.
- Per feeder: Exactly **365 of 366 days (99.73%)** have all 96 actual load values present, finite, and valid.
- **Affected Day and Timestamps:**
  - The single partial target day across all 15 feeders is **`2024-10-27`** (Daylight Saving Time autumn transition).
  - On `2024-10-27`, exactly 3 intervals are missing: `00:15:00 UTC`, `00:30:00 UTC`, and `00:45:00 UTC` (93 valid values out of 96).

---

### 7. Leakage and Vintage Verification Results

Every single selected weather record and historical load observation was subjected to explicit automated assertion checks:

| Verification Assertion | Violation Count | Status | Description |
|:---|:---:|:---:|:---|
| Future weather availability (`available_at > issue_time`) | **0** | **PASSED** | Zero future forecast records were selected. |
| Non-latest eligible version selections | **0** | **PASSED** | Selected version was strictly the latest eligible vintage published prior to cutoff. |
| Duplicate selected timestamps | **0** | **PASSED** | Exactly one forecast version selected per target interval. |
| Historical load cutoff violations (`timestamp > issue_time` or `available_at > issue_time`) | **0** | **PASSED** | Zero future load measurements included in historical inputs. |
| Target label leakage into inputs | **0** | **PASSED** | Target load labels were strictly isolated as future evaluation labels. |

---

### 8. Feeder-Level Availability Summary and Ranking

The 15 feeders are compared below based on transparent operational criteria (zero leakage, weather completeness, 7-day lag readiness, and target completeness):

| Feeder Identifier | Core Weather Days | Core Weather Cov | 7d Lag Days | Complete Target Days | Input-Ready Days | Fully Evaluable Days | Leakage Violations | Most Recent Age |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **OS Leiden Noord** | 346/366 (94.5%) | 94.74% | 358/366 (97.8%) | 365/366 (99.7%) | 345/366 (94.3%) | 344/366 (94.0%) | 0 | 0.0 min |
| **OS Weesp** | 346/366 (94.5%) | 94.74% | 358/366 (97.8%) | 365/366 (99.7%) | 345/366 (94.3%) | 344/366 (94.0%) | 0 | 0.0 min |
| **OS Waarderpolder** | 346/366 (94.5%) | 94.74% | 358/366 (97.8%) | 365/366 (99.7%) | 345/366 (94.3%) | 344/366 (94.0%) | 0 | 0.0 min |
| **RS Roodwilligen (Duiven)** | 346/366 (94.5%) | 94.74% | 358/366 (97.8%) | 365/366 (99.7%) | 345/366 (94.3%) | 344/366 (94.0%) | 0 | 0.0 min |
| **RS Angerlo** | 346/366 (94.5%) | 94.74% | 358/366 (97.8%) | 365/366 (99.7%) | 345/366 (94.3%) | 344/366 (94.0%) | 0 | 0.0 min |
| **OS Eibergen** | 346/366 (94.5%) | 94.74% | 358/366 (97.8%) | 365/366 (99.7%) | 345/366 (94.3%) | 344/366 (94.0%) | 0 | 0.0 min |
| **OS Naarden** | 346/366 (94.5%) | 94.74% | 358/366 (97.8%) | 365/366 (99.7%) | 345/366 (94.3%) | 344/366 (94.0%) | 0 | 0.0 min |
| **OS Watergraafsmeer** | 346/366 (94.5%) | 94.74% | 358/366 (97.8%) | 365/366 (99.7%) | 345/366 (94.3%) | 344/366 (94.0%) | 0 | 0.0 min |
| **OS Sassenheim** | 346/366 (94.5%) | 94.74% | 358/366 (97.8%) | 365/366 (99.7%) | 345/366 (94.3%) | 344/366 (94.0%) | 0 | 0.0 min |
| **OS Edam** | 346/366 (94.5%) | 94.74% | 358/366 (97.8%) | 365/366 (99.7%) | 345/366 (94.3%) | 344/366 (94.0%) | 0 | 0.0 min |
| **OS Gorredijk** | 346/366 (94.5%) | 94.74% | 358/366 (97.8%) | 365/366 (99.7%) | 345/366 (94.3%) | 344/366 (94.0%) | 0 | 0.0 min |
| **SS Harlingen** | 346/366 (94.5%) | 94.74% | 358/366 (97.8%) | 365/366 (99.7%) | 345/366 (94.3%) | 344/366 (94.0%) | 0 | 0.0 min |
| **SS Ureterp** | 346/366 (94.5%) | 94.74% | 358/366 (97.8%) | 365/366 (99.7%) | 345/366 (94.3%) | 344/366 (94.0%) | 0 | 0.0 min |
| **OS Sneek** | 346/366 (94.5%) | 94.74% | 358/366 (97.8%) | 365/366 (99.7%) | 345/366 (94.3%) | 344/366 (94.0%) | 0 | 0.0 min |
| **SS Heerenveen Pim Mulier** | 346/366 (94.5%) | 94.74% | 358/366 (97.8%) | 365/366 (99.7%) | 345/366 (94.3%) | 344/366 (94.0%) | 0 | 0.0 min |

#### Cross-Feeder Diagnostic Highlights:
1. **Uniform Operational Usability:**
   All 15 feeders exhibit identical operational day-ahead availability metrics: **346 core weather days (94.54%)**, **358 7-day lag days (97.81%)**, **365 complete target days (99.73%)**, **345 input-ready days (94.26%)**, and **344 fully evaluable days (93.99%)**.
2. **The Evaluability Boundary:**
   The 22 non-evaluable days (366 - 344) consist of:
   - Days 1 to 19 (`2024-01-01` to `2024-01-19`): Zero eligible advance weather forecasts exist.
   - Day 20 (`2024-01-20`): Partial weather day (73 of 96 intervals available).
   - Day 301 (`2024-10-27`): Partial target load day (3 DST missing values).
   - Day 308 (`2024-11-03`): Partial 7-day lag day (lag points to `2024-10-27`).
3. **Differentiation Between Feeders (from Task 1 & Task 2):**
   While calendar availability metrics are identical across feeders, internal load characteristics distinguish benchmark viability:
   - **Recommended Primary Candidates:**
     - `OS Leiden Noord`: 0.0% reverse power, 0 flatlines $\ge 4\text{h}$, 0 extreme outliers. Exceptional signal quality.
     - `OS Waarderpolder`: Only 1.72% negative load, 0 flatlines $\ge 4\text{h}$, 0 extreme outliers.
     - `OS Weesp`: Only 4.20% negative load, 0 flatlines $\ge 4\text{h}$, 0 extreme outliers.
   - **Feeders with Severe Telemetry Pathology:**
     - `OS Watergraafsmeer`: Contains a 22.98-day frozen sensor flatline (May 19 – June 11) despite 100% timestamp availability.
     - `SS Heerenveen Pim Mulier`: Contains a 55.0-hour flatline and 113 flatline episodes.
     - `OS Sneek`: 31.62% negative load (severe distributed generation backfeed).

---

### 9. Important Limitations

1. **No Operational Advance Forecasts in Early January:** Any benchmark model requiring day-ahead weather forecasts cannot be evaluated prior to `2024-01-21` without synthetic imputation or using non-operational forecasts.
2. **One-Day Lag Impossibility at D-1 06:00 UTC:** Forecasters cannot use yesterday's afternoon/evening load ($t - 24\text{h}$) to predict today's afternoon/evening load without violating operational time travel.
3. **Missing `wind_speed_80m` Period:** Models that treat 80m wind speed as an indispensable feature will experience an outage from Jan 20 to Feb 20, 2024.

---

### 10. Checks That Could Not Be Completed

- **Non-Feeder Infrastructure Groups:** Transformers, solar parks, wind parks, and station installations were excluded from calculations per scope instructions.
- **Model Training & Feature Evaluation:** In accordance with Task 2 exclusions, no LightGBM or statistical model was trained, and no hyperparameters or error metrics (MAE/RMSE) were evaluated.

---
*Report generated automatically by `validation/liander/scripts/task_02_operational_availability.py`.*
