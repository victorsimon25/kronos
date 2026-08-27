import re


def postprocess_relationships(
    relationships,
    full_text,
    persons=None
):

    if persons is None:
        persons = []

    final = []

    for relation in relationships:

        source = relation.get(
            "source_entity",
            ""
        )

        target = relation.get(
            "target_entity",
            ""
        )

        raw_relation = relation.get(
            "raw_relation",
            ""
        )

        evidence = relation.get(
            "evidence",
            ""
        )

        relationship = relation.get(
            "relationship",
            ""
        )

        raw_lower = raw_relation.lower()
        evidence_lower = evidence.lower()


        # =====================================================
        # NORMALIZE BASIC RELATION NAMES
        # =====================================================

        if "sold" in raw_lower:
            relationship = "SOLD_TO"

        elif "borrow" in raw_lower:
            relationship = "BORROWED_FROM"

        elif "travelled with" in raw_lower:
            relationship = "TRAVELLED_WITH"

        elif "introduced" in raw_lower:
            relationship = "INTRODUCED_TO"

        elif "works for" in raw_lower:
            relationship = "WORKS_FOR"

        elif "called" in raw_lower:
            relationship = "CALLED"

        elif raw_lower == "met":
            relationship = "MET"


        # =====================================================
        # ENTITY-AWARE PERSON TARGET CORRECTION
        # =====================================================

        other_persons = []

        for person in persons:

            person_lower = person.lower()

            if (
                person_lower in evidence_lower
                and
                person_lower != str(source).lower()
            ):
                other_persons.append(person)


        for person_target in other_persons:

            escaped_person = re.escape(
                person_target
            )

            # -----------------------------------------
            # FROM
            # -----------------------------------------

            if re.search(
                rf'\bfrom\s+{escaped_person}\b',
                evidence,
                re.IGNORECASE
            ):

                target = person_target

                if "rent" in raw_lower:
                    relationship = "RENTED_FROM"

                elif "borrow" in raw_lower:
                    relationship = "BORROWED_FROM"

                elif "receive" in raw_lower:
                    relationship = "RECEIVED_FROM"

                break


            # -----------------------------------------
            # TO
            # -----------------------------------------

            if re.search(
                rf'\bto\s+{escaped_person}\b',
                evidence,
                re.IGNORECASE
            ):

                target = person_target

                if "deliver" in raw_lower:
                    relationship = "DELIVERED_TO"

                elif "sold" in raw_lower:
                    relationship = "SOLD_TO"

                elif "return" in raw_lower:
                    relationship = "RETURNED_TO"

                break


            # -----------------------------------------
            # WITH
            # -----------------------------------------

            if re.search(
                rf'\bwith\s+{escaped_person}\b',
                evidence,
                re.IGNORECASE
            ):

                target = person_target

                if "share" in raw_lower:
                    relationship = "SHARED_WITH"

                elif "travel" in raw_lower:
                    relationship = "TRAVELLED_WITH"

                elif "stay" in raw_lower:
                    relationship = "STAYED_WITH"

                break


        # =====================================================
        # SPECIAL INTRODUCTION CORRECTION
        # =====================================================

        if "introduc" in raw_lower:

            introduced_match = re.search(
                r'\bintroduced\s+(.+?)\s+to\s+(.+?)(?:[.,]|$)',
                evidence,
                re.IGNORECASE
            )

            if introduced_match:

                introduced_person = (
                    introduced_match
                    .group(1)
                    .strip()
                )

                target_person = (
                    introduced_match
                    .group(2)
                    .strip()
                )

                source = introduced_person
                target = target_person
                relationship = "INTRODUCED_TO"


        # =====================================================
        # VEHICLE CORRECTION
        # =====================================================

        vehicle_match = re.search(
            r'\b[A-Z]{2}\d{1,2}[A-Z]{1,3}\d{4}\b',
            evidence,
            re.IGNORECASE
        )

        if vehicle_match:

            if (
                "used" in raw_lower
                or
                "vehicle" in raw_lower
                or
                "drove" in raw_lower
            ):

                relationship = "USED_VEHICLE"

                target = (
                    vehicle_match
                    .group(0)
                    .upper()
                )


        # =====================================================
        # PHONE CORRECTION
        # =====================================================

        phone_match = re.search(
            r'\b[6-9]\d{9}\b',
            evidence
        )

        if phone_match:

            if (
                "used" in raw_lower
                or
                "phone" in evidence_lower
                or
                "mobile" in evidence_lower
            ):

                relationship = "USES_PHONE"

                target = phone_match.group(
                    0
                )


        # =====================================================
        # ACCOUNT TRANSFER CORRECTION
        # =====================================================

        accounts = re.findall(
            r'\b(?:ACC|HDFC|ICICI|SBI|AXIS)[A-Z0-9]+\b',
            evidence,
            re.IGNORECASE
        )


        amount_match = re.search(
            r'(?:Rs\.?|₹)\s*[\d,]+(?:\.\d+)?',
            evidence,
            re.IGNORECASE
        )


        amount = None

        if amount_match:
            amount = amount_match.group(
                0
            )


        if (
            "transfer" in raw_lower
            and
            len(accounts) >= 2
        ):

            source = accounts[0].upper()

            target = accounts[1].upper()

            relationship = "TRANSFERRED_TO"


        # =====================================================
        # TIMESTAMP SAFETY
        # =====================================================

        timestamp = relation.get(
            "timestamp"
        )

        if (
            timestamp
            and
            timestamp.lower()
            not in evidence_lower
        ):
            timestamp = None


        # =====================================================
        # FINAL OBJECT
        # =====================================================

        updated = relation.copy()

        updated[
            "source_entity"
        ] = source

        updated[
            "target_entity"
        ] = target

        updated[
            "relationship"
        ] = relationship

        updated[
            "timestamp"
        ] = timestamp

        updated[
            "amount"
        ] = amount

        updated[
            "postprocessed"
        ] = True


        final.append(
            updated
        )


    return remove_duplicates(
        final
    )


def remove_duplicates(
    relationships
):

    seen = set()

    result = []


    for relation in relationships:

        key = (
            str(
                relation.get(
                    "source_entity",
                    ""
                )
            ).lower(),

            relation.get(
                "relationship",
                ""
            ),

            str(
                relation.get(
                    "target_entity",
                    ""
                )
            ).lower()
        )


        if key in seen:
            continue


        seen.add(
            key
        )


        result.append(
            relation
        )


    return result