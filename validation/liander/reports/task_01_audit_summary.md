# Task 1 — Raw Data Quality and Suitability Audit
## Liander 2024 Energy Forecasting Benchmark (MV Feeder Asset Group)

**Audit Execution Timestamp (UTC):** 2026-10-31 17:27:21 UTC  
**Audited Scope:** Medium Voltage Feeders (`mv_feeder`) load measurements and versioned weather forecasts  
**Observation Period:** 2024-01-01 00:00:00 UTC to 2025-01-01 00:00:00 UTC (366 days, 35,136 nominal 15-minute intervals)  

---

### 1. Audit Objective

The objective of this Task 1 audit is to evaluate the raw file integrity, schema consistency, date coverage, continuity, statistical distributions, and version structures of all downloaded medium-voltage feeder load files and their corresponding time-versioned weather forecast files. This provides an objective empirical foundation for subsequent day-ahead operational forecasting viability assessments without making premature modelling decisions.

---

### 2. Dataset Location and Discovered Files

- **Project Root:** `.` (relative) / `D:\UrjaDrishti`
- **Load Measurements Directory:** `validation/liander/data/raw/liander2024/load_measurements/mv_feeder/`
- **Versioned Weather Directory:** `validation/liander/data/raw/liander2024/weather_forecasts_versioned/mv_feeder/`
- **Target Metadata File:** `validation/liander/data/raw/liander2024/liander2024_targets.yaml`
- **Dataset Documentation:** `validation/liander/data/raw/liander2024/README.md`

| Category | Files Found | Readable Files | Total Uncompressed Size |
|:---|:---:|:---:|:---:|
| Load Measurements (`load_measurements/mv_feeder/`) | 15 | 15 | 10.07 MB |
| Versioned Weather (`weather_forecasts_versioned/mv_feeder/`) | 15 | 15 | 118.57 MB |
| **Total Discovered** | **30** | **30** | **128.63 MB** |

---

### 3. Target Metadata and Pairing Status

- **Total Targets in YAML Metadata:** 55 (spanning 5 infrastructure groups: wind_park (5), transformer (15), mv_feeder (15), solar_park (5), station_installation (15))
- **MV Feeder Targets in Metadata:** 15
- **Load Files Discovered:** 15
- **Weather Files Discovered:** 15
- **Successfully Matched Feeder Pairs:** 15 of 15 (100.0% pairing match rate)
- **Unmatched or Unexpected Files:** 0 unmatched files. Every load and weather Parquet file corresponds exactly to a declared `mv_feeder` target in the YAML metadata.

---

### 4. Overall Load Data Observations

1. **Uniform Schema and Length:** All 15 load files share an identical Arrow schema (`timestamp: timestamp[ns, tz=UTC]`, `load: double`, `available_at: timestamp[ns, tz=UTC]`) and contain exactly 35,136 rows.
2. **Timestamp Grid Completeness:** Every feeder contains all 35,136 expected 15-minute intervals spanning 2024-01-01 00:00:00+00:00 to 2024-12-31 23:45:00+00:00 without missing timestamps or irregular intervals (100.0% timestamp grid coverage).
3. **Missing Value Uniformity:** Every single feeder exhibits exactly 3 missing (`NaN`) load values (0.0085% missingness). These 3 missing values occur at the exact same timestamps across all 15 feeders: `2024-10-27 00:15:00 UTC`, `00:30:00 UTC`, and `00:45:00 UTC` (45-minute outage directly coinciding with the European Daylight Saving Time autumn clock change).
4. **Zero Duplicates:** 0 exact duplicate rows, 0 duplicate timestamps, and 0 duplicate `(timestamp, available_at)` combinations exist across all 15 feeders.
5. **Zero Availability Delay:** For all 15 feeder load files, `available_at` equals `timestamp` for 100% of rows (0.0 hours delay).
6. **Negative Load Infeed:** 14 of 15 feeders contain negative load values. Reverse flow percentages range from 0.0% (`OS Leiden Noord`) and 1.72% (`OS Waarderpolder`) up to 31.62% (`OS Sneek`). These negative values indicate distributed generation (commercial/residential solar) backfeeding into the substation.

