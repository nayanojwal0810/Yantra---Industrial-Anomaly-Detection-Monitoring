# FreshRetailNet-50K Full-Data Forecast Protocol and Leakage Audit (Task 2)

- **Task:** TASK 2 — Full-Data Forecast Protocol and Leakage Audit
- **Audit Execution Timestamp:** `2026-10-29T22:51:53.591554+00:00`
- **Overall Task Decision:** **PASS**
- **Git Branch:** `project1/freshretail-validation`
- **Validation Rule:** Full-Data Mandatory Rule (0% Sampling, 4,850,000 Total Rows Verified)

---

## 1. Executive Summary

| Verification Item | Training Partition (`train.parquet`) | Evaluation Partition (`eval.parquet`) | Combined Total | Audit Decision |
|:---|:---|:---|:---|:---|
| **Total Rows Processed** | 4,500,000 rows (100% full scan) | 350,000 rows (100% full scan) | 4,850,000 rows | **PASS** |
| **D1: Hourly Sequence Validity** | 0 nulls, 0 length != 24, 0 non-finite elements | 0 nulls, 0 length != 24, 0 non-finite elements | 100% valid 24h vectors | **PASS** |
| **D1: Binary Stock Status Domain** | 100% values in {0, 1} (0 invalid) | 100% values in {0, 1} (0 invalid) | 116,400,000 states verified | **PASS** |
| **D2: Daytime Stockout Consistency** | 0 mismatches (`sum(status[6:22]) == cnt`) | 0 mismatches (`sum(status[6:22]) == cnt`) | Max diff = 0 across 4.85M rows | **PASS** |
| **D3: Daily vs Hourly Sales Match** | 4,500,000 within 1e-6 tol (max diff 3.55e-15) | 350,000 within 1e-6 tol (max diff 3.55e-15) | Machine precision match | **PASS** |
| **D4: Grid Completeness** | Exactly 50,000 series x 90 days (0 dup keys) | Exactly 50,000 series x 7 days (0 dup keys) | 100% complete rectangular grid | **PASS** |
| **Temporal Split Structure** | 2024-03-28 to 2024-06-25 (90 days) | 2024-06-26 to 2024-07-02 (7 days) | 0 date overlap; forward split | **PASS** |
| **Stockout Mask Polarity** | Raw status: 1=Stockout, 0=In-stock | Paper formula: 1=Available, 0=Stockout | Mathematical inversion confirmed | **RESOLVED** |
| **Evaluation Filtering Protocol** | Documented in paper & official code | Evaluation scores only rows where `stock_hour6_22_cnt == 0` | 206,562 clean eval rows (59.02%) | **CONFIRMED** |

**Final Task 2 Assessment:** **PASS**

The full local dataset exhibits zero row-level corruption, zero dimensional mismatches, and perfect structural invariants across all 4,850,000 rows. The dual tasks, evaluation filter protocols, stockout polarity inversion, and covariate leakage boundaries are fully documented from official sources.

---

## 2. Reference Sources and Source Files Inspected

The audit directly inspected the official publications and codebase without relying on isolated snippets:

1. **Official Dataset Repository:**
   - URL: `https://huggingface.co/datasets/Dingdong-Inc/FreshRetailNet-50K`
   - Files inspected: Dataset card, schema definitions, Git LFS pointers.
2. **Technical Report / Paper:**
   - Citation: Yangyang Wang et al., *FreshRetailNet-50K: A Stockout-Annotated Censored Demand Dataset for Latent Demand Recovery and Forecasting in Fresh Retail*, arXiv:2505.16319 (May 2025).
   - Sections inspected:
     - Section 3.1–3.4: Data provenance, hierarchy, and MNAR censoring mechanisms.
     - Section 4.1: Task 1 formulation (Latent Demand Recovery, Equations 1–3).
     - Section 4.2: Task 2 formulation (Censoring-Robust Demand Forecasting).
     - Section 5.1–5.3: Evaluation metrics (WAPE, WPE, Decoupling Score, and operational un-censored period filtering).
     - Section 6: Limitations.
