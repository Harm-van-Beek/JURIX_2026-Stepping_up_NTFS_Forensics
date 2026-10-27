"""
Label NTFS timestamp structures from an MFT JSON export.

This script reads a newline-delimited JSON MFT export from MFTECmd.exe,
processes only file records (`IsDirectory` false), and writes a CSV with
structure labels and match flags for later statistics calculation.

The script analyzes 8 NTFS timestamps (SI and FN attributes with 4 timestamps each)
and groups them by identical values to create structure signatures. These signatures
are then matched against known reachable timestamp structures to classify file records.
"""

from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any
from functools import cmp_to_key
from normal_NTFS_TS.normal_NTFS_TS import normal_NTFS_TS
from normal_NTFS_TS.normal_NTFS_TS_restricted import normal_NTFS_TS_restricted

# Mapping of timestamp field names to MFTECmd.exe JSON field names
# SI = Standard Information attribute, FN = File Name attribute
# _1, _2, _3, _4 represent Created, LastModified, LastRecordChange, LastAccess
# 0x10 = SI attribute, 0x30 = FN attribute
TIMESTAMP_FIELDS = {
    "si_1": "Created0x10",
    "si_2": "LastModified0x10",
    "si_3": "LastRecordChange0x10",
    "si_4": "LastAccess0x10",
    "fn_1": "Created0x30",
    "fn_2": "LastModified0x30",
    "fn_3": "LastRecordChange0x30",
    "fn_4": "LastAccess0x30",
}

# CSV output field names in order
OUTPUT_FIELDS = [
    "EntryNumber",
    "ParentPath",
    "FileName",
    "Extension",
    "IsDirectory",
    "IsAds",
    "HasAds",
    "FileSize",
    "SourceFile",
    *TIMESTAMP_FIELDS.values(),
    "structure_8",        # Structure of all 8 timestamps
    "structure_6",        # Structure of 6 timestamps (without SI_4 and FN_4)
    "structure_8_match",  # Whether structure_8 matches known reachable structures
    "structure_6_match",  # Whether structure_6 matches known reachable structures
]


def parse_timestamp(value: Any) -> datetime | None:
    """
    Parse a timestamp value from the MFT JSON export.
    
    Handles ISO format strings and datetime objects. Returns None for empty/invalid values.
    
    Args:
        value: The timestamp value to parse (string, datetime, or None)
    
    Returns:
        A datetime object or None if the value is None, empty, or cannot be parsed
    """
    if value is None or value == "":
        return None
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return None
    return value

def si_before_fn(item1: str, item2: str) -> int:
    """
    Comparison function for sorting timestamp names: SI attributes before FN attributes.
    
    When timestamps have the same value, we want to group and sort them with SI (0x10)
    coming before FN (0x30) for consistent structure representation.
    
    Args:
        item1: First timestamp name (e.g., "si_1", "fn_2")
        item2: Second timestamp name
    
    Returns:
        -1 if item1 < item2, 0 if equal, 1 if item1 > item2
    """
    if item1.startswith("si_") and item2.startswith("fn_"):
        return -1
    if item1.startswith("fn_") and item2.startswith("si_"):
        return 1
    if item1 < item2:
        return -1
    if item1 > item2:
        return 1
    return 0

def group_timestamps_by_value(timestamps: dict[str, Any]) -> list[list[str]]:
    """
    Group timestamp names by their identical values.
    
    This function identifies which timestamps have the same value and groups them together.
    Groups are sorted by timestamp value (newest first) and within each group, names are
    sorted with SI attributes before FN attributes.
    
    Args:
        timestamps: Dictionary mapping timestamp names to datetime values
    
    Returns:
        List of groups, where each group is a list of timestamp names with identical values.
        Groups are ordered by timestamp value (descending).
    
    Example:
        Input: {"si_1": datetime(2023,1,1), "fn_1": datetime(2023,1,1), "si_2": datetime(2023,1,2)}
        Output: [["si_2"], ["si_1", "fn_1"]]
    """
    # Filter out None values (missing timestamps)
    present = {name: value for name, value in timestamps.items() if value is not None}
    
    # Group timestamp names by their datetime value
    groups: dict[datetime, list[str]] = {}
    for name, value in present.items():
        groups.setdefault(value, []).append(name)
    
    # Sort groups by timestamp value (newest first), then sort names within each group
    sorted_groups = sorted(groups.items(), key=lambda item: item[0], reverse=True)
    return [sorted(names, key=cmp_to_key(si_before_fn)) for _, names in sorted_groups]


def label_structure(groups: list[list[str]]) -> str:
    """
    Generate a structure label from grouped timestamp names.
    
    Creates a canonical string representation of timestamp groups separated by "::",
    with names within each group separated by ".".
    
    Args:
        groups: List of timestamp name groups (output of group_timestamps_by_value)
    
    Returns:
        Structure label string (e.g., "si_1.fn_1::si_2.fn_2::si_3")
    
    Example:
        Input: [["si_1", "fn_1"], ["si_2"], ["si_3", "fn_3", "fn_4"]]
        Output: "si_1.fn_1::si_2::si_3.fn_3.fn_4"
    """
    return "::".join(".".join(group) for group in groups)


