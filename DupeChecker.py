import pandas as pd
import argparse
import os
from collections import defaultdict

def check_duplicate_channel_cue(file_paths):
    """
    Checks multiple CSV files for duplicate (#Channel, #Cue) pairs across all files.
    The script assumes the column headers are in the 3rd row (header=2).
    A comprehensive report is generated listing all locations for every duplicate pair.

    Args:
        file_paths (list): A list of file paths to the CSV files to check.
    """
    # Dictionary to map a (channel, cue) pair to a list of ALL its occurrences.
    # Stores: (channel, cue) -> list of [(file_path, line_number), ...]
    pair_origins = defaultdict(list)

    duplicates_found = False
    required_columns = ['#Channel', '#Cue']

    print(f"--- Starting Duplicate Check across {len(file_paths)} files ---")
    print("-" * 70)
    print("NOTE: Line numbers refer to the absolute line in the CSV file (starting from 1).")
    print("-" * 70)

    # --- 1. Processing all files and collecting all occurrences ---
    for file_path in file_paths:
        if not os.path.exists(file_path):
            print(f"ERROR: File not found: {file_path}. Skipping.")
            continue

        try:
            # Read the CSV file, using the 3rd row (index 2) as the header
            # The data starts on line 4 (index 3).
            df = pd.read_csv(file_path, header=2)

            # Check for required columns
            if not all(col in df.columns for col in required_columns):
                print(f"WARNING: File {file_path} is missing one or more required columns ('#Channel' and '#Cue').")
                print("         Ensure these column names exist in the 3rd row of the file.")
                continue

            # Iterate over the rows of the DataFrame
            # The actual CSV line number is calculated as: idx + 3
            for idx, row in df.iterrows():
                # Check for null values in the key columns
                if pd.isna(row['#Channel']) or pd.isna(row['#Cue']):
                    continue # Skip rows where key data is missing

                try:
                    # Convert to integer and create the pair tuple
                    channel = int(row['#Channel'])
                    cue = int(row['#Cue'])
                    pair = (channel, cue)
                    csv_line_number = idx + 3 # Line number in original CSV file

                    # Store the occurrence (file and line)
                    pair_origins[pair].append((file_path, csv_line_number))

                except ValueError:
                    print(f"WARNING: Skipping row {idx+3} in {file_path}. #Channel or #Cue is not a valid integer. Check data type.")
                
        except pd.errors.EmptyDataError:
            print(f"WARNING: File {file_path} is empty. Skipping.")
        except pd.errors.ParserError:
            print(f"ERROR: Could not parse CSV file {file_path}. Is the format correct? Skipping.")
        except Exception as e:
            print(f"An unexpected error occurred while processing {file_path}: {e}")

    # --- 2. Generating the final report ---
    print("-" * 70)
    print("--- Duplicate Report Summary ---")
    
    # Iterate through all tracked pairs and identify duplicates (where count > 1)
    for pair, occurrences in pair_origins.items():
        if len(occurrences) > 1:
            duplicates_found = True
            channel, cue = pair
            print(f"\nDUPLICATE PAIR FOUND: Channel {channel}, Cue {cue}")
            print(f"  Total occurrences: {len(occurrences)}")
            print("  Locations:")
            
            # Print all locations
            for file_path, line_number in occurrences:
                print(f"    -> File: '{file_path}' (Line: {line_number+1})")

    print("-" * 70)

    if not duplicates_found:
        print("SUCCESS: No duplicate (#Channel, #Cue) pairs were found across any of the files.")
    else:
        print("COMPLETED: Review the 'DUPLICATE PAIR FOUND' reports above for all conflicting locations.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Check multiple CSV files for duplicate pairs of (#Channel, #Cue)."
    )
    parser.add_argument(
        'files',
        metavar='FILE',
        type=str,
        nargs='+',
        help='One or more paths to the CSV files to check.'
    )

    args = parser.parse_args()
    check_duplicate_channel_cue(args.files)