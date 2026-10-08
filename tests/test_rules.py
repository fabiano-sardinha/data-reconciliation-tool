import pandas as pd

from rules import get_status, get_changes


def test_matching_records():

    row = pd.Series({
        "_merge": "both",
        "Name_A": "John Smith",
        "Name_B": "John Smith",
        "Email_A": "john@email.com",
        "Email_B": "john@email.com",
        "Status_A": "Active",
        "Status_B": "Active"
    })

    result = get_status(row)

    assert result == "MATCHED"

def test_changed_record():

    row = pd.Series({
        "_merge": "both",
        "Name_A": "Maria Silva",
        "Name_B": "Maria Silva",
        "Email_A": "maria@email.com",
        "Email_B": "maria.new@email.com",
        "Status_A": "Active",
        "Status_B": "Active"
    })

    result = get_status(row)

    assert result == "CHANGED"


def test_missing_record():

    row = pd.Series({
        "_merge": "left_only",
        "Name_A": "Peter Jones",
        "Name_B": None,
        "Email_A": "peter@email.com",
        "Email_B": None,
        "Status_A": "Active",
        "Status_B": None
    })

    result = get_status(row)

    assert result == "MISSING"


def test_new_record():

    row = pd.Series({
        "_merge": "right_only",
        "Name_A": None,
        "Name_B": "Anna Brown",
        "Email_A": None,
        "Email_B": "anna@email.com",
        "Status_A": None,
        "Status_B": "Active"
    })

    result = get_status(row)

    assert result == "NEW"

def test_email_change():

    row = pd.Series({
        "_merge": "both",
        "Name_A": "Maria Silva",
        "Name_B": "Maria Silva",
        "Email_A": "maria@email.com",
        "Email_B": "maria.new@email.com",
        "Status_A": "Active",
        "Status_B": "Active"
    })

    result = get_changes(row)

    assert result == "Email: maria@email.com -> maria.new@email.com"

def test_missing_change():

    row = pd.Series({
        "_merge": "left_only",
        "Name_A": "Peter Jones",
        "Name_B": None,
        "Email_A": "peter@email.com",
        "Email_B": None,
        "Status_A": "Active",
        "Status_B": None
    })

    result = get_changes(row)

    assert result == "Customer exists only in File A"


def test_new_change():

    row = pd.Series({
        "_merge": "right_only",
        "Name_A": None,
        "Name_B": "Anna Brown",
        "Email_A": None,
        "Email_B": "anna@email.com",
        "Status_A": None,
        "Status_B": "Active"
    })

    result = get_changes(row)

    assert result == "Customer exists only in File B"