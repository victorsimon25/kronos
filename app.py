import streamlit as st
import pandas as pd

from graph_ready_formatter import (
    build_graph_ready_json
)

from parser import parse_file

from extractor import (
    extract_entities,
    structure_entities
)

from entity_resolution import (
    resolve_person_entities
)

from relationship_extractor import (
    extract_relationships_from_dataframe
)

from dynamic_relationship_extractor import (
    extract_dynamic_relationships
)

from relationship_postprocessor import (
    postprocess_relationships
)

from relationship_validator import (
    validate_relationships
)


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="KRONOS",
    page_icon="🕸️",
    layout="wide"
)


st.title("KRONOS")

st.caption(
    "Knowledge-driven Real-time Network Operations & Intelligence System"
)

st.markdown("---")


# =========================================================
# HELPER
# =========================================================

def empty_structure():

    return {
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


# =========================================================
# INPUT METHOD
# =========================================================

st.subheader(
    "Investigation Data Input"
)


input_type = st.radio(
    "Choose input method",
    [
        "Enter Text",
        "Upload File"
    ],
    horizontal=True
)


# =========================================================
# MANUAL TEXT INPUT
# =========================================================

if input_type == "Enter Text":

    text = st.text_area(
        "Enter Investigation Text",
        height=250,
        placeholder="""
Example:

On 24 August 2026, Arjun rented a warehouse from Bala in Guindy, Chennai.

Bala delivered three sealed boxes to Arjun.

Arjun shared an office with Kiran.

Kiran introduced Bala to Naveen.

Naveen used vehicle TN11CD7788.

Rohit transferred Rs. 62,000 from account ACC310 to account ACC920.
"""
    )


    if st.button(
        "Analyze Investigation"
    ):

        if not text.strip():

            st.warning(
                "Please enter investigation text."
            )

        else:

            # =================================================
            # ENTITY EXTRACTION
            # =================================================

            with st.spinner(
                "KRONOS is extracting entities..."
            ):

                entities = extract_entities(
                    text
                )


            if entities:

                st.success(
                    "Entity extraction completed."
                )


                entity_data = []


                for entity in entities:

                    entity_data.append({

                        "Entity":
                            entity["text"],

                        "Type":
                            entity["label"],

                        "Entity Confidence":
                            round(
                                entity["score"],
                                2
                            )
                    })


                entity_df = pd.DataFrame(
                    entity_data
                )


                st.subheader(
                    "Extracted Entities"
                )


                st.dataframe(
                    entity_df,
                    width="stretch"
                )


                structured_data = (
                    structure_entities(
                        entities
                    )
                )

            else:

                st.warning(
                    "No entities detected."
                )

                structured_data = (
                    empty_structure()
                )


            # =================================================
            # STRUCTURED DATA
            # =================================================

            st.subheader(
                "Structured Investigation Data"
            )


            st.json(
                structured_data
            )


            # =================================================
            # RELATIONSHIP EXTRACTION
            # =================================================

            st.subheader(
                "Relationship Extraction"
            )


            with st.spinner(
                "KRONOS is analyzing relationships..."
            ):

                relationships = (
                    extract_dynamic_relationships(
                        text,
                        source_file=
                            "manual_input"
                    )
                )


                # =============================================
                # POSTPROCESS
                # =============================================

                relationships = (
                    postprocess_relationships(
                        relationships,
                        text,
                        structured_data.get(
                            "persons",
                            []
                        )
                    )
                )


                # =============================================
                # VALIDATE
                # =============================================

                relationships = (
                    validate_relationships(
                        relationships
                    )
                )


            # =================================================
            # SHOW RELATIONSHIPS
            # =================================================

            if relationships:

                relationship_df = (
                    pd.DataFrame(
                        relationships
                    )
                )


                st.dataframe(
                    relationship_df,
                    width="stretch"
                )


                # =============================================
                # VALIDATION SUMMARY
                # =============================================

                accepted = [
                    r
                    for r in relationships
                    if r.get(
                        "validation_decision"
                    ) == "ACCEPT"
                ]


                review = [
                    r
                    for r in relationships
                    if r.get(
                        "validation_decision"
                    ) == "REVIEW"
                ]


                rejected = [
                    r
                    for r in relationships
                    if r.get(
                        "validation_decision"
                    ) == "REJECT"
                ]


                col1, col2, col3 = (
                    st.columns(3)
                )


                col1.metric(
                    "Accepted",
                    len(accepted)
                )

                col2.metric(
                    "Needs Review",
                    len(review)
                )

                col3.metric(
                    "Rejected",
                    len(rejected)
                )

            else:

                st.info(
                    "No relationships detected."
                )


            # =================================================
            # ENTITY RESOLUTION
            # =================================================

            st.subheader(
                "Entity Resolution"
            )


            matches = (
                resolve_person_entities(
                    structured_data.get(
                        "persons",
                        []
                    ),
                    structured_data.get(
                        "aliases",
                        []
                    )
                )
            )


            if matches:

                match_df = pd.DataFrame(
                    matches
                )


                st.dataframe(
                    match_df,
                    width="stretch"
                )

            else:

                st.info(
                    "No possible duplicate identities detected."
                )


            # =================================================
            # GRAPH READY JSON
            # =================================================

            st.markdown("---")

            st.subheader(
                "Graph-Ready KRONOS JSON"
            )


            graph_ready_data = (
                build_graph_ready_json(
                    structured_data,
                    relationships
                )
            )


            st.json(
                graph_ready_data
            )


# =========================================================
# MULTI FILE UPLOAD
# =========================================================

elif input_type == "Upload File":

    uploaded_files = (
        st.file_uploader(
            "Upload Investigation Files",

            type=[
                "pdf",
                "csv",
                "xlsx",
                "txt",
                "json"
            ],

            accept_multiple_files=True
        )
    )


    if uploaded_files:

        st.success(
            f"{len(uploaded_files)} file(s) uploaded successfully."
        )


        st.subheader(
            "Uploaded Files"
        )


        for uploaded_file in uploaded_files:

            st.write(
                f"{uploaded_file.name} - "
                f"{round(uploaded_file.size / 1024, 2)} KB"
            )


        if st.button(
            "Analyze Files"
        ):

            all_relationships = []

            all_structured_data = []

            all_entities = []


            # =================================================
            # PROCESS FILES
            # =================================================

            for uploaded_file in uploaded_files:

                st.markdown("---")


                st.subheader(
                    f"Processing: {uploaded_file.name}"
                )


                # =============================================
                # PARSE FILE
                # =============================================

                with st.spinner(
                    f"Reading {uploaded_file.name}..."
                ):

                    try:

                        parsed_file = (
                            parse_file(
                                uploaded_file
                            )
                        )

                    except Exception as error:

                        st.error(
                            f"Error reading "
                            f"{uploaded_file.name}: "
                            f"{error}"
                        )

                        continue


                extracted_text = (
                    parsed_file.get(
                        "text",
                        ""
                    )
                )


                if not extracted_text.strip():

                    st.warning(
                        f"Unable to extract readable content "
                        f"from {uploaded_file.name}"
                    )

                    continue


                # =============================================
                # DISPLAY PARSED CONTENT
                # =============================================

                st.text_area(
                    f"Parsed Content - {uploaded_file.name}",
                    extracted_text,
                    height=180,
                    key=
                        f"content_{uploaded_file.name}"
                )


                relationships = []

                structured_data = (
                    empty_structure()
                )


                # =================================================
                # STRUCTURED FILE
                # =================================================

                if (
                    parsed_file.get(
                        "file_type"
                    )
                    == "structured"
                ):

                    structured_data = (
                        parsed_file.get(
                            "structured",
                            empty_structure()
                        )
                    )


                    # =============================================
                    # CSV / XLSX
                    # =============================================

                    if (
                        "dataframe"
                        in parsed_file
                    ):

                        dataframe = (
                            parsed_file[
                                "dataframe"
                            ]
                        )


                        st.subheader(
                            f"Table Preview - "
                            f"{uploaded_file.name}"
                        )


                        st.dataframe(
                            dataframe,
                            width="stretch"
                        )


                        # -----------------------------------------
                        # OPTIONAL ENTITY EXTRACTION FROM
                        # SERIALIZED STRUCTURED TEXT
                        # -----------------------------------------

                        entities = (
                            extract_entities(
                                extracted_text
                            )
                        )


                        if entities:

                            extracted_structure = (
                                structure_entities(
                                    entities
                                )
                            )


                            for key in structured_data:

                                if (
                                    key
                                    in extracted_structure
                                ):

                                    existing = (
                                        structured_data.get(
                                            key,
                                            []
                                        )
                                    )

                                    new_values = (
                                        extracted_structure.get(
                                            key,
                                            []
                                        )
                                    )

                                    structured_data[
                                        key
                                    ] = list(
                                        dict.fromkeys(
                                            existing
                                            + new_values
                                        )
                                    )


                            entity_data = []

                            for entity in entities:

                                entity_data.append({

                                    "File":
                                        uploaded_file.name,

                                    "Entity":
                                        entity["text"],

                                    "Type":
                                        entity["label"],

                                    "Entity Confidence":
                                        round(
                                            entity[
                                                "score"
                                            ],
                                            2
                                        )
                                })


                            all_entities.extend(
                                entity_data
                            )


                            st.subheader(
                                f"Extracted Entities - "
                                f"{uploaded_file.name}"
                            )


                            st.dataframe(
                                pd.DataFrame(
                                    entity_data
                                ),
                                width="stretch"
                            )


                        # -----------------------------------------
                        # STRUCTURED RELATIONSHIPS
                        # -----------------------------------------

                        relationships = (
                            extract_relationships_from_dataframe(
                                dataframe,
                                source_file=
                                    uploaded_file.name
                            )
                        )


                        relationships = (
                            postprocess_relationships(
                                relationships,
                                extracted_text,
                                structured_data.get(
                                    "persons",
                                    []
                                )
                            )
                        )


                        relationships = (
                            validate_relationships(
                                relationships
                            )
                        )


                    # =============================================
                    # JSON
                    # =============================================

                    else:

                        entities = (
                            extract_entities(
                                extracted_text
                            )
                        )


                        if entities:

                            structured_data = (
                                structure_entities(
                                    entities
                                )
                            )


                            entity_data = []

                            for entity in entities:

                                entity_data.append({

                                    "File":
                                        uploaded_file.name,

                                    "Entity":
                                        entity["text"],

                                    "Type":
                                        entity["label"],

                                    "Entity Confidence":
                                        round(
                                            entity[
                                                "score"
                                            ],
                                            2
                                        )
                                })


                            all_entities.extend(
                                entity_data
                            )


                            st.subheader(
                                f"Extracted Entities - "
                                f"{uploaded_file.name}"
                            )


                            st.dataframe(
                                pd.DataFrame(
                                    entity_data
                                ),
                                width="stretch"
                            )


                        with st.spinner(
                            f"Extracting relationships from "
                            f"{uploaded_file.name}..."
                        ):

                            relationships = (
                                extract_dynamic_relationships(
                                    extracted_text,
                                    source_file=
                                        uploaded_file.name
                                )
                            )


                            relationships = (
                                postprocess_relationships(
                                    relationships,
                                    extracted_text,
                                    structured_data.get(
                                        "persons",
                                        []
                                    )
                                )
                            )


                            relationships = (
                                validate_relationships(
                                    relationships
                                )
                            )


                # =================================================
                # PDF / TXT
                # =================================================

                else:

                    # =============================================
                    # ENTITY EXTRACTION
                    # =============================================

                    with st.spinner(
                        f"Extracting entities from "
                        f"{uploaded_file.name}..."
                    ):

                        entities = (
                            extract_entities(
                                extracted_text
                            )
                        )


                    if entities:

                        structured_data = (
                            structure_entities(
                                entities
                            )
                        )


                        entity_data = []


                        for entity in entities:

                            entity_data.append({

                                "File":
                                    uploaded_file.name,

                                "Entity":
                                    entity["text"],

                                "Type":
                                    entity["label"],

                                "Entity Confidence":
                                    round(
                                        entity[
                                            "score"
                                        ],
                                        2
                                    )
                            })


                        all_entities.extend(
                            entity_data
                        )


                        st.subheader(
                            f"Extracted Entities - "
                            f"{uploaded_file.name}"
                        )


                        st.dataframe(
                            pd.DataFrame(
                                entity_data
                            ),
                            width="stretch"
                        )

                    else:

                        structured_data = (
                            empty_structure()
                        )


                        st.info(
                            f"No entities detected in "
                            f"{uploaded_file.name}"
                        )


                    # =============================================
                    # DYNAMIC RELATIONSHIPS
                    # =============================================

                    with st.spinner(
                        f"Extracting relationships from "
                        f"{uploaded_file.name}..."
                    ):

                        relationships = (
                            extract_dynamic_relationships(
                                extracted_text,
                                source_file=
                                    uploaded_file.name
                            )
                        )


                        relationships = (
                            postprocess_relationships(
                                relationships,
                                extracted_text,
                                structured_data.get(
                                    "persons",
                                    []
                                )
                            )
                        )


                        relationships = (
                            validate_relationships(
                                relationships
                            )
                        )


                # =================================================
                # STORE STRUCTURED DATA
                # =================================================

                all_structured_data.append({

                    "file_name":
                        uploaded_file.name,

                    "data":
                        structured_data
                })


                # =================================================
                # DISPLAY STRUCTURED DATA
                # =================================================

                st.subheader(
                    f"Structured Data - "
                    f"{uploaded_file.name}"
                )


                st.json(
                    structured_data
                )


                # =================================================
                # DISPLAY RELATIONSHIPS
                # =================================================

                if relationships:

                    st.subheader(
                        f"Relationships - "
                        f"{uploaded_file.name}"
                    )


                    st.dataframe(
                        pd.DataFrame(
                            relationships
                        ),
                        width="stretch"
                    )


                    all_relationships.extend(
                        relationships
                    )

                else:

                    st.info(
                        f"No relationships detected in "
                        f"{uploaded_file.name}"
                    )


            # =====================================================
            # COMBINED RESULTS
            # =====================================================

            st.markdown("---")

            st.header(
                "Combined Investigation Results"
            )


            # =====================================================
            # COMBINED ENTITIES
            # =====================================================

            if all_entities:

                st.subheader(
                    "Combined Extracted Entities"
                )


                st.dataframe(
                    pd.DataFrame(
                        all_entities
                    ),
                    width="stretch"
                )


            # =====================================================
            # COMBINED STRUCTURED DATA
            # =====================================================

            st.subheader(
                "Combined Structured Data"
            )


            st.json(
                all_structured_data
            )


            # =====================================================
            # REMOVE DUPLICATE RELATIONSHIPS
            # =====================================================

            unique_relationships = []

            seen_relationships = set()


            for relationship in all_relationships:

                key = (

                    str(
                        relationship.get(
                            "source_entity",
                            ""
                        )
                    ).lower(),

                    relationship.get(
                        "relationship",
                        ""
                    ),

                    str(
                        relationship.get(
                            "target_entity",
                            ""
                        )
                    ).lower(),

                    relationship.get(
                        "source_file",
                        ""
                    )
                )


                if key in seen_relationships:
                    continue


                seen_relationships.add(
                    key
                )


                unique_relationships.append(
                    relationship
                )


            all_relationships = (
                unique_relationships
            )


            # =====================================================
            # COMBINED RELATIONSHIPS
            # =====================================================

            st.subheader(
                "Combined Relationships"
            )


            if all_relationships:

                st.dataframe(
                    pd.DataFrame(
                        all_relationships
                    ),
                    width="stretch"
                )


                # =============================================
                # VALIDATION SUMMARY
                # =============================================

                accepted = [
                    r
                    for r in all_relationships
                    if r.get(
                        "validation_decision"
                    ) == "ACCEPT"
                ]


                review = [
                    r
                    for r in all_relationships
                    if r.get(
                        "validation_decision"
                    ) == "REVIEW"
                ]


                rejected = [
                    r
                    for r in all_relationships
                    if r.get(
                        "validation_decision"
                    ) == "REJECT"
                ]


                col1, col2, col3 = (
                    st.columns(3)
                )


                col1.metric(
                    "Accepted Relationships",
                    len(accepted)
                )

                col2.metric(
                    "Needs Review",
                    len(review)
                )

                col3.metric(
                    "Rejected Relationships",
                    len(rejected)
                )

            else:

                st.info(
                    "No relationships detected "
                    "across uploaded files."
                )


            # =====================================================
            # CROSS FILE ENTITY RESOLUTION
            # =====================================================

            st.subheader(
                "Cross-File Entity Resolution"
            )


            combined_persons = []

            combined_aliases = []


            for item in all_structured_data:

                data = item.get(
                    "data",
                    {}
                )


                combined_persons.extend(
                    data.get(
                        "persons",
                        []
                    )
                )


                combined_aliases.extend(
                    data.get(
                        "aliases",
                        []
                    )
                )


            combined_persons = list(
                dict.fromkeys(
                    combined_persons
                )
            )


            combined_aliases = list(
                dict.fromkeys(
                    combined_aliases
                )
            )


            matches = (
                resolve_person_entities(
                    combined_persons,
                    combined_aliases
                )
            )


            if matches:

                st.dataframe(
                    pd.DataFrame(
                        matches
                    ),
                    width="stretch"
                )

            else:

                st.info(
                    "No possible duplicate identities "
                    "detected across uploaded files."
                )


            # =====================================================
            # GRAPH READY KRONOS JSON
            # =====================================================

            st.markdown("---")

            st.header(
                "Graph-Ready KRONOS JSON"
            )


            graph_ready_data = (
                build_graph_ready_json(
                    all_structured_data,
                    all_relationships
                )
            )


            st.json(
                graph_ready_data
            )