#!/usr/bin/env python3
"""
run_pilot_experiment.py
-----------------------
Implements the limited modeling-value feasibility pilot for Gate 02.
Compares three levels of approaches across 1-minute, 5-minute, and 15-minute sampling rates:
  1. Simple Reference: Explicit physical/statistical domain rules
  2. Classical ML: Unsupervised Isolation Forest on window features
  3. Compact Temporal DL Probe: 1D-CNN Autoencoder sequence model

Evaluation Protocol:
  - Dataset: LBNL FCU (Simulated Fan Coil Unit)
  - Fault-Free baseline: Contiguous temporal split
      * Train (Normal only): First 60% of year (Jan 1 to Aug 7)
      * Calibration (Normal only): Next 15% of year (Aug 8 to Oct 1)
      * Untouched Test: Remaining 25% of year (Oct 2 to Dec 31)
  - Window duration: 60 physical minutes across all rates (60 steps @ 1m, 12 @ 5m, 4 @ 15m)
  - Operating Threshold: Derived strictly from Normal Calibration data at 99.5th percentile score
  - False Alarm Rate (FAR): Evaluated strictly on Untouched Normal Test windows
  - Scenario Evaluation: Evaluated on the matching counterfactual test period (Oct 2 to Dec 31)
    across multiple distinct fault mechanisms (valve leak, coil fouling, filter restriction,
    sensor bias, damper leak).

Outputs machine-readable summary to validation/review/evidence/pilot_evaluation_summary.json.

Usage:
    python validation/scripts/run_pilot_experiment.py \
        --data-dir tmp/fcu_data \
        --out-json validation/review/evidence/pilot_evaluation_summary.json

Dependencies:
    pandas, numpy, scipy, scikit-learn, torch, argparse, json, pathlib
"""

import argparse
import json
import time
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

# Target channels used for multi-channel modeling
MODEL_CHANNELS = [
    "FCU_DAT", "FCU_MAT", "FCU_RAT", "RM_TEMP",
    "FCU_DA_CFM", "FCU_SPD", "FCU_OAT",
    "FCU_CLG_GPM", "FCU_CVLV", "FCU_HTG_GPM", "FCU_HVLV", "FCU_DMPR"
]


def load_and_resample(fpath: Path, freq_str: str) -> pd.DataFrame:
    """Loads CSV and applies semantic aggregation if downsampling."""
    df = pd.read_csv(fpath)
    ts_col = "Datetime" if "Datetime" in df.columns else df.columns[0]
    df[ts_col] = pd.to_datetime(df[ts_col])
    if freq_str == "1min":
        return df

    df_indexed = df.set_index(ts_col).sort_index()
    has_ctrl = "FCU_CTRL" in df_indexed.columns
    if has_ctrl:
        df_indexed["_CTRL_0"] = (df_indexed["FCU_CTRL"] == 0).astype(float)
        df_indexed["_CTRL_1"] = (df_indexed["FCU_CTRL"] == 1).astype(float)
        df_indexed["_CTRL_2"] = (df_indexed["FCU_CTRL"] == 2).astype(float)

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
        shares = resampled[["_CTRL_0", "_CTRL_1", "_CTRL_2"]].to_numpy()
        resampled["FCU_CTRL"] = np.argmax(shares, axis=1)
        resampled.drop(columns=["_CTRL_0", "_CTRL_1", "_CTRL_2"], inplace=True)

    return resampled.reset_index()


def create_windows(df: pd.DataFrame, window_len: int, channels: list):
    """
    Slices dataframe into non-overlapping physical 60-minute windows.
    Returns:
        windows_3d: (num_windows, window_len, num_channels)
        ts_starts: list of window start timestamps
    """
    ts_col = "Datetime" if "Datetime" in df.columns else df.columns[0]
    data = df[channels].to_numpy()
    timestamps = df[ts_col].to_numpy()

    num_windows = len(df) // window_len
    truncated_len = num_windows * window_len
    data_trunc = data[:truncated_len]
    ts_trunc = timestamps[:truncated_len]

    windows_3d = data_trunc.reshape(num_windows, window_len, len(channels))
    ts_starts = ts_trunc[::window_len]
    return windows_3d, ts_starts


