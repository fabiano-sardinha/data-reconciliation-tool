import re

import pandas as pd
import pytest

from reconcile import run_reconciliation
from validation import InputFileError, DataValidationError


def read_report(path):
    return pd.read_excel(path).set_index("Customer ID")


def test_reconciliation_generates_report_with_all_statuses(
    valid_files, tmp_path
):

    file_a, file_b = valid_files
    output = tmp_path / "report.xlsx"

    run_reconciliation(file_a, file_b, output)

    report = read_report(output)

    assert report.loc[1, "Status"] == "MATCHED"
    assert report.loc[2, "Status"] == "CHANGED"
    assert report.loc[3, "Status"] == "MISSING"
    assert report.loc[4, "Status"] == "NEW"
    assert report.loc[5, "Status"] == "DUPLICATE"


def test_changed_record_reports_the_difference(valid_files, tmp_path):

    file_a, file_b = valid_files
    output = tmp_path / "report.xlsx"

    run_reconciliation(file_a, file_b, output)

    report = read_report(output)

    assert report.loc[2, "Changes"] == (
        "Email: maria@example.com -> maria.new@example.com"
    )


def test_duplicates_do_not_stop_processing(valid_files, tmp_path):

    file_a, file_b = valid_files
    output = tmp_path / "report.xlsx"

    run_reconciliation(file_a, file_b, output)

    report = read_report(output)

    # A single row per Customer ID, with the duplicate Excel rows
    assert len(report) == 5
    assert report.loc[5, "Duplicate Rows"] == "5, 6"
    assert "File A" in report.loc[5, "Changes"]


def test_empty_values_are_shown_as_empty_in_the_report(make_excel, tmp_path):

    file_a = make_excel("a.xlsx", [
        (1, "Ana Costa", None, "Active"),
        (2, "Bruno Dias", None, "Active"),
        (3, "Carla Melo", "carla@example.com", "Active"),
    ])

    file_b = make_excel("b.xlsx", [
        (1, "Ana Costa", None, "Active"),
        (2, "Bruno Dias", "bruno@x.com", "Active"),
        (3, "Carla Melo", None, "Active"),
    ])

    output = tmp_path / "report.xlsx"

    run_reconciliation(file_a, file_b, output)

    report = read_report(output)

    # Two empty emails: no changes
    assert report.loc[1, "Status"] == "MATCHED"
    assert pd.isna(report.loc[1, "Changes"])

    # Empty email only in file A
    assert report.loc[2, "Status"] == "CHANGED"
    assert report.loc[2, "Changes"] == "Email: (empty) -> bruno@x.com"

    # Empty email only in file B
    assert report.loc[3, "Status"] == "CHANGED"
    assert report.loc[3, "Changes"] == "Email: carla@example.com -> (empty)"

    # No raw missing value (nan, None, <NA>) where a message value is
    # expected. The boundaries avoid false positives with legitimate text,
    # for example a name such as "Fernando".
    raw_missing = re.compile(r"(?:: |-> )(?:nan|None|<NA>)(?: ->|;|$)")

    for message in report["Changes"].dropna().astype(str):
        assert not raw_missing.search(message)


def test_report_is_created_in_missing_output_folder(valid_files, tmp_path):

    file_a, file_b = valid_files
    output = tmp_path / "new_folder" / "nested" / "report.xlsx"

    run_reconciliation(file_a, file_b, output)

    assert output.is_file()


def test_missing_input_file_does_not_create_report(make_excel, tmp_path):

    file_a = make_excel("a.xlsx", [(1, "John", "john@example.com", "Active")])
    file_b = tmp_path / "does_not_exist.xlsx"
    output = tmp_path / "output" / "report.xlsx"

    with pytest.raises(InputFileError, match="File B not found"):
        run_reconciliation(file_a, file_b, output)

    assert not output.exists()


def test_invalid_file_does_not_create_partial_report(make_excel, tmp_path):

    file_a = make_excel("a.xlsx", [(1, "John", "john@example.com", "Active")])
    # The required column "Status" is missing
    file_b = make_excel(
        "b.xlsx",
        [(1, "John", "john@example.com")],
        columns=["Customer ID", "Name", "Email"],
    )
    output = tmp_path / "output" / "report.xlsx"

    with pytest.raises(
        DataValidationError,
        match="Missing required columns: Status"
    ):
        run_reconciliation(file_a, file_b, output)

    assert not output.exists()
