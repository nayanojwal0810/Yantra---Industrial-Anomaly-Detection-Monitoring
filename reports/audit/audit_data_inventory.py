"""
Audit script for dataset inventory and schema validation of the Fluid Mixing Benchmark.
Usage:
    python reports/audit/audit_data_inventory.py
"""

import os
import sys
import json
from pathlib import Path
import pandas as pd
import numpy as np

def run_audit():
    # Candidate data location in temp directory
    temp_dir = Path(os.environ.get("TEMP", r"C:\Users\nayan\AppData\Local\Temp")) / "fluid-mixing-audit"
    dataset_dir = temp_dir / "data" / "ModVA_Datasets"
    
    if not dataset_dir.exists():
        print(f"Error: dataset directory not found at {dataset_dir}")
        sys.exit(1)

    csv_files = sorted(list(dataset_dir.glob("*.csv")), key=lambda p: int(p.stem.split("_")[1]) if p.stem.split("_")[1].isdigit() else p.stem)
    
    print(f"Total CSV files found in {dataset_dir}: {len(csv_files)}")

    # Reference file for schema: dataset_1_normal_behaviour.csv
    ref_file = dataset_dir / "dataset_1_normal_behaviour.csv"
    ref_df = pd.read_csv(ref_file)
    ref_cols = list(ref_df.columns)
    
    results = []
    global_anomaly_values = set()
    scenario_counts = {}

    for file_path in csv_files:
        stem = file_path.stem
        parts = stem.split("_")
        run_id = int(parts[1]) if parts[1].isdigit() else -1
        scenario = "_".join(parts[2:])
        scenario_counts[scenario] = scenario_counts.get(scenario, 0) + 1

        file_size = file_path.stat().st_size
        df = pd.read_csv(file_path)
        row_count, col_count = df.shape

        cols = list(df.columns)
        cols_match_ref = (cols == ref_cols)
        missing_cols = list(set(ref_cols) - set(cols))
        extra_cols = list(set(cols) - set(ref_cols))

        null_count = int(df.isnull().sum().sum())
        
        # Check inf
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        inf_count = int(np.isinf(df[numeric_cols]).sum().sum())

        # Check duplicates
        dup_rows = int(df.duplicated().sum())
        
        dup_server_time = int(df["Server Time"].duplicated().sum()) if "Server Time" in df else None
        dup_session_time = int(df["Session Time Stamps"].duplicated().sum()) if "Session Time Stamps" in df else None

        # Check timestamp monotonicity & sampling
        dt_stats = {}
        is_monotonic = None
        if "Session Time Stamps" in df:
            st = df["Session Time Stamps"].values
            diffs = np.diff(st)
            is_monotonic = bool(np.all(diffs >= 0))
            strictly_monotonic = bool(np.all(diffs > 0))
            dt_stats = {
                "min_dt": float(np.min(diffs)) if len(diffs) > 0 else None,
                "max_dt": float(np.max(diffs)) if len(diffs) > 0 else None,
                "median_dt": float(np.median(diffs)) if len(diffs) > 0 else None,
                "mean_dt": float(np.mean(diffs)) if len(diffs) > 0 else None,
                "strictly_monotonic": strictly_monotonic
            }

        # Check constant columns
        constant_cols = [c for c in numeric_cols if df[c].std(ddof=0) == 0]

        # Anomaly label analysis
        anomaly_dist = {}
        if "Anomaly" in df:
            val_counts = df["Anomaly"].value_counts().to_dict()
            anomaly_dist = {str(k): int(v) for k, v in val_counts.items()}
            for v in val_counts.keys():
                global_anomaly_values.add(v)
            normal_rows = int(df["Anomaly"].eq(0).sum())
            fault_rows = int(df["Anomaly"].ne(0).sum())
            fault_ratio = float(fault_rows / row_count) if row_count > 0 else 0.0
        else:
            normal_rows, fault_rows, fault_ratio = None, None, None

        results.append({
            "run_id": run_id,
            "filename": file_path.name,
            "scenario": scenario,
            "file_size_bytes": file_size,
            "row_count": row_count,
            "col_count": col_count,
            "cols_match_ref": cols_match_ref,
            "missing_cols": missing_cols,
            "extra_cols": extra_cols,
            "null_count": null_count,
            "inf_count": inf_count,
            "dup_rows": dup_rows,
            "dup_server_time": dup_server_time,
            "dup_session_time": dup_session_time,
            "is_monotonic": is_monotonic,
            "dt_stats": dt_stats,
            "constant_cols": constant_cols,
            "normal_rows": normal_rows,
            "fault_rows": fault_rows,
            "fault_ratio": fault_ratio,
            "anomaly_dist": anomaly_dist
        })

    # Summary statistics
    summary = {
        "total_files": len(results),
        "total_rows": sum(r["row_count"] for r in results),
        "file_size_min": min(r["file_size_bytes"] for r in results),
        "file_size_max": max(r["file_size_bytes"] for r in results),
        "file_size_total": sum(r["file_size_bytes"] for r in results),
        "row_count_min": min(r["row_count"] for r in results),
        "row_count_max": max(r["row_count"] for r in results),
        "scenario_counts": scenario_counts,
        "global_anomaly_values": sorted(list(global_anomaly_values)),
        "files_with_nulls": [r["filename"] for r in results if r["null_count"] > 0],
        "files_with_infs": [r["filename"] for r in results if r["inf_count"] > 0],
        "files_with_dup_rows": [r["filename"] for r in results if r["dup_rows"] > 0],
        "files_with_dup_timestamps": [r["filename"] for r in results if (r["dup_session_time"] or 0) > 0 or (r["dup_server_time"] or 0) > 0],
        "files_non_monotonic": [r["filename"] for r in results if not r["is_monotonic"]],
        "schema_mismatches": [{"file": r["filename"], "cols": r["col_count"], "missing": r["missing_cols"], "extra": r["extra_cols"]} for r in results if not r["cols_match_ref"]],
    }

    output_json = Path("reports/audit/audit_inventory_results.json")
    with open(output_json, "w") as f:
        json.dump({"summary": summary, "files": results}, f, indent=2)

    print("Audit completed successfully.")
    print(f"Summary saved to {output_json}")
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    run_audit()