class PhysicalRuleDetector:
    """Explicit domain rules grounded in FCU thermodynamics and control logic."""

    def __init__(self):
        self.clg_leak_thresh = 0.5  # GPM
        self.coil_dt_thresh = 3.0   # deg F
        self.airflow_ratio_min = 20.0 # CFM / SPD
        self.dmpr_leak_dt_thresh = 4.0 # deg F

    def fit_thresholds(self, train_windows: np.ndarray, channel_idx: dict):
        """Calibrates threshold bounds on normal training windows."""
        # 1. Cooling valve leak: when CVLV < 0.01, find 99.5th percentile of GPM
        cvlv_idx = channel_idx["FCU_CVLV"]
        gpm_idx = channel_idx["FCU_CLG_GPM"]
        closed_mask = train_windows[:, :, cvlv_idx] < 0.01
        closed_gpm = train_windows[:, :, gpm_idx][closed_mask]
        if len(closed_gpm) > 0:
            self.clg_leak_thresh = max(0.2, float(np.percentile(closed_gpm, 99.5)))

        # 2. Airflow to fan speed ratio during normal operation
        spd_idx = channel_idx["FCU_SPD"]
        cfm_idx = channel_idx["FCU_DA_CFM"]
        fan_active = train_windows[:, :, spd_idx] > 2.0
        active_ratio = train_windows[:, :, cfm_idx][fan_active] / (train_windows[:, :, spd_idx][fan_active] + 1e-4)
        if len(active_ratio) > 0:
            self.airflow_ratio_min = max(10.0, float(np.percentile(active_ratio, 0.5)))

        # 3. Uncommanded coil temperature change
        dat_idx = channel_idx["FCU_DAT"]
        mat_idx = channel_idx["FCU_MAT"]
        hvlv_idx = channel_idx["FCU_HVLV"]
        uncommanded_mask = (train_windows[:, :, cvlv_idx] < 0.01) & (train_windows[:, :, hvlv_idx] < 0.01) & fan_active
        uncommanded_dt = np.abs(train_windows[:, :, dat_idx][uncommanded_mask] - train_windows[:, :, mat_idx][uncommanded_mask])
        if len(uncommanded_dt) > 0:
            self.coil_dt_thresh = max(2.0, float(np.percentile(uncommanded_dt, 99.5)))

    def evaluate_windows(self, windows: np.ndarray, channel_idx: dict) -> np.ndarray:
        """Evaluates whether each window violates any physical domain rule."""
        num_win = len(windows)
        flags = np.zeros(num_win, dtype=int)

        cvlv = windows[:, :, channel_idx["FCU_CVLV"]]
        hvlv = windows[:, :, channel_idx["FCU_HVLV"]]
        gpm = windows[:, :, channel_idx["FCU_CLG_GPM"]]
        dat = windows[:, :, channel_idx["FCU_DAT"]]
        mat = windows[:, :, channel_idx["FCU_MAT"]]
        spd = windows[:, :, channel_idx["FCU_SPD"]]
        cfm = windows[:, :, channel_idx["FCU_DA_CFM"]]
        dmpr = windows[:, :, channel_idx["FCU_DMPR"]]
        oat = windows[:, :, channel_idx["FCU_OAT"]]
        rat = windows[:, :, channel_idx["FCU_RAT"]]

        for i in range(num_win):
            # Rule 1: Valve leak (closed command but substantial flow)
            w_closed = cvlv[i] < 0.01
            if np.any(w_closed) and np.mean(gpm[i][w_closed]) > self.clg_leak_thresh:
                flags[i] = 1
                continue

            # Rule 2: Uncommanded coil heat transfer
            w_no_cmd = (cvlv[i] < 0.01) & (hvlv[i] < 0.01) & (spd[i] > 1.0)
            if np.any(w_no_cmd) and np.mean(np.abs(dat[i][w_no_cmd] - mat[i][w_no_cmd])) > self.coil_dt_thresh:
                flags[i] = 1
                continue

            # Rule 3: Airflow restriction (CFM / SPD significantly reduced)
            w_active_fan = spd[i] > 2.0
            if np.any(w_active_fan):
                mean_ratio = np.mean(cfm[i][w_active_fan] / (spd[i][w_active_fan] + 1e-4))
                if mean_ratio < self.airflow_ratio_min:
                    flags[i] = 1
                    continue

            # Rule 4: Outdoor damper leak (closed damper but mixed air shifts toward outdoor air)
            w_closed_dmpr = (dmpr[i] < 0.01) & (spd[i] > 1.0) & (np.abs(oat[i] - rat[i]) > 10.0)
            if np.any(w_closed_dmpr):
                # When OA damper is 0, MAT should closely track RAT
                mat_rat_diff = np.mean(np.abs(mat[i][w_closed_dmpr] - rat[i][w_closed_dmpr]))
                if mat_rat_diff > self.dmpr_leak_dt_thresh:
                    flags[i] = 1
                    continue

        return flags


