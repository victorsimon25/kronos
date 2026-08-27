from gliner2 import GLiNER2
import re

from relation_normalizer import normalize_relation


# Load model once
model = GLiNER2.from_pretrained(
    "fastino/gliner2-base-v1"
)


RELATION_SCHEMA = [
    "MET",
    "CALLED",
    "CONTACTED",
    "USES_PHONE",
    "USED_VEHICLE",
    "USES_ACCOUNT",
    "TRANSFERRED_TO",
    "ASSOCIATED_WITH",
    "LOCATED_AT",
    "WORKS_FOR"
]


def extract_gliner2_relationships(
    text,
    source_file="manual_input"
):

    schema = model.create_schema().relations(
        RELATION_SCHEMA
    )

    result = model.extract(
        text,
        schema
    )

    relations = []

    relation_data = result.get(
        "relation_extraction",
        {}
    )

    for relation_type, pairs in relation_data.items():

        for pair in pairs:

            source = None
            target = None
            confidence = 0.85

            # Tuple format
            if isinstance(pair, tuple):

                if len(pair) >= 2:
                    source = pair[0]
                    target = pair[1]

                if len(pair) >= 3:
                    try:
                        confidence = float(pair[2])
                    except:
                        confidence = 0.85

            # Dictionary format
            elif isinstance(pair, dict):

                head = pair.get("head", {})
                tail = pair.get("tail", {})

                if isinstance(head, dict):
                    source = head.get("text")

                    head_conf = head.get(
                        "confidence",
                        0.85
                    )

                else:
                    source = head
                    head_conf = 0.85

                if isinstance(tail, dict):
                    target = tail.get("text")

                    tail_conf = tail.get(
                        "confidence",
                        0.85
                    )

                else:
                    target = tail
                    tail_conf = 0.85

                confidence = (
                    float(head_conf)
                    +
                    float(tail_conf)
                ) / 2

            else:
                continue


            if not source or not target:
                continue


            # Normalize relationship
            normalized = normalize_relation(
                relation_type
            )


            evidence = find_evidence_sentence(
                text,
                source,
                target
            )


            timestamp = extract_timestamp(
                evidence
            )


            relations.append({
                "source_entity": str(source),

                "relationship":
                    normalized["relationship"],

                "target_entity": str(target),

                "timestamp": timestamp,

                "confidence": round(
                    confidence,
                    2
                ),

                "source_file": source_file,

                "evidence": evidence,

                "method": "GLiNER2",

                "relation_status":
                    normalized["status"]
            })

    return relations


def find_evidence_sentence(
    text,
    source,
    target
):

    sentences = re.split(
        r'(?<=[.!?])\s+',
        text
    )

    source_lower = str(
        source
    ).lower()

    target_lower = str(
        target
    ).lower()

    for sentence in sentences:

        sentence_lower = (
            sentence.lower()
        )

        if (
            source_lower
            in sentence_lower

            and

            target_lower
            in sentence_lower
        ):

            return sentence.strip()

    return ""


def extract_timestamp(text):

    if not text:
        return None

    patterns = [

        # 10 August 2026
        r'\b\d{1,2}\s+'
        r'(?:January|February|March|April|May|June|July|August|September|October|November|December)'
        r'\s+\d{4}\b',

        # 2026-08-10
        r'\b\d{4}-\d{2}-\d{2}\b',

        # 10/08/2026
        r'\b\d{1,2}/\d{1,2}/\d{4}\b'
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:
            return match.group(0)

    return None


def validate_relation_with_rules(
    relation,
    text
):

    relation_type = (
        relation.get(
            "relationship",
            ""
        )
    )

    evidence = (
        relation.get(
            "evidence",
            ""
        )
        or ""
    ).lower()

    rule_score = 0.0


    if relation_type == "MET":

        if re.search(
            r'\bmet\b|\bmeet\b|\bencountered\b',
            evidence
        ):
            rule_score += 0.20


    elif relation_type == "CALLED":

        if re.search(
            r'\bcalled\b|\bcall\b|\btelephoned\b',
            evidence
        ):
            rule_score += 0.20


    elif relation_type == "CONTACTED":

        if re.search(
            r'\bcontacted\b|\bcommunicated\b|\bmessaged\b',
            evidence
        ):
            rule_score += 0.20


    elif relation_type == "USES_PHONE":

        if re.search(
            r'\bused\b.*\bmobile\b'
            r'|\bphone\b'
            r'|\bmobile number\b',
            evidence
        ):
            rule_score += 0.20


    elif relation_type == "USED_VEHICLE":

        if re.search(
            r'\bused\b.*\bvehicle\b'
            r'|\bdrove\b'
            r'|\bvehicle\b',
            evidence
        ):
            rule_score += 0.20


    elif relation_type == "USES_ACCOUNT":

        if re.search(
            r'\baccount\b'
            r'|\bbank account\b',
            evidence
        ):
            rule_score += 0.20


    elif relation_type == "TRANSFERRED_TO":

        if re.search(
            r'\btransferred\b'
            r'|\btransfer\b'
            r'|\bsent money\b'
            r'|\bpayment\b',
            evidence
        ):
            rule_score += 0.20


    elif relation_type == "ASSOCIATED_WITH":

        if re.search(
            r'\bassociated with\b'
            r'|\bconnected with\b'
            r'|\blinked to\b',
            evidence
        ):
            rule_score += 0.20


    elif relation_type == "LOCATED_AT":

        if re.search(
            r'\bnear\b'
            r'|\bat\b'
            r'|\blocated\b'
            r'|\bseen\b'
            r'|\bobserved\b',
            evidence
        ):
            rule_score += 0.20


    elif relation_type == "WORKS_FOR":

        if re.search(
            r'\bworks for\b'
            r'|\bemployed by\b'
            r'|\bemployee of\b',
            evidence
        ):
            rule_score += 0.20


    return rule_score


def calculate_final_confidence(
    relation,
    rule_score
):

    model_score = float(
        relation.get(
            "confidence",
            0.85
        )
    )

    final_score = (
        model_score * 0.8
        +
        rule_score
    )

    return min(
        round(
            final_score,
            2
        ),
        1.0
    )


def classify_relation(
    confidence
):

    if confidence >= 0.85:
        return "ACCEPT"

    elif confidence >= 0.60:
        return "REVIEW"

    else:
        return "REJECT"


def extract_hybrid_relationships(
    text,
    source_file="manual_input"
):

    gliner_relations = (
        extract_gliner2_relationships(
            text,
            source_file
        )
    )

    final_relations = []

    seen = set()


    for relation in gliner_relations:

        rule_score = (
            validate_relation_with_rules(
                relation,
                text
            )
        )


        final_confidence = (
            calculate_final_confidence(
                relation,
                rule_score
            )
        )


        decision = classify_relation(
            final_confidence
        )


        source = str(
            relation.get(
                "source_entity",
                ""
            )
        )

        target = str(
            relation.get(
                "target_entity",
                ""
            )
        )


        key = (
            source.lower(),
            relation.get(
                "relationship",
                ""
            ),
            target.lower()
        )


        if key in seen:
            continue


        seen.add(key)


        relation[
            "confidence"
        ] = final_confidence


        relation[
            "decision"
        ] = decision


        relation[
            "rule_support"
        ] = round(
            rule_score,
            2
        )


        final_relations.append(
            relation
        )


    return final_relations