"""
Minimal technical smoke check:
Load samples from normal run and fault scenarios (leakage, clogging, reconfiguration).
Verify columns, datatypes, and sensor access.
"""
import os
import sys
from pathlib import Path
import pandas as pd
import numpy as np

def run_smoke_test():
    temp_dir = Path(os.environ.get("TEMP", r"C:\Users\nayan\AppData\Local\Temp")) / "fluid-mixing-audit"
    data_dir = temp_dir / "data" / "ModVA_Datasets"

    test_files = [
        ("Normal", data_dir / "dataset_1_normal_behaviour.csv"),
        ("Fault - Leakage", data_dir / "dataset_10_leakage.csv"),
        ("Fault - Clogging", data_dir / "dataset_15_clogging.csv"),
        ("Fault - Reconfiguration", data_dir / "dataset_12_reconfiguration.csv"),
    ]

    for label, filepath in test_files:
        if not filepath.exists():
            print(f"Error: {filepath} does not exist.")
            continue
        
        df = pd.read_csv(filepath)
        print(f"[{label}] File: {filepath.name}")
        print(f"  Shape: {df.shape}")
        print(f"  Columns: {len(df.columns)}")
        print(f"  Server Time range: {df['Server Time'].iloc[0]} to {df['Server Time'].iloc[-1]}")
        print(f"  Session Time range: {df['Session Time Stamps'].iloc[0]:.2f}s to {df['Session Time Stamps'].iloc[-1]:.2f}s (duration: {df['Session Time Stamps'].iloc[-1] - df['Session Time Stamps'].iloc[0]:.2f}s)")
        print(f"  Anomaly label values: {df['Anomaly'].unique().tolist()}")
        
        # Verify key sensor channels
        key_sensors = [
            "Tank_B201_Volume", "Tank_B204_Volume",
            "Pressure_below_B201", "Pressure_below_B204",
            "Flow_after_Pump_P201", "Flow_after_Pump_P202",
            "Tempreature_before_Pump_P201", "Temperature_in_B204",
            "Pump_P201_active", "Valve_V201_opening"
        ]
        sensor_present = all(s in df.columns for s in key_sensors)
        print(f"  Key sensors accessible: {sensor_present}")
        sample_stats = {s: float(df[s].mean()) for s in key_sensors[:4]}
        print(f"  Sample sensor means: {sample_stats}")
        print()

if __name__ == "__main__":
    run_smoke_test()
