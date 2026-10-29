"""Unit tests for validate_dataset.py validation routines."""

import hashlib
import tempfile
import unittest
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from validation.freshretail.scripts.validate_dataset import (
    DATASET_METADATA,
    compute_sha256,
)


class TestValidateDataset(unittest.TestCase):
    """Test suite for validation functions."""

    def test_compute_sha256(self):
        """Verifies chunked SHA-256 calculation matches hashlib on known bytes."""
        test_bytes = b"FreshRetailNet-50K Data Integrity Test Payload 123456789"
        expected_sha = hashlib.sha256(test_bytes).hexdigest()

        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(test_bytes)
            tmp_path = Path(tmp.name)

        try:
            calc_sha = compute_sha256(tmp_path)
            self.assertEqual(calc_sha, expected_sha)
        finally:
            if tmp_path.exists():
                tmp_path.unlink()

    def test_documented_fields_completeness(self):
        """Ensures all 19 documented fields are cataloged in DATASET_METADATA."""
        fields = DATASET_METADATA["documented_fields"]
        self.assertEqual(len(fields), 19)
        required_concepts = [
            "city_id", "store_id", "product_id", "dt", "sale_amount",
            "hours_sale", "stock_hour6_22_cnt", "hours_stock_status"
        ]
        for field in required_concepts:
            self.assertIn(field, fields)

    def test_grain_uniqueness_logic(self):
        """Tests uniqueness detection at (store_id, product_id, dt) grain."""
        data = {
            "store_id": [1, 1, 2, 1],
            "product_id": [10, 20, 10, 10],
            "dt": ["2024-03-28", "2024-03-28", "2024-03-28", "2024-03-28"]
        }
        df = pd.DataFrame(data)
        # Row 0 and Row 3 are duplicates on (store_id, product_id, dt)
        dup_count = df.duplicated(subset=["store_id", "product_id", "dt"]).sum()
        self.assertEqual(dup_count, 1)


if __name__ == "__main__":
    unittest.main()
