import pandas as pd

from validation import (
    EXCEL_ROW_OFFSET,
    validate_input_files,
    validate_file,
    find_duplicates,
)
from reporting import create_excel_report
from rules import get_status, get_changes, values_differ


FILE_A_LABEL = "File A"
FILE_B_LABEL = "File B"

# Shown in the main sheet when the occurrences of a duplicated Customer ID
# have different values in the same file
DIFFERENT_VALUES = "(different values)"

RESULT_COLUMNS = [
    "Customer ID",
    "Name_A",
    "Name_B",
    "Email_A",
    "Email_B",
    "Status_A",
    "Status_B",
    "Status",
    "Changes",
    "Duplicate Rows"
]

DETAILS_COLUMNS = [
    "Customer ID",
    "Source File",
    "Excel Row",
    "Name",
    "Email",
    "Status",
    "Occurrences in File"
]


def sort_by_customer_id(df):

    # A stable sort keeps File A before File B and the original row order
    try:
        sorted_df = df.sort_values("Customer ID", kind="stable")
    except TypeError:
        # Customer IDs of different types cannot be compared directly
        sorted_df = df.sort_values(
            "Customer ID",
            key=lambda ids: ids.astype(str),
            kind="stable"
        )

    return sorted_df.reset_index(drop=True)


def build_unique_result(df_a, df_b):
    """Compare the Customer IDs that are not duplicated in any file."""

    merged = pd.merge(
        df_a,
        df_b,
        on="Customer ID",
        how="outer",
        suffixes=("_A", "_B"),
        indicator=True
    )

    if merged.empty:
        merged["Status"] = pd.Series(dtype="object")
        merged["Changes"] = pd.Series(dtype="object")
    else:
        merged["Status"] = merged.apply(get_status, axis=1)
        merged["Changes"] = merged.apply(get_changes, axis=1)

    result = merged[
        [column for column in RESULT_COLUMNS if column != "Duplicate Rows"]
    ].copy()

    result["Duplicate Rows"] = ""

    return result


def build_duplicate_details(df_a, df_b, duplicate_ids):
    """List every occurrence of the duplicated Customer IDs.

    There is one row per occurrence in each file. The occurrences of File A
    and File B are never combined with each other.
    """

    parts = []

    for label, df in ((FILE_A_LABEL, df_a), (FILE_B_LABEL, df_b)):

        occurrences = df[df["Customer ID"].isin(duplicate_ids)]

        if occurrences.empty:
            continue

        parts.append(pd.DataFrame({
            "Customer ID": occurrences["Customer ID"].to_numpy(),
            "Source File": label,
            "Excel Row": occurrences.index.to_numpy() + EXCEL_ROW_OFFSET,
            "Name": occurrences["Name"].to_numpy(),
            "Email": occurrences["Email"].to_numpy(),
            "Status": occurrences["Status"].to_numpy()
        }))

    if not parts:
        return pd.DataFrame(columns=DETAILS_COLUMNS)

    details = sort_by_customer_id(pd.concat(parts, ignore_index=True))

    details["Occurrences in File"] = details.groupby(
        ["Customer ID", "Source File"]
    )["Excel Row"].transform("size")

    return details[DETAILS_COLUMNS]


def summarize_values(values):
    """Single value to show in the main sheet for one file.

    Empty when the Customer ID is not in the file. The value itself when all
    the occurrences agree. Otherwise a marker, because choosing one of the
    values would hide the others.
    """

    if values.empty:
        return float("nan")

    first = values.iloc[0]

    if any(values_differ(first, value) for value in values.iloc[1:]):
        return DIFFERENT_VALUES

    return first


def build_duplicate_summary(details, duplicates_a, duplicates_b):
    """One row per duplicated Customer ID for the main sheet."""

    rows = []

    for customer_id, group in details.groupby("Customer ID", sort=False):

        occurrences = {
            label: group[group["Source File"] == label]
            for label in (FILE_A_LABEL, FILE_B_LABEL)
        }

        # Files where the Customer ID appears more than once
        sources = []

        if customer_id in duplicates_a:
            sources.append(FILE_A_LABEL)

        if customer_id in duplicates_b:
            sources.append(FILE_B_LABEL)

        row = {"Customer ID": customer_id}

        for column in ("Name", "Email", "Status"):
            row[f"{column}_A"] = summarize_values(
                occurrences[FILE_A_LABEL][column]
            )
            row[f"{column}_B"] = summarize_values(
                occurrences[FILE_B_LABEL][column]
            )

        row["Status"] = "DUPLICATE"
        row["Changes"] = (
            "Customer ID appears multiple times in "
            + " and ".join(sources)
        )

        # Every occurrence, with the file it comes from
        row["Duplicate Rows"] = "; ".join(
            f"{label}: " + ", ".join(map(str, rows_of_file["Excel Row"]))
            for label, rows_of_file in occurrences.items()
            if not rows_of_file.empty
        )

        rows.append(row)

    return pd.DataFrame(rows, columns=RESULT_COLUMNS)


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

    # A duplicated Customer ID cannot be compared record by record: merging
    # its occurrences would create artificial A/B combinations, and dropping
    # some of them would lose information. So these IDs are left out of the
    # comparison and reported with all their occurrences.
    duplicate_ids = set(duplicates_a) | set(duplicates_b)

    unique_a = df_a[~df_a["Customer ID"].isin(duplicate_ids)]
    unique_b = df_b[~df_b["Customer ID"].isin(duplicate_ids)]

    # Compare the files using Customer ID
    result_df = build_unique_result(unique_a, unique_b)

    # Every occurrence of the duplicated Customer IDs
    details = build_duplicate_details(df_a, df_b, duplicate_ids)

    if not details.empty:

        summary = build_duplicate_summary(
            details, duplicates_a, duplicates_b
        )

        parts = [part for part in (result_df, summary) if not part.empty]

        result_df = sort_by_customer_id(
            pd.concat(parts, ignore_index=True)
        )

    # Show the result in the terminal
    print("\nReconciliation result:")
    print(result_df)

    if not details.empty:
        print("\nDuplicate details:")
        print(details)

    # Create the Excel report
    create_excel_report(result_df, output_file, details)

    return {
        "MATCHED": int((result_df["Status"] == "MATCHED").sum()),
        "CHANGED": int((result_df["Status"] == "CHANGED").sum()),
        "MISSING": int((result_df["Status"] == "MISSING").sum()),
        "NEW": int((result_df["Status"] == "NEW").sum()),
        "DUPLICATE": int((result_df["Status"] == "DUPLICATE").sum()),
        "TOTAL": len(result_df),
    }
