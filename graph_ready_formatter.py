import os
import re
from datetime import datetime


# =========================================================
# ENTITY ID PREFIXES
# =========================================================

ENTITY_PREFIXES = {
    "PERSON": "P",
    "PHONE": "PH",
    "VEHICLE": "V",
    "ACCOUNT": "A",
    "LOCATION": "L",
    "ORGANIZATION": "O",
    "UNKNOWN": "X"
}


# =========================================================
# BASIC NORMALIZATION
# =========================================================

def normalize_text(value):
    if value is None:
        return ""

    return str(value).strip()


def normalize_person_key(value):
    value = normalize_text(value).lower()
    value = re.sub(r"[^a-z0-9\s]", "", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def normalize_phone(value):
    if not value:
        return ""

    digits = re.sub(
        r"\D",
        "",
        str(value)
    )

    if len(digits) == 12 and digits.startswith("91"):
        digits = digits[2:]

    return digits


def normalize_vehicle(value):
    if not value:
        return ""

    return re.sub(
        r"[^A-Za-z0-9]",
        "",
        str(value)
    ).upper()


def normalize_account(value):
    if not value:
        return ""

    return re.sub(
        r"[^A-Za-z0-9]",
        "",
        str(value)
    ).upper()


def normalize_location(value):
    value = normalize_text(value)

    if not value:
        return ""

    value = re.sub(
        r"\s+",
        " ",
        value
    )

    return value.strip()


def normalize_organization(value):
    value = normalize_text(value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def canonical_value(
    value,
    entity_type
):
    entity_type = normalize_text(
        entity_type
    ).upper()

    if entity_type == "PERSON":
        return normalize_text(value)

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


def canonical_lookup_key(
    value,
    entity_type
):
    entity_type = normalize_text(
        entity_type
    ).upper()

    if entity_type == "PERSON":
        normalized = normalize_person_key(
            value
        )

    elif entity_type == "PHONE":
        normalized = normalize_phone(
            value
        )

    elif entity_type == "VEHICLE":
        normalized = normalize_vehicle(
            value
        )

    elif entity_type == "ACCOUNT":
        normalized = normalize_account(
            value
        )

    elif entity_type == "LOCATION":
        normalized = normalize_location(
            value
        ).lower()

    elif entity_type == "ORGANIZATION":
        normalized = normalize_organization(
            value
        ).lower()

    else:
        normalized = normalize_text(
            value
        ).lower()

    return (
        entity_type,
        normalized
    )


# =========================================================
# SOURCE TYPE
# =========================================================

def get_source_type(source_name):
    if not source_name:
        return "UNKNOWN"

    if source_name == "manual_input":
        return "MANUAL"

    extension = os.path.splitext(
        source_name
    )[1].lower()

    mapping = {
        ".pdf": "PDF",
        ".txt": "TXT",
        ".csv": "CSV",
        ".xlsx": "XLSX",
        ".xls": "XLS",
        ".json": "JSON"
    }

    return mapping.get(
        extension,
        "UNKNOWN"
    )


# =========================================================
# TIMESTAMP NORMALIZATION
# =========================================================

def normalize_timestamp(value):
    if not value:
        return None

    value = str(
        value
    ).strip()

    formats = [
        "%d %B %Y",
        "%d %b %Y",
        "%Y-%m-%d",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%d %B %Y %H:%M",
        "%d %b %Y %H:%M"
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(
                value,
                fmt
            )

            if "%H" in fmt:
                return dt.isoformat()

            return dt.strftime(
                "%Y-%m-%d"
            )

        except ValueError:
            continue

    return value


# =========================================================
# LOCATION FROM EVIDENCE
# =========================================================

def find_location(
    evidence,
    locations
):
    if not evidence:
        return None

    evidence_lower = (
        evidence.lower()
    )

    matches = []

    for location in locations:
        if not location:
            continue

        location_text = normalize_text(
            location
        )

        if (
            location_text
            and
            location_text.lower()
            in evidence_lower
        ):
            matches.append(
                location_text
            )

    if not matches:
        return None

    matches.sort(
        key=len,
        reverse=True
    )

    return matches[0]


# =========================================================
# DYNAMIC ENTITY TYPE GUESSER
# =========================================================

def guess_entity_type(value):
    value = normalize_text(
        value
    )

    if not value:
        return "UNKNOWN"

    # PHONE:
    # 9876543210
    # 98765-43210
    # 98765 43210
    # +91 9876543210
    phone_digits = normalize_phone(
        value
    )

    if (
        len(phone_digits) == 10
        and
        phone_digits[0] in "6789"
        and
        re.fullmatch(
            r"(?:\+?91[\s\-]?)?[6-9](?:[\s\-]?\d){9}",
            value
        )
    ):
        return "PHONE"

    # VEHICLE:
    # TN11CD7788
    # TN 11 CD 7788
    # TN-11-CD-7788
    if re.fullmatch(
        r"[A-Z]{2}[\s\-]?\d{1,2}[\s\-]?[A-Z]{1,3}[\s\-]?\d{4}",
        value,
        re.IGNORECASE
    ):
        return "VEHICLE"

    # Vehicle prefix accidentally included by extractor:
    # "vehicle TN 11 CD 7788"
    if re.fullmatch(
        r"(?:vehicle\s+)?[A-Z]{2}[\s\-]?\d{1,2}[\s\-]?[A-Z]{1,3}[\s\-]?\d{4}",
        value,
        re.IGNORECASE
    ):
        return "VEHICLE"

    # ACCOUNT
    if re.fullmatch(
        r"(?:ACC|HDFC|ICICI|SBI|AXIS)[\s\-]?[A-Z0-9]+",
        value,
        re.IGNORECASE
    ):
        return "ACCOUNT"

    return "UNKNOWN"


# =========================================================
# RELATION-ENDPOINT TYPE HINTS
# =========================================================

def infer_source_type_from_relation(
    relation_type,
    source_name
):
    relation_type = normalize_text(
        relation_type
    ).upper()

    if relation_type == "TRANSFERRED_TO":
        return "ACCOUNT"

    guessed = guess_entity_type(
        source_name
    )

    if guessed != "UNKNOWN":
        return guessed

    return None


def infer_target_type_from_relation(
    relation_type,
    target_name
):
    relation_type = normalize_text(
        relation_type
    ).upper()

    if relation_type in {
        "USED_VEHICLE",
        "USES_VEHICLE"
    }:
        return "VEHICLE"

    if relation_type in {
        "USES_PHONE",
        "USED_PHONE",
        "HAS_PHONE"
    }:
        return "PHONE"

    if relation_type in {
        "USES_ACCOUNT",
        "USED_ACCOUNT",
        "HAS_ACCOUNT",
        "TRANSFERRED_TO"
    }:
        return "ACCOUNT"

    if relation_type in {
        "LOCATED_AT",
        "VISITED",
        "LIVES_AT",
        "RESIDES_AT",
        "STAYED_AT"
    }:
        return "LOCATION"

    if relation_type in {
        "WORKS_FOR",
        "MEMBER_OF"
    }:
        return "ORGANIZATION"

    guessed = guess_entity_type(
        target_name
    )

    if guessed != "UNKNOWN":
        return guessed

    return None


# =========================================================
# RELATION ENDPOINT CLEANUP
# =========================================================

def clean_endpoint_for_type(
    value,
    entity_type
):
    value = normalize_text(
        value
    )

    entity_type = normalize_text(
        entity_type
    ).upper()

    if entity_type == "VEHICLE":
        match = re.search(
            r"[A-Z]{2}[\s\-]?\d{1,2}[\s\-]?[A-Z]{1,3}[\s\-]?\d{4}",
            value,
            re.IGNORECASE
        )

        if match:
            return normalize_vehicle(
                match.group(0)
            )

    if entity_type == "PHONE":
        match = re.search(
            r"(?:\+?91[\s\-]?)?[6-9](?:[\s\-]?\d){9}",
            value
        )

        if match:
            return normalize_phone(
                match.group(0)
            )

    if entity_type == "ACCOUNT":
        match = re.search(
            r"(?:ACC|HDFC|ICICI|SBI|AXIS)[\s\-]?[A-Z0-9]+",
            value,
            re.IGNORECASE
        )

        if match:
            return normalize_account(
                match.group(0)
            )

    return canonical_value(
        value,
        entity_type
    )


# =========================================================
# EVENT TYPE
# =========================================================

def get_event_type(relationship):
    relation = normalize_text(
        relationship
    ).upper()

    mapping = {
        "MET": "MEETING",
        "CALLED": "COMMUNICATION",
        "CONTACTED": "COMMUNICATION",
        "MESSAGED": "COMMUNICATION",
        "TRANSFERRED_TO": "TRANSACTION",
        "USED_VEHICLE": "VEHICLE_USE",
        "USES_PHONE": "PHONE_USAGE",
        "TRAVELLED_WITH": "TRAVEL",
        "VISITED": "VISIT",
        "DELIVERED_TO": "DELIVERY",
        "INTRODUCED_TO": "INTRODUCTION",
        "SOLD_TO": "SALE",
        "BORROWED_FROM": "BORROWING",
        "RENTED_FROM": "RENTAL",
        "RETURNED_TO": "RETURN",
        "LENT_TO": "LENDING",
        "LENT_ITEM_TO": "LENDING",
        "SHARED_WITH": "ASSOCIATION",
        "WORKS_FOR": "EMPLOYMENT"
    }

    return mapping.get(
        relation,
        relation
    )


# =========================================================
# MAIN GRAPH READY FORMATTER
# =========================================================

def build_graph_ready_json(
    structured_data,
    relationships,
    aliases_by_person=None
):
    if aliases_by_person is None:
        aliases_by_person = {}

    if relationships is None:
        relationships = []

    # =====================================================
    # COMBINE STRUCTURED DATA
    # =====================================================

    combined = {
        "persons": [],
        "phones": [],
        "vehicles": [],
        "accounts": [],
        "locations": [],
        "organizations": [],
        "aliases": []
    }

    # MULTI FILE
    if isinstance(
        structured_data,
        list
    ):
        for item in structured_data:
            data = item.get(
                "data",
                item
            )

            if not isinstance(
                data,
                dict
            ):
                continue

            for key in combined:
                values = data.get(
                    key,
                    []
                )

                if isinstance(
                    values,
                    list
                ):
                    combined[
                        key
                    ].extend(
                        values
                    )

    # SINGLE FILE
    elif isinstance(
        structured_data,
        dict
    ):
        for key in combined:
            values = (
                structured_data.get(
                    key,
                    []
                )
            )

            if isinstance(
                values,
                list
            ):
                combined[
                    key
                ].extend(
                    values
                )

    # Raw dedup first.
    for key in combined:
        combined[key] = list(
            dict.fromkeys(
                value
                for value
                in combined[key]
                if value is not None
            )
        )

    # =====================================================
    # ENTITY STORAGE
    # =====================================================

    entities = []

    # Key is:
    # (ENTITY_TYPE, normalized_value)
    #
    # This prevents:
    # PERSON "1234"
    # and ACCOUNT "1234"
    # from accidentally sharing an ID.
    entity_lookup = {}

    counters = {
        "PERSON": 0,
        "PHONE": 0,
        "VEHICLE": 0,
        "ACCOUNT": 0,
        "LOCATION": 0,
        "ORGANIZATION": 0,
        "UNKNOWN": 0
    }

    # =====================================================
    # ADD ENTITY
    # =====================================================

    def add_entity(
        entity_type,
        value,
        aliases=None
    ):
        entity_type = normalize_text(
            entity_type
        ).upper()

        if entity_type not in ENTITY_PREFIXES:
            entity_type = "UNKNOWN"

        value = clean_endpoint_for_type(
            value,
            entity_type
        )

        if not value:
            return None

        lookup_key = canonical_lookup_key(
            value,
            entity_type
        )

        if not lookup_key[1]:
            return None

        # ---------------------------------------------
        # EXISTING ENTITY
        # ---------------------------------------------

        if lookup_key in entity_lookup:
            existing_id = entity_lookup[
                lookup_key
            ]

            # Preserve different textual forms as aliases
            # for PERSON only.
            if entity_type == "PERSON":
                for entity in entities:
                    if (
                        entity.get("id") == existing_id
                        and
                        entity.get("type") == "PERSON"
                    ):
                        existing_name = entity.get(
                            "name",
                            ""
                        )

                        candidate_values = []

                        original_value = normalize_text(
                            value
                        )

                        if (
                            original_value
                            and
                            normalize_person_key(
                                original_value
                            )
                            ==
                            normalize_person_key(
                                existing_name
                            )
                            and
                            original_value
                            !=
                            existing_name
                        ):
                            candidate_values.append(
                                original_value
                            )

                        for alias in aliases or []:
                            alias = normalize_text(
                                alias
                            )

                            if alias:
                                candidate_values.append(
                                    alias
                                )

                        for candidate in candidate_values:
                            if (
                                candidate != existing_name
                                and
                                candidate not in entity[
                                    "aliases"
                                ]
                            ):
                                entity[
                                    "aliases"
                                ].append(
                                    candidate
                                )

                        break

            return existing_id

        # ---------------------------------------------
        # CREATE NEW ENTITY
        # ---------------------------------------------

        counters[
            entity_type
        ] += 1

        prefix = ENTITY_PREFIXES[
            entity_type
        ]

        entity_id = (
            f"{prefix}"
            f"{counters[entity_type]:03d}"
        )

        if entity_type == "PERSON":
            cleaned_aliases = []

            for alias in aliases or []:
                alias = normalize_text(
                    alias
                )

                if (
                    alias
                    and
                    alias != value
                    and
                    alias not in cleaned_aliases
                ):
                    cleaned_aliases.append(
                        alias
                    )

            entity_object = {
                "id": entity_id,
                "type": "PERSON",
                "name": value,
                "aliases": cleaned_aliases
            }

        else:
            entity_object = {
                "id": entity_id,
                "type": entity_type,
                "value": value
            }

        entities.append(
            entity_object
        )

        entity_lookup[
            lookup_key
        ] = entity_id

        return entity_id

    # =====================================================
    # STRUCTURED PERSONS
    # =====================================================

    for person in combined[
        "persons"
    ]:
        aliases = aliases_by_person.get(
            person,
            []
        )

        add_entity(
            "PERSON",
            person,
            aliases
        )

    # =====================================================
    # STRUCTURED ALIASES
    # =====================================================

    # We intentionally DO NOT blindly merge an alias
    # into a person because alias ownership is not known.
    #
    # However, if an alias is only a formatting/casing
    # variation of an existing person, add_entity() will
    # safely deduplicate it.

    for alias in combined[
        "aliases"
    ]:
        add_entity(
            "PERSON",
            alias
        )

    # =====================================================
    # PHONES
    # =====================================================

    for phone in combined[
        "phones"
    ]:
        add_entity(
            "PHONE",
            phone
        )

    # =====================================================
    # VEHICLES
    # =====================================================

    for vehicle in combined[
        "vehicles"
    ]:
        add_entity(
            "VEHICLE",
            vehicle
        )

    # =====================================================
    # ACCOUNTS
    # =====================================================

    for account in combined[
        "accounts"
    ]:
        add_entity(
            "ACCOUNT",
            account
        )

    # =====================================================
    # LOCATIONS
    # =====================================================

    for location in combined[
        "locations"
    ]:
        add_entity(
            "LOCATION",
            location
        )

    # =====================================================
    # ORGANIZATIONS
    # =====================================================

    for organization in combined[
        "organizations"
    ]:
        add_entity(
            "ORGANIZATION",
            organization
        )

    # =====================================================
    # RELATIONSHIPS
    # =====================================================

    final_relationships = []

    evidence_list = []

    events = []

    evidence_counter = 0

    event_counter = 0

    for relation in relationships:
        source_name = normalize_text(
            relation.get(
                "source_entity"
            )
        )

        target_name = normalize_text(
            relation.get(
                "target_entity"
            )
        )

        relation_type = normalize_text(
            relation.get(
                "relationship"
            )
        ).upper()

        if not source_name:
            continue

        if not target_name:
            continue

        if not relation_type:
            continue

        # =================================================
        # DETERMINE ENDPOINT TYPES
        # =================================================

        source_type_hint = (
            infer_source_type_from_relation(
                relation_type,
                source_name
            )
        )

        target_type_hint = (
            infer_target_type_from_relation(
                relation_type,
                target_name
            )
        )

        # -------------------------------------------------
        # Existing entity matching should first try
        # semantic relation hints.
        # -------------------------------------------------

        source_id = None

        if source_type_hint:
            source_name = (
                clean_endpoint_for_type(
                    source_name,
                    source_type_hint
                )
            )

            source_id = (
                entity_lookup.get(
                    canonical_lookup_key(
                        source_name,
                        source_type_hint
                    )
                )
            )

        # Person fallback.
        if not source_id:
            person_key = (
                canonical_lookup_key(
                    source_name,
                    "PERSON"
                )
            )

            source_id = (
                entity_lookup.get(
                    person_key
                )
            )

        # Generic guessed fallback.
        if not source_id:
            source_type = (
                source_type_hint
                or
                guess_entity_type(
                    source_name
                )
            )

            if (
                source_type == "UNKNOWN"
                and
                normalize_person_key(
                    source_name
                )
            ):
                # If text endpoint matches an extracted
                # person by normalized form, use PERSON.
                person_candidate = (
                    entity_lookup.get(
                        canonical_lookup_key(
                            source_name,
                            "PERSON"
                        )
                    )
                )

                if person_candidate:
                    source_id = (
                        person_candidate
                    )

            if not source_id:
                source_id = add_entity(
                    source_type,
                    source_name
                )

        # =================================================
        # TARGET ID
        # =================================================

        target_id = None

        if target_type_hint:
            target_name = (
                clean_endpoint_for_type(
                    target_name,
                    target_type_hint
                )
            )

            target_id = (
                entity_lookup.get(
                    canonical_lookup_key(
                        target_name,
                        target_type_hint
                    )
                )
            )

        # Person-to-person relations.
        person_target_relations = {
            "MET",
            "CALLED",
            "CONTACTED",
            "MESSAGED",
            "RENTED_FROM",
            "BORROWED_FROM",
            "RECEIVED_FROM",
            "DELIVERED_TO",
            "SOLD_TO",
            "RETURNED_TO",
            "LENT_TO",
            "LENT_ITEM_TO",
            "SHARED_WITH",
            "TRAVELLED_WITH",
            "STAYED_WITH",
            "INTRODUCED_TO",
            "ASSOCIATED_WITH"
        }

        if (
            not target_id
            and
            relation_type
            in person_target_relations
        ):
            target_id = (
                entity_lookup.get(
                    canonical_lookup_key(
                        target_name,
                        "PERSON"
                    )
                )
            )

            if not target_id:
                target_id = add_entity(
                    "PERSON",
                    target_name
                )

        if not target_id:
            target_type = (
                target_type_hint
                or
                guess_entity_type(
                    target_name
                )
            )

            target_id = add_entity(
                target_type,
                target_name
            )

        if not source_id or not target_id:
            continue

        # =================================================
        # EVIDENCE
        # =================================================

        evidence_text = normalize_text(
            relation.get(
                "evidence"
            )
        )

        source_file = normalize_text(
            relation.get(
                "source_file"
            )
        )

        # =================================================
        # RELATIONSHIP CONFIDENCE
        # Prefer validator confidence
        # =================================================

        confidence = relation.get(
            "validation_confidence",
            relation.get(
                "confidence",
                0.5
            )
        )

        try:
            confidence = float(
                confidence
            )

        except (
            ValueError,
            TypeError
        ):
            confidence = 0.5

        evidence_id = None

        if evidence_text:
            evidence_counter += 1

            evidence_id = (
                f"EV{evidence_counter:03d}"
            )

            evidence_object = {
                "id": evidence_id,

                "source_type":
                    get_source_type(
                        source_file
                    ),

                "source_name":
                    source_file,

                "excerpt":
                    evidence_text,

                "timestamp":
                    normalize_timestamp(
                        relation.get(
                            "timestamp"
                        )
                    ),

                "confidence":
                    round(
                        confidence,
                        2
                    ),

                "method":
                    relation.get(
                        "method"
                    )
            }

            evidence_list.append(
                evidence_object
            )

        # =================================================
        # FINAL RELATIONSHIP
        # =================================================

        relationship_object = {
            "source_id":
                source_id,

            "target_id":
                target_id,

            "type":
                relation_type,

            "confidence":
                round(
                    confidence,
                    2
                ),

            "decision":
                relation.get(
                    "validation_decision",
                    relation.get(
                        "decision",
                        "REVIEW"
                    )
                )
        }

        if relation.get(
            "amount"
        ):
            relationship_object[
                "amount"
            ] = relation.get(
                "amount"
            )

        timestamp = normalize_timestamp(
            relation.get(
                "timestamp"
            )
        )

        if timestamp:
            relationship_object[
                "timestamp"
            ] = timestamp

        if evidence_id:
            relationship_object[
                "evidence_id"
            ] = evidence_id

        final_relationships.append(
            relationship_object
        )

        # =================================================
        # EVENT
        # =================================================

        location = find_location(
            evidence_text,
            combined[
                "locations"
            ]
        )

        if (
            timestamp
            or
            location
        ):
            event_counter += 1

            event_id = (
                f"E{event_counter:03d}"
            )

            participants = []

            if (
                source_id.startswith(
                    "P"
                )
                and
                not source_id.startswith(
                    "PH"
                )
            ):
                participants.append(
                    source_id
                )

            if (
                target_id.startswith(
                    "P"
                )
                and
                not target_id.startswith(
                    "PH"
                )
                and
                target_id
                not in participants
            ):
                participants.append(
                    target_id
                )

            event_object = {
                "id":
                    event_id,

                "type":
                    get_event_type(
                        relation_type
                    ),

                "timestamp":
                    timestamp,

                "location":
                    location,

                "participants":
                    participants
            }

            if evidence_id:
                event_object[
                    "evidence_id"
                ] = evidence_id

            events.append(
                event_object
            )

    # =====================================================
    # REMOVE DUPLICATE RELATIONSHIPS
    # =====================================================

    seen = set()

    unique_relationships = []

    for relation in final_relationships:
        # Keep timestamp in the key when available so two
        # repeated interactions at different times are not
        # accidentally collapsed into one.
        key = (
            relation[
                "source_id"
            ],

            relation[
                "target_id"
            ],

            relation[
                "type"
            ],

            relation.get(
                "timestamp"
            ),

            relation.get(
                "amount"
            )
        )

        if key in seen:
            continue

        seen.add(
            key
        )

        unique_relationships.append(
            relation
        )

    # =====================================================
    # FINAL GRAPH READY JSON
    # =====================================================

    return {
        "entities":
            entities,

        "relationships":
            unique_relationships,

        "events":
            events,

        "evidence":
            evidence_list
    }
