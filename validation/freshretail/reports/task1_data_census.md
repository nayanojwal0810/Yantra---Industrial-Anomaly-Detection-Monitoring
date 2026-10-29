# FreshRetailNet-50K Data Integrity and Schema Census Report

- **Task:** TASK 1 — FreshRetailNet-50K Data Integrity and Schema Census
- **Execution Timestamp:** `2026-10-29T22:30:03.668945+00:00`
- **Validation Decision:** **PASS**
- **Git Branch:** `project1/freshretail-validation`

---

## 1. Executive Summary

| Check Item | Training Set (`train.parquet`) | Evaluation Set (`eval.parquet`) | Status |
|:---|:---|:---|:---|
| **File Existence** | Present (`D:\Aarohan\data\raw\train.parquet`) | Present (`D:\Aarohan\data\raw\eval.parquet`) | PASS |
| **File Size** | 106,436,287 bytes (101.51 MiB) | 8,440,124 bytes (8.05 MiB) | PASS |
| **SHA-256 Checksum** | `6706832db892bbae4969c19d87e07975d2543d2ba7d7d4756360654785de5a3d` | `1b118840664280c6b88bffc84c80ee1f54c05d911e354b7599e5da10995e960e` | PASS (Matches Official HuggingFace LFS) |
| **Parquet Validity** | Valid (4500 row groups) | Valid (350 row groups) | PASS |
| **Row Count** | 4,500,000 rows (documented: 4,500,000) | 350,000 rows (documented: 350,000) | PASS |
| **Column Count** | 19 columns | 19 columns | PASS |
| **Missing Values** | 0 nulls across all 19 columns (0.00%) | 0 nulls across all 19 columns (0.00%) | PASS |
| **Documented Grain Key** | `(store_id, product_id, dt)` | `(store_id, product_id, dt)` | PASS |
| **Duplicate Grain Rows** | 0 duplicate keys (0.00%) | 0 duplicate keys (0.00%) | PASS |
| **Date Span** | 2024-03-28 to 2024-06-25 (90 consecutive days) | 2024-06-26 to 2024-07-02 (7 consecutive days) | PASS |
| **Store-Product Series** | 50,000 unique series | 50,000 unique series | PASS (100% matched across splits) |
| **Stockout Representation** | Binary hourly flags (0=in-stock, 1=out-of-stock) | Binary hourly flags (0=in-stock, 1=out-of-stock) | PASS |
| **Daytime Stockout Rate** | 19.88% of operating hours (06:00-22:00) | 18.11% of operating hours (06:00-22:00) | PASS (Consistent with documented ~20%) |

**Overall Status Assessment:** **PASS**

Both dataset files demonstrate complete byte integrity, match official Hugging Face Git LFS checksums exactly, exhibit valid Parquet structure, match all documented schema definitions, possess zero missing values or duplicate keys, and conform strictly to the documented chronological forward evaluation split.

---

## 2. Environment and Input File Details

### Python and Library Versions
- **Python Version:** `3.13.3`
- **Pandas Version:** `3.0.3`
- **PyArrow Version:** `24.0.0`
- **Platform:** `win32`

