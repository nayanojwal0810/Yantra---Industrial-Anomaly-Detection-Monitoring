#!/usr/bin/env python3
"""
resample_fcu_subset.py
----------------------
Reproduces the multi-rate downsampling evaluation across 1-minute, 5-minute, and 15-minute
resolutions using semantically valid aggregation rules:
  - Continuous sensor measurements: time-weighted / block mean
  - Analog actuator commands: block mean
  - Discrete categorical operating modes (FCU_CTRL: 0=shutdown, 1=operate, 2=setback):
      - Categorical majority mode (mode)
      - Mode duration shares (share_shutdown, share_operate, share_setback)
      - Transition indicator (mode_changed: 1 if mode switched during window, else 0)

Evaluates distribution preservation, peak/transient attenuation, and write performance.
Outputs machine-readable summary to validation/review/evidence/aggregation_summary.json.

Usage:
    python validation/scripts/resample_fcu_subset.py \
        --data-dir tmp/fcu_data \
        --out-json validation/review/evidence/aggregation_summary.json

Dependencies:
    pandas, numpy, scipy, argparse, json, pathlib
"""

import argparse
import json
import time
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats


def semantically_valid_resample(df: pd.DataFrame, freq_str: str) -> pd.DataFrame:
    """
    Applies domain-appropriate aggregation rules across physical telemetry,
    actuator commands, and discrete control states with fast vectorized operations.
    """
    ts_col = "Datetime" if "Datetime" in df.columns else df.columns[0]
    df_indexed = df.set_index(ts_col).sort_index()

    # Create one-hot indicators for FCU_CTRL if present
    has_ctrl = "FCU_CTRL" in df_indexed.columns
    if has_ctrl:
        df_indexed["_CTRL_0"] = (df_indexed["FCU_CTRL"] == 0).astype(float)
        df_indexed["_CTRL_1"] = (df_indexed["FCU_CTRL"] == 1).astype(float)
        df_indexed["_CTRL_2"] = (df_indexed["FCU_CTRL"] == 2).astype(float)

    # Identify channel groups
    skip_cols = {"FCU_CTRL", "_CTRL_0", "_CTRL_1", "_CTRL_2"}
    constant_cols = [c for c in df_indexed.columns if df_indexed[c].nunique() <= 1 and c not in skip_cols]
    continuous_cols = [c for c in df_indexed.columns if c not in constant_cols and c not in skip_cols]

    agg_dict = {col: "mean" for col in continuous_cols}
    for col in constant_cols:
        agg_dict[col] = "first"

    if has_ctrl:
        agg_dict["_CTRL_0"] = "mean"
        agg_dict["_CTRL_1"] = "mean"
        agg_dict["_CTRL_2"] = "mean"

    resampled = df_indexed.resample(freq_str).agg(agg_dict)

    if has_ctrl:
        # Determine majority mode via argmax across shares
        shares = resampled[["_CTRL_0", "_CTRL_1", "_CTRL_2"]].to_numpy()
        modes = np.argmax(shares, axis=1)
        max_shares = np.max(shares, axis=1)
        transitions = (max_shares < 1.0).astype(int)

        resampled["FCU_CTRL"] = modes
        resampled["FCU_CTRL_TRANSITION"] = transitions
        resampled["FCU_CTRL_SHUTDOWN_SHARE"] = resampled["_CTRL_0"].round(4)
        resampled["FCU_CTRL_OPERATE_SHARE"] = resampled["_CTRL_1"].round(4)
        resampled["FCU_CTRL_SETBACK_SHARE"] = resampled["_CTRL_2"].round(4)
        resampled.drop(columns=["_CTRL_0", "_CTRL_1", "_CTRL_2"], inplace=True)

    resampled = resampled.reset_index()
    return resampled


