import re


PHONE_FULL_PATTERN = re.compile(
    r"^(?:\+?91[\s\-]?)?[6-9](?:[\s\-]?\d){9}$"
)

VEHICLE_FULL_PATTERN = re.compile(
    r"^[A-Z]{2}[\s\-]?\d{1,2}[\s\-]?[A-Z]{1,3}[\s\-]?\d{4}$",
    re.IGNORECASE
)

ACCOUNT_FULL_PATTERN = re.compile(
    r"^(?:"
    r"ACC[\s\-]?\d[A-Z0-9]*"
    r"|HDFC[\s\-]?\d[A-Z0-9]*"
    r"|ICICI[\s\-]?\d[A-Z0-9]*"
    r"|SBI[\s\-]?\d[A-Z0-9]*"
    r"|AXIS[\s\-]?\d[A-Z0-9]*"
    r")$",
    re.IGNORECASE
)


def normalize_text(value):
    if value is None:
        return ""
    return str(value).strip()


def normalize_person_key(value):
    value = normalize_text(value).lower()
    value = re.sub(r"[^a-z0-9\s]", "", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def normalize_person_display(value):
    value = normalize_text(value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def normalize_phone(value):
    if not value:
        return ""

    value = normalize_text(value)

    if not PHONE_FULL_PATTERN.fullmatch(value):
        return ""

    digits = re.sub(r"\D", "", value)

    if len(digits) == 12 and digits.startswith("91"):
        digits = digits[2:]

    if not re.fullmatch(r"[6-9]\d{9}", digits):
        return ""

    return digits


def is_phone(value):
    return bool(normalize_phone(value))


def normalize_vehicle(value):
    if not value:
        return ""

    value = normalize_text(value)

    if not VEHICLE_FULL_PATTERN.fullmatch(value):
        return ""

    normalized = re.sub(
        r"[^A-Za-z0-9]",
        "",
        value
    ).upper()

    if not re.fullmatch(
        r"[A-Z]{2}\d{1,2}[A-Z]{1,3}\d{4}",
        normalized
    ):
        return ""

    return normalized


def is_vehicle(value):
    return bool(normalize_vehicle(value))


def normalize_account(value):
    if not value:
        return ""

    value = normalize_text(value)

    if not ACCOUNT_FULL_PATTERN.fullmatch(value):
        return ""

    normalized = re.sub(
        r"[^A-Za-z0-9]",
        "",
        value
    ).upper()

    if not re.fullmatch(
        r"(?:ACC|HDFC|ICICI|SBI|AXIS)\d[A-Z0-9]*",
        normalized,
        re.IGNORECASE
    ):
        return ""

    return normalized


def is_account(value):
    return bool(normalize_account(value))


def normalize_location(value):
    value = normalize_text(value)
    if not value:
        return ""
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def normalize_location_key(value):
    return normalize_location(value).lower()


def normalize_organization(value):
    value = normalize_text(value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def normalize_organization_key(value):
    return normalize_organization(value).lower()


def normalize_entity_value(value, entity_type):
    entity_type = normalize_text(entity_type).upper()

    if entity_type == "PERSON":
        return normalize_person_display(value)

    if entity_type == "PHONE":
        return normalize_phone(value)

    if entity_type == "VEHICLE":
        return normalize_vehicle(value)

    if entity_type == "ACCOUNT":
        return normalize_account(value)

    if entity_type == "LOCATION":
        return normalize_location(value)

    if entity_type == "ORGANIZATION":
        return normalize_organization(value)

    return normalize_text(value)


def canonical_lookup_key(value, entity_type):
    entity_type = normalize_text(entity_type).upper()

    if entity_type == "PERSON":
        normalized = normalize_person_key(value)

    elif entity_type == "PHONE":
        normalized = normalize_phone(value)

    elif entity_type == "VEHICLE":
        normalized = normalize_vehicle(value)

    elif entity_type == "ACCOUNT":
        normalized = normalize_account(value)

    elif entity_type == "LOCATION":
        normalized = normalize_location_key(value)

    elif entity_type == "ORGANIZATION":
        normalized = normalize_organization_key(value)

    else:
        normalized = normalize_text(value).lower()

    return entity_type, normalized


def guess_entity_type(value):
    value = normalize_text(value)

    if not value:
        return "UNKNOWN"

    if is_phone(value):
        return "PHONE"

    if is_vehicle(value):
        return "VEHICLE"

    if is_account(value):
        return "ACCOUNT"

    vehicle_match = re.search(
        r"\b[A-Z]{2}[\s\-]?\d{1,2}[\s\-]?[A-Z]{1,3}[\s\-]?\d{4}\b",
        value,
        re.IGNORECASE
    )

    if vehicle_match and normalize_vehicle(vehicle_match.group(0)):
        return "VEHICLE"

    phone_match = re.search(
        r"(?<!\d)(?:\+?91[\s\-]?)?[6-9](?:[\s\-]?\d){9}(?!\d)",
        value
    )

    if phone_match and normalize_phone(phone_match.group(0)):
        return "PHONE"

    account_match = re.search(
        r"\b(?:ACC|HDFC|ICICI|SBI|AXIS)[\s\-]?\d[A-Z0-9]*\b",
        value,
        re.IGNORECASE
    )

    if account_match and normalize_account(account_match.group(0)):
        return "ACCOUNT"

    return "UNKNOWN"


def clean_entity_endpoint(value, entity_type):
    value = normalize_text(value)
    entity_type = normalize_text(entity_type).upper()

    if not value:
        return ""

    if entity_type == "VEHICLE":
        match = re.search(
            r"\b[A-Z]{2}[\s\-]?\d{1,2}[\s\-]?[A-Z]{1,3}[\s\-]?\d{4}\b",
            value,
            re.IGNORECASE
        )
        return normalize_vehicle(match.group(0)) if match else ""

    if entity_type == "PHONE":
        match = re.search(
            r"(?<!\d)(?:\+?91[\s\-]?)?[6-9](?:[\s\-]?\d){9}(?!\d)",
            value
        )
        return normalize_phone(match.group(0)) if match else ""

    if entity_type == "ACCOUNT":
        match = re.search(
            r"\b(?:ACC|HDFC|ICICI|SBI|AXIS)[\s\-]?\d[A-Z0-9]*\b",
            value,
            re.IGNORECASE
        )
        return normalize_account(match.group(0)) if match else ""

    if entity_type == "PERSON":
        return normalize_person_display(value)

    if entity_type == "LOCATION":
        return normalize_location(value)

    if entity_type == "ORGANIZATION":
        return normalize_organization(value)

    return normalize_text(value)


def get_source_type_hint(relationship, source_value=""):
    relationship = normalize_text(relationship).upper()

    if relationship == "TRANSFERRED_TO":
        return "ACCOUNT"

    guessed = guess_entity_type(source_value)

    if guessed != "UNKNOWN":
        return guessed

    return None


def get_target_type_hint(relationship, target_value=""):
    relationship = normalize_text(relationship).upper()

    if relationship in {
        "USED_VEHICLE",
        "USES_VEHICLE",
        "HAS_VEHICLE"
    }:
        return "VEHICLE"

    if relationship in {
        "USES_PHONE",
        "USED_PHONE",
        "HAS_PHONE"
    }:
        return "PHONE"

    if relationship in {
        "USES_ACCOUNT",
        "USED_ACCOUNT",
        "HAS_ACCOUNT",
        "TRANSFERRED_TO"
    }:
        return "ACCOUNT"

    if relationship in {
        "LOCATED_AT",
        "VISITED",
        "LIVES_AT",
        "RESIDES_AT",
        "STAYED_AT"
    }:
        return "LOCATION"

    if relationship in {
        "WORKS_FOR",
        "MEMBER_OF",
        "ASSOCIATED_WITH_ORGANIZATION"
    }:
        return "ORGANIZATION"

    guessed = guess_entity_type(target_value)

    if guessed != "UNKNOWN":
        return guessed

    return None
