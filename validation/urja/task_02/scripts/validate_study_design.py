#!/usr/bin/env python3
"""
Urja Task 2 — Experiment Design, Panel Structure & Outcome Suitability Validation Script

This script audits the experimental design, household panel structure, treatment
allocation, and outcome availability for Project Urja without modifying raw files.

Outputs generated:
    1. treatment_assignment_audit.csv
    2. sample_flow_by_round.csv
    3. household_panel_integrity.csv
    4. outcome_availability_by_round_treatment.csv
    5. household_outcome_coverage.csv
    6. attrition_and_followup_audit.csv

Usage:
    python scripts/validate_study_design.py --raw-dir <path_to_raw_data> --output-dir <path_to_reports>
"""

import argparse
import io
import os
import sys
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd


TREATMENT_MAPPING = {
    0: "Control group (T0)",
    1: "Neighbor comparison treatment (T1)",
    2: "Suburb comparison treatment (T2)",
    3: "Knowledge / information treatment (T3)",
}

ROUND_MAPPING = {
    0: "Round 0",
    1: "Round 1",
    2: "Round 2",
    3: "Round 3",
    4: "Round 4",
    5: "Round 5",
    6: "Round 6",
}


def load_dataset(raw_dir: Path) -> pd.DataFrame:
    """Load replication_data.dta from zip archive in raw_dir in-memory."""
    if not raw_dir.exists():
        raise FileNotFoundError(f"Raw directory does not exist: {raw_dir}")

    # Look for zip file
    zip_files = list(raw_dir.glob("*.zip"))
    if zip_files:
        archive_path = zip_files[0]
        with zipfile.ZipFile(archive_path, "r") as z:
            target_name = None
            for name in z.namelist():
                if name.endswith("replication_data.dta") and not name.startswith("__MACOSX"):
                    target_name = name
                    break
            if not target_name:
                raise FileNotFoundError(f"replication_data.dta not found in archive {archive_path}")
            with z.open(target_name) as f:
                reader = pd.io.stata.StataReader(io.BytesIO(f.read()))
                df = reader.read()
                return df

    # Alternatively look for uncompressed dta file
    dta_files = list(raw_dir.rglob("replication_data.dta"))
    if dta_files:
        return pd.read_stata(dta_files[0])

    raise FileNotFoundError(f"No archive or replication_data.dta found in {raw_dir}")


def audit_treatment_assignment(df: pd.DataFrame) -> pd.DataFrame:
    """Audit treatment assignment, consistency, and neighborhood distribution."""
    required_cols = ["hid", "round", "nid", "treatment"]
    for col in required_cols:
        if col not in df.columns:
            raise KeyError(f"Missing required column for treatment audit: {col}")

    # Standardize treatment names if categorical or numeric
    treat_series = df["treatment"].astype(str)

    results = []

    # Overall counts
    total_obs = len(df)
    unique_hids = df["hid"].nunique()

    # Per treatment group counts
    for t_val in sorted(treat_series.unique()):
        sub = df[treat_series == t_val]
        hids_in_t = sub["hid"].nunique()
        obs_in_t = len(sub)
        r0_hids = sub[sub["round"].isin(["Round 0", 0])]["hid"].nunique()
        r1_hids = sub[sub["round"].isin(["Round 1", 1])]["hid"].nunique()

        results.append({
            "metric_type": "treatment_group_summary",
            "treatment_group": t_val,
            "unique_households": hids_in_t,
            "total_observations": obs_in_t,
            "baseline_r0_households": r0_hids,
            "baseline_r1_households": r1_hids,
            "attrited_households": r0_hids - r1_hids,
            "attrition_rate_pct": round(((r0_hids - r1_hids) / r0_hids) * 100, 2) if r0_hids > 0 else 0.0,
            "share_of_total_households_pct": round((hids_in_t / unique_hids) * 100, 2) if unique_hids > 0 else 0.0,
        })

    # Within-household consistency check
    treat_per_hid = df.groupby("hid")["treatment"].nunique()
    inconsistent_hids = int((treat_per_hid > 1).sum())

    # Neighborhood distribution check
    # Check if multiple treatments exist within neighborhoods in Round 1
    r1_df = df[df["round"].isin(["Round 1", 1])]
    nid_treat_matrix = r1_df.groupby(["nid", "treatment"], observed=False).size().unstack(fill_value=0)
    treats_per_nid = (nid_treat_matrix > 0).sum(axis=1)

    nids_with_4_treatments = int((treats_per_nid == 4).sum())
    nids_with_3_treatments = int((treats_per_nid == 3).sum())
    nids_with_less = int((treats_per_nid < 3).sum())

    results.append({
        "metric_type": "design_structural_summary",
        "treatment_group": "ALL_GROUPS_COMBINED",
        "unique_households": unique_hids,
        "total_observations": total_obs,
        "baseline_r0_households": df[df["round"].isin(["Round 0", 0])]["hid"].nunique(),
        "baseline_r1_households": df[df["round"].isin(["Round 1", 1])]["hid"].nunique(),
        "attrited_households": inconsistent_hids,  # reused field for consistency check = 0
        "attrition_rate_pct": float(inconsistent_hids),  # 0 indicates 100% consistent
        "share_of_total_households_pct": 100.0,
    })

    return pd.DataFrame(results)