3. **Official Benchmark Codebase:**
   - Repository: `https://github.com/Dingdong-Inc/frn-50k-baseline`
   - Complete files inspected:
     - `latent_demand_recovery/exp/app.py`: Imputation pipeline, MNAR evaluation, decoupling evaluation.
     - `latent_demand_recovery/exp/data/generate_data.py`: Synthetic missingness mechanism (`mimic_missing`), hourly stock status filtering (`hours_stock_status == 1 -> np.nan`), and covariate loading.
     - `demand_forecasting/DLinear/data_provider/data_loader.py`: Series sequencing, split boundaries, covariate selection.
     - `demand_forecasting/DLinear/exp/exp_main.py`: Prediction evaluation, daily aggregation, and operational filtering (`df1.stock_hour6_22_cnt == 0`).
     - `demand_forecasting/DLinear/models/dlinear.py`: Linear decomposition architecture.
     - `demand_forecasting/SSA/ssa_forecasting.py`: Similar Scenario Average implementation and evaluation filter.
     - `demand_forecasting/TFT/configs/tft_config.py`: Temporal Fusion Transformer covariate classification.

---

## 3. Exact Definitions of Both Benchmark Tasks

### Task A: Latent-Demand Recovery (Retrospective De-Censoring)
- **Problem Unit:** Hourly time series at the store-product-day level (16 daytime operating hours, [06:00, 22:00)).
- **Observed Quantity:** Partially observed hourly sales $\mathbf{y} \in \mathbb{R}^{T \times 1}$.
- **Censored Phenomenon:** When inventory reaches zero ($i_t = 0$), customer purchase transactions are artificially suppressed to zero or truncated, concealing genuine customer latent demand $d_t$.
- **Stockout Polarity & Recovery Formula:**
  - In raw Parquet: `hours_stock_status` is $1$ for stockout, $0$ for in-stock.
  - In Paper Eq. (1): Stock-availability mask $\mathbf{s}_t = 1 - \text{hours\_stock\_status}_t$ ($1$ for in-stock, $0$ for stockout).
  - Recovered latent demand (Eq. 2):
    $$\mathbf{d} = \mathbf{y} \odot \mathbf{s} + \hat{\mathbf{d}} \odot (1 - \mathbf{s})$$
  - Estimated missing demand (Eq. 3): $\hat{\mathbf{d}} = f_\theta(\mathbf{y} \odot \mathbf{s}, \mathbf{p}, \mathbf{w}, \mathbf{c}, \mathbf{s})$ conditioned on observed sales, promotional discounts $\mathbf{p}$, weather covariates $\mathbf{w}$, calendar context $\mathbf{c}$, and stockout mask $\mathbf{s}$.
- **Ground Truth Evaluation:** True customer demand during actual stockouts is fundamentally unobservable in real retail operations. To evaluate recovery models rigorously:
  - Synthetic Controlled MNAR Simulation: The benchmark identifies operational periods with zero stockouts (`stock_hour_origin == 0`) where observed sales represent true unconstrained demand. It then artificially masks out sales intervals (`mimic_missing`) to create synthetic stockouts.
  - WAPE and WPE are calculated exclusively over these synthetically masked ground-truth periods.
  - Decoupling Score ($\rho_{DS}$): Evaluates whether recovered demand on real stockouts has decoupled from artificial inventory constraints by measuring the weighted correlation between stockout ratios and recovered demand (TimesNet achieves $\rho_{DS} = 0.07$ vs. raw sales $-0.57$).

