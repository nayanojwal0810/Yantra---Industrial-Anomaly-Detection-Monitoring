#!/usr/bin/env python3
"""
Profiles real UI-downloaded USAspending sample exports and generates:
- reports/data_feasibility/ui_sample_manifest.json
- reports/data_feasibility/ui_sample_profile.md
- reports/data_feasibility/ui_sample_schema.json
- reports/data_feasibility/ui_sample_awards_preview.csv
- reports/data_feasibility/ui_sample_transactions_preview.csv
- reports/data_feasibility/ui_sample_handoff.zip
"""

import csv
import hashlib
import json
import math
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def compute_sha256(file_path: Path) -> str:
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def calculate_quantiles(values: list[float]) -> dict[str, float]:
    if not values:
        return {"min": 0.0, "p25": 0.0, "median": 0.0, "p75": 0.0, "max": 0.0, "mean": 0.0}
    s = sorted(values)
    n = len(s)

    def _get_q(q: float) -> float:
        idx = (n - 1) * q
        low = math.floor(idx)
        high = math.ceil(idx)
        if low == high:
            return s[low]
        return s[low] * (high - idx) + s[high] * (idx - low)

    return {
        "min": float(s[0]),
        "p25": float(_get_q(0.25)),
        "median": float(_get_q(0.50)),
        "p75": float(_get_q(0.75)),
        "max": float(s[-1]),
        "mean": float(sum(s) / n),
    }


def analyze_csv(csv_path: Path, max_preview_rows: int = 25) -> dict[str, Any]:
    with open(csv_path, "r", encoding="utf-8-sig", errors="replace") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if not header:
            return {"columns": [], "row_count": 0, "preview_rows": [], "stats": {}}

        columns = header
        rows = []
        col_missing_counts = {col: 0 for col in columns}
        amount_values: list[float] = []
        zero_amount_count = 0
        negative_amount_count = 0
        missing_amount_count = 0
        date_values: list[str] = []

        # Find probable amount and date columns
        amount_col_idx = None
        date_col_idx = None
        award_id_col_idx = None

        for idx, col in enumerate(columns):
            cl = col.lower().strip()
            if amount_col_idx is None and any(k in cl for k in ("award_amount", "total_obligation", "federal_action_obligation", "award amount")):
                amount_col_idx = idx
            if date_col_idx is None and any(k in cl for k in ("start_date", "action_date", "date_signed", "start date")):
                date_col_idx = idx
            if award_id_col_idx is None and any(k in cl for k in ("award_id_piid", "piid", "award id", "generated_unique_award_id")):
                award_id_col_idx = idx

        row_count = 0
        unique_award_ids: set[str] = set()
        missing_award_ids = 0

        for r in reader:
            row_count += 1
            if len(rows) < max_preview_rows:
                rows.append(r)

            for idx, col in enumerate(columns):
                val = r[idx].strip() if idx < len(r) else ""
                if not val:
                    col_missing_counts[col] += 1

            if award_id_col_idx is not None and award_id_col_idx < len(r):
                aid = r[award_id_col_idx].strip()
                if aid:
                    unique_award_ids.add(aid)
                else:
                    missing_award_ids += 1

            if amount_col_idx is not None and amount_col_idx < len(r):
                raw_amt = r[amount_col_idx].strip()
                if raw_amt:
                    try:
                        amt = float(raw_amt.replace("$", "").replace(",", ""))
                        amount_values.append(amt)
                        if amt == 0.0:
                            zero_amount_count += 1
                        elif amt < 0.0:
                            negative_amount_count += 1
                    except ValueError:
                        missing_amount_count += 1
                else:
                    missing_amount_count += 1

            if date_col_idx is not None and date_col_idx < len(r):
                raw_dt = r[date_col_idx].strip()
                if raw_dt and len(raw_dt) >= 10:
                    date_values.append(raw_dt[:10])

        missing_percentages = {
            col: round((count / row_count * 100), 2) if row_count > 0 else 0.0
            for col, count in col_missing_counts.items()
        }
        sorted_missing = sorted(missing_percentages.items(), key=lambda x: x[1], reverse=True)

        return {
            "columns": columns,
            "row_count": row_count,
            "preview_rows": rows,
            "unique_award_ids_count": len(unique_award_ids),
            "missing_award_ids": missing_award_ids,
            "award_id_col_name": columns[award_id_col_idx] if award_id_col_idx is not None else None,
            "amount_col_name": columns[amount_col_idx] if amount_col_idx is not None else None,
            "amount_quantiles": calculate_quantiles(amount_values),
            "zero_amount_count": zero_amount_count,
            "negative_amount_count": negative_amount_count,
            "missing_amount_count": missing_amount_count,
            "date_col_name": columns[date_col_idx] if date_col_idx is not None else None,
            "min_date": min(date_values) if date_values else None,
            "max_date": max(date_values) if date_values else None,
            "top_missing_columns": sorted_missing[:15],
            "all_missing_counts": col_missing_counts,
        }


