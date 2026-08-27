import re

from value_normalizer import (
    normalize_person_key,
    normalize_phone,
    normalize_vehicle,
    normalize_account
)


VEHICLE_PATTERN = re.compile(
    r"\b[A-Z]{2}[\s\-]?\d{1,2}[\s\-]?[A-Z]{1,3}[\s\-]?\d{4}\b",
    re.IGNORECASE
)

PHONE_PATTERN = re.compile(
    r"(?<!\d)(?:\+?91[\s\-]?)?[6-9](?:[\s\-]?\d){9}(?!\d)"
)

ACCOUNT_PATTERN = re.compile(
    r"\b(?:ACC|HDFC|ICICI|SBI|AXIS)[\s\-]?\d[A-Z0-9]*\b",
    re.IGNORECASE
)

AMOUNT_PATTERN = re.compile(
    r"(?:Rs\.?|₹)\s*[\d,]+(?:\.\d+)?",
    re.IGNORECASE
)


def _contains_word(text, word):
    return word.lower() in str(text).lower()


def _normalize_relation_name(raw_relation, relationship, evidence):
    combined = " ".join([
        str(raw_relation),
        str(relationship),
        str(evidence)
    ]).lower()

    if "sold" in combined:
        return "SOLD_TO"

    if "borrow" in combined:
        return "BORROWED_FROM"

    if "travelled with" in combined or "traveled with" in combined:
        return "TRAVELLED_WITH"

    if "introduc" in combined:
        return "INTRODUCED_TO"

    if "works for" in combined:
        return "WORKS_FOR"

    if "called" in str(raw_relation).lower():
        return "CALLED"

    if str(raw_relation).strip().lower() == "met":
        return "MET"

    return str(relationship).strip().upper().replace(" ", "_")


def _find_other_persons(persons, source, evidence):
    source_key = normalize_person_key(source)
    result = []

    for person in persons or []:
        person = str(person).strip()

        if not person:
            continue

        if normalize_person_key(person) == source_key:
            continue

        if re.search(
            rf"\b{re.escape(person)}\b",
            evidence,
            re.IGNORECASE
        ):
            result.append(person)

    return result


