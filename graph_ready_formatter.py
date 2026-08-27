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
# NORMALIZATION
# =========================================================

def normalize_text(value):

    if value is None:
        return ""

    return str(value).strip()


def normalize_key(value):

    return normalize_text(
        value
    ).lower()


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

        if (
            location
            and
            location.lower()
            in evidence_lower
        ):

            matches.append(
                location
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

    # PHONE
    if re.fullmatch(
        r'[6-9]\d{9}',
        value
    ):
        return "PHONE"

    # VEHICLE
    if re.fullmatch(
        r'[A-Z]{2}\d{1,2}[A-Z]{1,3}\d{4}',
        value,
        re.IGNORECASE
    ):
        return "VEHICLE"

    # ACCOUNT
    if re.fullmatch(
        r'(?:ACC|HDFC|ICICI|SBI|AXIS)[A-Z0-9]+',
        value,
        re.IGNORECASE
    ):
        return "ACCOUNT"

    return "UNKNOWN"


# =========================================================
# EVENT TYPE
# =========================================================

def get_event_type(relationship):

    relation = normalize_text(
        relationship
    ).upper()

    mapping = {

        "MET":
            "MEETING",

        "CALLED":
            "COMMUNICATION",

        "CONTACTED":
            "COMMUNICATION",

        "MESSAGED":
            "COMMUNICATION",

        "TRANSFERRED_TO":
            "TRANSACTION",

        "USED_VEHICLE":
            "VEHICLE_USE",

        "USES_PHONE":
            "PHONE_USAGE",

        "TRAVELLED_WITH":
            "TRAVEL",

        "VISITED":
            "VISIT",

        "DELIVERED_TO":
            "DELIVERY",

        "INTRODUCED_TO":
            "INTRODUCTION",

        "SOLD_TO":
            "SALE",

        "BORROWED_FROM":
            "BORROWING",

        "RENTED_FROM":
            "RENTAL",

        "RETURNED_TO":
            "RETURN",

        "LENT_TO":
            "LENDING",

        "SHARED_WITH":
            "ASSOCIATION",

        "WORKS_FOR":
            "EMPLOYMENT"
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


    # =====================================================
    # REMOVE DUPLICATES
    # =====================================================

    for key in combined:

        combined[key] = list(
            dict.fromkeys(
                combined[key]
            )
        )


    # =====================================================
    # ENTITY STORAGE
    # =====================================================

    entities = []

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

        value = normalize_text(
            value
        )

        if not value:
            return None

        lookup_key = normalize_key(
            value
        )

        if lookup_key in entity_lookup:

            return entity_lookup[
                lookup_key
            ]


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

            entity_object = {

                "id":
                    entity_id,

                "type":
                    "PERSON",

                "name":
                    value,

                "aliases":
                    aliases or []
            }

        else:

            entity_object = {

                "id":
                    entity_id,

                "type":
                    entity_type,

                "value":
                    value
            }


        entities.append(
            entity_object
        )


        entity_lookup[
            lookup_key
        ] = entity_id


        return entity_id


    # =====================================================
    # PERSONS
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
        # SOURCE ID
        # =================================================

        source_id = entity_lookup.get(
            normalize_key(
                source_name
            )
        )


        if not source_id:

            source_type = guess_entity_type(
                source_name
            )

            source_id = add_entity(
                source_type,
                source_name
            )


        # =================================================
        # TARGET ID
        # =================================================

        target_id = entity_lookup.get(
            normalize_key(
                target_name
            )
        )


        if not target_id:

            target_type = guess_entity_type(
                target_name
            )

            target_id = add_entity(
                target_type,
                target_name
            )


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

                "id":
                    evidence_id,

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
                    "REVIEW"
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
            ):

                if (
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

        key = (

            relation[
                "source_id"
            ],

            relation[
                "target_id"
            ],

            relation[
                "type"
            ]
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