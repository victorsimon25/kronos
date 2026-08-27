from difflib import SequenceMatcher
import re


# =========================================================
# NORMALIZATION HELPERS
# =========================================================

def normalize_name(value):
    if not value:
        return ""

    value = str(value).strip().lower()
    value = re.sub(r"[^a-z0-9\s]", "", value)
    value = re.sub(r"\s+", " ", value)

    return value.strip()


def normalize_phone(value):
    if not value:
        return ""

    return re.sub(
        r"\D",
        "",
        str(value)
    )


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
    if not value:
        return ""

    value = str(value).strip().lower()
    value = re.sub(r"[^a-z0-9\s]", "", value)
    value = re.sub(r"\s+", " ", value)

    return value.strip()


# =========================================================
# BASIC SIMILARITY
# =========================================================

def similarity(a, b):
    a = normalize_name(a)
    b = normalize_name(b)

    if not a or not b:
        return 0.0

    return SequenceMatcher(
        None,
        a,
        b
    ).ratio()


# =========================================================
# LIST HELPERS
# =========================================================

def _clean_list(values):
    if values is None:
        return []

    if not isinstance(values, list):
        values = [values]

    result = []

    for value in values:
        if value is None:
            continue

        text = str(value).strip()

        if text and text not in result:
            result.append(text)

    return result


def _normalized_set(values, normalizer):
    return {
        normalizer(value)
        for value in _clean_list(values)
        if normalizer(value)
    }


def _set_overlap_score(values1, values2, normalizer):
    set1 = _normalized_set(
        values1,
        normalizer
    )

    set2 = _normalized_set(
        values2,
        normalizer
    )

    if not set1 or not set2:
        return 0.0

    return 1.0 if set1.intersection(set2) else 0.0


def _location_similarity(values1, values2):
    locations1 = _clean_list(values1)
    locations2 = _clean_list(values2)

    if not locations1 or not locations2:
        return 0.0

    best = 0.0

    for location1 in locations1:
        for location2 in locations2:
            normalized1 = normalize_location(
                location1
            )

            normalized2 = normalize_location(
                location2
            )

            if not normalized1 or not normalized2:
                continue

            score = SequenceMatcher(
                None,
                normalized1,
                normalized2
            ).ratio()

            best = max(
                best,
                score
            )

    return best


# =========================================================
# PERSON RECORD BUILDING
# =========================================================

def _ensure_record(records, person_name):
    if not person_name:
        return None

    normalized = normalize_name(
        person_name
    )

    if not normalized:
        return None

    if normalized not in records:
        records[normalized] = {
            "name": str(person_name).strip(),
            "aliases": [],
            "phones": [],
            "vehicles": [],
            "accounts": [],
            "locations": [],
            "organizations": [],
            "source_files": [],
            "evidence": []
        }

    return records[normalized]


def _append_unique(record, field, value):
    if record is None or value is None:
        return

    if field not in record:
        record[field] = []

    value = str(value).strip()

    if value and value not in record[field]:
        record[field].append(
            value
        )


def _append_evidence(record, relationship):
    if record is None:
        return

    evidence = relationship.get(
        "evidence"
    )

    if evidence:
        _append_unique(
            record,
            "evidence",
            evidence
        )

    source_file = relationship.get(
        "source_file"
    )

    if source_file:
        _append_unique(
            record,
            "source_files",
            source_file
        )


