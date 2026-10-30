#!/usr/bin/env python3
"""
Urja Task 1 — Dataset Integrity Audit & Structural Profiling Script

This script audits the raw dataset for Project Urja without modifying raw files.
It calculates checksums, inspects archive contents in-memory, extracts schema
metadata and variable labels, and produces structural quality profiles.

Usage:
    python scripts/audit_dataset.py --raw-dir <path_to_raw_data> --output-dir <path_to_reports>
"""

import argparse
import csv
import hashlib
import io
import os
import sys
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd


# Official release metadata from Harvard Dataverse (doi:10.7910/DVN/4FLFRE)
DATAVERSE_METADATA = {
    "Replication package - Ahsanuzzaman et al 2024 JEEM-1.zip": {
        "original_filename": "Replication package - Ahsanuzzaman et al 2024 JEEM-1.zip",
        "size_bytes": 2145810,
        "format": "ZIP archive (application/zip)",
        "checksum_type": "MD5",
        "checksum_value": "7d22412f622a0845ac4e78d989ef9999",
        "file_role": "Replication Archive (Contains Data, Code, and Documentation)",
    }
}

# Documentation descriptions from '0 README.docx'
DOCUMENTED_DESCRIPTIONS = {
    "replication_data.dta": {
        "hid": "Household unique identifying number",
        "round": "Survey rounds 0-6",
        "nid": "Neighborhood unique identifying number",
        "suburb": "Area/suburb name and code",
        "city": "City name",
        "attrited": "Attrition status of the household after pre-baseline round 0 (0=Remained, 1=Attrited/left)",
        "sbill": "Electricity bills (last month, in taka), self reported, rounds 0 and 1",
        "rbill": "Electricity bills (last month, in taka), verified, rounds 1-6",
        "runit": "Electricity use (last month, kWh), verified, rounds 1-6",
        "treatment": "Treatment status: T0=Control, T1=Neighbor comparison, T2=Suburb comparison, T3=Knowledge advice",
        "user_sub_high1": "Pre-baseline median use of sbill (excl. attrited): suburb comparison (0=Below avg, 1=Above avg)",
        "user_nid_high1": "Pre-baseline median use of sbill (excl. attrited): neighbor comparison (0=Below avg, 1=Above avg)",
        "eff_sub": "Pre-baseline efficiency level of sbill (excl. attrited): suburb comparison (1=Inefficient, 2=Avg, 3=Efficient)",
        "eff_nid": "Pre-baseline efficiency level of sbill (excl. attrited): neighbor comparison (1=Inefficient, 2=Avg, 3=Efficient)",
        "followup": "Follow-up status in rounds 5 and 6 (0=Not followed up, 1=Followed up)",
        "eff0": "Pre-baseline consumption type, sbill (excl. attrited) (0=Above median baseline use, 1=Below median baseline use)",
        "flatsize": "Size of residential flat/household unit (square feet / rooms)",
        "hh_rooms": "Number of rooms in household dwelling",
        "hh_outage": "Frequency of power outages in last 3 days",
        "freq_ac": "Daily air conditioner (AC) use during hot months",
    },
    "electricity_demand.dta": {
        "year": "Year of projection (2000-2040)",
        "world": "World electricity demand projections 2000-2040 (ExxonMobil 2019)",
        "oecd": "OECD electricity demand projections 2000-2040 (ExxonMobil 2019)",
        "non_oecd": "Non-OECD electricity demand projections 2000-2040 (ExxonMobil 2019)",
    },
    "wdi_electricity.dta": {
        "country": "Country name",
        "iso": "ISO country codes",
        "year": "Observation year",
        "access": "% of population with access to electricity (World Bank WDI)",
        "access_urban": "% of urban population with access to electricity (World Bank WDI)",
        "access_rural": "% of rural population with access to electricity (World Bank WDI)",
        "outage_firm": "% of firms experiencing electrical power outages",
        "outage_number": "Average number of power outages experienced by a firm monthly",
        "outage_loss": "% of value lost due to power outages",
    },
    "coord_bangladesh.dta": {
        "_ID": "Administrative polygon boundary feature identifier (DIVA-GIS BGD_adm3)",
        "_X": "Geographic longitude coordinate for administrative boundary polygon",
        "_Y": "Geographic latitude coordinate for administrative boundary polygon",
    },
    "db_bangladesh.dta": {
        "ID_0": "Country identifier code",
        "ISO": "Country 3-letter ISO code (BGD)",
        "NAME_0": "Country name (Bangladesh)",
        "ID_1": "First-order administrative subdivision ID (Division)",
        "NAME_1": "First-order administrative division name",
        "ID_2": "Second-order administrative subdivision ID (District / Zila)",
        "NAME_2": "Second-order administrative district name",
        "ID_3": "Third-order administrative subdivision ID (Upazila / Sub-district)",
        "NAME_3": "Third-order administrative subdivision name",
        "TYPE_3": "Subdivision administrative type",
        "ENGTYPE_3": "English translation of administrative type",
        "NL_NAME_3": "National language subdivision name",
        "VARNAME_3": "Alternative subdivision name variants",
    },
}