def postprocess_relationships(
    relationships,
    full_text,
    persons=None
):
    if persons is None:
        persons = []

    final = []

    for relation in relationships or []:
        source = str(
            relation.get("source_entity", "")
        ).strip()

        target = str(
            relation.get("target_entity", "")
        ).strip()

        raw_relation = str(
            relation.get(
                "raw_relation",
                relation.get("relationship", "")
            )
        ).strip()

        evidence = str(
            relation.get("evidence", "")
        ).strip()

        relationship = str(
            relation.get("relationship", "")
        ).strip()

        raw_lower = raw_relation.lower()
        evidence_lower = evidence.lower()

        relationship = _normalize_relation_name(
            raw_relation,
            relationship,
            evidence
        )

        # =================================================
        # PERSON TARGET CORRECTION
        # =================================================

        other_persons = _find_other_persons(
            persons,
            source,
            evidence
        )

        for person_target in other_persons:
            escaped = re.escape(person_target)

            if re.search(
                rf"\bfrom\s+{escaped}\b",
                evidence,
                re.IGNORECASE
            ):
                target = person_target

                if "rent" in raw_lower or "rent" in evidence_lower:
                    relationship = "RENTED_FROM"

                elif "borrow" in raw_lower or "borrow" in evidence_lower:
                    relationship = "BORROWED_FROM"

                elif "receive" in raw_lower or "receive" in evidence_lower:
                    relationship = "RECEIVED_FROM"

                break

            if re.search(
                rf"\bto\s+{escaped}\b",
                evidence,
                re.IGNORECASE
            ):
                target = person_target

                if "deliver" in raw_lower or "deliver" in evidence_lower:
                    relationship = "DELIVERED_TO"

                elif "sold" in raw_lower or "sold" in evidence_lower:
                    relationship = "SOLD_TO"

                elif "return" in raw_lower or "return" in evidence_lower:
                    relationship = "RETURNED_TO"

                elif "lent" in raw_lower or "lent" in evidence_lower:
                    relationship = "LENT_ITEM_TO"

                break

            if re.search(
                rf"\bwith\s+{escaped}\b",
                evidence,
                re.IGNORECASE
            ):
                target = person_target

                if "share" in raw_lower or "shared" in evidence_lower:
                    relationship = "SHARED_WITH"

                elif "travel" in raw_lower or "travel" in evidence_lower:
                    relationship = "TRAVELLED_WITH"

                elif "stay" in raw_lower or "stay" in evidence_lower:
                    relationship = "STAYED_WITH"

                break

        # =================================================
        # INTRODUCTION
        # =================================================

        if "introduc" in raw_lower or "introduced" in evidence_lower:
            match = re.search(
                r"\bintroduced\s+(.+?)\s+to\s+(.+?)(?:[.,]|$)",
                evidence,
                re.IGNORECASE
            )

            if match:
                source = match.group(1).strip()
                target = match.group(2).strip()
                relationship = "INTRODUCED_TO"

        # =================================================
        # ACCOUNT TRANSFER - DO THIS BEFORE GENERIC TARGETS
        # =================================================

        account_matches = ACCOUNT_PATTERN.findall(
            evidence
        )

        normalized_accounts = []

        for account in account_matches:
            normalized = normalize_account(account)

            if normalized and normalized not in normalized_accounts:
                normalized_accounts.append(normalized)

        transfer_context = (
            "transfer" in raw_lower
            or "transfer" in evidence_lower
            or relationship == "TRANSFERRED_TO"
        )

        if transfer_context and len(normalized_accounts) >= 2:
            source = normalized_accounts[0]
            target = normalized_accounts[1]
            relationship = "TRANSFERRED_TO"

        # =================================================
        # VEHICLE
        # =================================================

        vehicle_match = VEHICLE_PATTERN.search(
            evidence
        )

        protected_person_relations = {
            "CALLED",
            "CONTACTED",
            "MET",
            "RENTED_FROM",
            "BORROWED_FROM",
            "DELIVERED_TO",
            "SOLD_TO",
            "RETURNED_TO",
            "INTRODUCED_TO",
            "TRAVELLED_WITH",
            "SHARED_WITH",
            "STAYED_WITH",
            "WORKS_FOR",
            "TRANSFERRED_TO"
        }

        if vehicle_match:
            vehicle = normalize_vehicle(
                vehicle_match.group(0)
            )

            vehicle_context = (
                "vehicle" in evidence_lower
                or "vehicle" in raw_lower
                or "drove" in evidence_lower
                or "drive" in raw_lower
                or relationship in {
                    "USED",
                    "USED_VEHICLE",
                    "USES_VEHICLE"
                }
            )

            if (
                vehicle
                and vehicle_context
                and relationship not in protected_person_relations
            ):
                relationship = "USED_VEHICLE"
                target = vehicle

            elif normalize_vehicle(target) == vehicle and vehicle:
                target = vehicle

        # =================================================
        # PHONE
        # =================================================

        phone_match = PHONE_PATTERN.search(
            evidence
        )

        if phone_match:
            phone = normalize_phone(
                phone_match.group(0)
            )

            phone_context = (
                "phone" in evidence_lower
                or "mobile" in evidence_lower
                or "phone" in raw_lower
                or "mobile" in raw_lower
                or relationship in {
                    "USES_PHONE",
                    "USED_PHONE",
                    "HAS_PHONE"
                }
            )

            if (
                phone
                and phone_context
                and relationship not in {
                    "CALLED",
                    "CONTACTED",
                    "TRANSFERRED_TO"
                }
            ):
                relationship = "USES_PHONE"
                target = phone

            elif normalize_phone(target) == phone and phone:
                target = phone

        # =================================================
        # ACCOUNT TARGET NORMALIZATION
        # =================================================

        if relationship in {
            "USES_ACCOUNT",
            "USED_ACCOUNT",
            "HAS_ACCOUNT"
        }:
            match = ACCOUNT_PATTERN.search(
                target
            )

            if match:
                normalized = normalize_account(
                    match.group(0)
                )

                if normalized:
                    target = normalized

        # =================================================
        # AMOUNT
        # =================================================

        amount = None

        amount_match = AMOUNT_PATTERN.search(
            evidence
        )

        if amount_match:
            amount = amount_match.group(0).strip()

        # =================================================
        # FINAL
        # =================================================

        updated = relation.copy()

        updated["source_entity"] = source
        updated["target_entity"] = target
        updated["relationship"] = relationship
        updated["timestamp"] = relation.get("timestamp")
        updated["amount"] = amount
        updated["postprocessed"] = True

        final.append(updated)

    return remove_duplicates(final)


def remove_duplicates(relationships):
    seen = set()
    result = []

    for relation in relationships:
        relationship = str(
            relation.get("relationship", "")
        ).strip().upper()

        source = str(
            relation.get("source_entity", "")
        ).strip()

        target = str(
            relation.get("target_entity", "")
        ).strip()

        if relationship == "TRANSFERRED_TO":
            source_key = normalize_account(source)
            target_key = normalize_account(target)

        elif relationship in {
            "USED_VEHICLE",
            "USES_VEHICLE",
            "HAS_VEHICLE"
        }:
            source_key = normalize_person_key(source)
            target_key = normalize_vehicle(target)

        elif relationship in {
            "USES_PHONE",
            "USED_PHONE",
            "HAS_PHONE"
        }:
            source_key = normalize_person_key(source)
            target_key = normalize_phone(target)

        else:
            source_key = normalize_person_key(source)
            target_key = normalize_person_key(target)

        key = (
            source_key,
            relationship,
            target_key,
            str(
                relation.get("source_file", "")
            ).strip().lower(),
            relation.get("timestamp"),
            relation.get("amount")
        )

        if key in seen:
            continue

        seen.add(key)
        result.append(relation)

    return result
