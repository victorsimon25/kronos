import json
import os


REGISTRY_FILE = "relation_registry.json"


def load_registry():

    if not os.path.exists(
        REGISTRY_FILE
    ):
        return {}

    try:

        with open(
            REGISTRY_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(
                file
            )

    except:

        return {}


def save_registry(
    registry
):

    with open(
        REGISTRY_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            registry,
            file,
            indent=4,
            ensure_ascii=False
        )


def approve_relation(
    raw_relation,
    normalized_relation
):

    registry = load_registry()

    key = (
        str(
            raw_relation
        )
        .strip()
        .lower()
    )

    if not key:
        return False

    registry[
        key
    ] = normalized_relation

    save_registry(
        registry
    )

    return True


def reject_relation(
    raw_relation
):

    return True