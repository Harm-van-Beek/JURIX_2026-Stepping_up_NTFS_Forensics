"""
Calculate and display timestamp structure statistics from labeled MFT records.

This script reads one or more CSV files produced by timestamp_structure_labeller.py,
aggregates timestamp structure statistics across multiple forensic images, and generates
a comprehensive statistical overview including:
- Match counts for 6-timestamp and 8-timestamp structures
- Breakdown of matched vs unmatched structures
- Frequency distribution of specific timestamp patterns

Output includes statistics per image as well as aggregated totals.
"""

import argparse
import sys
from pathlib import Path
import pandas as pd


def convert_structure_tag(tag_value: str) -> str:
    """
    Convert a structure tag to a human-readable format.
    
    Transforms the internal structure representation (e.g., "8_si_1.fn_1::si_2")
    into a readable format with bracket notation and '>' separators
    (e.g., "[si_1,fn_1] > [si_2]").
    
    Args:
        tag_value: Raw structure tag from timestamp_structure_labeller.py
    
    Returns:
        Formatted structure tag with readable notation
    
    Example:
        "8_si_1.fn_1::si_2.fn_2" -> "[si_1,fn_1] > [si_2,fn_2]"
    """
    # Remove the 8_ or 6_ prefix that indicates structure type
    if tag_value.startswith("8_") or tag_value.startswith("6_"):
        tag_value = tag_value[2:]
    
    # Convert each timestamp group from dot notation to bracket notation
    parts = []
    for part in tag_value.split("::"):  # Split groups separated by ::
        subparts = part.split(".")      # Split timestamps within group separated by .
        part = "[" + ",".join(subparts) + "]"  # Convert to [ts1,ts2,...] format
        parts.append(part)
    
    # Join groups with " > " separator for readability
    return " > ".join(parts)


def sort_and_total_dataframe(df: pd.DataFrame, imageTotal: bool = True) -> pd.DataFrame:
    """
    Sort and add totals to a DataFrame of structure counts.
    
    Sorts columns alphabetically, calculates row totals, sorts rows by total descending,
    and optionally adds a grand total row.
    
    Args:
        df: DataFrame with structure names as rows and image labels as columns
        imageTotal: If True, add a "Total" row with sum across all images (default True)
    
    Returns:
        Processed DataFrame with sorted columns, row totals, and optional grand total
    """
    # Sort columns alphabetically for consistent output
    df = df.reindex(sorted(df.columns), axis=1)
    
    # Calculate total count for each structure across all images
    df["Total"] = df.sum(numeric_only=True, axis=1)
    
    # Sort structures by total count (most frequent first)
    df = df.sort_values(by="Total", ascending=False)
    
    # Add grand total row if requested
    if imageTotal:
        df.loc["Total"] = df.sum(numeric_only=True)
    
    return df


def add_match_percentage(df: pd.DataFrame, match_suffix: str, nomatch_suffix: str, percent_label: str) -> pd.DataFrame:
    """
    Calculate and add match percentage row to the DataFrame.
    
    Computes the percentage of matched structures vs unmatched for a given structure type
    and adds the result as a new row.
    
    Args:
        df: DataFrame with match counts
        match_suffix: Row name suffix for matched structures (e.g., "8_match")
        nomatch_suffix: Row name suffix for unmatched structures (e.g., "8_no_match")
        percent_label: Label for the new percentage row
    
    Returns:
        DataFrame with added percentage row
    """
    # Find rows for matched and unmatched structures
    match_row = None
    nomatch_row = None
    for idx in df.index:
        if idx.endswith(match_suffix):
            match_row = idx
        elif idx.endswith(nomatch_suffix):
            nomatch_row = idx

    # Calculate percentages if both rows exist
    if match_row and nomatch_row:
        match_counts = df.loc[match_row]
        nomatch_counts = df.loc[nomatch_row]
        totals = match_counts + nomatch_counts
        percentages = (match_counts / totals * 100).round(2)
        df.loc[percent_label] = percentages
    
    return df