---

### 5. Overall Weather Observations

1. **Identical Row Counts and Horizons:** All 15 weather forecast files contain exactly 201,534 rows spanning 35,229 distinct target timestamps (2024-01-01 00:00:00 UTC through 2025-01-01 23:00:00 UTC).
2. **Forecast Lead Time Range:** Lead times (`timestamp - available_at`) range from 0.0 hours to 120.0 hours (5.0 days) with a median lead time of 48.0 hours.
3. **Version Distribution:** Across all feeders, target timestamps possess between 1 and 6 forecast versions (median: 6.0 versions, 95th percentile: 6.0 versions). 33,453 target timestamps (94.96%) have multiple versions, while 1,776 timestamps (5.04% at the beginning and end of the series) have a single version.
4. **Variable Completeness:** 10 of 11 numerical weather variables have 0 missing values (100.0% completeness).
5. **Upstream Missing Window in `wind_speed_80m`:** Exactly one variable, `wind_speed_80m`, has 13,320 null values across all 15 feeders (6.61% missingness). This missing window spans from `2024-01-19 12:00:00 UTC` to `2024-02-20 05:45:00 UTC` across all lead times, representing an upstream OpenMeteo parameter outage.
6. **Physical Plausibility:** All non-null weather values fall strictly within physically realistic bounds for the Dutch climate (temperature: -6.6°C to +34.6°C, relative humidity: 0–100%, surface pressure: 968–1039 hPa, radiation: non-negative).

---

### 6. Preliminary Feeder Comparison Highlights

The 15 feeders are ranked below using transparent, deterministic criteria (pairing status, 2024 load coverage, missingness, continuity, and weather completeness, with ties broken by shorter longest flatline duration, fewer flatline episodes, and lower reverse-flow percentage):

