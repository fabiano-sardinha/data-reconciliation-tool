"""Generate fictional Excel files that demonstrate the reconciliation tool."""

from pathlib import Path
import sys

import pandas as pd


EXAMPLES_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = EXAMPLES_DIR.parent
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from reconcile import run_reconciliation


COLUMNS = ["Customer ID", "Name", "Email", "Status"]

FILE_A_ROWS = [
    (1001, "Northwind Retail", "contact@northwind.example", "Active"),
    (1002, "Contoso Services", "billing@contoso.example", "Active"),
    (1003, "Fabrikam Logistics", "ops@fabrikam.example", "Active"),
    (1005, "Adventure Works", "orders@adventureworks.example", "Active"),
    (1005, "Adventure Works", "support@adventureworks.example", "Inactive"),
]

FILE_B_ROWS = [
    (1001, "Northwind Retail", "contact@northwind.example", "Active"),
    (1002, "Contoso Services", "billing-updated@contoso.example", "Active"),
    (1004, "Tailspin Toys", "sales@tailspin.example", "Active"),
    (1005, "Adventure Works", "finance@adventureworks.example", "Active"),
    (1005, "Adventure Works", "returns@adventureworks.example", "Closed"),
]


def write_input(path, rows):
    """Write one fictional input workbook with the required columns."""

    pd.DataFrame(rows, columns=COLUMNS).to_excel(path, index=False)


def main():
    """Create the inputs and generate the demonstration report."""

    file_a = EXAMPLES_DIR / "demo_file_a.xlsx"
    file_b = EXAMPLES_DIR / "demo_file_b.xlsx"
    report = EXAMPLES_DIR / "demo_reconciliation_report.xlsx"

    write_input(file_a, FILE_A_ROWS)
    write_input(file_b, FILE_B_ROWS)
    run_reconciliation(file_a, file_b, report)


if __name__ == "__main__":
    main()