### Task B: Seven-Day-Ahead Demand Forecasting (Prospective Forecasting)
- **Problem Unit:** Store-product series at daily resolution ($D_t$) over a 7-day prediction horizon ($t = T+1$ to $T+7$, covering 2024-06-26 to 2024-07-02).
- **Daily Target Construction:**
  - Raw Pipeline: Sum of raw observed hourly sales ($D_t = \sum_{\tau=0}^{23} y_{\tau}$).
  - Imputation-Augmented Pipeline: Sum of recovered hourly demand ($D_t = \sum_{\tau=0}^{23} d_{\tau}$).
- **Forecasting Formulation (Eq. 3):**
  $$\hat{D}_{T+1:T+7} = f(D_{T-H:T}, P_{T-H:T+7}, W_{T-H:T+7}, C_{T-H:T+7})$$
- **Operational Evaluation Filtering:**
  - Evaluated exclusively during operational periods without stockouts (`stock_hour6_22_cnt == 0`).
  - Across the 350,000 evaluation rows, exactly 206,562 rows (59.02%) satisfy `stock_hour6_22_cnt == 0`.
  - Rows with daytime stockouts are excluded from scoring because their observed sales are truncated and do not represent true ground truth.
- **Benchmark Reproduction vs. Deployment Realism:**
  - Benchmark Reproduction: Assumes future promotional schedules ($P$), future statutory calendar flags ($C$), and future weather features ($W$) are known across $T+1:T+7$. The official code passes realized weather station readings from `eval.parquet`.
  - Deployment Realism: In production, weather over a 7-day horizon is only available via meteorological forecasts (carrying forecast error), not observed truth.

---

## 4. Complete 19-Field Availability and Leakage Matrix