def format_dataframe_for_print(df: pd.DataFrame) -> pd.DataFrame:
    """
    Format DataFrame for console display with proper number formatting.
    
    Converts NaN values to "-", integers to strings, and percentages with 2 decimal places.
    Handles both older pandas (applymap) and newer versions (map).
    
    Args:
        df: DataFrame to format
    
    Returns:
        DataFrame with formatted values as strings
    """
    import math

    def format_value(val):
        # Display NaN as dash
        if isinstance(val, float) and math.isnan(val):
            return "-"
        
        # Format numbers: integers without decimals, floats with 2 decimals and %
        if isinstance(val, (int, float)):
            if float(val) == int(float(val)):
                return str(int(float(val)))
            return f"{val:.2f} %"
        
        # Keep other values as strings
        return str(val)

    # Use applymap for pandas < 2.1.0, map for pandas >= 2.1.0
    return df.applymap(format_value) if hasattr(df, "applymap") else df.map(format_value)


def read_labeller_csv(path: Path) -> pd.DataFrame:
    """
    Read a CSV file produced by timestamp_structure_labeller.py.
    
    Treats all values as strings to preserve format and avoids automatic NA conversion
    for better control of missing value handling.
    
    Args:
        path: Path to the CSV file
    
    Returns:
        Pandas DataFrame with all columns as strings
    
    Raises:
        RuntimeError: If the CSV file cannot be read
    """
    try:
        return pd.read_csv(path, dtype=str, keep_default_na=False, na_values=[""])
    except Exception as exc:
        raise RuntimeError(f"Failed to read CSV file {path}: {exc}") from exc


def make_image_ids(count: int) -> list[str]:
    """
    Generate sequential image IDs (A, B, C, ..., Z, AA, AB, ...) for CSV file labels.
    
    Creates a list of unique letter-based identifiers useful for distinguishing
    multiple input CSV files in the output.
    
    Args:
        count: Number of IDs to generate
    
    Returns:
        List of alphabetic IDs in sequence (e.g., ["A", "B", "C"])
    
    Example:
        make_image_ids(3) -> ["A", "B", "C"]
        make_image_ids(28) -> ["A", ..., "Z", "AA", "AB"]
    """
    ids: list[str] = []
    index = 0
    while len(ids) < count:
        result = ""
        value = index
        # Generate base-26 letter representation
        while True:
            result = chr(ord("A") + (value % 26)) + result
            value = value // 26 - 1
            if value < 0:
                break
        ids.append(result)
        index += 1
    return ids


def collect_counts(df: pd.DataFrame) -> tuple[dict[str, int], dict[str, int], dict[str, int], dict[str, int], dict[str, int]]:
    """
    Aggregate timestamp structure counts from a labeled CSV file.
    
    Processes all records in the CSV and groups them by:
    - Match status (matched vs unmatched)
    - Structure type (6-timestamp vs 8-timestamp)
    - Specific structure pattern
    
    Args:
        df: DataFrame from timestamp_structure_labeller.py output
    
    Returns:
        Tuple of 5 dictionaries:
        - match_tags: Overall match counts ("8_match", "8_no_match", "6_match", "6_no_match")
        - structure_8_match_tags: Count per matched 8-timestamp structure
        - structure_8_nomatch_tags: Count per unmatched 8-timestamp structure
        - structure_6_match_tags: Count per matched 6-timestamp structure
        - structure_6_nomatch_tags: Count per unmatched 6-timestamp structure
    """
    # Initialize count dictionaries
    structure_8_match_tags: dict[str, int] = {}
    structure_8_nomatch_tags: dict[str, int] = {}
    structure_6_match_tags: dict[str, int] = {}
    structure_6_nomatch_tags: dict[str, int] = {}
    match_tags: dict[str, int] = {}  # Overall match/nomatch counts

    # Iterate through each record and aggregate counts
    for _, row in df.iterrows():
        structure_8 = row.get("structure_8", "")
        structure_8_match = row.get("structure_8_match", "")
        structure_6 = row.get("structure_6", "")
        structure_6_match = row.get("structure_6_match", "")

        # Process 8-timestamp structures
        if structure_8:
            normalized = convert_structure_tag(structure_8)
            if structure_8_match == "8_match":
                structure_8_match_tags[normalized] = structure_8_match_tags.get(normalized, 0) + 1
                match_tags["8_match"] = match_tags.get("8_match", 0) + 1
            elif structure_8_match == "8_no_match":
                structure_8_nomatch_tags[normalized] = structure_8_nomatch_tags.get(normalized, 0) + 1
                match_tags["8_no_match"] = match_tags.get("8_no_match", 0) + 1

        # Process 6-timestamp structures
        if structure_6:
            normalized = convert_structure_tag(structure_6)
            if structure_6_match == "6_match":
                structure_6_match_tags[normalized] = structure_6_match_tags.get(normalized, 0) + 1
                match_tags["6_match"] = match_tags.get("6_match", 0) + 1
            elif structure_6_match == "6_no_match":
                structure_6_nomatch_tags[normalized] = structure_6_nomatch_tags.get(normalized, 0) + 1
                match_tags["6_no_match"] = match_tags.get("6_no_match", 0) + 1

    return (
        match_tags,
        structure_8_match_tags,
        structure_8_nomatch_tags,
        structure_6_match_tags,
        structure_6_nomatch_tags,
    )


