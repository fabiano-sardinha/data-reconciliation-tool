import pandas as pd
import pytest


@pytest.fixture
def make_excel(tmp_path):
    """Create a temporary Excel file from a list of rows.

    Each row is a tuple (Customer ID, Name, Email, Status).
    Returns the path of the created file.
    """

    def _make_excel(file_name, rows, columns=None):
        columns = columns or ["Customer ID", "Name", "Email", "Status"]
        path = tmp_path / file_name
        pd.DataFrame(rows, columns=columns).to_excel(path, index=False)
        return path

    return _make_excel


@pytest.fixture
def valid_files(make_excel):
    """Pair of valid files covering every possible status.

    1 -> MATCHED
    2 -> CHANGED (different email)
    3 -> MISSING (only in file A)
    4 -> NEW (only in file B)
    5 -> DUPLICATE (twice in file A)
    """

    file_a = make_excel("a.xlsx", [
        (1, "John Smith", "john@example.com", "Active"),
        (2, "Maria Silva", "maria@example.com", "Active"),
        (3, "Peter Jones", "peter@example.com", "Active"),
        (5, "Carl Dup", "carl@example.com", "Active"),
        (5, "Carl Dup", "carl@example.com", "Active"),
    ])

    file_b = make_excel("b.xlsx", [
        (1, "John Smith", "john@example.com", "Active"),
        (2, "Maria Silva", "maria.new@example.com", "Active"),
        (4, "Anna Brown", "anna@example.com", "Active"),
        (5, "Carl Dup", "carl@example.com", "Active"),
    ])

    return file_a, file_b
