#!/usr/bin/env python3
"""
extract_fcu_subset.py
---------------------
Selectively inspects and extracts members of the official LBNL FCU dataset ZIP archive
(Simulated_LBNL_FDD_Data_Sets_FCU.zip, ~506.1 MB) using HTTP Range requests without
downloading the entire archive over unmetered bandwidth.

Dataset Source:
    LBNL DataFDD / OpenEI Submission 5763:
    https://fdddata.lbl.gov/data/Simulated_LBNL_FDD_Data_Sets_FCU/LBNL_FDD_Data_Sets_FCU.zip

Usage:
    # List all archive entries without downloading CSVs
    python validation/scripts/extract_fcu_subset.py --list

    # Extract selected representative files to a target directory
    python validation/scripts/extract_fcu_subset.py \
        --files FCU_FaultFree.csv,FCU_VLVLeak_Cooling_20.csv,FCU_FilterRestriction_10%.csv \
        --out-dir tmp/fcu_data

Dependencies:
    Standard library only (urllib, struct, zlib, argparse, json, pathlib).
"""

import argparse
import json
import os
import struct
import sys
import urllib.request
import zlib
from pathlib import Path

DEFAULT_FCU_ZIP_URL = "https://fdddata.lbl.gov/data/Simulated_LBNL_FDD_Data_Sets_FCU/LBNL_FDD_Data_Sets_FCU.zip"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


def fetch_bytes(url: str, start: int, end: int) -> bytes:
    """Fetch byte range [start, end] via HTTP Range request."""
    req = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Range": f"bytes={start}-{end}"}
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        if resp.status not in (200, 206):
            raise RuntimeError(f"HTTP request failed with status {resp.status}")
        return resp.read()