| Rank | Feeder Identifier | Load Status | Weather Status | 2024 Load Cov | Load Miss % | Max Gap | Weather Cov | Median Versions | Negative Load % | Flatlines (>=4h) | Major Warnings |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---|
| 1 | **OS Leiden Noord** | Readable (35,136) | Readable (201,534) | 100.00% | 0.0085% | 0.0h | 100.00% | 6.0 | 0.00% | 0 | wind_speed_80m missing: 6.6093% |
| 2 | **OS Weesp** | Readable (35,136) | Readable (201,534) | 100.00% | 0.0085% | 0.0h | 100.00% | 6.0 | 4.20% | 0 | wind_speed_80m missing: 6.6093% |
| 3 | **OS Waarderpolder** | Readable (35,136) | Readable (201,534) | 100.00% | 0.0085% | 0.0h | 100.00% | 6.0 | 1.72% | 0 | wind_speed_80m missing: 6.6093% |
| 4 | **RS Angerlo** | Readable (35,136) | Readable (201,534) | 100.00% | 0.0085% | 0.0h | 100.00% | 6.0 | 16.62% | 0 | Heavy reverse power: 16.6225% negative load; Extreme load outliers: 1259 points; wind_speed_80m missing: 6.6093% |
| 5 | **RS Roodwilligen (Duiven)** | Readable (35,136) | Readable (201,534) | 100.00% | 0.0085% | 0.0h | 100.00% | 6.0 | 9.34% | 0 | wind_speed_80m missing: 6.6093% |
| 6 | **OS Sassenheim** | Readable (35,136) | Readable (201,534) | 100.00% | 0.0085% | 0.0h | 100.00% | 6.0 | 15.44% | 1 | Flatlines: 1 episodes >= 4h (max 4.0h); Heavy reverse power: 15.4413% negative load; Extreme load outliers: 1370 points; wind_speed_80m missing: 6.6093% |
| 7 | **OS Edam** | Readable (35,136) | Readable (201,534) | 100.00% | 0.0085% | 0.0h | 100.00% | 6.0 | 16.78% | 22 | Flatlines: 22 episodes >= 4h (max 5.75h); Heavy reverse power: 16.7819% negative load; wind_speed_80m missing: 6.6093% |
| 8 | **OS Gorredijk** | Readable (35,136) | Readable (201,534) | 100.00% | 0.0085% | 0.0h | 100.00% | 6.0 | 20.95% | 1 | Flatlines: 1 episodes >= 4h (max 6.5h); Heavy reverse power: 20.9461% negative load; Extreme load outliers: 1044 points; wind_speed_80m missing: 6.6093% |
| 9 | **SS Harlingen** | Readable (35,136) | Readable (201,534) | 100.00% | 0.0085% | 0.0h | 100.00% | 6.0 | 22.96% | 159 | Flatlines: 159 episodes >= 4h (max 9.25h); Heavy reverse power: 22.9613% negative load; Extreme load outliers: 2501 points; wind_speed_80m missing: 6.6093% |
| 10 | **OS Eibergen** | Readable (35,136) | Readable (201,534) | 100.00% | 0.0085% | 0.0h | 100.00% | 6.0 | 4.59% | 1 | Flatlines: 1 episodes >= 4h (max 9.5h); wind_speed_80m missing: 6.6093% |
| 11 | **OS Naarden** | Readable (35,136) | Readable (201,534) | 100.00% | 0.0085% | 0.0h | 100.00% | 6.0 | 5.44% | 1 | Flatlines: 1 episodes >= 4h (max 10.5h); wind_speed_80m missing: 6.6093% |
| 12 | **SS Ureterp** | Readable (35,136) | Readable (201,534) | 100.00% | 0.0085% | 0.0h | 100.00% | 6.0 | 18.68% | 125 | Flatlines: 125 episodes >= 4h (max 16.0h); Heavy reverse power: 18.6776% negative load; Extreme load outliers: 1887 points; wind_speed_80m missing: 6.6093% |
| 13 | **OS Sneek** | Readable (35,136) | Readable (201,534) | 100.00% | 0.0085% | 0.0h | 100.00% | 6.0 | 31.62% | 63 | Flatlines: 63 episodes >= 4h (max 35.75h); Heavy reverse power: 31.6227% negative load; wind_speed_80m missing: 6.6093% |
| 14 | **SS Heerenveen Pim Mulier** | Readable (35,136) | Readable (201,534) | 100.00% | 0.0085% | 0.0h | 100.00% | 6.0 | 19.12% | 113 | Flatlines: 113 episodes >= 4h (max 55.0h); Heavy reverse power: 19.1159% negative load; Extreme load outliers: 840 points; wind_speed_80m missing: 6.6093% |
| 15 | **OS Watergraafsmeer** | Readable (35,136) | Readable (201,534) | 100.00% | 0.0085% | 0.0h | 100.00% | 6.0 | 1.89% | 1 | Flatlines: 1 episodes >= 4h (max 551.75h); wind_speed_80m missing: 6.6093% |

#### Key Groupings Among Feeders

- **Tier 1 (High Quality / Benchmark Candidates):**
  - `OS Leiden Noord`: 0% negative load, 0 zeros, 0 flatlines >= 4h, 0 extreme outliers. Exceptionally clean load profile.
  - `OS Waarderpolder`: Only 1.72% negative load, 0 flatlines >= 4h, 0 extreme outliers.
  - `OS Weesp`: Only 4.20% negative load, 0 flatlines >= 4h, 0 extreme outliers.
  - `RS Angerlo`: 16.62% negative load, but 0 flatlines >= 4h and strict continuity.
  - `RS Roodwilligen (Duiven)`: 9.34% negative load, 0 flatlines >= 4h, 79 extreme outliers.

- **Tier 2 (Moderate Anomalies / Reverse Flow Feeders):**
  - `OS Eibergen`, `OS Naarden`, `OS Sassenheim`, `OS Gorredijk`: 1 flatline episode each (4 to 10.5 hours duration).
  - `OS Edam`: 22 flatline episodes >= 4h (maximum flatline: 5.75 hours).

