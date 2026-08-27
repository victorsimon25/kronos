from gliner import GLiNER
import re

model = GLiNER.from_pretrained("urchade/gliner_medium-v2.1")

labels = [
    "person",
    "alias",
    "phone number",
    "location",
    "vehicle number",
    "bank account",
    "organization",
    "date",
    "transaction amount",
    "incident",
    "FIR number"
]


def extract_entities(text):

    entities = model.predict_entities(
        text,
        labels,
        threshold=0.3
    )

    results = []

    for entity in entities:
        results.append({
            "text": entity["text"],
            "label": entity["label"],
            "score": entity["score"]
        })

    phones = re.findall(r'\b[6-9]\d{9}\b', text)

    for phone in phones:
        results.append({
            "text": phone,
            "label": "phone number",
            "score": 1.0
        })

    vehicles = re.findall(
        r'\b[A-Z]{2}\d{1,2}[A-Z]{1,3}\d{4}\b',
        text
    )

    for vehicle in vehicles:
        results.append({
            "text": vehicle,
            "label": "vehicle number",
            "score": 1.0
        })

    fir_numbers = re.findall(
        r'\bFIR[\/\-A-Z0-9]+\b',
        text,
        re.IGNORECASE
    )

    for fir in fir_numbers:
        results.append({
            "text": fir,
            "label": "FIR number",
            "score": 1.0
        })

    accounts = re.findall(
        r'\b(?:ACC|HDFC|ICICI|SBI|AXIS)[A-Z0-9]+\b',
        text
    )

    for account in accounts:
        results.append({
            "text": account,
            "label": "bank account",
            "score": 1.0
        })

    return remove_duplicates(results)


def remove_duplicates(entities):

    unique = []
    seen = set()

    for entity in entities:

        key = (
            entity["text"].lower(),
            entity["label"].lower()
        )

        if key not in seen:
            seen.add(key)
            unique.append(entity)

    return unique


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

    mapping = {
        "person": "persons",
        "alias": "aliases",
        "phone number": "phones",
        "location": "locations",
        "vehicle number": "vehicles",
        "bank account": "accounts",
        "organization": "organizations",
        "date": "dates",
        "transaction amount": "amounts",
        "incident": "incidents",
        "FIR number": "fir_numbers"
    }

    for entity in entities:

        label = entity["label"]

        if label in mapping:

            key = mapping[label]

            if entity["text"] not in structured[key]:
                structured[key].append(entity["text"])

    return structured