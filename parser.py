import pandas as pd
import json
from pypdf import PdfReader


def parse_file(uploaded_file):

    file_name = uploaded_file.name.lower()

    if file_name.endswith(".pdf"):
        return {
            "file_type": "unstructured",
            "text": parse_pdf(uploaded_file),
            "structured": None
        }

    elif file_name.endswith(".txt"):
        return {
            "file_type": "unstructured",
            "text": parse_txt(uploaded_file),
            "structured": None
        }

    elif file_name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)

        return {
            "file_type": "structured",
            "text": df.to_string(index=False),
            "structured": parse_dataframe(df)
        }

    elif file_name.endswith(".xlsx"):
        df = pd.read_excel(uploaded_file)

        return {
            "file_type": "structured",
            "text": df.to_string(index=False),
            "structured": parse_dataframe(df)
        }

    elif file_name.endswith(".json"):
        data = json.load(uploaded_file)

        return {
            "file_type": "structured",
            "text": json.dumps(data, indent=2),
            "structured": parse_json(data)
        }

    return {
        "file_type": "unknown",
        "text": "",
        "structured": None
    }


def parse_pdf(uploaded_file):

    reader = PdfReader(uploaded_file)

    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


def parse_txt(uploaded_file):

    return uploaded_file.read().decode(
        "utf-8",
        errors="ignore"
    )


def empty_structure():

    return {
        "persons": [],
        "aliases": [],
        "phones": [],
        "locations": [],
        "vehicles": [],
        "accounts": [],
        "organizations": [],
        "dates": [],
        "amounts": [],
        "incidents": [],
        "fir_numbers": []
    }


def add_unique(data, key, value):

    if pd.isna(value):
        return

    value = str(value).strip()

    if not value:
        return

    if value not in data[key]:
        data[key].append(value)


def parse_dataframe(df):

    result = empty_structure()

    column_map = {
        "name": "persons",
        "person": "persons",
        "person_name": "persons",
        "suspect": "persons",
        "caller_name": "persons",
        "receiver_name": "persons",
        "sender_name": "persons",
        "receiver_person": "persons",

        "alias": "aliases",
        "aliases": "aliases",

        "phone": "phones",
        "phone_number": "phones",
        "mobile": "phones",
        "mobile_number": "phones",
        "caller": "phones",
        "receiver": "phones",
        "caller_number": "phones",
        "receiver_number": "phones",

        "location": "locations",
        "place": "locations",
        "area": "locations",
        "city": "locations",

        "vehicle": "vehicles",
        "vehicle_number": "vehicles",
        "registration": "vehicles",
        "registration_number": "vehicles",

        "account": "accounts",
        "account_number": "accounts",
        "account_from": "accounts",
        "account_to": "accounts",
        "sender_account": "accounts",
        "receiver_account": "accounts",

        "organization": "organizations",
        "organisation": "organizations",
        "company": "organizations",

        "date": "dates",
        "transaction_date": "dates",
        "call_date": "dates",

        "amount": "amounts",
        "transaction_amount": "amounts",

        "incident": "incidents",
        "incident_type": "incidents",

        "fir": "fir_numbers",
        "fir_number": "fir_numbers",
        "case_id": "fir_numbers"
    }

    for column in df.columns:

        normalized_column = (
            str(column)
            .strip()
            .lower()
            .replace(" ", "_")
        )

        if normalized_column in column_map:

            target = column_map[normalized_column]

            for value in df[column]:
                add_unique(
                    result,
                    target,
                    value
                )

    return result


def parse_json(data):

    result = empty_structure()

    def walk(obj, parent_key=""):

        if isinstance(obj, dict):

            for key, value in obj.items():

                normalized_key = (
                    str(key)
                    .strip()
                    .lower()
                    .replace(" ", "_")
                )

                mapping = {
                    "name": "persons",
                    "person": "persons",
                    "alias": "aliases",

                    "phone": "phones",
                    "mobile": "phones",
                    "phone_number": "phones",

                    "location": "locations",
                    "place": "locations",
                    "city": "locations",

                    "vehicle": "vehicles",
                    "vehicle_number": "vehicles",

                    "account": "accounts",
                    "accounts": "accounts",
                    "account_number": "accounts",

                    "organization": "organizations",
                    "organisation": "organizations",
                    "company": "organizations",

                    "date": "dates",

                    "amount": "amounts",

                    "incident": "incidents",

                    "fir": "fir_numbers",
                    "fir_number": "fir_numbers",
                    "case_id": "fir_numbers"
                }

                if normalized_key in mapping:

                    target = mapping[normalized_key]

                    if isinstance(value, list):

                        for item in value:

                            if isinstance(
                                item,
                                (str, int, float)
                            ):
                                add_unique(
                                    result,
                                    target,
                                    item
                                )

                    elif isinstance(
                        value,
                        (str, int, float)
                    ):

                        add_unique(
                            result,
                            target,
                            value
                        )

                walk(
                    value,
                    normalized_key
                )

        elif isinstance(obj, list):

            for item in obj:
                walk(
                    item,
                    parent_key
                )

    walk(data)

    return result