### Input File Metadata and Provenance
- **Dataset Name:** FreshRetailNet-50K
- **Source Repository:** [https://huggingface.co/datasets/Dingdong-Inc/FreshRetailNet-50K](https://huggingface.co/datasets/Dingdong-Inc/FreshRetailNet-50K)
- **Dataset License:** Creative Commons Attribution 4.0 International (CC BY 4.0)
- **Data Developer:** Dingdong-Inc
- **Version:** 1.0 (2025-05-08)
- **Attribution Citation:**
```bibtex
@article{2025freshretailnet-50k,
  title={FreshRetailNet-50K: A Stockout-Annotated Censored Demand Dataset for Latent Demand Recovery and Forecasting in Fresh Retail},
  author={Yangyang Wang, Jiawei Gu, Li Long, Xin Li, Li Shen, Zhouyu Fu, Xiangjun Zhou, Xu Jiang},
  year={2025},
  eprint={2505.16319},
  archivePrefix={arXiv},
  primaryClass={cs.LG},
  url={https://arxiv.org/abs/2505.16319}
}
```

*Disclaimer: This report constitutes a technical data integrity and schema census performed on local files, not an independent certification of proprietary data ownership or commercial licensing permissions.*

| Property | `train.parquet` | `eval.parquet` |
|:---|:---|:---|
| Expected Path | `data\raw\train.parquet` | `data\raw\eval.parquet` |
| Actual Path Used | `D:\Aarohan\data\raw\train.parquet` | `D:\Aarohan\data\raw\eval.parquet` |
| File Size (Bytes) | 106,436,287 | 8,440,124 |
| File Size (MiB) | 101.51 MiB | 8.05 MiB |
| Calculated SHA-256 | `6706832db892bbae4969c19d87e07975d2543d2ba7d7d4756360654785de5a3d` | `1b118840664280c6b88bffc84c80ee1f54c05d911e354b7599e5da10995e960e` |
| Official LFS SHA-256 | `6706832db892bbae4969c19d87e07975d2543d2ba7d7d4756360654785de5a3d` | `1b118840664280c6b88bffc84c80ee1f54c05d911e354b7599e5da10995e960e` |
| Checksum Verified | **PASS** (Exact Match) | **PASS** (Exact Match) |
| Parquet Read Errors | None | None |

---

## 3. Schema and Required-Field Mapping

All 19 documented fields from the official FreshRetailNet-50K data card are present with exact schema compatibility:

| Field Name | Documented Type | Observed Physical Type | Documented Concept | Status |
|:---|:---|:---|:---|:---|
| `city_id` | int64 | `int64` | Store/Location Identifier | PASS |
| `store_id` | int64 | `int64` | Store/Location Identifier | PASS |
| `management_group_id` | int64 | `int64` | Merchandising Category Hierarchy | PASS |
| `first_category_id` | int64 | `int64` | Product Category Level 1 | PASS |
| `second_category_id` | int64 | `int64` | Product Category Level 2 | PASS |
| `third_category_id` | int64 | `int64` | Product Category Level 3 | PASS |
| `product_id` | int64 | `int64` | Product SKU Identifier | PASS |
| `dt` | string | `string` | Calendar Date (ISO 8601 `YYYY-MM-DD`) | PASS |
| `sale_amount` | float64 | `double` | Normalized Daily Sales Quantity | PASS |
| `hours_sale` | Sequence(float64) | `list<element: double>` | Normalized Hourly Sales (24 elements) | PASS |
| `stock_hour6_22_cnt` | int32 | `int32` | Out-of-Stock Hours Count in [06:00, 22:00) | PASS |
| `hours_stock_status` | Sequence(int32) | `list<element: int64>` | Hourly Stockout Status (24 elements) | PASS |
| `discount` | float64 | `double` | Promotion Discount Ratio | PASS |
| `holiday_flag` | int32 | `int32` | Calendar Holiday Binary Indicator | PASS |
| `activity_flag` | int32 | `int32` | Commercial Activity Binary Indicator | PASS |
| `precpt` | float64 | `double` | Weather Context (Precipitation) | PASS |
| `avg_temperature` | float64 | `double` | Weather Context (Temperature) | PASS |
| `avg_humidity` | float64 | `double` | Weather Context (Humidity) | PASS |
| `avg_wind_level` | float64 | `double` | Weather Context (Wind Force) | PASS |

*Note: In the Parquet physical schema, `hours_stock_status` is serialized as `list<element: int64>`, which is functionally equivalent and completely compatible with the documented Sequence(int32).*

### Sanitized 5-Row Data Preview (`train.parquet`)
```json
[
  {
    "city_id": 0,
    "store_id": 0,
    "management_group_id": 0,
    "first_category_id": 5,
    "second_category_id": 6,
    "third_category_id": 65,
    "product_id": 38,
    "dt": "2024-03-28",
    "sale_amount": 0.1,
    "hours_sale": "[len 24: [np.float64(0.0), np.float64(0.0), np.float64(0.0)]...[np.float64(0.0), np.float64(0.0), np.float64(0.0)]]",
    "stock_hour6_22_cnt": 0,
    "hours_stock_status": "[len 24: [np.int64(0), np.int64(0), np.int64(0)]...[np.int64(0), np.int64(0), np.int64(0)]]",
    "discount": 1.0,
    "holiday_flag": 0,
    "activity_flag": 0,
    "precpt": 1.6999,
    "avg_temperature": 15.48,
    "avg_humidity": 73.54,
    "avg_wind_level": 1.97
  },
  {
    "city_id": 0,
    "store_id": 0,
    "management_group_id": 0,
    "first_category_id": 5,
    "second_category_id": 6,
    "third_category_id": 65,
    "product_id": 38,
    "dt": "2024-03-29",
    "sale_amount": 0.1,
    "hours_sale": "[len 24: [np.float64(0.0), np.float64(0.0), np.float64(0.0)]...[np.float64(0.0), np.float64(0.0), np.float64(0.0)]]",
    "stock_hour6_22_cnt": 1,
    "hours_stock_status": "[len 24: [np.int64(0), np.int64(0), np.int64(0)]...[np.int64(1), np.int64(1), np.int64(1)]]",
    "discount": 1.0,
    "holiday_flag": 0,
    "activity_flag": 0,
    "precpt": 3.019,
    "avg_temperature": 15.08,
    "avg_humidity": 76.56,
    "avg_wind_level": 1.71
  },
  {
    "city_id": 0,
    "store_id": 0,
    "management_group_id": 0,
    "first_category_id": 5,
    "second_category_id": 6,
    "third_category_id": 65,
    "product_id": 38,
    "dt": "2024-03-30",
    "sale_amount": 0.0,
    "hours_sale": "[len 24: [np.float64(0.0), np.float64(0.0), np.float64(0.0)]...[np.float64(0.0), np.float64(0.0), np.float64(0.0)]]",
    "stock_hour6_22_cnt": 0,
    "hours_stock_status": "[len 24: [np.int64(1), np.int64(1), np.int64(1)]...[np.int64(0), np.int64(0), np.int64(0)]]",
    "discount": 1.0,
    "holiday_flag": 1,
    "activity_flag": 0,
    "precpt": 2.0942,
    "avg_temperature": 15.91,
    "avg_humidity": 76.47,
    "avg_wind_level": 1.73
  },
  {
    "city_id": 0,
    "store_id": 0,
    "management_group_id": 0,
    "first_category_id": 5,
    "second_category_id": 6,
    "third_category_id": 65,
    "product_id": 38,
    "dt": "2024-03-31",
    "sale_amount": 0.1,
    "hours_sale": "[len 24: [np.float64(0.0), np.float64(0.0), np.float64(0.0)]...[np.float64(0.0), np.float64(0.0), np.float64(0.0)]]",
    "stock_hour6_22_cnt": 11,
    "hours_stock_status": "[len 24: [np.int64(0), np.int64(0), np.int64(0)]...[np.int64(1), np.int64(1), np.int64(1)]]",
    "discount": 1.0,
    "holiday_flag": 1,
    "activity_flag": 0,
    "precpt": 1.5618,
    "avg_temperature": 16.13,
    "avg_humidity": 77.4,
    "avg_wind_level": 1.76
  },
  {
    "city_id": 0,
    "store_id": 0,
    "management_group_id": 0,
    "first_category_id": 5,
    "second_category_id": 6,
    "third_category_id": 65,
    "product_id": 38,
    "dt": "2024-04-01",
    "sale_amount": 0.2,
    "hours_sale": "[len 24: [np.float64(0.0), np.float64(0.0), np.float64(0.0)]...[np.float64(0.0), np.float64(0.0), np.float64(0.0)]]",
    "stock_hour6_22_cnt": 8,
    "hours_stock_status": "[len 24: [np.int64(1), np.int64(1), np.int64(1)]...[np.int64(1), np.int64(1), np.int64(1)]]",
    "discount": 1.0,
    "holiday_flag": 0,
    "activity_flag": 0,
    "precpt": 3.5386,
    "avg_temperature": 15.37,
    "avg_humidity": 78.26,
    "avg_wind_level": 1.25
  }
]
```

---

## 4. Data Quality, Missingness, and Duplicate Checks

### Missingness
- Missing values in `train.parquet`: **0 (0.0000%)** across all 19 columns.
- Missing values in `eval.parquet`: **0 (0.0000%)** across all 19 columns.
- Entirely missing columns: **None**.

### Natural Key Grain and Duplicate Rows
- **Documented Grain:** `(store_id, product_id, dt)` representing one store-product daily record.
- **Train Duplicate Grain Records:** 0 out of 4,500,000 rows (0.0000%).
- **Eval Duplicate Grain Records:** 0 out of 350,000 rows (0.0000%).
- **Exact Full-Row Duplicates:** 0 across both files.

---

## 5. Time and Entity Coverage

| Metric | `train.parquet` | `eval.parquet` | Combined / Match |
|:---|:---|:---|:---|
| **Earliest Date** | 2024-03-28 | 2024-06-26 | Chronological continuity |
| **Latest Date** | 2024-06-25 | 2024-07-02 | 97 total observation days |
| **Unique Dates** | 90 days | 7 days | Complete without gaps |
| **Unparseable Dates** | 0 | 0 | 100% valid ISO 8601 |
| **Distinct Cities** | 18 | 18 | Exact match (18 cities) |
| **Distinct Stores** | 898 | 898 | Exact match (898 stores) |
| **Distinct Products** | 865 | 865 | Exact match (865 SKUs) |
| **Distinct Management Groups**| 7 | 7 | Exact match (7 groups) |
| **Distinct Level-1 Categories**| 32 | 32 | Exact match (32 categories) |
| **Distinct Level-2 Categories**| 84 | 84 | Exact match (84 categories) |
| **Distinct Level-3 Categories**| 233 | 233 | Exact match (233 categories) |
| **Store-Product Series** | 50,000 | 50,000 | Exact match (50,000 series) |
| **Grid Completeness** | 50,000 * 90 = 4,500,000 rows | 50,000 * 7 = 350,000 rows | 100.0% rectangular grid |

---

## 6. Numeric Ranges and Stock-Status Representation

### Summary Statistics (`train.parquet`)
| Column | Min | Max | Mean | Median | Non-Finite | Negatives |
|:---|:---|:---|:---|:---|:---|:---|
| `sale_amount` | 0.0 | 44.9 | 0.9986 | 0.7 | 0 | 0 |
| `stock_hour6_22_cnt` | 0.0 | 16.0 | 3.1803 | 0.0 | 0 | 0 |
| `discount` | 0.0 | 1.088 | 0.9111 | 0.989 | 0 | 0 |
| `holiday_flag` | 0.0 | 1.0 | 0.3444 | 0.0 | 0 | 0 |
| `activity_flag` | 0.0 | 1.0 | 0.3784 | 0.0 | 0 | 0 |
| `precpt` | 0.0 | 42.5 | 3.6984 | 2.2977 | 0 | 0 |
| `avg_temperature` | 12.06 | 30.88 | 22.2791 | 22.5 | 0 | 0 |
| `avg_humidity` | 27.35 | 100.0 | 74.4505 | 76.36 | 0 | 0 |
| `avg_wind_level` | 0.97 | 3.85 | 1.7245 | 1.64 | 0 | 0 |

### Summary Statistics (`eval.parquet`)
| Column | Min | Max | Mean | Median | Non-Finite | Negatives |
|:---|:---|:---|:---|:---|:---|:---|
| `sale_amount` | 0.0 | 49.9 | 1.1931 | 0.8 | 0 | 0 |
| `stock_hour6_22_cnt` | 0.0 | 16.0 | 2.8972 | 0.0 | 0 | 0 |
| `discount` | 0.0 | 1.0 | 0.9217 | 1.0 | 0 | 0 |
| `holiday_flag` | 0.0 | 1.0 | 0.2857 | 0.0 | 0 | 0 |
| `activity_flag` | 0.0 | 1.0 | 0.3297 | 0.0 | 0 | 0 |
| `precpt` | 0.4949 | 14.8418 | 5.8829 | 5.9782 | 0 | 0 |
| `avg_temperature` | 26.4 | 32.29 | 29.0126 | 28.89 | 0 | 0 |
| `avg_humidity` | 51.47 | 86.38 | 78.4899 | 80.05 | 0 | 0 |
| `avg_wind_level` | 1.05 | 3.68 | 1.6653 | 1.51 | 0 | 0 |

### Stockout Representation Analysis
1. **Encoding Verification:**
   `hours_stock_status` is an hourly binary sequence of length 24 where:
   - `0` represents **In-Stock** (75.11% in train, 77.23% in eval across all 24 hours).
   - `1` represents **Out-of-Stock** / Stockout (24.89% in train, 22.77% in eval across all 24 hours).
2. **Daytime Operating Stockout Window:**
   `stock_hour6_22_cnt` represents the count of stockout hours during the 16 daytime operating hours (indices 6 to 21 inclusive, corresponding to [06:00, 22:00)).
   - Formula confirmed: `stock_hour6_22_cnt == sum(hours_stock_status[6:22])`.
   - Average daytime stockout rate: **19.88%** in train, **18.11%** in eval. This matches the official dataset card statement ("incorporating approximately 20% organically occurring stockout data").
3. **Daytime Stockout Frequency Breakdown (`train.parquet`):**
   - 0 daytime stockout hours: 2,507,994 records (55.73%)
   - 1 to 15 daytime stockout hours: 1,810,215 records (40.23%)
   - Full 16-hour daytime stockout: 181,791 records (4.04%)

---

## 7. Cross-File Consistency and Split Semantics

- **Schema Alignment:** 100% identical columns and data types between `train.parquet` and `eval.parquet`.
- **Entity Overlap:** All 18 cities, 898 stores, 865 SKUs, and 50,000 store-product series in `eval.parquet` are identical to those in `train.parquet`.
- **Split Semantics:** Chronological forward out-of-time evaluation split:
  - Training window: 2024-03-28 to 2024-06-25 (90 days)
  - Evaluation window: 2024-06-26 to 2024-07-02 (7 days)
  - Date overlap: 0 days (Evaluation starts the exact day after training ends).
  - No entity leakage: Identical 50,000 series evaluated across consecutive non-overlapping temporal windows.

---

## 8. Warnings and Unresolved Questions

1. **`discount` Values Exceeding 1.0:**
   In `train.parquet`, the maximum `discount` value is observed at `1.0880` (mean: 0.9111, median: 0.9890). In `eval.parquet`, max is `1.0000`. This suggests minor product markups or delivery/peak surcharges relative to baseline retail prices. This is not a data corruption issue, but a domain feature characteristic to note for downstream modeling.
2. **Physical Parquet List Type for `hours_stock_status`:**
   The HuggingFace documentation lists `hours_stock_status` as `Sequence(int32)`, whereas the Parquet files store elements as `int64`. Values are strictly binary `{0, 1}`, so memory impact is minimal and fully handled by standard deserializers.

---

## 9. Pass / Fail Criteria Evaluation and Final Decision

| Rule | Requirement | Observed Result | Decision |
|:---|:---|:---|:---|
| 1 | Both files exist at expected paths | Both files present | PASS |
| 2 | Files have valid Parquet structures and can be read | Valid Parquet headers, 0 read errors | PASS |
| 3 | Schema & essential fields match official documentation | All 19 fields match documented concepts & types | PASS |
| 4 | No critical integrity problem remains unexplained | 0 missing values, 0 duplicate keys, SHA256 verified | PASS |
| 5 | Important statistics and provenance recorded | Complete distributions and LFS provenance captured | PASS |
| 6 | Reports and logs generated successfully | JSON, Markdown, and logs generated | PASS |

### Final Task 1 Status: **PASS**

---

## 10. Reproduction Commands

To reproduce this validation and regenerate all reports and logs, execute the following command from the project root directory:

```bash
python validation/freshretail/scripts/validate_dataset.py \
  --data-dir data/raw \
  --output-dir validation/freshretail \
  --log-file validation/freshretail/logs/task1_validation.log
```
