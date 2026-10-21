# Data Reconciliation Tool

A Python desktop utility that compares two Excel workbooks by Customer ID and produces a formatted reconciliation report.

Built as a portfolio project for data operations, application support, finance, and business workflows where teams need to identify matching, changed, missing, new, or duplicated customer records without manually comparing spreadsheets.

Repository: https://github.com/fabiano-sardinha/data-reconciliation-tool

## The Problem It Solves

Manual spreadsheet reconciliation is slow and error-prone, especially when files contain missing records, changed values, or repeated identifiers.

This tool compares two `.xlsx` files using `Customer ID` as the record key and creates an Excel report that highlights the result for each ID. It also handles duplicate IDs safely: duplicated records are not forced into artificial A/B matches, so no occurrence is silently discarded.

## Features

- Compares two Excel workbooks using `Customer ID`
- Identifies matching, changed, missing, new, and duplicated records
- Compares `Name`, `Email`, and `Status`
- Treats two empty values as equal; reports a change when a value is empty in only one file
- Generates a formatted Excel report with filters, frozen headers, column sizing, and status-based conditional formatting
- Reports duplicate source files and original Excel row numbers
- Creates a `Duplicate Details` worksheet when duplicates exist
- Validates missing files, folder paths, required columns, and empty `Customer ID` values before writing a report

## Reconciliation Results

| Status | Description |
|---|---|
| `MATCHED` | Record exists in both files and the tracked values match |
| `CHANGED` | Record exists in both files but one or more tracked values differ |
| `MISSING` | Record exists only in File A |
| `NEW` | Record exists only in File B |
| `DUPLICATE` | Customer ID appears more than once in File A, File B, or both |

Records that exist in both files are compared using `Name`, `Email`, and `Status`. A missing value is displayed as `(empty)` in a change description.

## Duplicate-ID Handling

Duplicate IDs require special handling. A regular merge between repeated IDs can create artificial A/B record combinations and hide the original data structure.

For every duplicated Customer ID, the tool:

1. Excludes that ID from the record-to-record comparison.
2. Creates one summary row in the main report with status `DUPLICATE`.
3. Lists the source file and Excel row number of every occurrence.
4. Adds every occurrence to the `Duplicate Details` worksheet.
5. Uses `(different values)` in a summary field when the occurrences within one source file do not agree.

This preserves all duplicated records and avoids implying that unrelated repeated rows are direct matches. Repeated rows with identical values are still reported as duplicates.

## Input Requirements

The supported input format is Excel `.xlsx`. The file picker also displays `.xls`, but that format is not supported by the current dependencies.

The first worksheet is read, and the first row must contain these exact column names:

| Column | Purpose |
|---|---|
| `Customer ID` | Record identifier used for reconciliation; must not be empty |
| `Name` | Compared between File A and File B |
| `Email` | Compared between File A and File B |
| `Status` | Compared between File A and File B |

Additional columns are allowed but are not included in the reconciliation rules.

## Output

The application writes the report to:

```text
output/reconciliation_report.xlsx
```

The main worksheet contains:

| Column | Description |
|---|---|
| `Customer ID` | Identifier used to reconcile records |
| `Name_A`, `Name_B` | Name from File A and File B |
| `Email_A`, `Email_B` | Email from File A and File B |
| `Status_A`, `Status_B` | Source status values |
| `Status` | Reconciliation outcome |
| `Changes` | Field-level changes or duplicate explanation |
| `Duplicate Rows` | Source file and Excel row numbers for duplicated IDs |

When duplicates are found, the report also contains a `Duplicate Details` worksheet with one row per occurrence: Customer ID, source file, Excel row, Name, Email, Status, and the number of occurrences in that source file.

The output folder is created automatically when needed. A report with the same filename is overwritten.

## Quick Start

### Prerequisites

- Python 3.14 was used during project validation
- Tkinter, included with the standard Windows Python installer
- `pandas`
- `openpyxl`
- `pytest` for automated tests

### Installation

Clone the repository and enter the project folder:

```powershell
git clone https://github.com/fabiano-sardinha/data-reconciliation-tool.git
cd data-reconciliation-tool
```

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

### Run the Application

From the project root:

```powershell
python src/main.py
```

A file-selection dialog asks for File A and then File B. After validation, the report is generated at `output/reconciliation_report.xlsx`.

## Validation and Quality Checks

### Permanent automated test suite

The repository contains a pytest suite covering reconciliation statuses, field-level changes, empty-value rules, input validation, report generation, duplicate-ID scenarios, and application exit codes.

Latest recorded result:

```text
97 passed
```

Run the permanent test suite from the project root with:

```powershell
python -m pytest
```

### Independent volume check

An additional one-off volume validation was run outside the permanent pytest suite using files with approximately 10,000 records.

- 18 integrity checks passed
- The Excel report was generated in approximately 4.28 seconds

This was a targeted validation scenario, not a general performance guarantee or benchmark across all machines, workbook structures, and data distributions.

## Error Handling

Expected input problems are reported with an `ERROR:` message and exit code `1`, including:

- Missing input files
- A selected path that is a folder rather than a file
- Missing required columns
- Empty `Customer ID` values

When input validation fails, the application stops before writing a new report. An existing report is not deleted.

Unexpected problems, such as unreadable workbooks or files locked by another application, are not specially converted into user-friendly messages and may show a Python traceback.

## Project Structure

```text
data-reconciliation-tool/
├── src/
│   ├── main.py          # Tkinter entry point and predictable error handling
│   ├── reconcile.py     # Reconciliation and duplicate-ID workflow
│   ├── reporting.py     # Excel report creation and formatting
│   ├── rules.py         # Status and field-change rules
│   └── validation.py    # Input validation and duplicate detection
├── tests/
│   ├── conftest.py
│   ├── test_duplicates.py
│   ├── test_main.py
│   ├── test_reconcile.py
│   ├── test_rules.py
│   └── test_validation.py
├── requirements.txt
├── pytest.ini
└── README.md
```

## Current Limitations

- Only `.xlsx` files are supported. The file picker displays `.xls`, but that format requires an additional dependency and is not supported by the current setup.
- Only the first worksheet in each input workbook is read.
- The output path is fixed at `output/reconciliation_report.xlsx`.
- Required column names must match exactly.
- Comparisons are exact: the tool does not trim whitespace, normalize values, or ignore capitalization.
- Dependency versions are not pinned.
- The interface is a desktop Tkinter file picker; there is no command-line argument interface or web interface.
