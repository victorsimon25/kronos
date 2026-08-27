import pandas as pd


def extract_relationships_from_dataframe(
    df,
    source_file="structured_file"
):

    relationships = []

    columns = {
        str(col).strip().lower().replace(" ", "_"): col
        for col in df.columns
    }

    # =====================================================
    # CDR: caller -> receiver
    # =====================================================

    if "caller" in columns and "receiver" in columns:

        caller_col = columns["caller"]
        receiver_col = columns["receiver"]

        date_col = columns.get("date")
        time_col = columns.get("time")
        location_col = columns.get("location")

        for _, row in df.iterrows():

            timestamp = None

            if date_col is not None:
                timestamp = str(row[date_col])

                if time_col is not None:
                    timestamp += " " + str(row[time_col])

            evidence = (
                f"{row[caller_col]} called "
                f"{row[receiver_col]}"
            )

            if location_col is not None:
                evidence += (
                    f" from {row[location_col]}"
                )

            relationships.append({
                "source_entity": str(
                    row[caller_col]
                ),
                "relationship": "CALLED",
                "target_entity": str(
                    row[receiver_col]
                ),
                "timestamp": timestamp,
                "confidence": 1.0,
                "source_file": source_file,
                "evidence": evidence,
                "method": "COLUMN_MAPPING",
                "decision": "ACCEPT"
            })

    # =====================================================
    # TRANSACTION: account_from -> account_to
    # =====================================================

    if (
        "account_from" in columns
        and
        "account_to" in columns
    ):

        from_col = columns["account_from"]
        to_col = columns["account_to"]

        amount_col = columns.get("amount")
        date_col = columns.get("date")
        time_col = columns.get("time")

        for _, row in df.iterrows():

            timestamp = None

            if date_col is not None:
                timestamp = str(
                    row[date_col]
                )

                if time_col is not None:
                    timestamp += (
                        " "
                        + str(row[time_col])
                    )

            evidence = (
                f"{row[from_col]} transferred "
                f"to {row[to_col]}"
            )

            if amount_col is not None:
                evidence += (
                    f" amount {row[amount_col]}"
                )

            relationships.append({
                "source_entity": str(
                    row[from_col]
                ),
                "relationship": "TRANSFERRED_TO",
                "target_entity": str(
                    row[to_col]
                ),
                "timestamp": timestamp,
                "confidence": 1.0,
                "source_file": source_file,
                "evidence": evidence,
                "method": "COLUMN_MAPPING",
                "decision": "ACCEPT"
            })

    # =====================================================
    # PERSON -> ACCOUNT
    # =====================================================

    if (
        "sender_name" in columns
        and
        "account_from" in columns
    ):

        person_col = columns["sender_name"]
        account_col = columns["account_from"]

        for _, row in df.iterrows():

            relationships.append({
                "source_entity": str(
                    row[person_col]
                ),
                "relationship": "USES_ACCOUNT",
                "target_entity": str(
                    row[account_col]
                ),
                "timestamp": None,
                "confidence": 1.0,
                "source_file": source_file,
                "evidence": (
                    f"{row[person_col]} uses "
                    f"account {row[account_col]}"
                ),
                "method": "COLUMN_MAPPING",
                "decision": "ACCEPT"
            })

    # =====================================================
    # PERSON -> VEHICLE
    # =====================================================

    if (
        "person" in columns
        and
        "vehicle" in columns
    ):

        person_col = columns["person"]
        vehicle_col = columns["vehicle"]

        for _, row in df.iterrows():

            relationships.append({
                "source_entity": str(
                    row[person_col]
                ),
                "relationship": "USED_VEHICLE",
                "target_entity": str(
                    row[vehicle_col]
                ),
                "timestamp": None,
                "confidence": 1.0,
                "source_file": source_file,
                "evidence": (
                    f"{row[person_col]} used "
                    f"vehicle {row[vehicle_col]}"
                ),
                "method": "COLUMN_MAPPING",
                "decision": "ACCEPT"
            })

    # =====================================================
    # PERSON -> PHONE
    # =====================================================

    if (
        "person" in columns
        and
        "phone" in columns
    ):

        person_col = columns["person"]
        phone_col = columns["phone"]

        for _, row in df.iterrows():

            relationships.append({
                "source_entity": str(
                    row[person_col]
                ),
                "relationship": "USES_PHONE",
                "target_entity": str(
                    row[phone_col]
                ),
                "timestamp": None,
                "confidence": 1.0,
                "source_file": source_file,
                "evidence": (
                    f"{row[person_col]} uses "
                    f"phone {row[phone_col]}"
                ),
                "method": "COLUMN_MAPPING",
                "decision": "ACCEPT"
            })

    return relationships