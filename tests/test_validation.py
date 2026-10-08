import pandas as pd
import pytest

from validation import validate_file, find_duplicates


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