def audit_sample_flow_by_round(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate sample flow and observation counts by round."""
    rows = []
    round_order = sorted(df["round"].unique(), key=lambda x: str(x))

    for r in round_order:
        sub = df[df["round"] == r]
        n_obs = len(sub)
        n_hid = sub["hid"].nunique()

        # Attrition breakdown
        n_attrited = 0
        n_remained = 0
        if "attrited" in sub.columns:
            attr_counts = sub["attrited"].value_counts()
            for k, v in attr_counts.items():
                if "attrited" in str(k).lower() or str(k) in ["1", "1.0"]:
                    n_attrited += v
                else:
                    n_remained += v

        # Followup breakdown
        n_fup = 0
        n_not_fup = 0
        if "followup" in sub.columns:
            fup_valid = sub["followup"].dropna()
            for k, v in fup_valid.value_counts().items():
                if "followed up" in str(k).lower() and "not" not in str(k).lower() or str(k) in ["1", "1.0"]:
                    n_fup += v
                else:
                    n_not_fup += v

        # Outcomes observed
        sbill_obs = int(sub["sbill"].notna().sum()) if "sbill" in sub.columns else 0
        rbill_obs = int(sub["rbill"].notna().sum()) if "rbill" in sub.columns else 0
        runit_obs = int(sub["runit"].notna().sum()) if "runit" in sub.columns else 0

        rows.append({
            "round": str(r),
            "total_observations": n_obs,
            "unique_households": n_hid,
            "attrited_indicator_count": n_attrited,
            "remained_indicator_count": n_remained,
            "scrutinized_followup_count": n_fup,
            "non_scrutinized_count": n_not_fup,
            "sbill_observed_count": sbill_obs,
            "rbill_observed_count": rbill_obs,
            "runit_observed_count": runit_obs,
        })

    return pd.DataFrame(rows)


def audit_household_panel_integrity(df: pd.DataFrame) -> pd.DataFrame:
    """Audit key uniqueness, observations per household, and consistency."""
    total_rows = len(df)
    unique_hids = df["hid"].nunique()
    missing_hids = int(df["hid"].isna().sum())
    missing_rounds = int(df["round"].isna().sum())
    dup_keys = int(df.duplicated(subset=["hid", "round"]).sum())

    obs_per_hid = df.groupby("hid").size()
    hids_with_7_rounds = int((obs_per_hid == 7).sum())
    hids_with_1_round = int((obs_per_hid == 1).sum())
    hids_with_other_rounds = int(((obs_per_hid != 7) & (obs_per_hid != 1)).sum())

    # Consistency checks within hid
    inconsistent_treatment = int((df.groupby("hid")["treatment"].nunique() > 1).sum())
    inconsistent_nid = int((df.groupby("hid")["nid"].nunique() > 1).sum())
    inconsistent_suburb = int((df.groupby("hid")["suburb"].nunique() > 1).sum())
    inconsistent_city = int((df.groupby("hid")["city"].nunique() > 1).sum())
    inconsistent_attrited = int((df.groupby("hid")["attrited"].nunique() > 1).sum())

    # Check followup consistency in Rounds 5 and 6
    df_r56 = df[df["round"].isin(["Round 5", 5, "Round 6", 6])]
    inconsistent_followup = int((df_r56.groupby("hid")["followup"].nunique() > 1).sum())

    summary_rows = [
        {"check_category": "Key Uniqueness", "metric_name": "total_records", "metric_value": total_rows, "status": "PASS"},
        {"check_category": "Key Uniqueness", "metric_name": "unique_households", "metric_value": unique_hids, "status": "PASS"},
        {"check_category": "Key Uniqueness", "metric_name": "missing_household_ids", "metric_value": missing_hids, "status": "PASS" if missing_hids == 0 else "FAIL"},
        {"check_category": "Key Uniqueness", "metric_name": "missing_round_ids", "metric_value": missing_rounds, "status": "PASS" if missing_rounds == 0 else "FAIL"},
        {"check_category": "Key Uniqueness", "metric_name": "duplicate_hid_round_pairs", "metric_value": dup_keys, "status": "PASS" if dup_keys == 0 else "FAIL"},
        {"check_category": "Panel Structure", "metric_name": "households_with_7_rounds", "metric_value": hids_with_7_rounds, "status": "VERIFIED"},
        {"check_category": "Panel Structure", "metric_name": "households_with_1_round_attrited", "metric_value": hids_with_1_round, "status": "VERIFIED"},
        {"check_category": "Panel Structure", "metric_name": "households_with_partial_rounds_2_to_6", "metric_value": hids_with_other_rounds, "status": "PASS" if hids_with_other_rounds == 0 else "WARNING"},
        {"check_category": "Attribute Consistency", "metric_name": "inconsistent_treatment_within_household", "metric_value": inconsistent_treatment, "status": "PASS" if inconsistent_treatment == 0 else "FAIL"},
        {"check_category": "Attribute Consistency", "metric_name": "inconsistent_neighborhood_within_household", "metric_value": inconsistent_nid, "status": "PASS" if inconsistent_nid == 0 else "FAIL"},
        {"check_category": "Attribute Consistency", "metric_name": "inconsistent_suburb_within_household", "metric_value": inconsistent_suburb, "status": "PASS" if inconsistent_suburb == 0 else "FAIL"},
        {"check_category": "Attribute Consistency", "metric_name": "inconsistent_city_within_household", "metric_value": inconsistent_city, "status": "PASS" if inconsistent_city == 0 else "FAIL"},
        {"check_category": "Attribute Consistency", "metric_name": "inconsistent_attrition_indicator_within_household", "metric_value": inconsistent_attrited, "status": "PASS" if inconsistent_attrited == 0 else "FAIL"},
        {"check_category": "Attribute Consistency", "metric_name": "inconsistent_followup_indicator_within_household_r5_r6", "metric_value": inconsistent_followup, "status": "PASS" if inconsistent_followup == 0 else "FAIL"},
    ]

    return pd.DataFrame(summary_rows)


def audit_outcome_availability(df: pd.DataFrame) -> pd.DataFrame:
    """Generate round x treatment availability table for outcomes."""
    outcomes = ["runit", "rbill", "sbill"]
    rows = []

    for outcome in outcomes:
        if outcome not in df.columns:
            continue

        grouped = df.groupby(["round", "treatment"], observed=False)[outcome].agg(
            total="size",
            observed=lambda s: int(s.notna().sum()),
            missing=lambda s: int(s.isna().sum()),
        ).reset_index()

        for _, row in grouped.iterrows():
            total_n = row["total"]
            obs_n = row["observed"]
            miss_n = row["missing"]
            obs_pct = round((obs_n / total_n) * 100, 2) if total_n > 0 else 0.0
            miss_pct = round((miss_n / total_n) * 100, 2) if total_n > 0 else 0.0

            rows.append({
                "outcome_variable": outcome,
                "round": str(row["round"]),
                "treatment_group": str(row["treatment"]),
                "total_observations": total_n,
                "observed_count": obs_n,
                "missing_count": miss_n,
                "observed_pct": obs_pct,
                "missing_pct": miss_pct,
            })

    return pd.DataFrame(rows)


def audit_household_coverage(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate household-level outcome coverage across intended rounds."""
    # Retained households are those present in Round 1 (2,248 households)
    retained_hids = df[df["round"].isin(["Round 1", 1])]["hid"].unique()
    retained_df = df[df["hid"].isin(retained_hids)]
    all_hids = df["hid"].unique()

    rows = []

    # 1. sbill: intended rounds are Round 0 and Round 1
    sbill_r0_r1 = (
        df[df["round"].isin(["Round 0", 0, "Round 1", 1])]
        .groupby("hid")["sbill"]
        .count()
        .reindex(all_hids, fill_value=0)
    )
    rows.append({
        "outcome_variable": "sbill",
        "evaluation_period": "Pre-baseline & Baseline (Rounds 0 & 1)",
        "target_universe": "All Recruited Households",
        "target_sample_size": len(all_hids),
        "at_least_one_observed": int((sbill_r0_r1 >= 1).sum()),
        "zero_observed": int((sbill_r0_r1 == 0).sum()),
        "observed_all_intended_rounds": int((sbill_r0_r1 == 2).sum()),
        "missing_one_or_more_intended_rounds": int((sbill_r0_r1 < 2).sum()),
        "coverage_all_intended_pct": round(((sbill_r0_r1 == 2).sum() / len(all_hids)) * 100, 2),
    })

    # 2. runit: Main intervention period (Rounds 1 to 4)
    runit_main = (
        retained_df[retained_df["round"].isin(["Round 1", 1, "Round 2", 2, "Round 3", 3, "Round 4", 4])]
        .groupby("hid")["runit"]
        .count()
        .reindex(retained_hids, fill_value=0)
    )
    rows.append({
        "outcome_variable": "runit",
        "evaluation_period": "Main Intervention Period (Rounds 1 to 4)",
        "target_universe": "Retained Panel Households",
        "target_sample_size": len(retained_hids),
        "at_least_one_observed": int((runit_main >= 1).sum()),
        "zero_observed": int((runit_main == 0).sum()),
        "observed_all_intended_rounds": int((runit_main == 4).sum()),
        "missing_one_or_more_intended_rounds": int((runit_main < 4).sum()),
        "coverage_all_intended_pct": round(((runit_main == 4).sum() / len(retained_hids)) * 100, 2),
    })

    # 3. runit: Full evaluation including long-term (Rounds 1, 2, 3, 4, 6)
    runit_full = (
        retained_df[retained_df["round"].isin(["Round 1", 1, "Round 2", 2, "Round 3", 3, "Round 4", 4, "Round 6", 6])]
        .groupby("hid")["runit"]
        .count()
        .reindex(retained_hids, fill_value=0)
    )
    rows.append({
        "outcome_variable": "runit",
        "evaluation_period": "Full Longitudinal Evaluation (Rounds 1, 2, 3, 4, 6)",
        "target_universe": "Retained Panel Households",
        "target_sample_size": len(retained_hids),
        "at_least_one_observed": int((runit_full >= 1).sum()),
        "zero_observed": int((runit_full == 0).sum()),
        "observed_all_intended_rounds": int((runit_full == 5).sum()),
        "missing_one_or_more_intended_rounds": int((runit_full < 5).sum()),
        "coverage_all_intended_pct": round(((runit_full == 5).sum() / len(retained_hids)) * 100, 2),
    })

    # 4. rbill: Main intervention period (Rounds 1 to 4)
    rbill_main = (
        retained_df[retained_df["round"].isin(["Round 1", 1, "Round 2", 2, "Round 3", 3, "Round 4", 4])]
        .groupby("hid")["rbill"]
        .count()
        .reindex(retained_hids, fill_value=0)
    )
    rows.append({
        "outcome_variable": "rbill",
        "evaluation_period": "Main Intervention Period (Rounds 1 to 4)",
        "target_universe": "Retained Panel Households",
        "target_sample_size": len(retained_hids),
        "at_least_one_observed": int((rbill_main >= 1).sum()),
        "zero_observed": int((rbill_main == 0).sum()),
        "observed_all_intended_rounds": int((rbill_main == 4).sum()),
        "missing_one_or_more_intended_rounds": int((rbill_main < 4).sum()),
        "coverage_all_intended_pct": round(((rbill_main == 4).sum() / len(retained_hids)) * 100, 2),
    })

    # 5. rbill: Full evaluation including long-term (Rounds 1, 2, 3, 4, 6)
    rbill_full = (
        retained_df[retained_df["round"].isin(["Round 1", 1, "Round 2", 2, "Round 3", 3, "Round 4", 4, "Round 6", 6])]
        .groupby("hid")["rbill"]
        .count()
        .reindex(retained_hids, fill_value=0)
    )
    rows.append({
        "outcome_variable": "rbill",
        "evaluation_period": "Full Longitudinal Evaluation (Rounds 1, 2, 3, 4, 6)",
        "target_universe": "Retained Panel Households",
        "target_sample_size": len(retained_hids),
        "at_least_one_observed": int((rbill_full >= 1).sum()),
        "zero_observed": int((rbill_full == 0).sum()),
        "observed_all_intended_rounds": int((rbill_full == 5).sum()),
        "missing_one_or_more_intended_rounds": int((rbill_full < 5).sum()),
        "coverage_all_intended_pct": round(((rbill_full == 5).sum() / len(retained_hids)) * 100, 2),
    })

    return pd.DataFrame(rows)


def audit_attrition_and_followup(df: pd.DataFrame) -> pd.DataFrame:
    """Audit attrition and follow-up participation by treatment, city, and suburb."""
    r0 = df[df["round"].isin(["Round 0", 0])]
    r1 = df[df["round"].isin(["Round 1", 1])]
    r5 = df[df["round"].isin(["Round 5", 5])]

    rows = []

    # 1. Overall
    tot_r0 = len(r0)
    tot_r1 = len(r1)
    tot_attr = tot_r0 - tot_r1

    is_fup = (
        (r5["followup"].astype(str).str.strip() == "Followed up")
        | (r5["followup"].isin([1, 1.0, "1"]))
    ) if "followup" in r5.columns else pd.Series(False, index=r5.index)

    fup_count = int(is_fup.sum())

    rows.append({
        "group_level": "OVERALL",
        "stratum_name": "Full Sample",
        "initial_sample_r0": tot_r0,
        "retained_sample_r1": tot_r1,
        "attrited_count": tot_attr,
        "attrition_rate_pct": round((tot_attr / tot_r0) * 100, 2),
        "scrutinized_followup_sample_r5": fup_count,
        "followup_share_of_retained_pct": round((fup_count / tot_r1) * 100, 2),
    })

    # 2. By treatment group
    for t in sorted(r0["treatment"].astype(str).unique()):
        t_r0 = int((r0["treatment"].astype(str) == t).sum())
        t_r1 = int((r1["treatment"].astype(str) == t).sum())
        t_attr = t_r0 - t_r1
        t_fup = int(((r5["treatment"].astype(str) == t) & is_fup).sum())

        rows.append({
            "group_level": "TREATMENT_GROUP",
            "stratum_name": t,
            "initial_sample_r0": t_r0,
            "retained_sample_r1": t_r1,
            "attrited_count": t_attr,
            "attrition_rate_pct": round((t_attr / t_r0) * 100, 2),
            "scrutinized_followup_sample_r5": t_fup,
            "followup_share_of_retained_pct": round((t_fup / t_r1) * 100, 2) if t_r1 > 0 else 0.0,
        })

    # 3. By city
    for c in sorted(r0["city"].astype(str).unique()):
        c_r0 = int((r0["city"].astype(str) == c).sum())
        c_r1 = int((r1["city"].astype(str) == c).sum())
        c_attr = c_r0 - c_r1
        c_fup = int(((r5["city"].astype(str) == c) & is_fup).sum())

        rows.append({
            "group_level": "CITY",
            "stratum_name": c,
            "initial_sample_r0": c_r0,
            "retained_sample_r1": c_r1,
            "attrited_count": c_attr,
            "attrition_rate_pct": round((c_attr / c_r0) * 100, 2),
            "scrutinized_followup_sample_r5": c_fup,
            "followup_share_of_retained_pct": round((c_fup / c_r1) * 100, 2) if c_r1 > 0 else 0.0,
        })

    return pd.DataFrame(rows)


def run_validation(raw_dir: Path, output_dir: Path) -> None:
    """Run full validation suite and write CSV reports."""
    output_dir.mkdir(parents=True, exist_ok=True)
    df = load_dataset(raw_dir)

    print(f"Loaded dataset successfully. Rows: {len(df)}, Cols: {len(df.columns)}")

    # 1. Treatment assignment audit
    df_treatment = audit_treatment_assignment(df)
    p_treat = output_dir / "treatment_assignment_audit.csv"
    df_treatment.to_csv(p_treat, index=False)
    print(f"Generated: {p_treat} ({len(df_treatment)} rows)")

    # 2. Sample flow by round
    df_flow = audit_sample_flow_by_round(df)
    p_flow = output_dir / "sample_flow_by_round.csv"
    df_flow.to_csv(p_flow, index=False)
    print(f"Generated: {p_flow} ({len(df_flow)} rows)")

    # 3. Household panel integrity
    df_panel = audit_household_panel_integrity(df)
    p_panel = output_dir / "household_panel_integrity.csv"
    df_panel.to_csv(p_panel, index=False)
    print(f"Generated: {p_panel} ({len(df_panel)} rows)")

    # 4. Outcome availability by round and treatment
    df_avail = audit_outcome_availability(df)
    p_avail = output_dir / "outcome_availability_by_round_treatment.csv"
    df_avail.to_csv(p_avail, index=False)
    print(f"Generated: {p_avail} ({len(df_avail)} rows)")

    # 5. Household outcome coverage
    df_cov = audit_household_coverage(df)
    p_cov = output_dir / "household_outcome_coverage.csv"
    df_cov.to_csv(p_cov, index=False)
    print(f"Generated: {p_cov} ({len(df_cov)} rows)")

    # 6. Attrition and follow-up audit
    df_attr = audit_attrition_and_followup(df)
    p_attr = output_dir / "attrition_and_followup_audit.csv"
    df_attr.to_csv(p_attr, index=False)
    print(f"Generated: {p_attr} ({len(df_attr)} rows)")


def main():
    parser = argparse.ArgumentParser(
        description="Urja Task 2 Study Design & Panel Validation Script"
    )
    parser.add_argument(
        "--raw-dir",
        type=Path,
        required=True,
        help="Path to raw dataset directory containing ZIP archive or dta file",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("validation/urja/task_02/reports"),
        help="Path to reports output directory",
    )

    args = parser.parse_args()

    print(f"Starting Task 2 study design validation...")
    print(f"Raw directory: {args.raw_dir}")
    print(f"Output directory: {args.output_dir}")

    run_validation(args.raw_dir, args.output_dir)
    print("Task 2 study design audit completed successfully.")


if __name__ == "__main__":
    main()