def compute_file_hashes(file_path: Path) -> Tuple[str, str, int]:
    """Compute MD5, SHA-256, and size for a file."""
    md5_hash = hashlib.md5()
    sha256_hash = hashlib.sha256()
    size = 0
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            md5_hash.update(chunk)
            sha256_hash.update(chunk)
            size += len(chunk)
    return md5_hash.hexdigest(), sha256_hash.hexdigest(), size


def format_bytes(size: int) -> str:
    """Format bytes into readable string."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024.0:
            return f"{size:.2f} {unit}" if unit != "B" else f"{size} B"
        size /= 1024.0
    return f"{size:.2f} TB"


def classify_file_role(filename: str) -> str:
    """Classify the role of a file based on name and extension."""
    lower = filename.lower()
    if lower.endswith(".docx") or "readme" in lower:
        return "Documentation / Codebook"
    if lower.endswith(".do"):
        return "Replication Code (Stata script)"
    if "replication_data" in lower:
        return "Primary RCT Experimental Dataset"
    if "coord" in lower or "db_" in lower:
        return "GIS Geographic Boundary Data"
    if "savings" in lower:
        return "Welfare / Benefit Calculations"
    if "electricity" in lower or "wdi" in lower:
        return "Contextual / Macro Supplementary Data"
    if lower.endswith(".dta") or lower.endswith(".xlsx") or lower.endswith(".csv"):
        return "Data Table"
    if lower.endswith(".zip"):
        return "Replication Archive"
    return "Supplementary Material"


def profile_dataframe(
    df: pd.DataFrame,
    source_file: str,
    table_name: str,
    var_labels: Optional[Dict[str, str]] = None,
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """Profile a dataframe for structural quality and schema inventory."""
    total_rows = len(df)
    total_cols = len(df.columns)
    dup_rows = int(df.duplicated().sum())

    table_missing_cells = int(df.isna().sum().sum())
    total_cells = total_rows * total_cols
    table_missing_pct = round((table_missing_cells / total_cells) * 100, 4) if total_cells > 0 else 0.0

    table_profile = {
        "table_name": table_name,
        "source_file": source_file,
        "total_rows": total_rows,
        "total_columns": total_cols,
        "fully_duplicated_rows": dup_rows,
        "missing_cells_total": table_missing_cells,
        "missing_cells_pct": table_missing_pct,
        "fully_readable": True,
        "status": "VALID",
    }

    schema_rows = []
    base_file = Path(source_file).name
    doc_map = DOCUMENTED_DESCRIPTIONS.get(base_file, {})

    for col in df.columns:
        series = df[col]
        col_str = str(col)
        n_missing = int(series.isna().sum())
        pct_missing = round((n_missing / total_rows) * 100, 4) if total_rows > 0 else 0.0
        n_distinct = int(series.nunique(dropna=True))

        min_val = None
        max_val = None
        inf_count = 0

        if pd.api.types.is_numeric_dtype(series):
            valid_num = series.dropna()
            inf_count = int(np.isinf(valid_num).sum()) if len(valid_num) > 0 else 0
            finite_num = valid_num[np.isfinite(valid_num)]
            if len(finite_num) > 0:
                min_val = float(finite_num.min())
                max_val = float(finite_num.max())

        # Determine documented description
        description = "Not documented"
        doc_source = "None"

        if col_str in doc_map:
            description = doc_map[col_str]
            doc_source = "0 README.docx / Paper"
        elif var_labels and col_str in var_labels and var_labels[col_str].strip():
            description = var_labels[col_str].strip()
            doc_source = "Stata dataset variable label"

        schema_rows.append({
            "source_file": source_file,
            "table_or_sheet": table_name,
            "column_name": col_str,
            "detected_dtype": str(series.dtype),
            "documented_description": description,
            "documentation_source": doc_source,
            "missing_count": n_missing,
            "missing_pct": pct_missing,
            "distinct_values": n_distinct,
            "min_value": min_val if min_val is not None else "",
            "max_value": max_val if max_val is not None else "",
            "inf_count": inf_count,
        })

    return table_profile, schema_rows


def inspect_archive(
    zip_path: Path, relative_dir: Path
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Inspect contents of a zip archive in-memory without extracting to disk."""
    file_rows = []
    table_profiles = []
    schema_rows = []

    with zipfile.ZipFile(zip_path, "r") as z:
        for info in z.infolist():
            # Skip macOS metadata resource forks and directory entries
            if info.filename.startswith("__MACOSX") or info.filename.endswith("/"):
                continue

            entry_name = Path(info.filename).name
            if entry_name.startswith("._") or entry_name == ".DS_Store":
                continue

            file_role = classify_file_role(info.filename)
            detected_format = Path(info.filename).suffix.lstrip(".").upper()
            if not detected_format:
                detected_format = "UNKNOWN"

            is_readable = True
            error_msg = ""

            # Profile data formats
            if info.filename.endswith(".dta"):
                try:
                    with z.open(info.filename) as f:
                        buf = io.BytesIO(f.read())
                        reader = pd.io.stata.StataReader(buf)
                        df = reader.read()
                        var_labels = reader.variable_labels()
                        t_prof, s_rows = profile_dataframe(
                            df, info.filename, entry_name, var_labels
                        )
                        table_profiles.append(t_prof)
                        schema_rows.extend(s_rows)
                        detected_format = f"Stata dta (v{getattr(reader, '_format_version', '118')})"
                except Exception as e:
                    is_readable = False
                    error_msg = str(e)
                    table_profiles.append({
                        "table_name": entry_name,
                        "source_file": info.filename,
                        "total_rows": 0,
                        "total_columns": 0,
                        "fully_duplicated_rows": 0,
                        "missing_cells_total": 0,
                        "missing_cells_pct": 0.0,
                        "fully_readable": False,
                        "status": f"ERROR: {error_msg}",
                    })

            elif info.filename.endswith(".xlsx"):
                try:
                    with z.open(info.filename) as f:
                        buf = io.BytesIO(f.read())
                        excel_file = pd.ExcelFile(buf)
                        detected_format = "Excel xlsx"
                        for sheet in excel_file.sheet_names:
                            buf.seek(0)
                            df = pd.read_excel(buf, sheet_name=sheet)
                            t_prof, s_rows = profile_dataframe(
                                df, info.filename, f"{entry_name} [{sheet}]", None
                            )
                            table_profiles.append(t_prof)
                            schema_rows.extend(s_rows)
                except Exception as e:
                    is_readable = False
                    error_msg = str(e)
                    table_profiles.append({
                        "table_name": entry_name,
                        "source_file": info.filename,
                        "total_rows": 0,
                        "total_columns": 0,
                        "fully_duplicated_rows": 0,
                        "missing_cells_total": 0,
                        "missing_cells_pct": 0.0,
                        "fully_readable": False,
                        "status": f"ERROR: {error_msg}",
                    })

            elif info.filename.endswith(".docx"):
                detected_format = "Word docx"
            elif info.filename.endswith(".do"):
                detected_format = "Stata do-script"

            file_rows.append({
                "original_filename": entry_name,
                "local_filename": info.filename,
                "source_match": "Yes",
                "original_size_bytes": info.file_size,
                "local_size_bytes": info.file_size,
                "local_size_readable": format_bytes(info.file_size),
                "format": detected_format,
                "official_checksum_type": "N/A (Inside Archive)",
                "official_checksum_value": "N/A",
                "local_sha256": "N/A (Archive Member)",
                "checksum_comparison": "Not available (Archive Member)",
                "readability": "Readable" if is_readable else f"Unreadable ({error_msg})",
                "file_role": file_role,
            })

    return file_rows, table_profiles, schema_rows


