import json
import os


REGISTRY_FILE = "relation_registry.json"


def load_registry():
    if not os.path.exists(REGISTRY_FILE):
        return {}

    with open(REGISTRY_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_registry(registry):
    with open(REGISTRY_FILE, "w", encoding="utf-8") as file:
        json.dump(
            registry,
            file,
            indent=4,
            ensure_ascii=False
        )


def normalize_relation(raw_relation):

    registry = load_registry()

    raw = raw_relation.lower().strip()

    if raw in registry:
        return {
            "relationship": registry[raw],
            "status": "KNOWN"
        }

    candidate = (
        raw
        .upper()
        .replace(" ", "_")
    )

    return {
        "relationship": candidate,
        "status": "REVIEW"
    }


def approve_relation(raw_relation):

    registry = load_registry()

    raw = raw_relation.lower().strip()

    normalized = (
        raw
        .upper()
        .replace(" ", "_")
    )

    registry[raw] = normalized

    save_registry(registry)

    return normalized