| Field Name | Type | Documented Role & Meaning | Recovery Role | Forecasting Role | Legitimately Available at Origin? | Depends on Assumption? | Leakage Risk & Assessment | Supporting Source | Recommended Treatment |
|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|
| `city_id` | `int64` | Encoded city id (18 cities) | Static spatial hierarchy | Static spatial covariate | YES | NO | None (Fixed geographic attribute) | Paper 3.1; TFT config | Safe static categorical |
| `store_id` | `int64` | Encoded store id (898 stores) | Series grouping key | Series grouping key | YES | NO | None (Fixed store identity) | Paper 3.1; TFT group_ids | Safe grouping key |
| `management_group_id`| `int64` | Merchandising group (7 groups)| Static hierarchy | Static product covariate | YES | NO | None (Fixed catalog classification) | Paper 3.1; TFT config | Safe static categorical |
| `first_category_id` | `int64` | Level-1 category (32 cat.) | Static hierarchy | Static product covariate | YES | NO | None (Fixed catalog classification) | Paper 3.1; TFT config | Safe static categorical |
| `second_category_id` | `int64`| Level-2 category (84 cat.) | Static hierarchy | Static product covariate | YES | NO | None (Fixed catalog classification) | Paper 3.1; TFT config | Safe static categorical |
| `third_category_id` | `int64` | Level-3 category (233 cat.) | Static hierarchy | Static product covariate | YES | NO | None (Fixed catalog classification) | Paper 3.1; TFT config | Safe static categorical |
| `product_id` | `int64` | Product SKU id (865 SKUs) | Series grouping key | Series grouping key | YES | NO | None (Fixed SKU identity) | Paper 3.1; TFT group_ids | Safe grouping key |
| `dt` | `string`| Calendar date (YYYY-MM-DD) | Temporal sequence index | Temporal index / calendar derivation | YES | NO | None (Deterministic calendar index) | Paper 4.2; TFT datetime | Safe temporal index |
| `sale_amount` | `double`| Daily normalized sales quantity | Benchmark comparison | Primary prediction target | Historical ($t \le T$) only | NO | **CRITICAL LEAKAGE** if used as future predictor ($t > T$). Contains target. | Paper 4.2; TFT config | Target only; strict lags ($t \le T$) for features |
| `hours_sale` | `list<double>`| Hourly normalized sales (24h) | Observed input series ($y$) | Lagged intraday features ($t \le T$) | Historical ($t \le T$) only | NO | **CRITICAL LEAKAGE** if future hours used in forecasting. | Paper 4.1; generate_data.py | Recovery input; lagged features only for forecasting |
| `stock_hour6_22_cnt` | `int32` | Out-of-stock hours in [06:00, 22:00) | Identifies clean days for MNAR eval | Evaluation scoring filter | Historical ($t \le T$) only | YES (Impossible in production) | **CRITICAL LEAKAGE** if used as future covariate. Future stockouts depend on demand. | Paper 5.1; ssa_forecasting.py; exp_main.py | Evaluation filter only; forbid future predictor use |
| `hours_stock_status` | `list<int64>`| Hourly stockout status (0/1) | Mask (inverted to $s=1-\text{status}$) | Historical supply context ($t \le T$) | Historical ($t \le T$) only | YES (Post-outcome realization) | **CRITICAL LEAKAGE** if used as future predictor. Inverted polarity from paper. | Paper 4.1; generate_data.py | Invert for recovery; forbid future forecasting use |
| `discount` | `double`| Discount rate (1.0 = full price) | Promotional conditioning | Planned future covariate | YES (Planned schedule) | YES (Planned promotion execution) | Moderate if retail markdowns are dynamic rather than pre-planned. | Paper 4.2; TFT config | Permitted planned future covariate |
| `holiday_flag` | `int32` | Statutory holiday indicator (0/1)| Calendar covariate | Known future calendar covariate | YES | NO | None (Statutory holidays known in advance) | Paper 3.1, 4.2; TFT config | Legitimate known future covariate |
| `activity_flag` | `int32` | Commercial activity indicator (0/1)| Promotional context | Planned future campaign covariate | YES (Planned schedule) | YES (Campaign pre-planning) | Low to moderate. Assumes planned campaign execution. | Paper 3.1, 4.2; TFT config | Permitted planned future covariate |
| `precpt` | `double`| Daily precipitation (rainfall mm)| Weather context | Benchmark future weather covariate | Forecast assumption only | YES (Weather forecast availability) | **BENCHMARK-REALISM GAP**. Uses realized weather station truth. | Paper 4.2; TFT config; ssa_forecasting.py | Permitted benchmark reproduction; note oracle gap |
| `avg_temperature` | `double`| Average daily temperature (°C) | Weather context | Benchmark future weather covariate | Forecast assumption only | YES (Weather forecast availability) | **BENCHMARK-REALISM GAP**. Uses realized weather station truth. | Paper 4.2; TFT config | Permitted benchmark reproduction; note oracle gap |
| `avg_humidity` | `double`| Average daily relative humidity (%) | Weather context | Benchmark future weather covariate | Forecast assumption only | YES (Weather forecast availability) | **BENCHMARK-REALISM GAP**. Uses realized weather station truth. | Paper 4.2; TFT config | Permitted benchmark reproduction; note oracle gap |
| `avg_wind_level` | `double`| Average daily wind force level | Weather context | Benchmark future weather covariate | Forecast assumption only | YES (Weather forecast availability) | **BENCHMARK-REALISM GAP**. Uses realized weather station truth. | Paper 4.2; TFT config | Permitted benchmark reproduction; note oracle gap |

---

## 5. Stockout-Mask Polarity Resolution

An essential finding of this audit is the explicit polarity inversion between the dataset's physical fields and the paper's mathematical formulas:

1. **Dataset Physical Representation:**
   - Field: `hours_stock_status`
   - Polarity: `1` = **Out-of-Stock (Stockout / Supply depletion)**; `0` = **In-Stock (Stock available)**.
   - Verified by `stock_hour6_22_cnt == sum(hours_stock_status[6:22])` and official code (`generate_data.py` line 63: `hours_sale = np.where(hours_stock_status == 1, np.nan, hours_sale_origin)`).