def audit_directory(raw_dir: Path) -> Tuple[
    List[Dict[str, Any]],
    List[Dict[str, Any]],
    List[Dict[str, Any]],
    List[str],
]:
    """Audit the supplied raw directory recursively."""
    if not raw_dir.exists() or not raw_dir.is_dir():
        raise FileNotFoundError(f"Raw data directory does not exist or is not a directory: {raw_dir}")

    all_file_rows = []
    all_table_profiles = []
    all_schema_rows = []
    sha256_manifest_lines = []

    # Find all files in raw_dir recursively
    raw_files = [p for p in raw_dir.rglob("*") if p.is_file()]

    if not raw_files:
        raise ValueError(f"No files found in raw directory: {raw_dir}")

    for file_path in sorted(raw_files):
        rel_path = file_path.relative_to(raw_dir)
        filename = file_path.name

        # Calculate hashes
        md5_hash, sha256_hash, file_size = compute_file_hashes(file_path)
        sha256_manifest_lines.append(f"{sha256_hash}  {rel_path.as_posix()}\n")

        # Compare with Dataverse metadata
        dv_info = DATAVERSE_METADATA.get(filename)
        source_match = "Yes" if dv_info else "Unverified"
        orig_size = dv_info["size_bytes"] if dv_info else "N/A"
        official_csum_type = dv_info["checksum_type"] if dv_info else "N/A"
        official_csum_val = dv_info["checksum_value"] if dv_info else "N/A"

        csum_match = "Not available"
        if dv_info and dv_info["checksum_type"] == "MD5":
            csum_match = "Match" if md5_hash.lower() == dv_info["checksum_value"].lower() else "Mismatch"

        file_role = dv_info["file_role"] if dv_info else classify_file_role(filename)
        detected_format = dv_info["format"] if dv_info else file_path.suffix.lstrip(".").upper()

        all_file_rows.append({
            "original_filename": filename,
            "local_filename": rel_path.as_posix(),
            "source_match": source_match,
            "original_size_bytes": orig_size,
            "local_size_bytes": file_size,
            "local_size_readable": format_bytes(file_size),
            "format": detected_format,
            "official_checksum_type": official_csum_type,
            "official_checksum_value": official_csum_val,
            "local_sha256": sha256_hash,
            "checksum_comparison": csum_match,
            "readability": "Readable",
            "file_role": file_role,
        })

        # If it's a zip archive, inspect contents in-memory
        if zipfile.is_zipfile(file_path):
            archive_files, archive_tables, archive_schemas = inspect_archive(file_path, rel_path)
            all_file_rows.extend(archive_files)
            all_table_profiles.extend(archive_tables)
            all_schema_rows.extend(archive_schemas)

    return all_file_rows, all_table_profiles, all_schema_rows, sha256_manifest_lines