def build_person_records(
    structured_data,
    relationships=None
):
    """
    Builds enriched person records from extracted entities
    and relationships.

    This does not merge identities.
    It only attaches available attributes to persons.
    """

    if structured_data is None:
        structured_data = {}

    if relationships is None:
        relationships = []

    persons = _clean_list(
        structured_data.get(
            "persons",
            []
        )
    )

    aliases = _clean_list(
        structured_data.get(
            "aliases",
            []
        )
    )

    locations = _clean_list(
        structured_data.get(
            "locations",
            []
        )
    )

    organizations = _clean_list(
        structured_data.get(
            "organizations",
            []
        )
    )

    records = {}

    # -----------------------------------------------------
    # PERSONS
    # -----------------------------------------------------

    for person in persons:
        _ensure_record(
            records,
            person
        )

    # -----------------------------------------------------
    # ALIASES
    # -----------------------------------------------------

    # Without explicit alias ownership, aliases are kept
    # as candidate person records. We do not auto-attach
    # them to a person here.

    for alias in aliases:
        record = _ensure_record(
            records,
            alias
        )

        if record is not None:
            _append_unique(
                record,
                "aliases",
                alias
            )

    # -----------------------------------------------------
    # RELATIONSHIP-BASED ATTRIBUTE ENRICHMENT
    # -----------------------------------------------------

    for relation in relationships:
        source = str(
            relation.get(
                "source_entity",
                ""
            )
        ).strip()

        target = str(
            relation.get(
                "target_entity",
                ""
            )
        ).strip()

        relationship = str(
            relation.get(
                "relationship",
                ""
            )
        ).strip().upper()

        raw_relation = str(
            relation.get(
                "raw_relation",
                ""
            )
        ).strip().upper()

        combined_relation = (
            relationship
            or
            raw_relation
        )

        source_record = records.get(
            normalize_name(source)
        )

        target_record = records.get(
            normalize_name(target)
        )

        # If a person appears in relationships but was not
        # extracted as a person, do not create it blindly.
        # Only enrich known person records.

        if source_record is not None:
            _append_evidence(
                source_record,
                relation
            )

        if target_record is not None:
            _append_evidence(
                target_record,
                relation
            )

        # -------------------------------------------------
        # PHONE
        # -------------------------------------------------

        if combined_relation in {
            "USES_PHONE",
            "USED_PHONE",
            "HAS_PHONE",
            "PHONE"
        }:
            if source_record is not None:
                _append_unique(
                    source_record,
                    "phones",
                    target
                )

        # -------------------------------------------------
        # VEHICLE
        # -------------------------------------------------

        if combined_relation in {
            "USED_VEHICLE",
            "USES_VEHICLE",
            "HAS_VEHICLE"
        }:
            if source_record is not None:
                _append_unique(
                    source_record,
                    "vehicles",
                    target
                )

        # -------------------------------------------------
        # ACCOUNT
        # -------------------------------------------------

        if combined_relation in {
            "USES_ACCOUNT",
            "USED_ACCOUNT",
            "HAS_ACCOUNT"
        }:
            if source_record is not None:
                _append_unique(
                    source_record,
                    "accounts",
                    target
                )

        # -------------------------------------------------
        # LOCATION
        # -------------------------------------------------

        if combined_relation in {
            "LOCATED_AT",
            "STAYED_AT",
            "LIVES_AT",
            "RESIDES_AT",
            "VISITED"
        }:
            if source_record is not None:
                _append_unique(
                    source_record,
                    "locations",
                    target
                )

        # -------------------------------------------------
        # ORGANIZATION
        # -------------------------------------------------

        if combined_relation in {
            "WORKS_FOR",
            "MEMBER_OF",
            "ASSOCIATED_WITH_ORGANIZATION"
        }:
            if source_record is not None:
                _append_unique(
                    source_record,
                    "organizations",
                    target
                )

        # -------------------------------------------------
        # CONTEXT LOCATION FALLBACK
        # -------------------------------------------------

        evidence = str(
            relation.get(
                "evidence",
                ""
            )
        )

        for location in locations:
            if (
                source_record is not None
                and
                normalize_location(location)
                in normalize_location(evidence)
            ):
                _append_unique(
                    source_record,
                    "locations",
                    location
                )

            if (
                target_record is not None
                and
                normalize_location(location)
                in normalize_location(evidence)
            ):
                _append_unique(
                    target_record,
                    "locations",
                    location
                )

        # -------------------------------------------------
        # ORGANIZATION CONTEXT FALLBACK
        # -------------------------------------------------

        evidence_lower = evidence.lower()

        for organization in organizations:
            if organization.lower() in evidence_lower:
                if source_record is not None:
                    _append_unique(
                        source_record,
                        "organizations",
                        organization
                    )

                if target_record is not None:
                    _append_unique(
                        target_record,
                        "organizations",
                        organization
                    )

    return list(
        records.values()
    )


# =========================================================
# MULTI-SIGNAL SCORING
# =========================================================

