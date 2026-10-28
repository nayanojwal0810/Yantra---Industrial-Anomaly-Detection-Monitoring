# Sanket — USAspending Controlled FY2020 Pilot Validation Report

**Run Status**: `transaction_precheck_rejected`  
**Timestamp (UTC)**: `2026-10-28T06:37:46.273131+00:00`  
**Cohort ID**: `nasa_naics541330_fy2020` (NASA Awarding Agency, NAICS 541330 (Engineering Services), FY2020 new awards (base transaction date in FY2020))  

## 1. Executive Summary & Query Architecture

This controlled pilot implements a two-stage asynchronous bulk download architecture:
1. **Stage 1 (Award Cohort)**: NASA + NAICS 541330 (`require: ['541330']`) + FY2020 new awards (`date_type: 'new_awards_only'`).
2. **Stage 2 (Transaction History)**: Full modification history queried by cohort `award_ids` with **NO date filter**.

## 2. Stage 1: Award Cohort Reconciliation

| Stage 1 Metric | Count / Value |
| :--- | :--- |
| Count API Precheck (`calculated_count`) | `221` |
| Job Status Metadata (`total_rows`) | `221` |
| Downloaded CSV Data Rows | `221` |
| Same-Query Reconciliation Status | **MATCH** |
| Total Columns in Award CSV | `286` |
| Unique PIIDs Extracted | `221` |
| Blank PIID Count | `0` |
| Repeated PIID Count | `0` |

- **ZIP File Path**: `data\raw\sample\bulk_api\PrimeAwardSummaries_nasa_naics541330_fy2020_20261028T063731Z.zip`
- **SHA-256**: `0b91c0ebf93473b7dd9100fae9fe029aaf70f364709e408b4a139783866cea89`
- **File Size**: `51,763` bytes

## 3. Stage 2: Transaction History Retrieval

**Transaction Stage Status**: `rejected_by_server`  
**Batches Planned**: `3`  
**Exact Match Quoting Used**: `True`  

### Server Rejection of Documented Form
**Endpoint**: `/api/v2/download/count/`  
**HTTP Status**: `503`  
**Reason / Message**: `Count endpoint returned HTTP 503 for spending_level='transactions': `  

> [!IMPORTANT]
> Per specification: 'If the endpoint rejects the documented form, preserve the server response
> and stop rather than trying arbitrary payload variants.' The client recorded the server rejection
> and halted honestly without silently inventing workarounds.

