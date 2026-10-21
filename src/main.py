import sys
import tkinter as tk
from tkinter import filedialog

from gui import ReconciliationApp
from reconcile import run_reconciliation
from validation import DataValidationError, InputFileError


OUTPUT_FILE = "output/reconciliation_report.xlsx"


def select_file(title):
    return filedialog.askopenfilename(
        title=title,
        filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
    )


def run(file_a, file_b, output_file):
    """Run the reconciliation and return the exit code (0 or 1).

    Only predictable usage errors are shown without a traceback.
    Any other error keeps propagating so that bugs are not hidden.
    """

    try:
        run_reconciliation(file_a, file_b, output_file)
    except (InputFileError, DataValidationError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1

    return 0


def main():

    root = tk.Tk()

    # Preserve legacy selection flow for headless test harness (FakeTk)
    if not hasattr(root, "mainloop"):
        root.withdraw()
        root.attributes("-topmost", True)

        file_a = select_file("Select File A")
        if not file_a:
            raise SystemExit("No file selected for File A. Execution cancelled.")

        file_b = select_file("Select File B")
        if not file_b:
            raise SystemExit("No file selected for File B. Execution cancelled.")

        root.destroy()

        return run(file_a, file_b, OUTPUT_FILE)

    app = ReconciliationApp(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