def evaluate_distribution_changes(raw_df: pd.DataFrame, resampled_df: pd.DataFrame, target_cols: list) -> dict:
    """Measures mean, std, 5th/50th/95th percentiles, and peak retention."""
    res = {}
    for col in target_cols:
        if col not in raw_df.columns or col not in resampled_df.columns:
            continue
        r_vals = raw_df[col].to_numpy()
        d_vals = resampled_df[col].to_numpy()

        r_peak = float(np.max(np.abs(r_vals)))
        d_peak = float(np.max(np.abs(d_vals)))
        peak_ratio = round(d_peak / r_peak, 4) if r_peak > 0 else 1.0

        res[col] = {
            "raw": {
                "mean": round(float(np.mean(r_vals)), 5),
                "std": round(float(np.std(r_vals)), 5),
                "p05": round(float(np.percentile(r_vals, 5)), 5),
                "p50": round(float(np.percentile(r_vals, 50)), 5),
                "p95": round(float(np.percentile(r_vals, 95)), 5),
                "max": round(float(np.max(r_vals)), 5),
                "min": round(float(np.min(r_vals)), 5)
            },
            "resampled": {
                "mean": round(float(np.mean(d_vals)), 5),
                "std": round(float(np.std(d_vals)), 5),
                "p05": round(float(np.percentile(d_vals, 5)), 5),
                "p50": round(float(np.percentile(d_vals, 50)), 5),
                "p95": round(float(np.percentile(d_vals, 95)), 5),
                "max": round(float(np.max(d_vals)), 5),
                "min": round(float(np.min(d_vals)), 5)
            },
            "delta_mean": round(float(np.mean(d_vals) - np.mean(r_vals)), 6),
            "peak_retention_ratio": peak_ratio,
            "peak_attenuation_pct": round((1.0 - peak_ratio) * 100.0, 2)
        }
    return res


def main():
    parser = argparse.ArgumentParser(description="Evaluate FCU downsampling and aggregation semantics.")
    parser.add_argument("--data-dir", type=str, default="tmp/fcu_data", help="Directory with raw 1-min FCU CSVs.")
    parser.add_argument("--out-json", type=str, default="validation/review/evidence/aggregation_summary.json", help="Path to save output JSON.")
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    files_to_test = [
        "FCU_FaultFree.csv",
        "FCU_VLVLeak_Cooling_20.csv",
        "FCU_Fouling_Cooling_Airside_Minor.csv",
        "FCU_FilterRestriction_10%.csv"
    ]

    target_channels = [
        "FCU_CLG_GPM", "FCU_CVLV", "FCU_DAT", "RM_TEMP",
        "FCU_SPD", "FCU_CTRL", "FCU_DA_CFM", "FCU_MAT"
    ]

    results = {}

    for fname in files_to_test:
        fpath = data_dir / fname
        if not fpath.exists():
            print(f"Skipping {fname} (not found in {data_dir})")
            continue

        print(f"\nEvaluating resampling for: {fname} ...")
        t0 = time.time()
        df_1m = pd.read_csv(fpath)
        ts_col = "DateTime" if "DateTime" in df_1m.columns else df_1m.columns[0]
        df_1m[ts_col] = pd.to_datetime(df_1m[ts_col])
        load_time = time.time() - t0

        file_eval = {
            "raw_1min": {
                "rows": len(df_1m),
                "load_time_sec": round(load_time, 3),
                "memory_mb": round(df_1m.memory_usage(deep=True).sum() / (1024 * 1024), 2)
            }
        }

        for freq, label in [("5min", "resampled_5min"), ("15min", "resampled_15min")]:
            t1 = time.time()
            df_res = semantically_valid_resample(df_1m, freq)
            resample_time = time.time() - t1

            dist_changes = evaluate_distribution_changes(df_1m, df_res, target_channels)

            file_eval[label] = {
                "rows": len(df_res),
                "resample_time_sec": round(resample_time, 3),
                "memory_mb": round(df_res.memory_usage(deep=True).sum() / (1024 * 1024), 2),
                "row_reduction_pct": round((1.0 - len(df_res) / len(df_1m)) * 100.0, 2),
                "channel_distributions": dist_changes
            }

        results[fname] = file_eval

    out_json = Path(args.out_json)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"\nAggregation evaluation complete. Machine-readable summary saved to: {out_json.resolve()}")


if __name__ == "__main__":
    main()