def compute_structure_tags(record: dict[str, Any]) -> dict[str, str]:
    """
    Compute timestamp structure labels and match flags for an MFT file record.
    
    Extracts 8 timestamps from the record and computes two structure signatures:
    - structure_8: All 8 timestamps (SI_1-4, FN_1-4)
    - structure_6: 6 timestamps (SI_1-3, FN_1-3) - excluding last access times
    
    Each structure is checked against known reachable NTFS timestamp patterns.
    
    Args:
        record: MFT file record dictionary from MFTECmd JSON
    
    Returns:
        Dictionary with keys:
        - structure_8: Canonical structure label for 8 timestamps
        - structure_6: Canonical structure label for 6 timestamps
        - structure_8_match: "8_match" or "8_no_match"
        - structure_6_match: "6_match" or "6_no_match"
    """
    # Extract and parse all 8 timestamps from the record
    timestamps_8 = {
        name: parse_timestamp(record.get(field))
        for name, field in TIMESTAMP_FIELDS.items()
    }
    
    # Extract subset of 6 timestamps (exclude SI_4 and FN_4 - last access times)
    timestamps_6 = {
        name: timestamps_8[name]
        for name in ("si_1", "si_2", "si_3", "fn_1", "fn_2", "fn_3")
    }

    # Group timestamps by value and create structure labels
    structure_8 = group_timestamps_by_value(timestamps_8)
    structure_6 = group_timestamps_by_value(timestamps_6)

    return {
        "structure_8": f"8_{label_structure(structure_8)}",
        "structure_6": f"6_{label_structure(structure_6)}",
        "structure_8_match": "8_match" if structure_8 in normal_NTFS_TS else "8_no_match",
        "structure_6_match": "6_match" if structure_6 in normal_NTFS_TS_restricted else "6_no_match",
    }


def read_json_records(path: Path):
    """
    Read newline-delimited JSON records from a file.
    
    Parses MFTECmd.exe JSON output where each line contains one JSON object.
    Skips empty lines and raises descriptive errors for invalid JSON.
    
    Args:
        path: Path to the newline-delimited JSON file
    
    Yields:
        Parsed JSON objects (dictionaries)
    
    Raises:
        ValueError: If a line contains invalid JSON
    """
    with path.open("r", encoding="utf-8") as fh:
        for line_number, line in enumerate(fh, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON on line {line_number}: {exc}") from exc


def build_output_row(record: dict[str, Any]) -> dict[str, Any]:
    """
    Build a CSV output row from an MFT file record.
    
    Extracts file metadata and computes timestamp structure information for a single record.
    
    Args:
        record: MFT file record dictionary from MFTECmd JSON
    
    Returns:
        Dictionary with all fields ready for CSV output
    """
    # Extract basic file metadata
    data = {
        "EntryNumber": record.get("EntryNumber"),
        "ParentPath": record.get("ParentPath"),
        "FileName": record.get("FileName"),
        "Extension": record.get("Extension"),
        "IsDirectory": record.get("IsDirectory"),
        "IsAds": record.get("IsAds"),
        "HasAds": record.get("HasAds"),
        "FileSize": record.get("FileSize"),
        "SourceFile": record.get("SourceFile"),
    }
    
    # Add all timestamp fields
    for field in TIMESTAMP_FIELDS.values():
        data[field] = record.get(field)
    
    # Compute and add structure labels and match flags
    data.update(compute_structure_tags(record))
    return data


def write_csv(rows: list[dict[str, Any]], output_path: Path) -> None:
    """
    Write rows to a CSV file.
    
    Args:
        rows: List of dictionaries to write (one row per dictionary)
        output_path: Path to the output CSV file
    """
    with output_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main() -> None:
    """
    Main entry point: parse arguments, process MFT JSON, and write CSV output.
    
    Reads newline-delimited JSON from MFTECmd.exe, processes file records (excluding directories),
    computes timestamp structures, and writes results to CSV.
    """
    parser = argparse.ArgumentParser(
        description="Label NTFS timestamp structures from an MFT JSON export."
    )
    parser.add_argument("input", type=Path, help="Path to newline-delimited MFT JSON file")
    parser.add_argument(
        "output",
        type=Path,
        nargs="?",
        default=Path("timestamp_structures_labeled.csv"),
        help="Output CSV path (default: timestamp_structures_labeled.csv)",
    )
    args = parser.parse_args()

    # Process all file records (exclude directories)
    rows: list[dict[str, Any]] = []
    for record in read_json_records(args.input):
        if record.get("IsDirectory") is False:
            rows.append(build_output_row(record))

    # Write results to CSV
    write_csv(rows, args.output)
    print(f"Wrote {len(rows)} file records to {args.output}")


if __name__ == "__main__":
    main()