def calculate_entity_score(
    record1,
    record2
):
    """
    Weighted entity-resolution score.

    Weights:
      Name       30%
      Phone      30%
      Vehicle    15%
      Account    15%
      Location   10%
    """

    name_score = similarity(
        record1.get(
            "name",
            ""
        ),
        record2.get(
            "name",
            ""
        )
    )

    phone_score = _set_overlap_score(
        record1.get(
            "phones",
            []
        ),
        record2.get(
            "phones",
            []
        ),
        normalize_phone
    )

    vehicle_score = _set_overlap_score(
        record1.get(
            "vehicles",
            []
        ),
        record2.get(
            "vehicles",
            []
        ),
        normalize_vehicle
    )

    account_score = _set_overlap_score(
        record1.get(
            "accounts",
            []
        ),
        record2.get(
            "accounts",
            []
        ),
        normalize_account
    )

    location_score = _location_similarity(
        record1.get(
            "locations",
            []
        ),
        record2.get(
            "locations",
            []
        )
    )

    final_score = (
        name_score * 0.30
        +
        phone_score * 0.30
        +
        vehicle_score * 0.15
        +
        account_score * 0.15
        +
        location_score * 0.10
    )

    reasons = [
        f"Name similarity: {round(name_score, 2)}"
    ]

    if phone_score == 1.0:
        reasons.append(
            "Same phone number"
        )

    if vehicle_score == 1.0:
        reasons.append(
            "Same vehicle"
        )

    if account_score == 1.0:
        reasons.append(
            "Same account"
        )

    if location_score >= 0.85:
        reasons.append(
            f"Similar location/context: {round(location_score, 2)}"
        )

    return {
        "name_score": round(
            name_score,
            2
        ),
        "phone_score": round(
            phone_score,
            2
        ),
        "vehicle_score": round(
            vehicle_score,
            2
        ),
        "account_score": round(
            account_score,
            2
        ),
        "location_score": round(
            location_score,
            2
        ),
        "resolution_score": round(
            final_score,
            2
        ),
        "reasons": reasons
    }


# =========================================================
# DECISION
# =========================================================

def get_entity_decision(score):
    if score >= 0.85:
        return "MERGE"

    if score >= 0.60:
        return "REVIEW"

    return "SEPARATE"


# =========================================================
# ADVANCED RECORD RESOLUTION
# =========================================================

def resolve_person_records(
    records,
    include_separate=False
):
    matches = []

    for i in range(
        len(records)
    ):
        for j in range(
            i + 1,
            len(records)
        ):
            record1 = records[i]
            record2 = records[j]

            score_data = calculate_entity_score(
                record1,
                record2
            )

            score = score_data[
                "resolution_score"
            ]

            decision = get_entity_decision(
                score
            )

            if (
                not include_separate
                and
                decision == "SEPARATE"
            ):
                continue

            matches.append({
                "Entity 1":
                    record1.get(
                        "name",
                        ""
                    ),

                "Entity 2":
                    record2.get(
                        "name",
                        ""
                    ),

                "Name Score":
                    score_data[
                        "name_score"
                    ],

                "Phone Match":
                    score_data[
                        "phone_score"
                    ],

                "Vehicle Match":
                    score_data[
                        "vehicle_score"
                    ],

                "Account Match":
                    score_data[
                        "account_score"
                    ],

                "Location Score":
                    score_data[
                        "location_score"
                    ],

                "Resolution Score":
                    score,

                "Decision":
                    decision,

                "Reasons":
                    "; ".join(
                        score_data[
                            "reasons"
                        ]
                    )
            })

    return matches


# =========================================================
# BACKWARD-COMPATIBLE NAME-ONLY RESOLUTION
# =========================================================

def resolve_person_entities(
    persons,
    aliases
):
    all_names = []

    for name in (
        _clean_list(persons)
        +
        _clean_list(aliases)
    ):
        if name not in all_names:
            all_names.append(
                name
            )

    matches = []

    for i in range(
        len(all_names)
    ):
        for j in range(
            i + 1,
            len(all_names)
        ):
            name1 = all_names[i]
            name2 = all_names[j]

            score = similarity(
                name1,
                name2
            )

            if score >= 0.60:
                matches.append({
                    "Entity 1":
                        name1,

                    "Entity 2":
                        name2,

                    "Name Similarity":
                        round(
                            score,
                            2
                        ),

                    "Resolution Score":
                        round(
                            score * 0.30,
                            2
                        ),

                    "Decision":
                        "REVIEW",

                    "Reasons":
                        "Name similarity only; additional signals required"
                })

    return matches
