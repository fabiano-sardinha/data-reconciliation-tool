import pandas as pd


def values_differ(value_a, value_b):

    a_missing = pd.isna(value_a)
    b_missing = pd.isna(value_b)

    # Two missing values (NaN, None) are considered equal
    if a_missing and b_missing:
        return False

    # One missing value and one filled value are different
    if a_missing or b_missing:
        return True

    return value_a != value_b


def format_value(value):

    # Missing values (NaN, None, pd.NA) are shown as "(empty)" in the messages
    if pd.isna(value):
        return "(empty)"

    return value


def get_status(row):

    if row["_merge"] == "left_only":
        return "MISSING"

    if row["_merge"] == "right_only":
        return "NEW"

    # The record exists in both files
    name_same = not values_differ(row["Name_A"], row["Name_B"])
    email_same = not values_differ(row["Email_A"], row["Email_B"])
    status_same = not values_differ(row["Status_A"], row["Status_B"])

    if name_same and email_same and status_same:
        return "MATCHED"

    return "CHANGED"


def get_changes(row):

    changes = []

    if row["_merge"] == "left_only":
        return "Customer exists only in File A"

    if row["_merge"] == "right_only":
        return "Customer exists only in File B"

    if values_differ(row["Name_A"], row["Name_B"]):
        changes.append(
            f"Name: {format_value(row['Name_A'])} "
            f"-> {format_value(row['Name_B'])}"
        )

    if values_differ(row["Email_A"], row["Email_B"]):
        changes.append(
            f"Email: {format_value(row['Email_A'])} "
            f"-> {format_value(row['Email_B'])}"
        )

    if values_differ(row["Status_A"], row["Status_B"]):
        changes.append(
            f"Status: {format_value(row['Status_A'])} "
            f"-> {format_value(row['Status_B'])}"
        )

    return "; ".join(changes)
