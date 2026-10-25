"""
Validator script for data/run_manifest.csv.
Validates manifest consistency against audited raw dataset inventory, ensuring:
- All 55 source files are represented exactly once, with no duplicate filenames or run IDs.
- dataset_0 is excluded for approved schema mismatch and has no train/val/test split assignment.
- Exact approved split counts and exact run IDs match approved allocation:
    * Train (20 runs): all normal runs
    * Validation (8 runs): 5 normal runs + 3 approved non-normal runs (10, 12, 15)
    * Test (26 runs): 7 normal runs + 19 remaining non-normal runs
- Scenario matches the category derived from filename; binary_label is 0 for normal and 1 for non-normal.
- observed_anomaly_codes reflects raw audit evidence without forcing an unsupported single scenario code.
- Source revision matches the audited commit (07b9565c794da01b46ec76c442f416d509d6b73b).

Usage:
    python reports/audit/validate_run_manifest.py
"""

import sys
import csv
import json
from pathlib import Path

def validate_manifest():
    manifest_path = Path("data/run_manifest.csv")
    inventory_path = Path("reports/audit/audit_inventory_results.json")
    expected_revision = "07b9565c794da01b46ec76c442f416d509d6b73b"

    errors = []

    if not manifest_path.exists():
        print(f"FAILED: Manifest not found at {manifest_path}")
        sys.exit(1)

    if not inventory_path.exists():
        print(f"FAILED: Inventory results not found at {inventory_path}")
        sys.exit(1)

    with open(inventory_path, "r", encoding="utf-8") as f:
        inventory_data = json.load(f)
    audited_files = inventory_data.get("files", [])
    audited_map = {f["filename"]: f for f in audited_files}

    if len(audited_map) != 55:
        errors.append(f"Expected 55 audited files in inventory, found {len(audited_map)}")

    # Read manifest
    with open(manifest_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        manifest_rows = list(reader)

    print(f"Validating {manifest_path} ({len(manifest_rows)} rows) against audit evidence...")

    # Required fieldnames check
    required_fields = [
        "run_id", "filename", "scenario", "binary_label",
        "observed_anomaly_codes", "split", "include",
        "exclusion_reason", "source_revision"
    ]
    if reader.fieldnames != required_fields:
        errors.append(f"Header mismatch. Expected {required_fields}, got {reader.fieldnames}")

    # 1. Total rows and unique filenames / IDs
    if len(manifest_rows) != 55:
        errors.append(f"Manifest must contain exactly 55 rows, found {len(manifest_rows)}")

    seen_filenames = set()
    seen_run_ids = set()
    for row in manifest_rows:
        fn = row["filename"]
        rid = int(row["run_id"]) if row["run_id"].isdigit() else -1
        if fn in seen_filenames:
            errors.append(f"Duplicate filename in manifest: {fn}")
        seen_filenames.add(fn)
        if rid in seen_run_ids:
            errors.append(f"Duplicate run_id in manifest: {rid}")
        seen_run_ids.add(rid)

    missing_from_manifest = set(audited_map.keys()) - seen_filenames
    if missing_from_manifest:
        errors.append(f"Audited files missing from manifest: {missing_from_manifest}")

    # 2. Excluded runs verification
    excluded_rows = [r for r in manifest_rows if r["include"].lower() == "false"]
    if len(excluded_rows) != 1:
        errors.append(f"Expected exactly 1 excluded run, found {len(excluded_rows)}: {[r['filename'] for r in excluded_rows]}")
    else:
        ex = excluded_rows[0]
        if ex["filename"] != "dataset_0_normal_behaviour.csv":
            errors.append(f"Expected dataset_0_normal_behaviour.csv to be excluded, but found {ex['filename']}")
        if ex["exclusion_reason"] != "schema_mismatch_42_columns_missing_8_PI_derived_level_channels":
            errors.append(f"Unexpected exclusion_reason: {ex['exclusion_reason']}")
        if ex["split"] not in ("none", "", "excluded"):
            errors.append(f"Excluded run must have split 'none' or empty, found '{ex['split']}'")

    # 3. Included runs and splits
    included_rows = [r for r in manifest_rows if r["include"].lower() == "true"]
    if len(included_rows) != 54:
        errors.append(f"Expected 54 included runs, found {len(included_rows)}")

    splits = {}
    for r in included_rows:
        s = r["split"]
        splits.setdefault(s, []).append(r)

    train_runs = splits.get("train", [])
    val_runs = splits.get("val", [])
    test_runs = splits.get("test", [])

    # Exact split counts
    if len(train_runs) != 20:
        errors.append(f"Train split must have exactly 20 runs, found {len(train_runs)}")
    if len(val_runs) != 8:
        errors.append(f"Validation split must have exactly 8 runs, found {len(val_runs)}")
    if len(test_runs) != 26:
        errors.append(f"Test split must have exactly 26 runs, found {len(test_runs)}")

    # 4. Expected run ID sets (exact approved partition preserved with seed 42)
    expected_train_ids = {2, 6, 7, 16, 17, 18, 19, 20, 21, 22, 23, 25, 27, 28, 30, 32, 33, 34, 36, 38}
    expected_val_normal_ids = {3, 4, 24, 29, 37}
    expected_val_fault_ids = {10, 12, 15}
    expected_test_normal_ids = {1, 5, 8, 9, 31, 35, 39}
    expected_test_fault_ids = {11, 13, 14, 26, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54}

    actual_train_ids = {int(r["run_id"]) for r in train_runs}
    actual_val_normal_ids = {int(r["run_id"]) for r in val_runs if r["scenario"] == "normal_behaviour"}
    actual_val_fault_ids = {int(r["run_id"]) for r in val_runs if r["scenario"] != "normal_behaviour"}
    actual_test_normal_ids = {int(r["run_id"]) for r in test_runs if r["scenario"] == "normal_behaviour"}
    actual_test_fault_ids = {int(r["run_id"]) for r in test_runs if r["scenario"] != "normal_behaviour"}

    if actual_train_ids != expected_train_ids:
        errors.append(f"Train run IDs mismatch.\n  Expected: {sorted(list(expected_train_ids))}\n  Actual:   {sorted(list(actual_train_ids))}")
    if actual_val_normal_ids != expected_val_normal_ids:
        errors.append(f"Val normal run IDs mismatch.\n  Expected: {sorted(list(expected_val_normal_ids))}\n  Actual:   {sorted(list(actual_val_normal_ids))}")
    if actual_val_fault_ids != expected_val_fault_ids:
        errors.append(f"Val fault run IDs mismatch.\n  Expected: {sorted(list(expected_val_fault_ids))}\n  Actual:   {sorted(list(actual_val_fault_ids))}")
    if actual_test_normal_ids != expected_test_normal_ids:
        errors.append(f"Test normal run IDs mismatch.\n  Expected: {sorted(list(expected_test_normal_ids))}\n  Actual:   {sorted(list(actual_test_normal_ids))}")
    if actual_test_fault_ids != expected_test_fault_ids:
        errors.append(f"Test fault run IDs mismatch.\n  Expected: {sorted(list(expected_test_fault_ids))}\n  Actual:   {sorted(list(actual_test_fault_ids))}")

    # 5. Check scenario, binary label, observed anomaly codes, and audit agreement
    valid_scenarios = {
        "normal_behaviour", "leakage", "clogging", "leakage_and_clogging",
        "changed_initial_state", "reconfiguration", "sensor_errors",
        "stirring_error", "manual_mode"
    }

    for r in manifest_rows:
        fn = r["filename"]
        sc = r["scenario"]
        bl = r["binary_label"]
        codes = r["observed_anomaly_codes"]
        rev = r["source_revision"]

        # Check source revision
        if rev != expected_revision:
            errors.append(f"Revision mismatch in {fn}: got {rev}, expected {expected_revision}")

        # Check scenario valid
        if sc not in valid_scenarios:
            errors.append(f"Unknown scenario '{sc}' in {fn}")

        # Check audit inventory scenario matches filename scenario
        if fn in audited_map:
            audited_sc = audited_map[fn]["scenario"]
            if sc != audited_sc:
                errors.append(f"Scenario mismatch for {fn}: manifest='{sc}', audit='{audited_sc}'")

            # Check observed codes match raw audit distribution
            raw_dist = audited_map[fn]["anomaly_dist"]
            expected_codes = ";".join(sorted(list(raw_dist.keys()), key=lambda x: int(x) if x.isdigit() else x))
            if codes != expected_codes:
                errors.append(f"Observed codes mismatch for {fn}: manifest='{codes}', audit='{expected_codes}'")

        # Binary label check
        if sc == "normal_behaviour":
            if bl != "0":
                errors.append(f"Normal run {fn} must have binary_label=0, got {bl}")
        else:
            if bl != "1":
                errors.append(f"Non-normal run {fn} must have binary_label=1, got {bl}")

    # Output detailed report
    print("=" * 70)
    print("RUN MANIFEST VALIDATION SUMMARY")
    print("=" * 70)
    print(f"Total files audited:     {len(audited_map)}")
    print(f"Total files in manifest: {len(manifest_rows)}")
    print(f"Excluded runs:           {len(excluded_rows)} ({[r['filename'] for r in excluded_rows]})")
    print(f"Included runs:           {len(included_rows)}")
    print(f"  - Train split:         {len(train_runs)} runs (all normal)")
    print(f"    IDs:                 {sorted(list(actual_train_ids))}")
    print(f"  - Validation split:    {len(val_runs)} runs ({len(actual_val_normal_ids)} normal + {len(actual_val_fault_ids)} non-normal)")
    print(f"    Normal IDs:          {sorted(list(actual_val_normal_ids))}")
    print(f"    Non-normal IDs:      {sorted(list(actual_val_fault_ids))} ({[r['filename'] for r in val_runs if r['scenario'] != 'normal_behaviour']})")
    print(f"  - Test split:          {len(test_runs)} runs ({len(actual_test_normal_ids)} normal + {len(actual_test_fault_ids)} non-normal)")
    print(f"    Normal IDs:          {sorted(list(actual_test_normal_ids))}")
    print(f"    Non-normal IDs:      {sorted(list(actual_test_fault_ids))}")
    print("=" * 70)

    if errors:
        print("VALIDATION FAILED with the following errors:")
        for err in errors:
            print(f"  [ERROR] {err}")
        sys.exit(1)
    else:
        print("VALIDATION PASSED: All manifest schema, split, and label checks satisfied.")
        sys.exit(0)

if __name__ == "__main__":
    validate_manifest()
