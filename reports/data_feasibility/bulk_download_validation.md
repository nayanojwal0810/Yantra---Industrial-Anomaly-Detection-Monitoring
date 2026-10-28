# Sanket — USAspending Bulk Download Client Validation Report

**Run Status**: `count_mismatch`  
**Timestamp (UTC)**: `2026-10-28T05:07:52.435964+00:00`  
**Controlled Cohort**: `nasa_naics541330_fy2020` (NASA Awarding Agency, NAICS 541330 (Engineering Services), FY2020 action dates (Show New Awards Only OFF))  

## 1. Executive Summary

The bulk download workflow stopped with status: **`count_mismatch`**.

### Error / Halt Details
```
Count precheck mismatch for awards: API returned 194, expected reference UI count 785. Download aborted per contract.
```

### Controlled Filters Submitted
```json
{
  "award_type_codes": [
    "A",
    "B",
    "C",
    "D"
  ],
  "agencies": [
    {
      "type": "awarding",
      "tier": "toptier",
      "name": "National Aeronautics and Space Administration"
    }
  ],
  "naics_codes": [
    "541330"
  ],
  "time_period": [
    {
      "start_date": "2019-10-01",
      "end_date": "2020-09-30",
      "date_type": "action_date"
    }
  ]
}
```

### Count Precheck Comparison

| Spending Level | UI Reference Count | API Count Precheck | Status |
| :--- | :--- | :--- | :--- |
| Prime Awards | 785 | 194 | **MISMATCH** |
| Prime Transactions | 1384 | 1384 | MATCH |

### Count Precheck Raw Responses
```json
{
  "awards": {
    "level": "awards",
    "calculated_count": 194,
    "calculated_transaction_count": 194,
    "maximum_limit": 500000,
    "maximum_transaction_limit": 500000,
    "rows_gt_limit": false,
    "transaction_rows_gt_limit": false,
    "messages": [
      "For searches, time period start and end dates are currently limited to an earliest date of 2007-10-01.  For data going back to 2000-10-01, use either the Custom Award Download feature on the website or one of our download or bulk_download API endpoints as listed on https://api.usaspending.gov/docs/endpoints. ",
      "'subawards' will be deprecated in the future. Set \u2018spending_level\u2019 to \u2018subawards\u2019 instead. See documentation for more information. ",
      "The above fields containing the transaction_* naming convention will be deprecated and replaced with fields without the transaction_*. "
    ],
    "raw_response": {
      "calculated_transaction_count": 194,
      "maximum_transaction_limit": 500000,
      "transaction_rows_gt_limit": false,
      "calculated_count": 194,
      "spending_level": "awards",
      "maximum_limit": 500000,
      "rows_gt_limit": false,
      "messages": [
        "For searches, time period start and end dates are currently limited to an earliest date of 2007-10-01.  For data going back to 2000-10-01, use either the Custom Award Download feature on the website or one of our download or bulk_download API endpoints as listed on https://api.usaspending.gov/docs/endpoints. ",
        "'subawards' will be deprecated in the future. Set \u2018spending_level\u2019 to \u2018subawards\u2019 instead. See documentation for more information. ",
        "The above fields containing the transaction_* naming convention will be deprecated and replaced with fields without the transaction_*. "
      ]
    }
  },
  "transactions": {
    "level": "transactions",
    "calculated_count": 1384,
    "calculated_transaction_count": 1384,
    "maximum_limit": 500000,
    "maximum_transaction_limit": 500000,
    "rows_gt_limit": false,
    "transaction_rows_gt_limit": false,
    "messages": [
      "For searches, time period start and end dates are currently limited to an earliest date of 2007-10-01.  For data going back to 2000-10-01, use either the Custom Award Download feature on the website or one of our download or bulk_download API endpoints as listed on https://api.usaspending.gov/docs/endpoints. ",
      "'subawards' will be deprecated in the future. Set \u2018spending_level\u2019 to \u2018subawards\u2019 instead. See documentation for more information. ",
      "The above fields containing the transaction_* naming convention will be deprecated and replaced with fields without the transaction_*. "
    ],
    "raw_response": {
      "calculated_transaction_count": 1384,
      "maximum_transaction_limit": 500000,
      "transaction_rows_gt_limit": false,
      "calculated_count": 1384,
      "spending_level": "transactions",
      "maximum_limit": 500000,
      "rows_gt_limit": false,
      "messages": [
        "For searches, time period start and end dates are currently limited to an earliest date of 2007-10-01.  For data going back to 2000-10-01, use either the Custom Award Download feature on the website or one of our download or bulk_download API endpoints as listed on https://api.usaspending.gov/docs/endpoints. ",
        "'subawards' will be deprecated in the future. Set \u2018spending_level\u2019 to \u2018subawards\u2019 instead. See documentation for more information. ",
        "The above fields containing the transaction_* naming convention will be deprecated and replaced with fields without the transaction_*. "
      ]
    }
  }
}
```

