import pandas as pd

from validation import validate_input_files, validate_file, find_duplicates
from reporting import create_excel_report
from rules import get_status, get_changes


def run_reconciliation(file_a, file_b, output_file):

    # Check that the input files exist before trying to read them
    validate_input_files(file_a, file_b)

    # Read the Excel files
    df_a = pd.read_excel(file_a)
    df_b = pd.read_excel(file_b)

    # Validate the input files
    validate_file(df_a, file_a)
    validate_file(df_b, file_b)

    duplicates_a = find_duplicates(df_a, file_a)
    duplicates_b = find_duplicates(df_b, file_b)

    print("Input files validated successfully.")

    # Show the loaded files
    print("File A:")
    print(df_a)

    print("\nFile B:")
    print(df_b)

    # Compare the files using Customer ID
    merged = pd.merge(
        df_a,
        df_b,
        on="Customer ID",
        how="outer",
        suffixes=("_A", "_B"),
        indicator=True
    )

    # Create the Status column
    merged["Status"] = merged.apply(get_status, axis=1)
    merged["Changes"] = merged.apply(get_changes, axis=1)

    # Handle duplicate records
    duplicate_ids_a = set(duplicates_a.keys())
    duplicate_ids_b = set(duplicates_b.keys())

    all_duplicate_ids = duplicate_ids_a | duplicate_ids_b

    if all_duplicate_ids:

        for customer_id in all_duplicate_ids:

            mask = merged["Customer ID"] == customer_id

            merged.loc[mask, "Status"] = "DUPLICATE"

            sources = []

            if customer_id in duplicate_ids_a:
                sources.append("File A")

            if customer_id in duplicate_ids_b:
                sources.append("File B")

            lines = []

            if customer_id in duplicates_a:
                lines.extend(duplicates_a[customer_id])

            if customer_id in duplicates_b:
                lines.extend(duplicates_b[customer_id])

            lines = sorted(set(lines))

            merged.loc[mask, "Changes"] = (
                "Customer ID appears multiple times in "
                + " and ".join(sources)
            )

        # Keep only one row per Customer ID in the report
        merged = merged.drop_duplicates(
            subset=["Customer ID"],
            keep="first"
        )

    # Create the column with the duplicate rows
    result_df = merged[
        [
            "Customer ID",
            "Name_A",
            "Name_B",
            "Email_A",
            "Email_B",
            "Status_A",
            "Status_B",
            "Status",
            "Changes"
        ]
    ].copy()

    result_df["Duplicate Rows"] = ""

    for customer_id in all_duplicate_ids:

        rows = []

        if customer_id in duplicates_a:
            rows.extend(duplicates_a[customer_id])

        if customer_id in duplicates_b:
            rows.extend(duplicates_b[customer_id])

        rows = sorted(set(rows))

        mask = result_df["Customer ID"] == customer_id

        result_df.loc[mask, "Duplicate Rows"] = ", ".join(
            map(str, rows)
        )

    # Show the result in the terminal
    print("\nReconciliation result:")
    print(result_df)

    # Create the Excel report
    create_excel_report(result_df, output_file)