2. **Paper Mathematical Formulation:**
   - Equation (1): $\mathbf{s}_t = 1$ if $i_t > 0$ (**Stock Available**); $\mathbf{s}_t = 0$ if $i_t = 0$ (**Stockout**).
   - Equation (2): $\mathbf{d} = \mathbf{y} \odot \mathbf{s} + \hat{\mathbf{d}} \odot (1 - \mathbf{s})$.
3. **Polarity Mapping & Resolution:**
   $$\mathbf{s}_t = 1 - \text{hours\_stock\_status}_t$$
   - Retaining observed sales $\mathbf{y}$ requires $\mathbf{s} = 1$ (`hours_stock_status == 0`).
   - Reconstructing missing demand $\hat{\mathbf{d}}$ requires $1 - \mathbf{s} = 1$ (`hours_stock_status == 1`).
   - If an implementation applied `hours_stock_status` directly as $\mathbf{s}$ without inversion, it would incorrectly overwrite observed sales with synthetic predictions and retain zero-sales stockouts.

---

## 6. Full-Data Invariant Audit Results (4,850,000 Rows Scanned)

Every check below scanned 100% of rows in batches (50 row groups / 50,000 rows per batch) with zero sampling:

### D1. Hourly Sequence Validity
- **`hours_sale`:**
  - Train (4,500,000 rows): 0 null lists, 0 length != 24, 0 null elements, 0 non-finite elements.
  - Eval (350,000 rows): 0 null lists, 0 length != 24, 0 null elements, 0 non-finite elements.
- **`hours_stock_status`:**
  - Train (4,500,000 rows): 0 null lists, 0 length != 24, 0 null elements, 0 non-binary values (all 108,000,000 elements strictly in {0, 1}).
  - Eval (350,000 rows): 0 null lists, 0 length != 24, 0 null elements, 0 non-binary values (all 8,400,000 elements strictly in {0, 1}).

### D2. Stockout-Count Consistency (`sum(status[6:22]) == stock_hour6_22_cnt`)
- **Training Set:** 4,500,000 rows checked. **0 mismatches (0.00%)**. Max absolute difference = **0**.
- **Evaluation Set:** 350,000 rows checked. **0 mismatches (0.00%)**. Max absolute difference = **0**.
- **Combined:** 4,850,000 rows checked. Max absolute difference = **0**.

### D3. Daily versus Hourly Sales Consistency (`sale_amount == sum(hours_sale)`)
- **Tolerance Threshold:** $1 \times 10^{-6}$
- **Training Set:** 4,500,000 rows checked.
  - Within tolerance: 4,500,000 (100.00%)
  - Exceeding tolerance: 0 (0.00%)
  - Max absolute difference: $3.5527 \times 10^{-15}$ (IEEE 754 machine epsilon)
  - Max relative difference: $1.1102 \times 10^{-15}$
- **Evaluation Set:** 350,000 rows checked.
  - Within tolerance: 350,000 (100.00%)
  - Exceeding tolerance: 0 (0.00%)
  - Max absolute difference: $3.5527 \times 10^{-15}$
  - Max relative difference: $7.6712 \times 10^{-16}$

### D4. Temporal and Grid Completeness
- **Training Set:**
  - Date Range: `2024-03-28` to `2024-06-25` (90 calendar days, 0 gaps).
  - Rows per date: Exactly 50,000 on all 90 dates.
  - Store-product series: Exactly 50,000 series, each with exactly 90 records ($50,000 \times 90 = 4,500,000$).
  - Key uniqueness: 0 duplicate keys on `(store_id, product_id, dt)`.
- **Evaluation Set:**
  - Date Range: `2024-06-26` to `2024-07-02` (7 calendar days, 0 gaps).
  - Rows per date: Exactly 50,000 on all 7 dates.
  - Store-product series: Exactly 50,000 series, each with exactly 7 records ($50,000 \times 7 = 350,000$).
  - Key uniqueness: 0 duplicate keys on `(store_id, product_id, dt)`.
