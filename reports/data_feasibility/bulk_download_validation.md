# Sanket — USAspending Controlled FY2020 Pilot Validation Report

**Run Status**: `success`  
**Timestamp (UTC)**: `2026-10-28T07:13:12.221913+00:00`  
**Cohort ID**: `nasa_naics541330_fy2020` (NASA Awarding Agency, NAICS 541330 (Engineering Services), FY2020 new awards (base transaction date in FY2020))  

## Executive Summary & Query Architecture

This controlled pilot acquires and validates two related data layers:
1. **Award Summary Cohort**: Top-tier NASA, NAICS 541330 (`require: ['541330']`), procurement contracts `A, B, C, D`, and FY2020 new awards (`date_type: 'new_awards_only'`).
2. **Transaction History Pilot**: Full lifetime modification history for all 221 cohort awards queried via official natural award IDs (`contract_award_unique_key`) with **NO date filter**.

## Award Cohort Reconciliation

| Award Metric | Count / Value |
| :--- | :--- |
| Count API Precheck (`calculated_count`) | `221` |
| Job Status Metadata (`total_rows`) | `221` |
| Downloaded CSV Data Rows | `221` |
| Same-Query Reconciliation Status | **MATCH** |
| Total Columns in Award CSV | `286` |
| Unique Generated Natural Keys (`contract_award_unique_key`) | `221` |
| Blank Generated Natural Keys | `0` |
| Unique PIIDs Extracted (`award_id_piid`) | `221` |
| Blank PIID Count | `0` |
| Repeated PIID Count | `0` |

- **ZIP File Path**: `data\raw\sample\bulk_api\PrimeAwardSummaries_nasa_naics541330_fy2020_20261028T063731Z.zip`
- **SHA-256**: `0b91c0ebf93473b7dd9100fae9fe029aaf70f364709e408b4a139783866cea89`
- **File Size**: `51,763` bytes

## Bulk Endpoint Diagnostic

- **Sample Size**: 3 awards
- **Sample PIIDs**: `['80AFRC20C0012', '80AFRC20C0019', '80AFRC20C0020']`

| Probe Type | Endpoint | Status Code | Outcome / Interpretation |
| :--- | :--- | :--- | :--- |
| Documented Quoted PIIDs | `/api/v2/download/count/` | `503` | HTTP 503 indicates a service-side availability problem. It must NOT be treated as evidence of invalid JSON or filter syntax. |
| Unquoted PIIDs | `/api/v2/download/count/` | `200` (count: `11`) | HTTP 200 returned for unquoted award_ids, but unquoted filters are treated as potentially fuzzy. Exact natural award IDs on the per-award transaction endpoints are authoritative. |

> [!NOTE]
> HTTP 503 on the bulk count endpoint with quoted award IDs was preserved as a service availability response,
> NOT a schema rejection. As designed, the pipeline proceeds to the authoritative per-award transaction workflow.

## Transaction History Validation

| Transaction Quality Metric | Count / Value | Status |
| :--- | :--- | :--- |
| Total Cohort Awards Processed | `221` / 221 | PASS |
| Total Transaction Records Retrieved | `1056` | PASS |
| Expected Transactions (Sum of Count Endpoint) | `1056` | PASS |
| Aggregate Count Reconciliation | **MATCH** | PASS |
| Per-Award Count Discrepancies | `0` | PASS |
| Blank Transaction IDs (`id`) | `0` | PASS |
| Duplicate Transaction IDs (`id`) | `0` | PASS |
| Off-Cohort Unmatched Awards | `0` | PASS |
| Cohort Award Linkage Rate | 100.0% | PASS |

- **Transaction ZIP Path**: `data\raw\sample\bulk_api\PrimeTransactions_nasa_naics541330_fy2020_20261028T070949Z.zip`
- **SHA-256**: `9b3ffe150d0192e4ae7678ce0c0ac79177c959eb9982e7f14b876b88b0d9bc6b`
- **File Size**: `31,185` bytes

## Data Quality & Lifetime Date Audit

| Date Audit Metric | Value |
| :--- | :--- |
| Earliest Transaction Action Date | `2019-10-08` |
| Latest Transaction Action Date | `2026-10-06` |
| Transactions within FY2020 (2019-10-01 to 2020-09-30) | `390` |
| Transactions outside FY2020 (Lifetime Modifications) | `666` |

> [!NOTE]
> Full modification history captures actions occurring beyond FY2020 without artificial date truncation.
> The presence of modifications outside FY2020 validates that lifetime history acquisition succeeded.

## Context: Comparison with Prior Manual Downloads

| Archive | Filter Semantics | Awards | Transactions | Role in Sanket |
| :--- | :--- | :--- | :--- | :--- |
| Manual ON (`...H21M56S49644703.zip`) | FY2020, Show New Awards ON | 221 | 390 | Prior UI reference observation |
| Manual OFF (`NASA_2020.zip`) | FY2020, Show New Awards OFF | 785 | 1,384 | Prior UI reference observation |
| Validated Controlled Pilot | FY2020 New Awards + Full Lifetime History | 221 | 1056 | Authoritative reconciled pilot |

