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

## Current Status

The current version supports Excel files containing the following required columns:

- Customer ID
- Name
- Email
- Status

Additional columns may be present in the input files. The tool only uses the columns required for the reconciliation rules.

## Reconciliation Results

The tool currently generates the following statuses:

| Status | Description |
|---|---|
| MATCHED | Record exists in both files with the same information |
| CHANGED | Record exists in both files but one or more fields changed |
| MISSING | Record exists only in File A |
| NEW | Record exists only in File B |
| DUPLICATE | Customer ID appears more than once in an input file |

For duplicate records, the tool reports the Customer ID and the Excel rows where the duplicate was found.

## Output

The tool generates an Excel report containing:

- Customer ID
- Values from File A
- Values from File B
- Reconciliation status
- Description of detected changes
- Duplicate row information

The generated report includes formatting, filters, frozen headers and conditional formatting for the reconciliation statuses.

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
│   ├── test_rules.py
│   └── test_validation.py
│
├── input/
├── output/
├── .gitignore
├── pytest.ini
└── README.md
```

## Requirements

- Python 3.14+
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
pip install pandas openpyxl pytest
```

## Usage

Place the Excel input files in the `input` directory using the expected filenames:

```text
input/
├── customers_a.xlsx
└── customers_b.xlsx
```

Then run:

```powershell
python src/main.py
```

The reconciliation report will be generated in:

```text
output/reconciliation_report.xlsx
```

## Running Tests

Run the automated test suite with:

```powershell
pytest
```

The project currently includes automated tests covering reconciliation rules and input validation.

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