class Conv1dAutoencoder(nn.Module):
    """Compact temporal 1D-CNN autoencoder for sequence anomaly scoring."""

    def __init__(self, in_channels: int, seq_len: int):
        super().__init__()
        self.seq_len = seq_len
        self.encoder = nn.Sequential(
            nn.Conv1d(in_channels, 16, kernel_size=3, padding=1),
            nn.BatchNorm1d(16),
            nn.ReLU(),
            nn.Conv1d(16, 8, kernel_size=3, padding=1),
            nn.ReLU()
        )
        self.decoder = nn.Sequential(
            nn.ConvTranspose1d(8, 16, kernel_size=3, padding=1),
            nn.BatchNorm1d(16),
            nn.ReLU(),
            nn.ConvTranspose1d(16, in_channels, kernel_size=3, padding=1)
        )

    def forward(self, x):
        # x: (batch, channels, seq_len)
        latent = self.encoder(x)
        recon = self.decoder(latent)
        return recon


def extract_classical_features(windows_3d: np.ndarray) -> np.ndarray:
    """Extracts summary statistics (mean, std, min, max, delta) per channel for tabular ML."""
    # windows_3d: (N, W, C)
    means = np.mean(windows_3d, axis=1)
    stds = np.std(windows_3d, axis=1)
    mins = np.min(windows_3d, axis=1)
    maxs = np.max(windows_3d, axis=1)
    deltas = windows_3d[:, -1, :] - windows_3d[:, 0, :]
    return np.hstack([means, stds, mins, maxs, deltas])