def get_structure_stats(csv_paths: list[Path], labels: list[str]) -> None:
    """
    Read CSV files, aggregate statistics, and print a comprehensive statistical report.
    
    Processes multiple labeled CSV files, aggregates timestamp structure statistics,
    and outputs formatted tables showing match rates, structure distributions, and
    detailed frequency information.
    
    Args:
        csv_paths: List of paths to CSV files from timestamp_structure_labeller.py
        labels: List of labels corresponding to each CSV file
    """
    # Ensure UTF-8 output encoding for proper symbol and text display
    if sys.stdout.encoding != "utf-8" and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    # Initialize data storage for aggregation
    data_images: dict[str, dict[str, str]] = {}  # Image metadata
    data_match: dict[str, dict[str, int]] = {}  # Match/nomatch counts per image
    data_structure_8_match: dict[str, dict[str, int]] = {}  # 8-ts matched structures per image
    data_structure_8_nomatch: dict[str, dict[str, int]] = {}  # 8-ts unmatched structures per image
    data_structure_6_match: dict[str, dict[str, int]] = {}  # 6-ts matched structures per image
    data_structure_6_nomatch: dict[str, dict[str, int]] = {}  # 6-ts unmatched structures per image

    # Process each CSV file
    for csv_path, label in zip(csv_paths, labels):
        # Read and aggregate counts from this image
        df = read_labeller_csv(csv_path)
        (
            match_tags,
            structure_8_match_tags,
            structure_8_nomatch_tags,
            structure_6_match_tags,
            structure_6_nomatch_tags,
        ) = collect_counts(df)

        # Store results indexed by label
        data_match[label] = match_tags
        data_structure_8_match[label] = structure_8_match_tags
        data_structure_8_nomatch[label] = structure_8_nomatch_tags
        data_structure_6_match[label] = structure_6_match_tags
        data_structure_6_nomatch[label] = structure_6_nomatch_tags
        data_images[label] = {
            "label": label,
            "source": csv_path.name,
        }

    # Create DataFrames from aggregated data
    df_images = pd.DataFrame(data_images).transpose()
    #image_ids = make_image_ids(len(df_images))  # Generate short IDs (A, B, C, ...)
    #df_images["ID"] = image_ids
    #df_images.set_index("ID", inplace=True)

    # Create structure count DataFrames (fill missing values with 0)
    df_match = pd.DataFrame(data_match).fillna(0).astype(int)
    df_structure_8_match = pd.DataFrame(data_structure_8_match).fillna(0).astype(int)
    df_structure_8_nomatch = pd.DataFrame(data_structure_8_nomatch).fillna(0).astype(int)
    df_structure_6_match = pd.DataFrame(data_structure_6_match).fillna(0).astype(int)
    df_structure_6_nomatch = pd.DataFrame(data_structure_6_nomatch).fillna(0).astype(int)

    # Process match summary DataFrame: add totals and percentages
    if not df_match.empty:
        df_match["Total"] = df_match.sum(numeric_only=True, axis=1)
        # Add percentage rows for match rates
        df_match = add_match_percentage(df_match, "6_match", "6_no_match", "6_match %")
        df_match = add_match_percentage(df_match, "8_match", "8_no_match", "8_match %")
        df_match = add_match_percentage(df_match, "6_no_match", "6_match", "6_no_match %")
        df_match = add_match_percentage(df_match, "8_no_match", "8_match", "8_no_match %")
        df_match = df_match.sort_index()
    
    # Process structure DataFrames: sort by frequency and add totals
    if not df_structure_8_match.empty:
        df_structure_8_match = sort_and_total_dataframe(df_structure_8_match)
    if not df_structure_8_nomatch.empty:
        df_structure_8_nomatch = sort_and_total_dataframe(df_structure_8_nomatch)
    if not df_structure_6_match.empty:
        df_structure_6_match = sort_and_total_dataframe(df_structure_6_match)
    if not df_structure_6_nomatch.empty:
        df_structure_6_nomatch = sort_and_total_dataframe(df_structure_6_nomatch)

    # Print report header
    print('\nTimestamp Structure Statistics:')
    print('=' * 80)
    
    # Print image metadata
    print('Images:')
    print(df_images.to_string())
    print('\n' + '=' * 80)
    
    # Print overall match/nomatch summary
    print('Match Tags:')
    print(format_dataframe_for_print(df_match).to_string())

    # Print 6-timestamp structure statistics (matched)
    print('\n' + '=' * 80)
    if not df_structure_6_match.empty:
        print(f'Structure Tags (6) - MATCHED ({df_structure_6_match.shape[0]-1} structures):')
        print(format_dataframe_for_print(df_structure_6_match).to_string())
    else:
        print('Structure Tags (6) - MATCHED: (none)')

    # Print 6-timestamp structure statistics (unmatched)
    print('\n' + '-' * 80)
    if not df_structure_6_nomatch.empty:
        print(f'\nStructure Tags (6) - NO MATCH ({df_structure_6_nomatch.shape[0]-1} structures):')
        print(format_dataframe_for_print(df_structure_6_nomatch).to_string())
    else:
        print('\nStructure Tags (6) - NO MATCH: (none)')

    # Print 8-timestamp structure statistics (matched)
    print('\n' + '=' * 80)
    if not df_structure_8_match.empty:
        print(f'Structure Tags (8) - MATCHED ({df_structure_8_match.shape[0]-1} structures):')
        print(format_dataframe_for_print(df_structure_8_match).to_string())
    else:
        print('Structure Tags (8) - MATCHED: (none)')

    # Print 8-timestamp structure statistics (unmatched)
    print('\n' + '-' * 80)
    if not df_structure_8_nomatch.empty:
        print(f'\nStructure Tags (8) - NO MATCH ({df_structure_8_nomatch.shape[0]-1} structures):')
        print(format_dataframe_for_print(df_structure_8_nomatch).to_string())
    else:
        print('\nStructure Tags (8) - NO MATCH: (none)')

    print('=' * 80)


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Returns:
        Parsed arguments with csv_files and optional labels
    """
    parser = argparse.ArgumentParser(
        description='Calculate timestamp structure statistics from one or more CSV files produced by timestamp_structure_labeller.py'
    )
    parser.add_argument(
        'csv_files',
        nargs='+',
        type=Path,
        help='CSV files created by timestamp_structure_labeller.py',
    )
    parser.add_argument(
        '--labels',
        nargs='+',
        help='Optional labels for each CSV file; order must match the files',
    )
    return parser.parse_args()


def main() -> None:
    """
    Main entry point: parse arguments and generate statistics report.
    """
    args = parse_args()
    
    # Validate label count if provided
    if args.labels and len(args.labels) != len(args.csv_files):
        raise SystemExit('The number of labels must match the number of CSV files.')

    # Use provided labels or default to [A, B, C,...] for each CSV file
    labels = args.labels if args.labels else make_image_ids(len(args.csv_files))
    
    # Generate and display statistics
    get_structure_stats(args.csv_files, labels)


if __name__ == '__main__':
    main()
