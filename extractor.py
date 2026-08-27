import re
from gliner import GLiNER

from value_normalizer import (
    normalize_phone,
    normalize_vehicle,
    normalize_account
)


MODEL_NAME = "urchade/gliner_medium-v2.1"

model = GLiNER.from_pretrained(
    MODEL_NAME
)


ENTITY_LABELS = [
    "person",
    "alias",
    "location",
    "organization",
    "date",
    "amount",
    "incident"
]


PHONE_PATTERN = re.compile(
    r"(?<!\d)(?:\+?91[\s\-]?)?[6-9](?:[\s\-]?\d){9}(?!\d)"
)

VEHICLE_PATTERN = re.compile(
    r"\b[A-Z]{2}[\s\-]?\d{1,2}[\s\-]?[A-Z]{1,3}[\s\-]?\d{4}\b",
    re.IGNORECASE
)

ACCOUNT_PATTERN = re.compile(
    r"\b(?:ACC|HDFC|ICICI|SBI|AXIS)[\s\-]?\d[A-Z0-9]*\b",
    re.IGNORECASE
)

FIR_PATTERN = re.compile(
    r"\bFIR[\/\-A-Z0-9]+\b",
    re.IGNORECASE
)


def _append_unique_entity(
    results,
    text,
    label,
    score=1.0
):
    text = str(text).strip()

    if not text:
        return

    key = (
        text.lower(),
        label.lower()
    )

    for item in results:
        existing_key = (
            str(item.get("text", "")).lower(),
            str(item.get("label", "")).lower()
        )

        if existing_key == key:
            return

    results.append({
        "text": text,
        "label": label,
        "score": float(score)
    })


def extract_entities(text):
    if not text or not str(text).strip():
        return []

    text = str(text)

    results = []

    # =====================================================
    # GLINER SEMANTIC ENTITIES
    # =====================================================

    try:
        predictions = model.predict_entities(
            text,
            ENTITY_LABELS,
            threshold=0.35
        )

        for entity in predictions:
            _append_unique_entity(
                results,
                entity.get("text", ""),
                entity.get("label", ""),
                entity.get("score", 0.0)
            )

    except Exception:
        predictions = []

    # =====================================================
    # STRICT PHONE IDENTIFIERS
    # =====================================================

    for match in PHONE_PATTERN.finditer(text):
        raw = match.group(0)
        normalized = normalize_phone(raw)

        if normalized:
            _append_unique_entity(
                results,
                raw,
                "phone",
                1.0
            )

    # =====================================================
    # STRICT VEHICLE IDENTIFIERS
    # =====================================================

    for match in VEHICLE_PATTERN.finditer(text):
        raw = match.group(0)
        normalized = normalize_vehicle(raw)

        if normalized:
            _append_unique_entity(
                results,
                raw,
                "vehicle",
                1.0
            )

    # =====================================================
    # STRICT ACCOUNT IDENTIFIERS
    # =====================================================

    for match in ACCOUNT_PATTERN.finditer(text):
        raw = match.group(0)
        normalized = normalize_account(raw)

        if normalized:
            _append_unique_entity(
                results,
                raw,
                "account",
                1.0
            )

    # =====================================================
    # FIR
    # =====================================================

    for match in FIR_PATTERN.finditer(text):
        _append_unique_entity(
            results,
            match.group(0),
            "fir_number",
            1.0
        )

    return results


def structure_entities(entities):
    structured = {
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

    label_mapping = {
        "person": "persons",
        "alias": "aliases",
        "phone": "phones",
        "location": "locations",
        "vehicle": "vehicles",
        "account": "accounts",
        "organization": "organizations",
        "date": "dates",
        "amount": "amounts",
        "incident": "incidents",
        "fir_number": "fir_numbers",
        "fir": "fir_numbers"
    }

    for entity in entities or []:
        text = str(
            entity.get("text", "")
        ).strip()

        label = str(
            entity.get("label", "")
        ).strip().lower()

        if not text:
            continue

        target_list = label_mapping.get(
            label
        )

        if not target_list:
            continue

        # =============================================
        # VALIDATE STRICT IDENTIFIER TYPES
        # =============================================

        if target_list == "phones":
            if not normalize_phone(text):
                continue

        elif target_list == "vehicles":
            if not normalize_vehicle(text):
                continue

        elif target_list == "accounts":
            if not normalize_account(text):
                continue

        if text not in structured[
            target_list
        ]:
            structured[
                target_list
            ].append(
                text
            )

    # =====================================================
    # CROSS-TYPE SANITY CLEANUP
    # =====================================================

    clean_phones = []

    for value in structured["phones"]:
        if normalize_phone(value):
            clean_phones.append(value)

    structured["phones"] = list(
        dict.fromkeys(clean_phones)
    )

    clean_vehicles = []

    for value in structured["vehicles"]:
        if normalize_vehicle(value):
            clean_vehicles.append(value)

    structured["vehicles"] = list(
        dict.fromkeys(clean_vehicles)
    )

    clean_accounts = []

    for value in structured["accounts"]:
        if normalize_account(value):
            clean_accounts.append(value)

    structured["accounts"] = list(
        dict.fromkeys(clean_accounts)
    )

    # -----------------------------------------------------
    # REMOVE STRICT IDENTIFIERS FROM SEMANTIC CATEGORIES
    # -----------------------------------------------------

    cleaned_organizations = []

    for value in structured["organizations"]:

        if normalize_account(value):
            continue

        if normalize_phone(value):
            continue

        if normalize_vehicle(value):
            continue

        if value not in cleaned_organizations:
            cleaned_organizations.append(
                value
            )

    structured["organizations"] = (
        cleaned_organizations
    )

    # -----------------------------------------------------
    # REMOVE STRICT IDENTIFIERS FROM PERSONS
    # -----------------------------------------------------

    cleaned_persons = []

    for value in structured["persons"]:

        if normalize_account(value):
            continue

        if normalize_phone(value):
            continue

        if normalize_vehicle(value):
            continue

        if value not in cleaned_persons:
            cleaned_persons.append(
                value
            )

    structured["persons"] = (
        cleaned_persons
    )

    # -----------------------------------------------------
    # REMOVE STRICT IDENTIFIERS FROM LOCATIONS
    # -----------------------------------------------------

    cleaned_locations = []

    for value in structured["locations"]:

        if normalize_account(value):
            continue

        if normalize_phone(value):
            continue

        if normalize_vehicle(value):
            continue

        if value not in cleaned_locations:
            cleaned_locations.append(
                value
            )

    structured["locations"] = (
        cleaned_locations
    )

    return structured
