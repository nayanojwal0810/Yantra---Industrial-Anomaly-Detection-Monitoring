"""
Unit tests for Urja Task 2 Study Design & Panel Structure Validation.

These tests use synthetic data fixtures and temporary files.
They do not depend on or modify the actual research dataset.
"""

import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from validation.urja.task_02.scripts.validate_study_design import (
    audit_attrition_and_followup,
    audit_household_coverage,
    audit_household_panel_integrity,
    audit_outcome_availability,
    audit_sample_flow_by_round,
    audit_treatment_assignment,
    run_validation,
)


class TestValidateStudyDesign(unittest.TestCase):
    """Test suite for experimental design and panel validation functions."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

        # Create synthetic panel dataframe resembling replication_data.dta
        # 4 households:
        # hh 1, 2, 3: 7 rounds (Round 0 to Round 6) - retained
        # hh 4: 1 round (Round 0 only) - attrited
        data = []

        # Retained households (hh 1 in T0, hh 2 in T1, hh 3 in T2)
        treatments = {1: "T0", 2: "T1", 3: "T2", 4: "T3"}
        for h in [1, 2, 3]:
            for r in range(7):
                r_name = f"Round {r}"
                is_fup = "Followed up" if (r in [5, 6] and h == 1) else "Not followed up" if r in [5, 6] else np.nan
                sbill = 1000.0 + h * 10 if r in [0, 1] else np.nan
                rbill = 950.0 + h * 10 + r * 5 if r in [1, 2, 3, 4, 6] else np.nan
                runit = 150.0 + h * 2 + r if r in [1, 2, 3, 4, 6] else np.nan

                data.append({
                    "hid": h,
                    "round": r_name,
                    "nid": 101,
                    "suburb": "Suburb_A",
                    "city": "City_A",
                    "attrited": "Remained",
                    "treatment": treatments[h],
                    "followup": is_fup,
                    "sbill": sbill,
                    "rbill": rbill,
                    "runit": runit,
                })

        # Attrited household (hh 4 in T3, Round 0 only)
        data.append({
            "hid": 4,
            "round": "Round 0",
            "nid": 101,
            "suburb": "Suburb_A",
            "city": "City_A",
            "attrited": "Attrited",
            "treatment": "T3",
            "followup": np.nan,
            "sbill": 1200.0,
            "rbill": np.nan,
            "runit": np.nan,
        })

        self.df_synthetic = pd.DataFrame(data)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_treatment_assignment_counts(self):
        """Test treatment assignment count aggregation across groups."""
        res = audit_treatment_assignment(self.df_synthetic)
        group_rows = res[res["metric_type"] == "treatment_group_summary"]

        self.assertEqual(len(group_rows), 4)
        t_counts = dict(zip(group_rows["treatment_group"], group_rows["unique_households"]))
        self.assertEqual(t_counts["T0"], 1)
        self.assertEqual(t_counts["T1"], 1)
        self.assertEqual(t_counts["T2"], 1)
        self.assertEqual(t_counts["T3"], 1)

    def test_detection_of_changing_treatment_assignment(self):
        """Ensure inconsistent treatment within household is detected."""
        df_inconsistent = self.df_synthetic.copy()
        # Change treatment of household 1 in Round 2
        mask = (df_inconsistent["hid"] == 1) & (df_inconsistent["round"] == "Round 2")
        df_inconsistent.loc[mask, "treatment"] = "T3"

        res = audit_household_panel_integrity(df_inconsistent)
        inconsistent_metric = res[res["metric_name"] == "inconsistent_treatment_within_household"]["metric_value"].values[0]
        self.assertEqual(inconsistent_metric, 1)

    def test_key_uniqueness_and_duplicate_detection(self):
        """Ensure duplicate (hid, round) keys are caught."""
        df_dups = pd.concat([self.df_synthetic, self.df_synthetic.iloc[[0]]], ignore_index=True)
        res = audit_household_panel_integrity(df_dups)
        dup_metric = res[res["metric_name"] == "duplicate_hid_round_pairs"]["metric_value"].values[0]
        self.assertEqual(dup_metric, 1)

    def test_panel_round_counts(self):
        """Verify round-level observation and unique household counts."""
        flow = audit_sample_flow_by_round(self.df_synthetic)
        flow_dict = dict(zip(flow["round"], flow["total_observations"]))

        self.assertEqual(flow_dict["Round 0"], 4)
        self.assertEqual(flow_dict["Round 1"], 3)
        self.assertEqual(flow_dict["Round 6"], 3)

    def test_missingness_by_round_and_treatment(self):
        """Verify availability matrix across rounds and treatments."""
        avail = audit_outcome_availability(self.df_synthetic)
        # Check that sbill in Round 0 has 0 missing
        sbill_r0 = avail[(avail["outcome_variable"] == "sbill") & (avail["round"] == "Round 0")]
        self.assertEqual(sbill_r0["missing_count"].sum(), 0)

        # Check that rbill in Round 0 has 100% missing
        rbill_r0 = avail[(avail["outcome_variable"] == "rbill") & (avail["round"] == "Round 0")]
        self.assertEqual(rbill_r0["observed_count"].sum(), 0)

    def test_household_outcome_coverage(self):
        """Verify household coverage calculation across periods."""
        cov = audit_household_coverage(self.df_synthetic)
        cov_map = dict(zip(cov["outcome_variable"] + "_" + cov["evaluation_period"], cov["observed_all_intended_rounds"]))

        # For retained hhs (3 total), all 3 have complete runit in R1-R4
        self.assertEqual(cov_map["runit_Main Intervention Period (Rounds 1 to 4)"], 3)
        # For retained hhs, all 3 have complete runit in R1, R2, R3, R4, R6
        self.assertEqual(cov_map["runit_Full Longitudinal Evaluation (Rounds 1, 2, 3, 4, 6)"], 3)

    def test_attrition_calculation(self):
        """Verify attrition and follow-up calculation."""
        attr = audit_attrition_and_followup(self.df_synthetic)
        overall = attr[attr["group_level"] == "OVERALL"].iloc[0]

        self.assertEqual(overall["initial_sample_r0"], 4)
        self.assertEqual(overall["retained_sample_r1"], 3)
        self.assertEqual(overall["attrited_count"], 1)
        self.assertEqual(overall["attrition_rate_pct"], 25.0)
        self.assertEqual(overall["scrutinized_followup_sample_r5"], 1)

    def test_reconciliation_of_subgroup_totals_to_overall(self):
        """Verify treatment subgroup totals reconcile to overall sample totals."""
        attr = audit_attrition_and_followup(self.df_synthetic)
        overall = attr[attr["group_level"] == "OVERALL"].iloc[0]
        treatments = attr[attr["group_level"] == "TREATMENT_GROUP"]

        self.assertEqual(treatments["initial_sample_r0"].sum(), overall["initial_sample_r0"])
        self.assertEqual(treatments["retained_sample_r1"].sum(), overall["retained_sample_r1"])
        self.assertEqual(treatments["attrited_count"].sum(), overall["attrited_count"])
        self.assertEqual(treatments["scrutinized_followup_sample_r5"].sum(), overall["scrutinized_followup_sample_r5"])

    def test_missing_required_variables_handling(self):
        """Verify that missing critical columns raise explicit errors."""
        df_bad = self.df_synthetic.drop(columns=["treatment"])
        with self.assertRaises(KeyError):
            audit_treatment_assignment(df_bad)

    def test_source_files_unmodified_after_validation(self):
        """Verify that running validation does not modify raw files."""
        # Save synthetic data to temp csv
        raw_csv = self.temp_path / "raw_test.csv"
        self.df_synthetic.to_csv(raw_csv, index=False)
        mtime_before = raw_csv.stat().st_mtime_ns

        # Run checks in memory
        _ = audit_sample_flow_by_round(self.df_synthetic)
        _ = audit_household_panel_integrity(self.df_synthetic)

        mtime_after = raw_csv.stat().st_mtime_ns
        self.assertEqual(mtime_before, mtime_after)


if __name__ == "__main__":
    unittest.main()
