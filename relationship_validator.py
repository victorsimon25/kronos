import re


def validate_relationships(
    relationships
):

    validated = []

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
        ).strip()

        raw_relation = str(
            relation.get(
                "raw_relation",
                ""
            )
        ).strip()

        evidence = str(
            relation.get(
                "evidence",
                ""
            )
        ).strip()

        source_file = relation.get(
            "source_file",
            "unknown"
        )

        method = relation.get(
            "method",
            "unknown"
        )

        relation_status = relation.get(
            "relation_status",
            "UNKNOWN"
        )

        evidence_lower = evidence.lower()

        reasons = []

        score = 0.0


        # =====================================================
        # SOURCE VALIDATION
        # =====================================================

        if source:

            score += 0.10

            reasons.append(
                "Source entity exists"
            )


        if (
            source
            and
            source.lower()
            in evidence_lower
        ):

            score += 0.20

            reasons.append(
                "Source entity found in evidence"
            )


        # =====================================================
        # TARGET VALIDATION
        # =====================================================

        if target:

            score += 0.10

            reasons.append(
                "Target entity exists"
            )


        if (
            target
            and
            target.lower()
            in evidence_lower
        ):

            score += 0.20

            reasons.append(
                "Target entity found in evidence"
            )


        # =====================================================
        # RELATION VALIDATION
        # =====================================================

        if relationship:

            score += 0.10

            reasons.append(
                "Relationship exists"
            )


        if raw_relation:

            raw_words = (
                raw_relation
                .lower()
                .replace(
                    "_",
                    " "
                )
                .split()
            )

            found_words = 0

            for word in raw_words:

                if (
                    len(word) > 2
                    and
                    word in evidence_lower
                ):

                    found_words += 1


            if found_words > 0:

                score += 0.10

                reasons.append(
                    "Relation supported by evidence text"
                )


        # =====================================================
        # POSTPROCESSING VALIDATION
        # =====================================================

        if relation.get(
            "postprocessed"
        ):

            score += 0.05

            reasons.append(
                "Relationship postprocessed"
            )


        # =====================================================
        # STRUCTURED DATA BONUS
        # =====================================================

        if (
            method
            and
            "column" in method.lower()
        ):

            score += 0.15

            reasons.append(
                "Relationship extracted from structured columns"
            )


        # =====================================================
        # EVIDENCE QUALITY
        # =====================================================

        if len(evidence) >= 15:

            score += 0.05

            reasons.append(
                "Supporting evidence available"
            )


        # =====================================================
        # SPECIAL ENTITY FORMAT VALIDATION
        # =====================================================

        if relationship == "TRANSFERRED_TO":

            account_pattern = (
                r'\b(?:ACC|HDFC|ICICI|SBI|AXIS)'
                r'[A-Z0-9]+\b'
            )

            if (
                re.fullmatch(
                    account_pattern,
                    source,
                    re.IGNORECASE
                )
                and
                re.fullmatch(
                    account_pattern,
                    target,
                    re.IGNORECASE
                )
            ):

                score += 0.05

                reasons.append(
                    "Valid account-to-account transfer"
                )


        elif relationship == "USED_VEHICLE":

            vehicle_pattern = (
                r'[A-Z]{2}\d{1,2}'
                r'[A-Z]{1,3}\d{4}'
            )

            if re.fullmatch(
                vehicle_pattern,
                target,
                re.IGNORECASE
            ):

                score += 0.05

                reasons.append(
                    "Valid vehicle format"
                )


        elif relationship == "USES_PHONE":

            if re.fullmatch(
                r'[6-9]\d{9}',
                target
            ):

                score += 0.05

                reasons.append(
                    "Valid phone format"
                )


        # =====================================================
        # NORMALIZE SCORE
        # =====================================================

        score = min(
            score,
            1.0
        )

        score = round(
            score,
            2
        )


        # =====================================================
        # DECISION
        # =====================================================

        if score >= 0.85:

            decision = "ACCEPT"

        elif score >= 0.60:

            decision = "REVIEW"

        else:

            decision = "REJECT"


        # =====================================================
        # UNKNOWN DYNAMIC RELATION SAFETY
        # =====================================================

        if (
            relation_status == "REVIEW"
            and
            decision == "ACCEPT"
        ):

            decision = "REVIEW"

            reasons.append(
                "New dynamic relation requires review"
            )


        # =====================================================
        # PROVENANCE
        # =====================================================

        provenance = {

            "source_file":
                source_file,

            "evidence":
                evidence,

            "method":
                method
        }


        # =====================================================
        # FINAL OBJECT
        # =====================================================

        updated = relation.copy()


        updated[
            "validation_confidence"
        ] = score


        updated[
            "validation_decision"
        ] = decision


        updated[
            "validation_reasons"
        ] = reasons


        updated[
            "provenance"
        ] = provenance


        validated.append(
            updated
        )


    return validated