def write_reports(
    output_dir: Path,
    file_rows: List[Dict[str, Any]],
    table_profiles: List[Dict[str, Any]],
    schema_rows: List[Dict[str, Any]],
    sha256_lines: List[str],
) -> None:
    """Write audit outputs to CSV and text manifests."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. file_inventory.csv
    file_inv_path = output_dir / "file_inventory.csv"
    if file_rows:
        headers = list(file_rows[0].keys())
        with open(file_inv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(file_rows)
        print(f"Generated: {file_inv_path} ({len(file_rows)} rows)")

    # 2. schema_inventory.csv
    schema_inv_path = output_dir / "schema_inventory.csv"
    if schema_rows:
        headers = list(schema_rows[0].keys())
        with open(schema_inv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(schema_rows)
        print(f"Generated: {schema_inv_path} ({len(schema_rows)} fields profiled)")

    # 3. structural_quality.csv
    struct_path = output_dir / "structural_quality.csv"
    if table_profiles:
        headers = list(table_profiles[0].keys())
        with open(struct_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(table_profiles)
        print(f"Generated: {struct_path} ({len(table_profiles)} tables summarized)")

    # 4. sha256_manifest.txt
    sha256_path = output_dir / "sha256_manifest.txt"
    with open(sha256_path, "w", encoding="utf-8") as f:
        f.writelines(sha256_lines)
    print(f"Generated: {sha256_path} ({len(sha256_lines)} manifests)")


def main():
    parser = argparse.ArgumentParser(
        description="Urja Task 1 Dataset Integrity and Structural Profiler"
    )
    parser.add_argument(
        "--raw-dir",
        type=Path,
        required=True,
        help="Path to raw dataset directory",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("validation/urja/task_01/reports"),
        help="Path to reports output directory",
    )

    args = parser.parse_args()

    print(f"Starting audit for raw directory: {args.raw_dir}")
    print(f"Target reports directory: {args.output_dir}")

    file_rows, table_profiles, schema_rows, sha256_lines = audit_directory(args.raw_dir)
    write_reports(args.output_dir, file_rows, table_profiles, schema_rows, sha256_lines)
    print("Dataset audit complete. All outputs generated successfully.")


if __name__ == "__main__":
    main()