def process_sample_downloads(
    raw_dir_str: str = "data/raw/sample",
    reports_dir_str: str = "reports/data_feasibility",
    displayed_counts: dict[str, Any] | None = None,
) -> dict[str, Any]:
    raw_dir = Path(raw_dir_str)
    reports_dir = Path(reports_dir_str)
    reports_dir.mkdir(parents=True, exist_ok=True)

    if displayed_counts is None:
        displayed_counts = {}

    zip_files = list(raw_dir.glob("*.zip"))
    if not zip_files:
        print(f"No zip files found in {raw_dir}")
        return {"status": "no_zip_files_found"}

    manifest: dict[str, Any] = {
        "manifest_version": "1.0.0",
        "retrieved_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_url": "https://www.usaspending.gov/search",
        "workflow": "USAspending Advanced Search UI Export",
        "exact_filters": {
            "award_type": "Contracts",
            "time_period": {
                "type": "Fiscal Year",
                "fiscal_year": 2020,
                "start_date": "2019-10-01",
                "end_date": "2020-09-30",
                "show_new_awards_only": True,
            },
            "agency": {
                "type": "Awarding Agency",
                "name": "National Aeronautics and Space Administration (NASA)",
            },
            "naics": {
                "code": "541330",
                "description": "Engineering Services",
            },
            "location": None,
            "threshold": None,
        },
        "displayed_result_counts": displayed_counts,
        "downloaded_archives": [],
        "extracted_files": [],
        "status": "complete",
    }

    awards_analysis: dict[str, Any] | None = None
    tx_analysis: dict[str, Any] | None = None

    for zf_path in zip_files:
        sha256 = compute_sha256(zf_path)
        size_bytes = zf_path.stat().st_size
        extract_folder = raw_dir / f"extracted_{zf_path.stem}"
        extract_folder.mkdir(parents=True, exist_ok=True)

        contained_files = []
        with zipfile.ZipFile(zf_path, "r") as z:
            contained_files = z.namelist()
            z.extractall(extract_folder)

        manifest["downloaded_archives"].append({
            "local_file_name": zf_path.name,
            "byte_size": size_bytes,
            "sha256": sha256,
            "contained_files": contained_files,
            "extracted_directory": str(extract_folder),
        })

        for c_file in contained_files:
            if c_file.endswith(".csv"):
                csv_path = extract_folder / c_file
                is_tx = "transaction" in c_file.lower() or "transaction" in zf_path.name.lower()
                analysis = analyze_csv(csv_path)

                manifest["extracted_files"].append({
                    "file_name": c_file,
                    "relative_path": str(csv_path.relative_to(Path("."))),
                    "export_level": "transaction" if is_tx else "award",
                    "row_count": analysis["row_count"],
                    "column_count": len(analysis["columns"]),
                    "columns": analysis["columns"],
                    "encoding": "utf-8",
                    "delimiter": ",",
                })

                if is_tx:
                    tx_analysis = analysis
                    # Write transaction preview
                    preview_path = reports_dir / "ui_sample_transactions_preview.csv"
                    with open(preview_path, "w", newline="", encoding="utf-8") as pf:
                        writer = csv.writer(pf)
                        writer.writerow(analysis["columns"])
                        writer.writerows(analysis["preview_rows"])
                else:
                    awards_analysis = analysis
                    # Write awards preview
                    preview_path = reports_dir / "ui_sample_awards_preview.csv"
                    with open(preview_path, "w", newline="", encoding="utf-8") as pf:
                        writer = csv.writer(pf)
                        writer.writerow(analysis["columns"])
                        writer.writerows(analysis["preview_rows"])

    # Write manifest
    manifest_file = reports_dir / "ui_sample_manifest.json"
    with open(manifest_file, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    # Write schema
    schema_file = reports_dir / "ui_sample_schema.json"
    schema_data = {
        "awards": {
            "columns": awards_analysis["columns"] if awards_analysis else [],
            "column_count": len(awards_analysis["columns"]) if awards_analysis else 0,
            "row_count": awards_analysis["row_count"] if awards_analysis else 0,
        },
        "transactions": {
            "columns": tx_analysis["columns"] if tx_analysis else [],
            "column_count": len(tx_analysis["columns"]) if tx_analysis else 0,
            "row_count": tx_analysis["row_count"] if tx_analysis else 0,
        },
    }
    with open(schema_file, "w", encoding="utf-8") as f:
        json.dump(schema_data, f, indent=2)

    # Write profile report markdown
    profile_md = reports_dir / "ui_sample_profile.md"
    md_content = generate_markdown_profile(manifest, awards_analysis, tx_analysis)
    with open(profile_md, "w", encoding="utf-8") as f:
        f.write(md_content)

    # Create ui_sample_handoff.zip with only report/preview artifacts
    handoff_zip = reports_dir / "ui_sample_handoff.zip"
    with zipfile.ZipFile(handoff_zip, "w", zipfile.ZIP_DEFLATED) as hz:
        hz.write(manifest_file, arcname="ui_sample_manifest.json")
        hz.write(schema_file, arcname="ui_sample_schema.json")
        hz.write(profile_md, arcname="ui_sample_profile.md")
        if (reports_dir / "ui_sample_awards_preview.csv").exists():
            hz.write(reports_dir / "ui_sample_awards_preview.csv", arcname="ui_sample_awards_preview.csv")
        if (reports_dir / "ui_sample_transactions_preview.csv").exists():
            hz.write(reports_dir / "ui_sample_transactions_preview.csv", arcname="ui_sample_transactions_preview.csv")

    print("Profile processing complete.")
    return manifest


def generate_markdown_profile(
    manifest: dict[str, Any],
    awards: dict[str, Any] | None,
    tx: dict[str, Any] | None,
) -> str:
    lines = [
        "# USAspending UI Sample Data Feasibility Profile",
        "",
        "## 1. Overview & Export Provenance",
        "- **Source**: [USAspending Advanced Search](https://www.usaspending.gov/search)",
        f"- **Retrieval Timestamp (UTC)**: `{manifest['retrieved_at_utc']}`",
        "- **Filters Applied**:",
        "  - **Award Type**: `Contracts` (prime awards)",
        "  - **Awarding Agency**: `National Aeronautics and Space Administration (NASA)` (awarding agency)",
        "  - **NAICS**: `541330 — Engineering Services`",
        "  - **Time Period**: `Fiscal Year 2020` (2019-10-01 to 2020-09-30)",
        "  - **Date Semantics**: `Show New Awards Only` (base awards initiated in FY2020)",
        "  - **Location Filter**: `None`",
        "  - **Dollar Threshold**: `None` (exploratory pilot does not filter by $5M)",
        "",
        "## 2. Archive & File Inventory",
        "| Local Archive Name | Byte Size | SHA-256 Checksum | Contained CSV |",
        "| :--- | :--- | :--- | :--- |",
    ]

    for arc in manifest["downloaded_archives"]:
        c_str = ", ".join(arc["contained_files"])
        lines.append(f"| `{arc['local_file_name']}` | {arc['byte_size']} bytes | `{arc['sha256']}` | {c_str} |")

    lines.extend([
        "",
        "## 3. Award-Level Export Profile",
    ])

    if awards:
        lines.extend([
            f"- **Total Rows**: {awards['row_count']}",
            f"- **Total Columns**: {len(awards['columns'])}",
            f"- **Award ID Column**: `{awards['award_id_col_name']}`",
            f"- **Unique Award IDs**: {awards['unique_award_ids_count']} (Missing/Blank: {awards['missing_award_ids']})",
            f"- **Date Range (`{awards['date_col_name']}`)**: `{awards['min_date']}` to `{awards['max_date']}`",
            f"- **Amount Column**: `{awards['amount_col_name']}`",
            f"  - **Min**: ${awards['amount_quantiles']['min']:,.2f}",
            f"  - **25th Percentile**: ${awards['amount_quantiles']['p25']:,.2f}",
            f"  - **Median**: ${awards['amount_quantiles']['median']:,.2f}",
            f"  - **75th Percentile**: ${awards['amount_quantiles']['p75']:,.2f}",
            f"  - **Max**: ${awards['amount_quantiles']['max']:,.2f}",
            f"  - **Zero Values**: {awards['zero_amount_count']}",
            f"  - **Negative Values**: {awards['negative_amount_count']}",
            f"  - **Missing/Blank Values**: {awards['missing_amount_count']}",
            "",
            "### Top Missing Columns in Award Export",
            "| Column Name | Missing Count | Missing Percentage |",
            "| :--- | :--- | :--- |",
        ])
        for col, pct in awards["top_missing_columns"]:
            lines.append(f"| `{col}` | {awards['all_missing_counts'][col]} | {pct}% |")
    else:
        lines.append("- *No award-level export processed.*")

    lines.extend([
        "",
        "## 4. Transaction-Level Export Profile",
    ])

    if tx:
        lines.extend([
            f"- **Total Rows**: {tx['row_count']}",
            f"- **Total Columns**: {len(tx['columns'])}",
            f"- **Transaction Date Range (`{tx['date_col_name']}`)**: `{tx['min_date']}` to `{tx['max_date']}`",
            f"- **Obligation Column**: `{tx['amount_col_name']}`",
            f"  - **Min**: ${tx['amount_quantiles']['min']:,.2f}",
            f"  - **Median**: ${tx['amount_quantiles']['median']:,.2f}",
            f"  - **Max**: ${tx['amount_quantiles']['max']:,.2f}",
        ])
    else:
        lines.append("- *No transaction-level export was downloaded or available for this pilot.*")

    lines.extend([
        "",
        "## 5. Critical Scope & Methodological Limitations",
        "1. **Single Stratum Pilot**: This sample is strictly limited to one agency (NASA), one NAICS code (541330), and one fiscal year (FY2020). It is not a statistically representative sample of federal contracting.",
        "2. **Award vs Transaction Semantics**: An award summary row reflects total lifecycle obligation as of export time; it does not constitute a full transaction history. Successor matching and re-compete linkage cannot be established solely from an exploratory award export.",
        "3. **Threshold Application**: The $5,000,000 recompete threshold was intentionally omitted during data extraction to preserve distribution integrity and must be evaluated downstream during full pipeline development.",
    ])

    return "\n".join(lines)


if __name__ == "__main__":
    process_sample_downloads()
