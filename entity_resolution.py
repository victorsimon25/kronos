from difflib import SequenceMatcher


def similarity(a, b):
    return SequenceMatcher(
        None,
        a.lower(),
        b.lower()
    ).ratio()


def resolve_person_entities(persons, aliases):

    all_names = persons + aliases
    matches = []

    for i in range(len(all_names)):

        for j in range(i + 1, len(all_names)):

            name1 = all_names[i]
            name2 = all_names[j]

            score = similarity(name1, name2)

            if score >= 0.6:

                matches.append({
                    "Entity 1": name1,
                    "Entity 2": name2,
                    "Similarity": round(score, 2),
                    "Possible Match": "Yes"
                })

    return matches