import pandas as pd


REQUIRED_COLUMNS = [
    "Customer ID",
    "Name",
    "Email",
    "Status"
]


def validate_file(df, file_name):

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Invalid file '{file_name}'. "
            f"Missing required columns: {', '.join(missing_columns)}"
        )

    if df["Customer ID"].isna().any():
        raise ValueError(
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

        print(f"\nDuplicados encontrados em {file_name}:")

        for customer_id, group in duplicate_rows.groupby("Customer ID"):

            # +2 porque:
            # índice do pandas começa em 0
            # e a linha 1 do Excel é o cabeçalho
            excel_rows = (group.index + 2).tolist()

            duplicate_info[customer_id] = excel_rows

            print(
                f"- Customer ID: {customer_id} "
                f"(linhas: {', '.join(map(str, excel_rows))})"
            )

    return duplicate_info