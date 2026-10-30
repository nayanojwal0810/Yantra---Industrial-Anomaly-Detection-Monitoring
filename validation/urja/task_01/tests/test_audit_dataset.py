"""
Unit tests for Urja Task 1 Dataset Audit Script.

These tests verify audit functionality using temporary synthetic files.
They do not depend on or modify the original research dataset.
"""

import csv
import hashlib
import tempfile
import unittest
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

from validation.urja.task_01.scripts.audit_dataset import (
    classify_file_role,
    compute_file_hashes,
    format_bytes,
    profile_dataframe,
    audit_directory,
    write_reports,
)


class TestAuditDataset(unittest.TestCase):
    """Test suite for dataset audit utilities."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_sha256_known_content(self):
        """Test SHA-256 and MD5 hash calculations against known content."""
        test_file = self.temp_path / "known_content.txt"
        test_bytes = b"Urja dataset integrity audit test payload 12345\n"
        test_file.write_bytes(test_bytes)

        expected_md5 = hashlib.md5(test_bytes).hexdigest()
        expected_sha256 = hashlib.sha256(test_bytes).hexdigest()
        expected_size = len(test_bytes)

        calc_md5, calc_sha256, calc_size = compute_file_hashes(test_file)

        self.assertEqual(calc_md5, expected_md5)
        self.assertEqual(calc_sha256, expected_sha256)
        self.assertEqual(calc_size, expected_size)

    def test_format_bytes(self):
        """Test readable byte size formatting."""
        self.assertEqual(format_bytes(500), "500 B")
        self.assertEqual(format_bytes(2048), "2.00 KB")
        self.assertEqual(format_bytes(2145810), "2.05 MB")

    def test_classify_file_role(self):
        """Test file role classification logic."""
        self.assertEqual(
            classify_file_role("0 README.docx"),
            "Documentation / Codebook",
        )
        self.assertEqual(
            classify_file_role("01 JEEM replication codes.do"),
            "Replication Code (Stata script)",
        )
        self.assertEqual(
            classify_file_role("replication_data.dta"),
            "Primary RCT Experimental Dataset",
        )
        self.assertEqual(
            classify_file_role("coord_bangladesh.dta"),
            "GIS Geographic Boundary Data",
        )

    def test_profile_dataframe_missing_and_duplicates(self):
        """Test missing values, duplicate rows, and schema profiling on synthetic data."""
        data = {
            "hh_id": [101, 102, 103, 103, 104],
            "consumption_kwh": [120.5, np.nan, 340.0, 340.0, np.nan],
            "treatment_group": ["T0", "T1", "T2", "T2", "T3"],
            "flag": [1, 0, 1, 1, 0],
        }
        df = pd.DataFrame(data)

        table_profile, schema_rows = profile_dataframe(
            df,
            source_file="synthetic_test.csv",
            table_name="synthetic_test",
            var_labels={"hh_id": "Household ID", "consumption_kwh": "kWh used"},
        )

        # 5 rows total, row 3 and 4 are identical duplicates -> 1 duplicate row
        self.assertEqual(table_profile["total_rows"], 5)
        self.assertEqual(table_profile["total_columns"], 4)
        self.assertEqual(table_profile["fully_duplicated_rows"], 1)
        self.assertEqual(table_profile["missing_cells_total"], 2)
        self.assertEqual(table_profile["fully_readable"], True)

        schema_dict = {row["column_name"]: row for row in schema_rows}
        self.assertEqual(schema_dict["hh_id"]["missing_count"], 0)
        self.assertEqual(schema_dict["hh_id"]["distinct_values"], 4)
        self.assertEqual(schema_dict["consumption_kwh"]["missing_count"], 2)
        self.assertEqual(schema_dict["consumption_kwh"]["missing_pct"], 40.0)
        self.assertEqual(schema_dict["consumption_kwh"]["min_value"], 120.5)
        self.assertEqual(schema_dict["consumption_kwh"]["max_value"], 340.0)

    def test_source_files_unmodified_after_audit(self):
        """Ensure audit execution does not modify or corrupt source files."""
        # Create a synthetic zip archive containing a CSV
        zip_path = self.temp_path / "synthetic_bundle.zip"
        inner_content = b"col1,col2\n10,20\n30,40\n"

        with zipfile.ZipFile(zip_path, "w") as z:
            z.writestr("test_data.csv", inner_content)

        initial_sha256 = hashlib.sha256(zip_path.read_bytes()).hexdigest()
        initial_mtime = zip_path.stat().st_mtime_ns

        reports_dir = self.temp_path / "reports"
        file_rows, table_profiles, schema_rows, sha256_lines = audit_directory(self.temp_path)
        write_reports(reports_dir, file_rows, table_profiles, schema_rows, sha256_lines)

        final_sha256 = hashlib.sha256(zip_path.read_bytes()).hexdigest()
        final_mtime = zip_path.stat().st_mtime_ns

        self.assertEqual(initial_sha256, final_sha256, "Source file was modified!")
        self.assertEqual(initial_mtime, final_mtime, "Source file mtime was altered!")
        self.assertTrue((reports_dir / "file_inventory.csv").exists())
        self.assertTrue((reports_dir / "sha256_manifest.txt").exists())

    def test_empty_directory_error_handling(self):
        """Test that an empty directory raises an explicit ValueError without crashing silently."""
        empty_sub = self.temp_path / "empty_dir"
        empty_sub.mkdir()
        with self.assertRaises(ValueError):
            audit_directory(empty_sub)

    def test_nonexistent_directory_error_handling(self):
        """Test that a non-existent directory raises FileNotFoundError."""
        nonexistent = self.temp_path / "does_not_exist"
        with self.assertRaises(FileNotFoundError):
            audit_directory(nonexistent)


if __name__ == "__main__":
    unittest.main()
