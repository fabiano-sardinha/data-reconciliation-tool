from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = [
    "Customer ID",
    "Name",
    "Email",
    "Status"
]

# +2 because the pandas index starts at 0 and row 1 of the Excel file is the
# header. Used to convert a pandas index into an Excel row number.
EXCEL_ROW_OFFSET = 2


class InputFileError(Exception):
    """Predictable error: an input file is missing or invalid."""


class DataValidationError(ValueError):
    """Predictable error: the content of a file does not meet the rules.

    It is a subclass of ValueError to stay compatible with the code and
    tests that already expected ValueError.
    """


def validate_input_files(file_a, file_b):

    # Check both files before failing, so that the message lists all
    # problems at once
    problems = []

    for label, path in (("File A", file_a), ("File B", file_b)):

        file_path = Path(path)

        if not file_path.exists():
            problems.append(f"{label} not found: '{path}'")

        elif not file_path.is_file():
            problems.append(f"{label} is not a file: '{path}'")

    if problems:
        raise InputFileError(
            "Cannot start reconciliation.\n"
            + "\n".join(f"- {problem}" for problem in problems)
            + "\nCheck the file paths and try again."
        )


def validate_file(df, file_name):

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise DataValidationError(
            f"Invalid file '{file_name}'. "
            f"Missing required columns: {', '.join(missing_columns)}"
        )

    if df["Customer ID"].isna().any():
        raise DataValidationError(
            f"Invalid file '{file_name}'. "
            "Customer ID contains empty values"
        )

def find_duplicates(df, file_name):

    duplicate_rows = df[
        df.duplicated(
            subset=["Customer ID"],
            keep=False
        )
    ]

    duplicate_info = {}

    if not duplicate_rows.empty:

        print(f"\nDuplicates found in {file_name}:")

        for customer_id, group in duplicate_rows.groupby("Customer ID"):

            excel_rows = (group.index + EXCEL_ROW_OFFSET).tolist()

            duplicate_info[customer_id] = excel_rows

            print(
                f"- Customer ID: {customer_id} "
                f"(rows: {', '.join(map(str, excel_rows))})"
            )

    return duplicate_info
