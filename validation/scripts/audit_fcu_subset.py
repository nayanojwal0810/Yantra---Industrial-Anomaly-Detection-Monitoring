#!/usr/bin/env python3
"""
audit_fcu_subset.py
-------------------
Audits extracted CSV files from the LBNL FCU dataset to verify data integrity,
schema consistency, temporal continuity, missing values, constant sensor channels,
and physical/meteorological synchronization against the fault-free baseline.

Outputs a machine-readable summary JSON to validation/review/evidence/audit_summary.json.

Usage:
    python validation/scripts/audit_fcu_subset.py \
        --data-dir tmp/fcu_data \
        --out-json validation/review/evidence/audit_summary.json

Dependencies:
    pandas, numpy, argparse, json, pathlib
"""

import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd


def audit_file(filepath: Path, baseline_df: pd.DataFrame = None) -> dict:
    """Performs comprehensive structural and statistical audit on a single FCU CSV."""
    df = pd.read_csv(filepath)
    num_rows, num_cols = df.shape

    # Parse timestamps
    ts_col = "DateTime" if "DateTime" in df.columns else df.columns[0]
    df[ts_col] = pd.to_datetime(df[ts_col])
    min_ts = df[ts_col].min().isoformat()
    max_ts = df[ts_col].max().isoformat()
    ts_diffs = df[ts_col].diff().dropna()
    intervals_sec = ts_diffs.dt.total_seconds().unique().tolist()

    # Nulls, NaNs, and Infs
    numeric_df = df.select_dtypes(include=[np.number])
    null_count = int(df.isnull().sum().sum())
    inf_count = int(np.isinf(numeric_df.to_numpy()).sum())

    # Constant columns (std == 0 or nunique == 1)
    constant_cols = {}
    for col in numeric_df.columns:
        if numeric_df[col].nunique() <= 1:
            constant_cols[col] = float(numeric_df[col].iloc[0])

    # Counterfactual alignment check against baseline
    sync_check = {}
    if baseline_df is not None:
        # Check timestamps match exactly
        ts_match = bool((df[ts_col] == baseline_df[ts_col]).all())
        sync_check["timestamps_identical"] = ts_match

        # Check weather channels match exactly (OAT, OA_HUMD)
        for w_col in ["FCU_OAT", "FCU_OA_HUMD"]:
            if w_col in df.columns and w_col in baseline_df.columns:
                max_diff = float((df[w_col] - baseline_df[w_col]).abs().max())
                sync_check[f"{w_col}_max_delta"] = max_diff

    # Basic statistics for key physical channels
    channel_stats = {}
    key_channels = [
        "FCU_CLG_VLV", "FCU_HTG_VLV", "FCU_OA_DMPR", "FCU_WATER_FLOW_CLG",
        "FCU_WATER_FLOW_HTG", "FCU_DAT", "FCU_SAT", "FCU_RAT", "FCU_ZONE_T", "FCU_CTRL"
    ]
    for ch in key_channels:
        if ch in df.columns:
            channel_stats[ch] = {
                "mean": round(float(df[ch].mean()), 5),
                "std": round(float(df[ch].std()), 5),
                "min": round(float(df[ch].min()), 5),
                "max": round(float(df[ch].max()), 5)
            }

    return {
        "filename": filepath.name,
        "rows": num_rows,
        "columns": num_cols,
        "column_names": df.columns.tolist(),
        "time_range": {"start": min_ts, "end": max_ts},
        "sampling_intervals_sec": intervals_sec,
        "null_count": null_count,
        "inf_count": inf_count,
        "constant_columns": constant_cols,
        "synchronization_with_baseline": sync_check,
        "channel_stats": channel_stats
    }


def main():
    parser = argparse.ArgumentParser(description="Audit FCU dataset CSV files.")
    parser.add_argument("--data-dir", type=str, default="tmp/fcu_data", help="Directory containing extracted FCU CSVs.")
    parser.add_argument("--out-json", type=str, default="validation/review/evidence/audit_summary.json", help="Path to save summary JSON.")
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    if not data_dir.exists():
        raise FileNotFoundError(f"Data directory not found: {data_dir.resolve()}")

    csv_files = sorted(data_dir.glob("*.csv"))
    if not csv_files:
        raise ValueError(f"No CSV files found in {data_dir.resolve()}")

    print(f"Auditing {len(csv_files)} CSV files in {data_dir.resolve()} ...")

    # Load baseline if available
    baseline_path = data_dir / "FCU_FaultFree.csv"
    baseline_df = None
    if baseline_path.exists():
        print(f"Loading baseline file for counterfactual synchronization checks: {baseline_path.name}")
        baseline_df = pd.read_csv(baseline_path)
        ts_col = "DateTime" if "DateTime" in baseline_df.columns else baseline_df.columns[0]
        baseline_df[ts_col] = pd.to_datetime(baseline_df[ts_col])

    audit_results = {}
    for csv_path in csv_files:
        print(f"  Auditing: {csv_path.name} ...")
        is_baseline = (csv_path.name == "FCU_FaultFree.csv")
        res = audit_file(csv_path, None if is_baseline else baseline_df)
        audit_results[csv_path.name] = res

    out_json = Path(args.out_json)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(audit_results, f, indent=2)

    print(f"\nAudit complete. Machine-readable summary saved to: {out_json.resolve()}")


if __name__ == "__main__":
    main()
