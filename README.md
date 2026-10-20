# Data Reconciliation Tool

Reusable Python tool for automated data reconciliation and Excel reporting.

## Overview

The Data Reconciliation Tool compares data from two Excel files and identifies differences between them.

It is designed to automate manual reconciliation processes commonly found in IT operations, application support, data processing and business workflows.

The tool can identify:

- Records that match between both files
- Records with changed information
- Records missing from the second file
- New records found in the second file
- Duplicate Customer IDs
- The Excel rows where duplicates were found

## How It Works

1. Run `python src/main.py`. A Tkinter file dialog opens so you can select **File A** and then **File B**.
2. The tool checks that both selected paths exist and are files.
3. Each file is read and validated (required columns and non-empty Customer IDs).
4. Duplicate Customer IDs are detected and reported. They do not stop the processing.
5. The two files are compared using the Customer ID.
6. A formatted Excel report is written to `output/reconciliation_report.xlsx`.

Loaded data, detected duplicates and the reconciliation result are also printed to the terminal.

If you close a file dialog without selecting a file, the execution is cancelled.

## Input Files

**Format:** Excel workbooks in `.xlsx` format. Data is read from the first worksheet, and the first row must contain the column headers.

The file dialog also lists `.xls` files, but reading them requires an extra package (`xlrd`) that is not part of `requirements.txt`. Treat `.xls` as not supported (see [Known Limitations](#known-limitations)).

**Required columns** (the names must match exactly, including capitalization):

| Column | Rule |
|---|---|
| Customer ID | Required. Must not contain empty values. Used to match records between the two files |
| Name | Required. Compared between the two files |
| Email | Required. Compared between the two files |
| Status | Required. Compared between the two files |

Additional columns may be present in the input files. The tool only uses the columns required for the reconciliation rules.

Values are compared exactly as they appear in the files, with the following rules for empty cells in the Name, Email and Status columns:

- If the cell is empty in both files, the values are considered equal, and no change is reported for that field.
- If the cell is empty in only one of the files, the values are considered different and the record is reported as `CHANGED`.

## Reconciliation Results

The tool currently generates the following statuses:

| Status | Description |
|---|---|
| MATCHED | Record exists in both files with the same information |
| CHANGED | Record exists in both files but one or more fields changed |
| MISSING | Record exists only in File A |
| NEW | Record exists only in File B |
| DUPLICATE | Customer ID appears more than once in an input file |

Records are matched using the Customer ID. For Customer IDs that exist in both files, the Name, Email and Status values are compared.

### Duplicate Detection

A Customer ID is a duplicate when it appears more than once **within the same file** (File A, File B or both).

- Duplicates do not stop the reconciliation. They are reported in the result.
- The Customer ID receives the status `DUPLICATE`, which takes priority over the other statuses.
- The report contains a single row per duplicated Customer ID.
- The `Changes` column indicates in which file or files the Customer ID appears multiple times (for example, "Customer ID appears multiple times in File A").
- The `Duplicate Rows` column lists the Excel row numbers where the duplicate was found, in ascending order. Row 1 is the header, so the first data row is row 2. If the Customer ID is duplicated in both files, the rows from both files are combined in the same list.

## Output

The tool generates an Excel report containing the following columns:

| Column | Description |
|---|---|
| Customer ID | Identifier used to match the records |
| Name_A, Name_B | Name in File A and in File B |
| Email_A, Email_B | Email in File A and in File B |
| Status_A, Status_B | Value of the input `Status` column in File A and in File B |
| Status | Reconciliation result (MATCHED, CHANGED, MISSING, NEW or DUPLICATE) |
| Changes | Description of the detected differences |
| Duplicate Rows | Excel rows where the Customer ID is duplicated (empty when there are no duplicates) |

In the `Changes` column, a missing value is displayed as `(empty)`. For example: `Email: (empty) -> bruno@x.com` or `Email: maria@x.com -> (empty)`. A field that is empty in both files is not reported as a change.

The generated report includes formatting, filters, frozen headers and conditional formatting for the reconciliation statuses.

The report is always written to `output/reconciliation_report.xlsx`. The `output` folder is created automatically if it does not exist. An existing report with the same name is overwritten.

If an input file is not valid, no new report is generated.

## Project Structure

```text
data-reconciliation-tool/
│
├── src/
│   ├── main.py
│   ├── reconcile.py
│   ├── reporting.py
│   ├── rules.py
│   └── validation.py
│
├── tests/
│   ├── conftest.py
│   ├── test_main.py
│   ├── test_reconcile.py
│   ├── test_rules.py
│   └── test_validation.py
│
├── input/            # optional place for your input files (ignored by Git)
├── output/           # generated reports (created automatically, ignored by Git)
├── .gitignore
├── pytest.ini
├── requirements.txt
└── README.md
```

## Requirements

- Python 3.14+
- Tkinter (part of the Python standard library, used for the file selection dialog; it is included in the standard Windows installer, while some Linux distributions provide it as a separate package)
- pandas
- openpyxl
- pytest

## Installation

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the required packages:

```powershell
pip install -r requirements.txt
```

## Usage

Run the application from the project root folder:

```powershell
python src/main.py
```

A Tkinter window opens and asks you to select File A, and then File B. The files can be stored in any folder. The `input` folder is just a convenient place to keep them.

The reconciliation report is generated in the following path, relative to the folder from which you run the command (so run it from the project root to get the report in this project's `output` folder):

```text
output/reconciliation_report.xlsx
```

## Error Handling and Exit Codes

Predictable usage errors are shown as a short message on the error output, prefixed with `ERROR:`, without a Python traceback.

| Situation | Message (example) |
|---|---|
| File A and/or File B does not exist | `File A not found: '<path>'` |
| A selected path is a folder, not a file | `File B is not a file: '<path>'` |
| Required column is missing | `Invalid file '<path>'. Missing required columns: Status` |
| Customer ID contains empty values | `Invalid file '<path>'. Customer ID contains empty values` |

Both input paths are checked before any file is read, so a single message lists every path problem found. Content errors (missing columns, empty Customer IDs) are reported one file at a time, starting with File A. Example of a path error:

```text
ERROR: Cannot start reconciliation.
- File A not found: 'C:\data\customers_a.xlsx'
- File B is not a file: 'C:\data\folder'
Check the file paths and try again.
```

Exit codes:

| Code | Meaning |
|---|---|
| 0 | Success. The report was generated |
| 1 | Predictable error (see the table above). No new report was generated |

If you close a file dialog without selecting a file, the tool prints a cancellation message and also exits with code 1.

Errors that are not listed above are intentionally not caught, so that real problems are not hidden. In that case Python shows the full traceback. Python also exits with a non-zero status (1) for uncaught errors, so the exit code alone does not distinguish predictable errors from unexpected ones. An `ERROR:` message indicates a predictable error, while a traceback indicates an unexpected one.

Duplicate Customer IDs are not errors. They never stop the processing and are reported with the `DUPLICATE` status.

## Running Tests

Run the automated test suite from the project root with:

```powershell
pytest
```

`pytest.ini` adds the `src` folder to the Python path, so no extra configuration is needed.

The tests create temporary Excel files (using pytest's `tmp_path`) and replace the Tkinter dialog, so they do not depend on the files in `input/` or `output/` and do not open any window.

| Test file | Coverage |
|---|---|
| `tests/conftest.py` | Shared fixtures that create temporary Excel files |
| `tests/test_main.py` | Exit codes (0 and 1), error messages and the file selection flow |
| `tests/test_reconcile.py` | End-to-end reconciliation, the five statuses, duplicates, automatic creation of the output folder, no report on errors, and an end-to-end test of empty values in the generated Excel report |
| `tests/test_rules.py` | Status and change rules, comparison of empty values (two empty values are equal, one empty value is a change) and the `(empty)` display of missing values in the change messages |
| `tests/test_validation.py` | Input file checks, required columns, empty Customer IDs and duplicate detection |

## Known Limitations

- Only `.xlsx` files are supported. `.xls` files appear in the file dialog, but the package needed to read them (`xlrd`) is not included in `requirements.txt`.
- Only the first worksheet of each file is read.
- The report location is fixed (`output/reconciliation_report.xlsx`) and cannot be chosen in the interface.
- The required column names are fixed and must match exactly.
- Values are compared exactly, without trimming spaces or ignoring capitalization.
- Problems that are not covered by the predictable errors above (for example, an unreadable file, or a file or report that is open in another program) are not specially handled and may show a Python traceback.

## Development Goals

Future versions will focus on:

- Support for configurable column mappings
- More flexible reconciliation rules
- Additional data validation
- Improved handling of different Excel structures
- More detailed logging
- User-friendly interface
- Reusable configuration for different clients and business processes

## License

This project is currently intended as a portfolio and development project.