#### Rejected Request Sample Payload:
```json
{
  "filters": {
    "award_ids": [
      "\"80AFRC20C0012\"",
      "\"80AFRC20C0019\"",
      "\"80AFRC20C0020\"",
      "\"80AFRC20C0022\"",
      "\"80AFRC20F0095\"",
      "\"80AFRC20F0118\"",
      "\"80AFRC20F0163\"",
      "\"80ARC020F0002\"",
      "\"80ARC020F0015\"",
      "\"80ARC020F0017\"",
      "\"80ARC020F0029\"",
      "\"80ARC020F0030\"",
      "\"80ARC020F0035\"",
      "\"80ARC020F0036\"",
      "\"80ARC020F0037\"",
      "\"80ARC020F0038\"",
      "\"80ARC020F0040\"",
      "\"80ARC020F0044\"",
      "\"80ARC020F0049\"",
      "\"80ARC020F0054\"",
      "\"80ARC020F0055\"",
      "\"80ARC020F0059\"",
      "\"80ARC020F0060\"",
      "\"80ARC020F0061\"",
      "\"80ARC020F0062\"",
      "\"80ARC020F0088\"",
      "\"80ARC020F0100\"",
      "\"80ARC020F0101\"",
      "\"80ARC020F0103\"",
      "\"80ARC020F0107\"",
      "\"80ARC020F0108\"",
      "\"80ARC020F0112\"",
      "\"80ARC020F0117\"",
      "\"80ARC020F0119\"",
      "\"80ARC020F0120\"",
      "\"80ARC020F0123\"",
      "\"80GRC020F0009\"",
      "\"80GRC020F0017\"",
      "\"80GRC020F0019\"",
      "\"80GRC020F0068\"",
      "\"80GRC020F0080\"",
      "\"80GRC020F0094\"",
      "\"80GRC020F0186\"",
      "\"80GRC020F0187\"",
      "\"80GRC020F0209\"",
      "\"80GRC020F0212\"",
      "\"80GRC020F0217\"",
      "\"80GRC020F0222\"",
      "\"80GRC020F0223\"",
      "\"80GRC020F0224\"",
      "\"80GRC020F0227\"",
      "\"80GSFC20C0034\"",
      "\"80GSFC20C0115\"",
      "\"80GSFC20F0020\"",
      "\"80GSFC20F0021\"",
      "\"80GSFC20F0022\"",
      "\"80GSFC20F0023\"",
      "\"80GSFC20F0134\"",
      "\"80HQTR20F0021\"",
      "\"80HQTR20F0022\"",
      "\"80HQTR20F0023\"",
      "\"80HQTR20F0024\"",
      "\"80HQTR20F0034\"",
      "\"80HQTR20F0071\"",
      "\"80HQTR20F0105\"",
      "\"80HQTR20F0146\"",
      "\"80HQTR20F0239\"",
      "\"80JSC020C0019\"",
      "\"80JSC020F0005\"",
      "\"80JSC020F0139\"",
      "\"80JSC020F0162\"",
      "\"80JSC020F0181\"",
      "\"80JSC020F0318\"",
      "\"80KSC020F0005\"",
      "\"80KSC020F0031\"",
      "\"80KSC020F0043\"",
      "\"80KSC020F0044\"",
      "\"80KSC020F0045\"",
      "\"80KSC020F0046\"",
      "\"80KSC020F0047\"",
      "\"80KSC020F0048\"",
      "\"80KSC020F0067\"",
      "\"80KSC020F0078\"",
      "\"80KSC020F0079\"",
      "\"80KSC020F0080\"",
      "\"80KSC020F0087\"",
      "\"80KSC020F0093\"",
      "\"80KSC020F0096\"",
      "\"80KSC020F0098\"",
      "\"80KSC020F0100\"",
      "\"80KSC020F0103\"",
      "\"80KSC020F0107\"",
      "\"80KSC020F0119\"",
      "\"80KSC020F0132\"",
      "\"80KSC020F0135\"",
      "\"80KSC020F0138\"",
      "\"80KSC020F0139\"",
      "\"80KSC020F0143\"",
      "\"80KSC020F0155\"",
      "\"80KSC020F0157\""
    ]
  },
  "spending_level": "transactions"
}
```

## 4. Error / Halt Diagnostics
```
Transaction precheck rejected by server on batch 1: Count endpoint returned HTTP 503 for spending_level='transactions': . Halting per specification rule: 'If the endpoint rejects the documented form, preserve the server response and stop rather than trying arbitrary payload variants.'
```

## 5. Context: Comparison with Prior Manual Downloads

| Archive | Filter Semantics | Awards | Transactions | Role in Sanket |
| :--- | :--- | :--- | :--- | :--- |
| Manual ON (`...H21M56S49644703.zip`) | FY2020, Show New Awards ON | 221 | 390 | Prior reference observation |
| Manual OFF (`NASA_2020.zip`) | FY2020, Show New Awards OFF | 785 | 1,384 | Prior reference observation |
| Current Pilot Stage 1 | FY2020, `new_awards_only` | 221 | N/A (separate) | Official bulk API award cohort |

> [!NOTE]
> 'Show New Awards Only' ON filters by initial award obligation date (`new_awards_only`), yielding 221 awards.
> 'Show New Awards Only' OFF filters by transaction action dates (`action_date`), yielding 785 awards.
> The transaction export in the combined manual download was date-truncated to FY2020; querying transaction history
> separately without date filters is required to capture full lifetime modifications.