def run_experiment_for_rate(data_dir: Path, freq_str: str, window_len: int) -> dict:
    """Executes the 3-model pilot evaluation for a specific sampling rate."""
    print(f"\n==========================================")
    print(f"RUNNING PILOT FOR SAMPLING RATE: {freq_str} (Window: {window_len} steps = 60 mins)")
    print(f"==========================================")

    # 1. Load Baseline and split contiguously
    ff_path = data_dir / "FCU_FaultFree.csv"
    t_start = time.time()
    df_ff = load_and_resample(ff_path, freq_str)
    windows_ff, _ = create_windows(df_ff, window_len, MODEL_CHANNELS)
    total_ff_win = len(windows_ff)

    # Contiguous temporal splits
    n_train = int(total_ff_win * 0.60)
    n_calib = int(total_ff_win * 0.15)
    n_test = total_ff_win - n_train - n_calib

    win_train = windows_ff[:n_train]
    win_calib = windows_ff[n_train:n_train + n_calib]
    win_test_ff = windows_ff[n_train + n_calib:]

    print(f"Normal Windows: Train={len(win_train)}, Calib={len(win_calib)}, Untouched Test={len(win_test_ff)}")

    # Channel indices dictionary
    ch_idx = {col: i for i, col in enumerate(MODEL_CHANNELS)}

    # Normalization fitted on training normal windows only
    norm_mean = np.mean(win_train, axis=(0, 1), keepdims=True)
    norm_std = np.std(win_train, axis=(0, 1), keepdims=True) + 1e-6

    # ----------------------------------------------------
    # APPROACH 1: Physical Rules
    # ----------------------------------------------------
    t_rules_0 = time.time()
    rule_detector = PhysicalRuleDetector()
    rule_detector.fit_thresholds(win_train, ch_idx)
    rule_test_flags = rule_detector.evaluate_windows(win_test_ff, ch_idx)
    rule_far_pct = round(float(np.mean(rule_test_flags) * 100.0), 3)
    rule_fit_eval_time = time.time() - t_rules_0

    # ----------------------------------------------------
    # APPROACH 2: Classical ML (Isolation Forest)
    # ----------------------------------------------------
    t_ml_0 = time.time()
    feat_train = extract_classical_features(win_train)
    feat_calib = extract_classical_features(win_calib)
    feat_test_ff = extract_classical_features(win_test_ff)

    iso_forest = IsolationForest(n_estimators=100, random_state=42, n_jobs=-1)
    iso_forest.fit(feat_train)

    # Anomaly scores: negative decision function (higher = more abnormal)
    calib_scores_ml = -iso_forest.decision_function(feat_calib)
    threshold_ml = float(np.percentile(calib_scores_ml, 99.5))

    test_scores_ml_ff = -iso_forest.decision_function(feat_test_ff)
    ml_far_pct = round(float(np.mean(test_scores_ml_ff > threshold_ml) * 100.0), 3)
    ml_fit_eval_time = time.time() - t_ml_0

    # ----------------------------------------------------
    # APPROACH 3: Temporal DL Probe (1D-CNN Autoencoder)
    # ----------------------------------------------------
    t_dl_0 = time.time()
    train_norm = (win_train - norm_mean) / norm_std
    calib_norm = (win_calib - norm_mean) / norm_std
    test_ff_norm = (win_test_ff - norm_mean) / norm_std

    # PyTorch format: (batch, channels, seq_len)
    X_train_t = torch.tensor(train_norm.transpose(0, 2, 1), dtype=torch.float32)
    X_calib_t = torch.tensor(calib_norm.transpose(0, 2, 1), dtype=torch.float32)
    X_test_ff_t = torch.tensor(test_ff_norm.transpose(0, 2, 1), dtype=torch.float32)

    torch.manual_seed(42)
    model = Conv1dAutoencoder(in_channels=len(MODEL_CHANNELS), seq_len=window_len)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.003)
    criterion = nn.MSELoss()

    dataset = TensorDataset(X_train_t)
    loader = DataLoader(dataset, batch_size=64, shuffle=True)

    # Quick 5-epoch training
    model.train()
    for epoch in range(5):
        for batch in loader:
            optimizer.zero_grad()
            recon = model(batch[0])
            loss = criterion(recon, batch[0])
            loss.backward()
            optimizer.step()

    model.eval()
    with torch.no_grad():
        calib_recon = model(X_calib_t)
        calib_errors = torch.mean((calib_recon - X_calib_t) ** 2, dim=(1, 2)).numpy()
        threshold_dl = float(np.percentile(calib_errors, 99.5))

        test_recon_ff = model(X_test_ff_t)
        test_errors_ff = torch.mean((test_recon_ff - X_test_ff_t) ** 2, dim=(1, 2)).numpy()
        dl_far_pct = round(float(np.mean(test_errors_ff > threshold_dl) * 100.0), 3)

    dl_fit_eval_time = time.time() - t_dl_0

    # ----------------------------------------------------
    # EVALUATION ACROSS FAULT SCENARIOS
    # ----------------------------------------------------
    scenarios = [
        ("FCU_VLVLeak_Cooling_20.csv", "Valve Leak (Cooling 20%)"),
        ("FCU_Fouling_Cooling_Airside_Minor.csv", "Coil Fouling (Airside Minor)"),
        ("FCU_FilterRestriction_10%.csv", "Filter Restriction (Airflow 10%)"),
        ("FCU_SensorBias_RMTemp_+2C.csv", "Sensor Bias (Room Temp +2C)"),
        ("FCU_OADMPRLeak_20.csv", "Damper Leak (Outdoor Air 20%)")
    ]

    scenario_results = {}
    rule_detections = []
    ml_detections = []
    dl_detections = []

    for fname, desc in scenarios:
        fpath = data_dir / fname
        if not fpath.exists():
            print(f"Scenario file not found: {fname}")
            continue

        df_sc = load_and_resample(fpath, freq_str)
        windows_sc, _ = create_windows(df_sc, window_len, MODEL_CHANNELS)
        # Evaluate on matching test period
        win_test_sc = windows_sc[n_train + n_calib:]

        # Physical Rules detection
        flags_rule = rule_detector.evaluate_windows(win_test_sc, ch_idx)
        det_rule_pct = round(float(np.mean(flags_rule) * 100.0), 2)
        rule_detections.append(det_rule_pct)

        # Classical ML detection
        feat_sc = extract_classical_features(win_test_sc)
        scores_ml_sc = -iso_forest.decision_function(feat_sc)
        det_ml_pct = round(float(np.mean(scores_ml_sc > threshold_ml) * 100.0), 2)
        ml_detections.append(det_ml_pct)

        # Temporal DL probe detection
        sc_norm = (win_test_sc - norm_mean) / norm_std
        X_sc_t = torch.tensor(sc_norm.transpose(0, 2, 1), dtype=torch.float32)
        with torch.no_grad():
            recon_sc = model(X_sc_t)
            err_sc = torch.mean((recon_sc - X_sc_t) ** 2, dim=(1, 2)).numpy()
            det_dl_pct = round(float(np.mean(err_sc > threshold_dl) * 100.0), 2)
        dl_detections.append(det_dl_pct)

        scenario_results[fname] = {
            "fault_name": desc,
            "test_windows": len(win_test_sc),
            "detection_rates": {
                "physical_rules_pct": det_rule_pct,
                "classical_ml_pct": det_ml_pct,
                "temporal_dl_probe_pct": det_dl_pct
            }
        }
        print(f"  {desc:<35} | Rules: {det_rule_pct:6.2f}% | ML: {det_ml_pct:6.2f}% | DL: {det_dl_pct:6.2f}%")

    macro_rules = round(float(np.mean(rule_detections)), 2)
    macro_ml = round(float(np.mean(ml_detections)), 2)
    macro_dl = round(float(np.mean(dl_detections)), 2)

    return {
        "sampling_rate": freq_str,
        "window_steps": window_len,
        "window_duration_mins": 60,
        "windows_count": {
            "train": len(win_train),
            "calibration": len(win_calib),
            "untouched_test": len(win_test_ff)
        },
        "false_alarm_rate_on_untouched_test": {
            "physical_rules_pct": rule_far_pct,
            "classical_ml_pct": ml_far_pct,
            "temporal_dl_probe_pct": dl_far_pct
        },
        "macro_average_detection_pct": {
            "physical_rules": macro_rules,
            "classical_ml": macro_ml,
            "temporal_dl_probe": macro_dl
        },
        "compute_time_sec": {
            "physical_rules": round(rule_fit_eval_time, 3),
            "classical_ml": round(ml_fit_eval_time, 3),
            "temporal_dl_probe": round(dl_fit_eval_time, 3)
        },
        "scenario_results": scenario_results
    }


def main():
    parser = argparse.ArgumentParser(description="Run Gate 02 modeling value pilot experiment.")
    parser.add_argument("--data-dir", type=str, default="tmp/fcu_data", help="Directory containing extracted FCU CSVs.")
    parser.add_argument("--out-json", type=str, default="validation/review/evidence/pilot_evaluation_summary.json", help="Path to save summary JSON.")
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    if not data_dir.exists():
        raise FileNotFoundError(f"Data directory does not exist: {data_dir.resolve()}")

    rates = [
        ("15min", 4),   # 4 steps * 15m = 60 mins
        ("5min", 12),   # 12 steps * 5m = 60 mins
        ("1min", 60)    # 60 steps * 1m = 60 mins
    ]

    all_results = {}
    for freq_str, w_len in rates:
        res = run_experiment_for_rate(data_dir, freq_str, w_len)
        all_results[freq_str] = res

    out_json = Path(args.out_json)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2)

    print(f"\n==========================================")
    print(f"PILOT EXPERIMENT COMPLETE")
    print(f"Results saved to: {out_json.resolve()}")
    print(f"==========================================")


if __name__ == "__main__":
    main()
