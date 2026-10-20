import pandas as pd
import pytest

from validation import (
    InputFileError,
    DataValidationError,
    validate_input_files,
    validate_file,
    find_duplicates,
)


def test_valid_file():

    df = pd.DataFrame({
        "Customer ID": [1001],
        "Name": ["John Smith"],
        "Email": ["john@example.com"],
        "Status": ["Active"]
    })

    validate_file(df, "test.xlsx")


def test_missing_required_column():

    df = pd.DataFrame({
        "Customer ID": [1001],
        "Name": ["John Smith"],
        "Email": ["john@example.com"]
    })

    with pytest.raises(ValueError, match="Missing required columns: Status"):
        validate_file(df, "test.xlsx")

def test_no_duplicates():

    df = pd.DataFrame({
        "Customer ID": [1001, 1002, 1003],
        "Name": ["John", "Maria", "Peter"],
        "Email": [
            "john@example.com",
            "maria@example.com",
            "peter@example.com"
        ],
        "Status": ["Active", "Active", "Active"]
    })

    result = find_duplicates(df, "test.xlsx")

    assert result == {}


def test_duplicate_customer_id():

    df = pd.DataFrame({
        "Customer ID": [1001, 1002, 1002],
        "Name": ["John", "Maria", "Maria"],
        "Email": [
            "john@example.com",
            "maria@example.com",
            "maria@example.com"
        ],
        "Status": ["Active", "Active", "Active"]
    })

    result = find_duplicates(df, "test.xlsx")

    assert result == {
    1002: [3, 4]
    }

def test_empty_customer_id():

    df = pd.DataFrame({
        "Customer ID": [1001, None],
        "Name": ["John", "Maria"],
        "Email": [
            "john@example.com",
            "maria@example.com"
        ],
        "Status": ["Active", "Active"]
    })

    with pytest.raises(
        ValueError,
        match="Customer ID contains empty values"
    ):
        validate_file(df, "test.xlsx")


# --- Input file validation ---

def test_input_files_exist(tmp_path):

    file_a = tmp_path / "a.xlsx"
    file_b = tmp_path / "b.xlsx"
    file_a.write_text("x")
    file_b.write_text("x")

    validate_input_files(file_a, file_b)


def test_only_file_a_missing(tmp_path):

    file_a = tmp_path / "missing_a.xlsx"
    file_b = tmp_path / "b.xlsx"
    file_b.write_text("x")

    with pytest.raises(InputFileError) as error:
        validate_input_files(file_a, file_b)

    message = str(error.value)
    assert "File A not found" in message
    assert "missing_a.xlsx" in message
    assert "File B" not in message


def test_only_file_b_missing(tmp_path):

    file_a = tmp_path / "a.xlsx"
    file_b = tmp_path / "missing_b.xlsx"
    file_a.write_text("x")

    with pytest.raises(InputFileError) as error:
        validate_input_files(file_a, file_b)

    message = str(error.value)
    assert "File B not found" in message
    assert "missing_b.xlsx" in message
    assert "File A" not in message


def test_both_files_missing(tmp_path):

    file_a = tmp_path / "missing_a.xlsx"
    file_b = tmp_path / "missing_b.xlsx"

    with pytest.raises(InputFileError) as error:
        validate_input_files(file_a, file_b)

    message = str(error.value)
    assert "File A not found" in message
    assert "File B not found" in message


def test_path_is_a_directory(tmp_path):

    file_a = tmp_path / "a.xlsx"
    file_a.write_text("x")
    folder_b = tmp_path / "folder_b"
    folder_b.mkdir()

    with pytest.raises(InputFileError, match="File B is not a file"):
        validate_input_files(file_a, folder_b)


def test_data_validation_error_is_a_value_error():

    # Ensures compatibility with code that expects ValueError
    assert issubclass(DataValidationError, ValueError)
