def get_status(row):

    if row["_merge"] == "left_only":
        return "MISSING"

    if row["_merge"] == "right_only":
        return "NEW"

    # Registro existe nos dois arquivos
    name_same = row["Name_A"] == row["Name_B"]
    email_same = row["Email_A"] == row["Email_B"]
    status_same = row["Status_A"] == row["Status_B"]

    if name_same and email_same and status_same:
        return "MATCHED"

    return "CHANGED"


def get_changes(row):

    changes = []

    if row["_merge"] == "left_only":
        return "Customer exists only in File A"

    if row["_merge"] == "right_only":
        return "Customer exists only in File B"

    if row["Name_A"] != row["Name_B"]:
        changes.append(
            f"Name: {row['Name_A']} -> {row['Name_B']}"
        )

    if row["Email_A"] != row["Email_B"]:
        changes.append(
            f"Email: {row['Email_A']} -> {row['Email_B']}"
        )

    if row["Status_A"] != row["Status_B"]:
        changes.append(
            f"Status: {row['Status_A']} -> {row['Status_B']}"
        )

    return "; ".join(changes)