def get_remote_file_size(url: str) -> int:
    """Get total archive size via HTTP HEAD."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT}, method="HEAD")
    with urllib.request.urlopen(req, timeout=30) as resp:
        cl = resp.headers.get("Content-Length")
        if cl:
            return int(cl)
    raise RuntimeError("Could not determine remote content length from HEAD request.")


def parse_central_directory(url: str, total_size: int = None):
    """
    Parses ZIP End of Central Directory (EOCD) and Central Directory records
    using targeted HTTP range requests.
    """
    if total_size is None:
        total_size = get_remote_file_size(url)

    # Fetch last 65,536 bytes to find EOCD
    tail_len = min(65536, total_size)
    tail = fetch_bytes(url, total_size - tail_len, total_size - 1)

    eocd_sig = b"PK\x05\x06"
    eocd_pos = tail.rfind(eocd_sig)
    if eocd_pos == -1:
        raise RuntimeError("EOCD signature not found in the final 64KB of the archive.")

    eocd = tail[eocd_pos:]
    _, _, num_entries_disk, total_entries, cd_size, cd_offset = struct.unpack("<HHHHII", eocd[4:20])

    # Fetch central directory bytes
    cd_bytes = fetch_bytes(url, cd_offset, cd_offset + cd_size - 1)

    entries = []
    cd_sig = b"PK\x01\x02"
    offset = 0

    for _ in range(total_entries):
        if not cd_bytes.startswith(cd_sig, offset):
            break
        # Unpack central directory file header
        (sig, ver_made, ver_need, flags, comp_method, mod_time, mod_date, crc32,
         c_size, u_size, fn_len, extra_len, comment_len,
         disk_start, int_attr, ext_attr, local_offset) = struct.unpack("<IHHHHHHIIIHHHHHII", cd_bytes[offset:offset + 46])

        fn_start = offset + 46
        filename = cd_bytes[fn_start:fn_start + fn_len].decode("utf-8", errors="replace")
        entries.append({
            "name": filename,
            "comp_method": comp_method,
            "comp_size": c_size,
            "uncomp_size": u_size,
            "local_offset": local_offset,
            "crc32": crc32
        })
        offset += 46 + fn_len + extra_len + comment_len

    return entries, total_size


def extract_member(url: str, entry: dict, out_dir: Path) -> Path:
    """Extract a single member from remote zip into out_dir."""
    out_dir.mkdir(parents=True, exist_ok=True)
    basename = Path(entry["name"]).name
    out_file = out_dir / basename

    # Read local header (up to 512 bytes to include filename and extra fields)
    loc_offset = entry["local_offset"]
    loc_hdr_bytes = fetch_bytes(url, loc_offset, loc_offset + 511)
    if not loc_hdr_bytes.startswith(b"PK\x03\x04"):
        raise RuntimeError(f"Invalid local header signature for {entry['name']} at offset {loc_offset}")

    sig, ver, flags, comp_method, mtime, mdate, crc, loc_c_size, loc_u_size, fn_len, extra_len = struct.unpack(
        "<IHHHHHIIIHH", loc_hdr_bytes[:30]
    )
    # Use non-zero compressed size
    comp_size = loc_c_size if loc_c_size > 0 else entry["comp_size"]
    uncomp_size = loc_u_size if loc_u_size > 0 else entry["uncomp_size"]

    data_start = loc_offset + 30 + fn_len + extra_len
    data_end = data_start + comp_size - 1

    comp_data = fetch_bytes(url, data_start, data_end)

    if entry["comp_method"] == 0:
        raw_data = comp_data
    elif entry["comp_method"] == 8:
        # Deflate without zlib wrapper (-15)
        raw_data = zlib.decompressobj(-15).decompress(comp_data)
    else:
        raise ValueError(f"Unsupported compression method: {entry['comp_method']}")

    if len(raw_data) != uncomp_size:
        raise ValueError(f"Uncompressed size mismatch: expected {uncomp_size}, got {len(raw_data)}")

    with open(out_file, "wb") as f:
        f.write(raw_data)

    return out_file


def main():
    parser = argparse.ArgumentParser(description="Selective range extraction of LBNL FCU dataset members.")
    parser.add_argument("--url", default=DEFAULT_FCU_ZIP_URL, help="Remote URL of the dataset ZIP archive.")
    parser.add_argument("--list", action="store_true", help="List all members in the remote ZIP central directory.")
    parser.add_argument("--files", type=str, default="", help="Comma-separated filenames or substrings to extract.")
    parser.add_argument("--out-dir", type=str, default="tmp/fcu_data", help="Output directory to save extracted CSVs.")
    parser.add_argument("--seed-dir", type=str, default="", help="Optional local directory to copy pre-downloaded CSVs from.")
    parser.add_argument("--save-index", type=str, default="", help="Optional path to save central directory index JSON.")
    args = parser.parse_args()

    print(f"Connecting to archive: {args.url} ...")
    entries, total_size = parse_central_directory(args.url)
    print(f"Archive confirmed. Total size: {total_size / (1024*1024):.2f} MB, Total members: {len(entries)}")

    if args.save_index:
        idx_path = Path(args.save_index)
        idx_path.parent.mkdir(parents=True, exist_ok=True)
        with open(idx_path, "w", encoding="utf-8") as f:
            json.dump(entries, f, indent=2)
        print(f"Central directory index saved to: {idx_path}")

    if args.list:
        print("\n=== Archive Members Inventory ===")
        for i, e in enumerate(entries):
            mb = e["uncomp_size"] / (1024 * 1024)
            print(f"[{i:2d}] {e['name']:<50} {mb:6.2f} MB")
        return

    if not args.files:
        print("No files specified for extraction. Use --list or --files <pattern1,pattern2>.")
        return

    patterns = [p.strip() for p in args.files.split(",") if p.strip()]
    matched_entries = []
    for e in entries:
        for p in patterns:
            if p in e["name"] or p == Path(e["name"]).name:
                matched_entries.append(e)
                break

    if not matched_entries:
        print(f"No archive members matched the provided patterns: {patterns}")
        return

    out_dir = Path(args.out_dir)
    print(f"\nExtracting {len(matched_entries)} matched member(s) to: {out_dir.resolve()}")

    for e in matched_entries:
        basename = Path(e["name"]).name
        target = out_dir / basename
        if target.exists() and target.stat().st_size == e["uncomp_size"]:
            print(f"  [SKIPPED - EXISTS] {basename} ({e['uncomp_size'] / (1024*1024):.2f} MB)")
            continue
        if args.seed_dir:
            seed_file = Path(args.seed_dir) / basename
            if seed_file.exists() and seed_file.stat().st_size == e["uncomp_size"]:
                import shutil
                print(f"  [SEEDED] {basename} from seed dir")
                shutil.copy2(seed_file, target)
                continue
        print(f"  [EXTRACTING] {e['name']} (comp: {e['comp_size']/(1024*1024):.2f} MB -> uncomp: {e['uncomp_size']/(1024*1024):.2f} MB) ...")
        out_file = extract_member(args.url, e, out_dir)
        print(f"  [VERIFIED] Extracted to {out_file.name}")

    print("\nExtraction complete.")


if __name__ == "__main__":
    main()
