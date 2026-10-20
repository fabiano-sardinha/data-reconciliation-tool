import pandas as pd
import pytest

from rules import get_status, get_changes, format_value


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


# --- Empty values (NaN / None) ---

def make_row(**overrides):

    row = {
        "_merge": "both",
        "Name_A": "John Smith",
        "Name_B": "John Smith",
        "Email_A": "john@email.com",
        "Email_B": "john@email.com",
        "Status_A": "Active",
        "Status_B": "Active"
    }

    row.update(overrides)

    return pd.Series(row)


EMPTY_VALUES = [float("nan"), None, pd.NA]


@pytest.mark.parametrize("empty", EMPTY_VALUES)
@pytest.mark.parametrize("field", ["Name", "Email", "Status"])
def test_both_values_empty_are_matched(field, empty):

    row = make_row(**{f"{field}_A": empty, f"{field}_B": empty})

    assert get_status(row) == "MATCHED"


@pytest.mark.parametrize("empty", EMPTY_VALUES)
@pytest.mark.parametrize("field", ["Name", "Email", "Status"])
def test_both_values_empty_generate_no_change_message(field, empty):

    row = make_row(**{f"{field}_A": empty, f"{field}_B": empty})

    assert get_changes(row) == ""


def test_mixed_empty_types_in_both_files_are_equal():

    # NaN on one side and None on the other are still "two missing values"
    row = make_row(Email_A=float("nan"), Email_B=None)

    assert get_status(row) == "MATCHED"
    assert get_changes(row) == ""


@pytest.mark.parametrize("empty", EMPTY_VALUES)
@pytest.mark.parametrize("field", ["Name", "Email", "Status"])
def test_only_value_a_empty_is_changed(field, empty):

    row = make_row(**{f"{field}_A": empty, f"{field}_B": "Filled"})

    assert get_status(row) == "CHANGED"
    assert get_changes(row) == f"{field}: (empty) -> Filled"


@pytest.mark.parametrize("empty", EMPTY_VALUES)
@pytest.mark.parametrize("field", ["Name", "Email", "Status"])
def test_only_value_b_empty_is_changed(field, empty):

    row = make_row(**{f"{field}_A": "Filled", f"{field}_B": empty})

    assert get_status(row) == "CHANGED"
    assert get_changes(row) == f"{field}: Filled -> (empty)"


def test_empty_in_both_does_not_hide_a_real_change():

    # Email is empty in both files, but the name changed
    row = make_row(
        Email_A=float("nan"),
        Email_B=float("nan"),
        Name_B="John Brown"
    )

    assert get_status(row) == "CHANGED"
    assert get_changes(row) == "Name: John Smith -> John Brown"


def test_empty_values_do_not_affect_missing_and_new():

    missing = make_row(_merge="left_only", Name_B=None, Email_B=None)
    new = make_row(_merge="right_only", Name_A=None, Email_A=None)

    assert get_status(missing) == "MISSING"
    assert get_status(new) == "NEW"


# --- Display of missing values in the messages ---

@pytest.mark.parametrize("empty", EMPTY_VALUES)
def test_format_value_returns_empty_marker_for_missing_values(empty):

    assert format_value(empty) == "(empty)"


@pytest.mark.parametrize("value", ["Maria", "maria@x.com", 0, 0.0, 1001])
def test_format_value_keeps_filled_values(value):

    # Zero is a filled value and must not be treated as empty
    assert format_value(value) == value


def test_empty_email_in_a_is_shown_as_empty():

    row = make_row(Email_A=None, Email_B="bruno@x.com")

    assert get_changes(row) == "Email: (empty) -> bruno@x.com"


def test_empty_email_in_b_is_shown_as_empty():

    row = make_row(Email_A="maria@x.com", Email_B=None)

    assert get_changes(row) == "Email: maria@x.com -> (empty)"


@pytest.mark.parametrize("empty", EMPTY_VALUES)
def test_change_message_never_contains_raw_missing_text(empty):

    row = make_row(Email_A=empty, Email_B="bruno@x.com")

    message = get_changes(row)

    assert "nan" not in message
    assert "None" not in message
    assert "<NA>" not in message


def test_zero_is_shown_as_a_value_not_as_empty():

    row = make_row(Status_A=0, Status_B="Active")

    assert get_status(row) == "CHANGED"
    assert get_changes(row) == "Status: 0 -> Active"


def test_multiple_changed_fields_are_separated_and_show_empty():

    row = make_row(
        Name_A=float("nan"),
        Name_B="Anna Brown",
        Email_A="john@email.com",
        Email_B=None,
        Status_A="Active",
        Status_B="Inactive"
    )

    assert get_status(row) == "CHANGED"
    assert get_changes(row) == (
        "Name: (empty) -> Anna Brown; "
        "Email: john@email.com -> (empty); "
        "Status: Active -> Inactive"
    )


def test_field_empty_in_both_is_left_out_of_multiple_changes():

    row = make_row(
        Name_A="John Smith",
        Name_B="John Brown",
        Email_A=float("nan"),
        Email_B=float("nan"),
        Status_A="Active",
        Status_B="Inactive"
    )

    assert get_changes(row) == (
        "Name: John Smith -> John Brown; "
        "Status: Active -> Inactive"
    )