- **Cross-Partition Temporal Alignment:**
  - Train ends on `2024-06-25`; Eval begins on `2024-06-26`.
  - Date overlap: **0 days**.
  - All 50,000 series are identical between train and eval (temporal panel structure).

### D5. Feature Boundary Summary
- **Train Boundary:** `2024-03-28` to `2024-06-25` | 4,500,000 rows | 50,000 series x 90 days.
- **Forecast Origin:** End of `2024-06-25` (23:59:59).
- **Evaluation Horizon:** `2024-06-26` to `2024-07-02` | 350,000 rows | 50,000 series x 7 days.
- **Evaluation Scoring Subset:** Exactly 206,562 rows (59.02% of eval) where `stock_hour6_22_cnt == 0`.

---

## 7. Metric and Evaluation Protocol Audit

### Evaluation Metrics
1. **Weighted Absolute Percentage Error (WAPE):**
   $$\text{WAPE} = \frac{\sum_t |d_t - y_t|}{\sum_t y_t}$$
   Measures normalized magnitude accuracy; avoids division-by-zero on zero-demand intervals.
2. **Weighted Percentage Error (WPE):**
   $$\text{WPE} = \frac{\sum_t (d_t - y_t)}{\sum_t y_t}$$
   Measures systematic bias direction (negative indicates under-prediction; positive indicates over-prediction).
3. **Decoupling Score ($\rho_{DS}$):**
   $$\rho_{DS} = \sum_{i \in \mathcal{P}} w_i \cdot \text{Pearson}(\mathbf{SR}_i, \mathbf{d}_i), \quad w_i = \frac{\mu_i}{\sum \mu_i}$$
   Measures whether recovered demand has decoupled from supply stockout constraints.

### Evaluation Protocol Limitations & Caveats
1. **True Demand vs. Observed Sales during Stockouts:** True latent demand during real stockouts cannot be measured directly. High performance on synthetic MNAR experiments demonstrates model ability to interpolate simulated gaps, but does not guarantee perfect recovery of extreme unobserved spikes during genuine store-wide stockouts.
2. **Operational Filter Conditioning:** In forecasting, models are scored exclusively on un-censored days (`stock_hour6_22_cnt == 0`). While statistically sound (comparing predictions against un-truncated ground truth), this excludes 40.98% of evaluation days that experienced daytime stockouts.

---

## 8. Assumptions and Unresolved Issues for Next Stage

1. **Oracle Realized Weather vs. Operational Weather Forecast:**
   - Issue: Benchmark uses actual realized weather measurements for the 7-day forecast horizon.
   - Next Stage Remedy: Clearly differentiate between benchmark reproduction (using realized weather) and realistic operational deployment (using weather forecasts or lagged weather).
2. **Planned vs. Reactive Promotion Execution:**
   - Issue: Promotion discount is assumed known 7 days in advance.
   - Next Stage Remedy: Maintain planned discount as future covariate for benchmark alignment, but test sensitivity to promotion schedule uncertainty.
3. **Physical Schema Serialization:**
   - In `eval.parquet` and `train.parquet`, `hours_stock_status` is serialized as `list<element: int64>` rather than `Sequence(int32)`. Handled transparently by Arrow and NumPy.

---

## 9. Final Task Status

### Status: **PASS**

All requirements of Task 2 are satisfied:
1. Both tasks (recovery and forecasting) are rigorously defined from official paper formulations and code.
2. The complete 19-field availability/leakage matrix is documented with sources and risk assessments.
3. Stockout-mask polarity inversion ($s = 1 - \text{status}$) is definitively proven from mathematical equations and code.
4. Full-data checks ran across all 4,850,000 rows without sampling, verifying all invariants.
5. Benchmark reproduction vs. deployment realism trade-offs are explicitly detailed.