- **Tier 3 (Substantial Operational Flags / Problematic Sensors):**
  - `OS Watergraafsmeer`: Contains a severe **551.75-hour (22.98-day) frozen sensor flatline** of constant load (140,000 W) between 2024-05-19 and 2024-06-11.
  - `SS Heerenveen Pim Mulier`: Contains a **55.0-hour flatline** and 113 flatline episodes.
  - `OS Sneek`: 31.62% negative load values (11,110 intervals) and 63 flatline episodes.
  - `SS Harlingen`: 159 flatline episodes and 22.96% negative load values.
  - `SS Ureterp`: 125 flatline episodes and 18.68% negative load values.

---

### 7. Important Data-Quality Problems

1. **Sensor Freezing / Telemetry Stalls:** Feeders such as `OS Watergraafsmeer` (551.8h frozen load) and `SS Heerenveen Pim Mulier` (55.0h frozen load) show prolonged periods where measurement values remained frozen at a fixed reading. Operational forecasting models must incorporate detection or imputation flags for telemetry freezing.
2. **Negative Power Flow (Solar Infeed):** 14 of 15 feeders experience reverse power flow during peak daytime hours, reflecting solar rooftop generation. Net load forecasting must accommodate bidirectionality.
3. **Missing Weather Variable (`wind_speed_80m`):** The 32-day gap (Jan 19 – Feb 20, 2024) in `wind_speed_80m` means models cannot rely on 80m wind speed as an unconditioned predictor across the full year without imputation or omitting this feature.
4. **DST Transition Outage:** The 3 missing intervals on 2024-10-27 indicate that timestamp conversion or telemetry logging was interrupted during daylight saving time adjustment.

---

### 8. Unmatched Files and Missing Data

- **Unmatched Files:** 0. All 15 load files have corresponding weather forecast files.
- **Missing Target Files:** 0. All 15 `mv_feeder` targets defined in `liander2024_targets.yaml` have complete load and weather Parquet files.
- **Missing Intervals in 2024 Grid:** 0. All 35,136 expected 15-minute timestamps are present in the load index.

---

### 9. Data Source, Licensing, and Attribution Notes

- **Dataset Title:** Liander 2024 Short Term Energy Forecasting Benchmark
- **Curator:** OpenSTEF (Open Short Term Energy Forecasting)
- **Overall License:** Creative Commons Attribution 4.0 International (CC BY 4.0)
- **Components & Sources:**
  1. **Liander Operational Measurements:** Liander Open Data (15-minute historical operational measurements). Governed by Liander Open Data disclaimer. Coordinates are approximate; data is provided as-is without operational warranty.
  2. **OpenMeteo Weather Forecasts:** Licensed under CC BY 4.0. Weather forecasts simulated across 7-day horizons and interpolated to 15-minute resolution.
  3. **ENTSO-E Electricity Prices & Energiedatawijzer Profiles:** Excluded from Task 1 audit scope as instructed.
- **Legal Disclaimer Summary:** Liander disclaims liability for commercial or operational reliance on open operational telemetry. Formal institutional clearance recommended prior to production deployment.

---

### 10. Checks That Could Not Be Completed

- **Operational Forecast Availability Cutoff Check:** In accordance with Task 1 instructions, weather coverage was audited purely for raw timestamp presence across any version. Operational availability at D-1 06:00 UTC will be rigorously evaluated in Task 2.
- **Non-Feeder Asset Groups:** In accordance with instructions, other asset groups (`transformer`, `station_installation`, `solar_park`, `wind_park`) were excluded from audit calculations.

---

### 11. Limitations of This Audit

1. **Timestamp Uniformity vs Value Validity:** A 100% timestamp coverage does not imply 100% measurement validity, as evidenced by frozen flatlines (`OS Watergraafsmeer`) and DST nulls.
2. **Raw Parquet vs Operational Feasibility:** The presence of up to 6 weather versions per target timestamp requires strict temporal join logic (`asof` join on `available_at <= cutoff`) before any model can use them without data leakage.
3. **Physical Feeder Topology Uninspected:** Asset names and geographic coordinates provided in the metadata are approximate, and electrical network topologies (feeder length, customer mix) are not provided in the raw dataset.

---
*Report generated automatically by `validation/liander/scripts/task_01_data_audit.py`.*
