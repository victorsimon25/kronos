import streamlit as st
import pandas as pd

from parser import parse_file
from extractor import extract_entities, structure_entities
from entity_resolution import resolve_person_entities

from relationship_extractor import (
    extract_relationships_from_dataframe
)

from hybrid_relationship_extractor import (
    extract_hybrid_relationships
)


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

st.subheader("Investigation Data Input")

input_type = st.radio(
    "Choose input method",
    ["Enter Text", "Upload File"],
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

On 12 June 2026, Ravi Kumar contacted Arjun
using mobile 9876543210 near Chennai.

Ravi Kumar used vehicle TN01AB1234.
"""
    )

    if st.button("Analyze Investigation"):

        if not text.strip():

            st.warning(
                "Please enter investigation text."
            )

        else:

            # =====================================================
            # ENTITY EXTRACTION
            # =====================================================

            with st.spinner(
                "KRONOS is extracting entities..."
            ):

                entities = extract_entities(
                    text
                )

            if not entities:

                st.warning(
                    "No entities detected."
                )

            else:

                st.success(
                    "Entity extraction completed."
                )

                entity_data = []

                for entity in entities:

                    entity_data.append({
                        "Entity": entity["text"],
                        "Type": entity["label"],
                        "Confidence": round(
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
                    use_container_width=True
                )


                # =================================================
                # STRUCTURED ENTITY DATA
                # =================================================

                structured_data = (
                    structure_entities(
                        entities
                    )
                )

                st.subheader(
                    "Structured Investigation Data"
                )

                st.json(
                    structured_data
                )


                # =================================================
                # HYBRID RELATIONSHIP EXTRACTION
                # =================================================

                st.subheader(
                    "Relationship Extraction"
                )

                with st.spinner(
                    "KRONOS is analyzing relationships..."
                ):

                    relationships = (
                        extract_hybrid_relationships(
                            text,
                            source_file="manual_input"
                        )
                    )

                if relationships:

                    relationship_df = (
                        pd.DataFrame(
                            relationships
                        )
                    )

                    st.dataframe(
                        relationship_df,
                        use_container_width=True
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
                        structured_data["persons"],
                        structured_data["aliases"]
                    )
                )

                if matches:

                    match_df = pd.DataFrame(
                        matches
                    )

                    st.dataframe(
                        match_df,
                        use_container_width=True
                    )

                else:

                    st.info(
                        "No possible duplicate identities detected."
                    )


# =========================================================
# FILE UPLOAD
# =========================================================

elif input_type == "Upload File":

    uploaded_file = st.file_uploader(
        "Upload Investigation File",
        type=[
            "pdf",
            "csv",
            "xlsx",
            "txt",
            "json"
        ]
    )

    if uploaded_file:

        st.success(
            "File uploaded successfully."
        )

        st.write(
            "File Name:",
            uploaded_file.name
        )

        st.write(
            "File Size:",
            round(
                uploaded_file.size / 1024,
                2
            ),
            "KB"
        )

        if st.button("Analyze File"):

            # =====================================================
            # PARSING
            # =====================================================

            with st.spinner(
                "Reading investigation data..."
            ):

                parsed_file = parse_file(
                    uploaded_file
                )

            extracted_text = (
                parsed_file.get(
                    "text",
                    ""
                )
            )

            if not extracted_text.strip():

                st.error(
                    "Unable to extract readable data."
                )

            else:

                st.subheader(
                    "Parsed File Content"
                )

                st.text_area(
                    "Content",
                    extracted_text,
                    height=250
                )


                # =================================================
                # STRUCTURED FILE
                # CSV / XLSX / JSON
                # =================================================

                if (
                    parsed_file["file_type"]
                    == "structured"
                ):

                    st.success(
                        "Structured file parsed directly."
                    )

                    structured_data = (
                        parsed_file[
                            "structured"
                        ]
                    )

                    st.subheader(
                        "Structured Investigation Data"
                    )

                    st.json(
                        structured_data
                    )


                    # =============================================
                    # STRUCTURED RELATIONSHIP EXTRACTION
                    # =============================================

                    st.subheader(
                        "Relationship Extraction"
                    )

                    relationships = []

                    if (
                        "dataframe"
                        in parsed_file
                    ):

                        relationships = (
                            extract_relationships_from_dataframe(
                                parsed_file[
                                    "dataframe"
                                ],
                                source_file=uploaded_file.name
                            )
                        )

                    else:

                        # JSON does not have a dataframe.
                        # Use hybrid extraction on serialized JSON text.

                        with st.spinner(
                            "KRONOS is analyzing relationships..."
                        ):

                            relationships = (
                                extract_hybrid_relationships(
                                    extracted_text,
                                    source_file=uploaded_file.name
                                )
                            )

                    if relationships:

                        relationship_df = (
                            pd.DataFrame(
                                relationships
                            )
                        )

                        st.dataframe(
                            relationship_df,
                            use_container_width=True
                        )

                    else:

                        st.info(
                            "No relationships detected."
                        )


                    # =============================================
                    # ENTITY RESOLUTION
                    # =============================================

                    st.subheader(
                        "Entity Resolution"
                    )

                    matches = (
                        resolve_person_entities(
                            structured_data[
                                "persons"
                            ],
                            structured_data[
                                "aliases"
                            ]
                        )
                    )

                    if matches:

                        match_df = (
                            pd.DataFrame(
                                matches
                            )
                        )

                        st.dataframe(
                            match_df,
                            use_container_width=True
                        )

                    else:

                        st.info(
                            "No possible duplicate identities detected."
                        )


                # =================================================
                # UNSTRUCTURED FILE
                # PDF / TXT
                # =================================================

                else:

                    # =============================================
                    # ENTITY EXTRACTION
                    # =============================================

                    with st.spinner(
                        "KRONOS is extracting entities..."
                    ):

                        entities = (
                            extract_entities(
                                extracted_text
                            )
                        )

                    if not entities:

                        st.warning(
                            "No entities detected."
                        )

                    else:

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

                                "Confidence":
                                    round(
                                        entity[
                                            "score"
                                        ],
                                        2
                                    )
                            })

                        entity_df = (
                            pd.DataFrame(
                                entity_data
                            )
                        )

                        st.subheader(
                            "Extracted Entities"
                        )

                        st.dataframe(
                            entity_df,
                            use_container_width=True
                        )


                        # =========================================
                        # STRUCTURED ENTITIES
                        # =========================================

                        structured_data = (
                            structure_entities(
                                entities
                            )
                        )

                        st.subheader(
                            "Structured Investigation Data"
                        )

                        st.json(
                            structured_data
                        )


                        # =========================================
                        # HYBRID RELATIONSHIP EXTRACTION
                        # =========================================

                        st.subheader(
                            "Relationship Extraction"
                        )

                        with st.spinner(
                            "KRONOS is analyzing relationships..."
                        ):

                            relationships = (
                                extract_hybrid_relationships(
                                    extracted_text,
                                    source_file=uploaded_file.name
                                )
                            )

                        if relationships:

                            relationship_df = (
                                pd.DataFrame(
                                    relationships
                                )
                            )

                            st.dataframe(
                                relationship_df,
                                use_container_width=True
                            )

                        else:

                            st.info(
                                "No relationships detected."
                            )


                        # =========================================
                        # ENTITY RESOLUTION
                        # =========================================

                        st.subheader(
                            "Entity Resolution"
                        )

                        matches = (
                            resolve_person_entities(
                                structured_data[
                                    "persons"
                                ],
                                structured_data[
                                    "aliases"
                                ]
                            )
                        )

                        if matches:

                            match_df = (
                                pd.DataFrame(
                                    matches
                                )
                            )

                            st.dataframe(
                                match_df,
                                use_container_width=True
                            )

                        else:

                            st.info(
                                "No possible duplicate identities detected."
                            )