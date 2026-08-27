import streamlit as st
import pandas as pd

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

from graph_ready_formatter import (
    build_graph_ready_json
)

from review_manager import (
    approve_relation,
    reject_relation
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
# SESSION STATE INITIALIZATION
# =========================================================

SESSION_DEFAULTS = {
    "manual_relationships": [],
    "manual_structured_data": None,
    "manual_entity_rows": [],
    "manual_text_saved": "",
    "manual_analyzed": False,
    "file_results": [],
    "files_analyzed": False,
}

for key, value in SESSION_DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# EMPTY STRUCTURE
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
# MERGE STRUCTURED DATA
# =========================================================

def merge_structured_data(base, new_data):
    if not base:
        base = empty_structure()

    if not new_data:
        return base

    for key in base:
        current_values = base.get(key, [])
        new_values = new_data.get(key, [])

        if not isinstance(current_values, list):
            current_values = []

        if not isinstance(new_values, list):
            new_values = []

        base[key] = list(
            dict.fromkeys(
                current_values + new_values
            )
        )

    return base


# =========================================================
# ENTITY EXTRACTION
# =========================================================

def run_entity_extraction(text, source_file=None):
    entities = extract_entities(text)

    if not entities:
        return (
            [],
            empty_structure(),
            []
        )

    structured_data = structure_entities(
        entities
    )

    rows = []

    for entity in entities:
        row = {
            "Entity": entity["text"],
            "Type": entity["label"],
            "Entity Confidence": round(
                entity["score"],
                2
            )
        }

        if source_file:
            row["File"] = source_file

        rows.append(row)

    return (
        entities,
        structured_data,
        rows
    )


# =========================================================
# DYNAMIC RELATIONSHIP PIPELINE
# =========================================================

def run_dynamic_relationship_pipeline(
    text,
    source_file,
    structured_data
):
    relationships = extract_dynamic_relationships(
        text,
        source_file=source_file
    )

    relationships = postprocess_relationships(
        relationships,
        text,
        structured_data.get(
            "persons",
            []
        )
    )

    relationships = validate_relationships(
        relationships
    )

    return relationships


# =========================================================
# STRUCTURED RELATIONSHIP PIPELINE
# =========================================================

def run_structured_relationship_pipeline(
    dataframe,
    text,
    source_file,
    structured_data
):
    relationships = extract_relationships_from_dataframe(
        dataframe,
        source_file=source_file
    )

    relationships = postprocess_relationships(
        relationships,
        text,
        structured_data.get(
            "persons",
            []
        )
    )

    relationships = validate_relationships(
        relationships
    )

    return relationships


# =========================================================
# VALIDATION SUMMARY
# =========================================================

def show_validation_summary(relationships):
    accepted = sum(
        1
        for relation in relationships
        if relation.get(
            "validation_decision"
        ) == "ACCEPT"
    )

    review = sum(
        1
        for relation in relationships
        if relation.get(
            "validation_decision"
        ) == "REVIEW"
    )

    rejected = sum(
        1
        for relation in relationships
        if relation.get(
            "validation_decision"
        ) == "REJECT"
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Accepted",
        accepted
    )

    col2.metric(
        "Needs Review",
        review
    )

    col3.metric(
        "Rejected",
        rejected
    )


# =========================================================
# RELATION MATCH HELPER
# =========================================================

def relation_matches(item, relation):
    return (
        str(
            item.get(
                "source_entity",
                ""
            )
        ).strip().lower()
        ==
        str(
            relation.get(
                "source_entity",
                ""
            )
        ).strip().lower()

        and

        str(
            item.get(
                "relationship",
                ""
            )
        ).strip().upper()
        ==
        str(
            relation.get(
                "relationship",
                ""
            )
        ).strip().upper()

        and

        str(
            item.get(
                "target_entity",
                ""
            )
        ).strip().lower()
        ==
        str(
            relation.get(
                "target_entity",
                ""
            )
        ).strip().lower()

        and

        str(
            item.get(
                "source_file",
                ""
            )
        ).strip().lower()
        ==
        str(
            relation.get(
                "source_file",
                ""
            )
        ).strip().lower()
    )


# =========================================================
# HUMAN / INVESTIGATOR REVIEW UI
# =========================================================

def show_human_review(
    relationships,
    key_prefix,
    session_key=None,
    file_index=None
):
    if not relationships:
        return relationships

    st.subheader(
        "Investigator Review"
    )

    st.caption(
        "Review extracted relationships before they are included "
        "in the final graph-ready output."
    )

    for index, relation in enumerate(
        relationships
    ):
        source = relation.get(
            "source_entity",
            ""
        )

        target = relation.get(
            "target_entity",
            ""
        )

        relationship = relation.get(
            "relationship",
            ""
        )

        raw_relation = relation.get(
            "raw_relation",
            relationship
        )

        evidence = relation.get(
            "evidence",
            ""
        )

        confidence = relation.get(
            "validation_confidence",
            0
        )

        decision = relation.get(
            "validation_decision",
            "REVIEW"
        )

        relation_status = relation.get(
            "relation_status",
            "REVIEW"
        )

        title = (
            f"{source} → {relationship} → {target}"
        )

        with st.expander(title):
            if decision == "ACCEPT":
                st.success(
                    "Current status: ACCEPTED"
                )

            elif decision == "REVIEW":
                st.warning(
                    "Current status: NEEDS REVIEW"
                )

            else:
                st.error(
                    f"Current status: {decision}"
                )

            col_a, col_b = st.columns(2)

            with col_a:
                st.write(
                    f"**Source:** {source}"
                )

                st.write(
                    f"**Relationship:** {relationship}"
                )

                st.write(
                    f"**Target:** {target}"
                )

            with col_b:
                st.write(
                    f"**Validation Confidence:** {confidence}"
                )

                st.write(
                    f"**Relation Status:** {relation_status}"
                )

                st.write(
                    f"**Decision:** {decision}"
                )

            st.write(
                "**Supporting Evidence:**"
            )

            st.info(
                evidence
                if evidence
                else "No evidence available."
            )

            col1, col2 = st.columns(2)

            relation_key = (
                f"{key_prefix}_{index}_"
                f"{source}_{relationship}_{target}"
            )

            approve_key = (
                f"approve_{relation_key}"
            )

            reject_key = (
                f"reject_{relation_key}"
            )

            # =================================================
            # APPROVE
            # =================================================

            if col1.button(
                "✅ Approve",
                key=approve_key,
                disabled=(
                    decision == "ACCEPT"
                )
            ):
                approve_relation(
                    raw_relation,
                    relationship
                )

                updated_relationships = []

                for item in relationships:
                    if relation_matches(
                        item,
                        relation
                    ):
                        updated_item = dict(item)

                        updated_item[
                            "relation_status"
                        ] = "KNOWN"

                        updated_item[
                            "validation_decision"
                        ] = "ACCEPT"

                        updated_item[
                            "decision"
                        ] = "ACCEPT"

                        updated_relationships.append(
                            updated_item
                        )

                    else:
                        updated_relationships.append(
                            item
                        )

                if session_key == "manual":
                    st.session_state[
                        "manual_relationships"
                    ] = updated_relationships

                elif (
                    session_key == "file"
                    and file_index is not None
                ):
                    st.session_state[
                        "file_results"
                    ][file_index][
                        "relationships"
                    ] = updated_relationships

                st.rerun()

            # =================================================
            # REJECT
            # =================================================

            if col2.button(
                "❌ Reject",
                key=reject_key
            ):
                reject_relation(
                    raw_relation
                )

                updated_relationships = [
                    item
                    for item in relationships
                    if not relation_matches(
                        item,
                        relation
                    )
                ]

                if session_key == "manual":
                    st.session_state[
                        "manual_relationships"
                    ] = updated_relationships

                elif (
                    session_key == "file"
                    and file_index is not None
                ):
                    st.session_state[
                        "file_results"
                    ][file_index][
                        "relationships"
                    ] = updated_relationships

                st.rerun()

    return relationships


# =========================================================
# RELATIONSHIP TABLE
# =========================================================

def show_relationships(
    relationships,
    title,
    key_prefix,
    session_key=None,
    file_index=None,
    allow_review=True
):
    st.subheader(
        title
    )

    if not relationships:
        st.info(
            "No relationships detected."
        )

        return relationships

    important_columns = [
        "source_entity",
        "relationship",
        "target_entity",
        "timestamp",
        "amount",
        "validation_confidence",
        "validation_decision",
        "source_file",
        "evidence"
    ]

    relationship_df = pd.DataFrame(
        relationships
    )

    visible_columns = [
        column
        for column in important_columns
        if column in relationship_df.columns
    ]

    if visible_columns:
        relationship_df = relationship_df[
            visible_columns
        ]

    st.dataframe(
        relationship_df,
        width="stretch"
    )

    show_validation_summary(
        relationships
    )

    if allow_review:
        relationships = show_human_review(
            relationships,
            key_prefix,
            session_key=session_key,
            file_index=file_index
        )

    return relationships


# =========================================================
# ENTITY RESOLUTION
# =========================================================

def show_entity_resolution(
    structured_data,
    title="Entity Resolution"
):
    st.subheader(
        title
    )

    matches = resolve_person_entities(
        structured_data.get(
            "persons",
            []
        ),
        structured_data.get(
            "aliases",
            []
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
            "No possible duplicate identities detected."
        )


# =========================================================
# REMOVE RELATIONSHIP DUPLICATES
# =========================================================

def remove_relationship_duplicates(
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
            ).strip().lower(),

            str(
                relation.get(
                    "relationship",
                    ""
                )
            ).strip().upper(),

            str(
                relation.get(
                    "target_entity",
                    ""
                )
            ).strip().lower(),

            str(
                relation.get(
                    "source_file",
                    ""
                )
            ).strip().lower()
        )

        if key in seen:
            continue

        seen.add(key)
        result.append(relation)

    return result


# =========================================================
# RESET HELPERS
# =========================================================

def reset_manual_state():
    st.session_state[
        "manual_relationships"
    ] = []

    st.session_state[
        "manual_structured_data"
    ] = None

    st.session_state[
        "manual_entity_rows"
    ] = []

    st.session_state[
        "manual_text_saved"
    ] = ""

    st.session_state[
        "manual_analyzed"
    ] = False


def reset_file_state():
    st.session_state[
        "file_results"
    ] = []

    st.session_state[
        "files_analyzed"
    ] = False


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
# MANUAL TEXT
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

    button_col1, button_col2 = st.columns(
        [1, 1]
    )

    analyze_manual = button_col1.button(
        "Analyze Investigation"
    )

    if button_col2.button(
        "Clear Results"
    ):
        reset_manual_state()
        st.rerun()

    # =====================================================
    # ANALYZE
    # =====================================================

    if analyze_manual:
        if not text.strip():
            st.warning(
                "Please enter investigation text."
            )

        else:
            with st.spinner(
                "Extracting entities..."
            ):
                (
                    entities,
                    structured_data,
                    entity_rows
                ) = run_entity_extraction(
                    text
                )

            st.session_state[
                "manual_structured_data"
            ] = structured_data

            st.session_state[
                "manual_entity_rows"
            ] = entity_rows

            st.session_state[
                "manual_text_saved"
            ] = text

            with st.spinner(
                "NuExtract is discovering relationships..."
            ):
                try:
                    relationships = (
                        run_dynamic_relationship_pipeline(
                            text,
                            "manual_input",
                            structured_data
                        )
                    )

                except Exception as error:
                    st.error(
                        f"Relationship extraction failed: "
                        f"{error}"
                    )

                    relationships = []

            st.session_state[
                "manual_relationships"
            ] = relationships

            st.session_state[
                "manual_analyzed"
            ] = True

    # =====================================================
    # DISPLAY SAVED MANUAL RESULTS
    # =====================================================

    if st.session_state.get(
        "manual_analyzed",
        False
    ):
        structured_data = (
            st.session_state.get(
                "manual_structured_data"
            )
            or
            empty_structure()
        )

        entity_rows = st.session_state.get(
            "manual_entity_rows",
            []
        )

        relationships = st.session_state.get(
            "manual_relationships",
            []
        )

        st.subheader(
            "Extracted Entities"
        )

        if entity_rows:
            st.success(
                f"{len(entity_rows)} entities extracted."
            )

            st.dataframe(
                pd.DataFrame(
                    entity_rows
                ),
                width="stretch"
            )

        else:
            st.warning(
                "No entities detected."
            )

        st.subheader(
            "Structured Investigation Data"
        )

        st.json(
            structured_data
        )

        relationships = show_relationships(
            relationships,
            "Relationship Extraction",
            "manual",
            session_key="manual",
            allow_review=True
        )

        st.session_state[
            "manual_relationships"
        ] = relationships

        show_entity_resolution(
            structured_data
        )

        st.markdown("---")

        st.header(
            "Graph-Ready KRONOS JSON"
        )

        latest_relationships = (
            st.session_state.get(
                "manual_relationships",
                []
            )
        )

        graph_ready_data = (
            build_graph_ready_json(
                structured_data,
                latest_relationships
            )
        )

        st.json(
            graph_ready_data
        )


# =========================================================
# FILE UPLOAD
# =========================================================

elif input_type == "Upload File":

    uploaded_files = st.file_uploader(
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

    if uploaded_files:
        st.success(
            f"{len(uploaded_files)} file(s) uploaded."
        )

        for uploaded_file in uploaded_files:
            st.write(
                f"{uploaded_file.name} — "
                f"{round(uploaded_file.size / 1024, 2)} KB"
            )

        button_col1, button_col2 = st.columns(
            [1, 1]
        )

        analyze_files = button_col1.button(
            "Analyze Files"
        )

        if button_col2.button(
            "Clear File Results"
        ):
            reset_file_state()
            st.rerun()

        # =====================================================
        # ANALYZE FILES
        # =====================================================

        if analyze_files:
            file_results = []

            for file_index, uploaded_file in enumerate(
                uploaded_files
            ):
                try:
                    with st.spinner(
                        f"Reading {uploaded_file.name}..."
                    ):
                        parsed_file = parse_file(
                            uploaded_file
                        )

                except Exception as error:
                    st.error(
                        f"Unable to read "
                        f"{uploaded_file.name}: "
                        f"{error}"
                    )

                    continue

                extracted_text = parsed_file.get(
                    "text",
                    ""
                )

                if not extracted_text.strip():
                    st.warning(
                        f"No readable content found in "
                        f"{uploaded_file.name}"
                    )

                    continue

                file_type = parsed_file.get(
                    "file_type",
                    "unstructured"
                )

                with st.spinner(
                    f"Extracting entities from "
                    f"{uploaded_file.name}..."
                ):
                    (
                        entities,
                        extracted_structure,
                        entity_rows
                    ) = run_entity_extraction(
                        extracted_text,
                        uploaded_file.name
                    )

                structured_data = (
                    extracted_structure
                )

                dataframe = None

                if (
                    file_type == "structured"
                    and
                    "dataframe" in parsed_file
                ):
                    dataframe = parsed_file[
                        "dataframe"
                    ]

                    parsed_structure = (
                        parsed_file.get(
                            "structured",
                            empty_structure()
                        )
                    )

                    structured_data = (
                        merge_structured_data(
                            parsed_structure,
                            extracted_structure
                        )
                    )

                    try:
                        with st.spinner(
                            f"Extracting structured relationships "
                            f"from {uploaded_file.name}..."
                        ):
                            relationships = (
                                run_structured_relationship_pipeline(
                                    dataframe,
                                    extracted_text,
                                    uploaded_file.name,
                                    structured_data
                                )
                            )

                    except Exception as error:
                        st.error(
                            f"Relationship extraction failed "
                            f"for {uploaded_file.name}: "
                            f"{error}"
                        )

                        relationships = []

                else:
                    try:
                        with st.spinner(
                            f"NuExtract is discovering relationships "
                            f"in {uploaded_file.name}..."
                        ):
                            relationships = (
                                run_dynamic_relationship_pipeline(
                                    extracted_text,
                                    uploaded_file.name,
                                    structured_data
                                )
                            )

                    except Exception as error:
                        st.error(
                            f"Relationship extraction failed "
                            f"for {uploaded_file.name}: "
                            f"{error}"
                        )

                        relationships = []

                file_results.append({
                    "file_name":
                        uploaded_file.name,

                    "file_type":
                        file_type,

                    "text":
                        extracted_text,

                    "dataframe":
                        dataframe,

                    "structured_data":
                        structured_data,

                    "entity_rows":
                        entity_rows,

                    "relationships":
                        relationships
                })

            st.session_state[
                "file_results"
            ] = file_results

            st.session_state[
                "files_analyzed"
            ] = True

    # =====================================================
    # DISPLAY SAVED FILE RESULTS
    # =====================================================

    if st.session_state.get(
        "files_analyzed",
        False
    ):
        file_results = st.session_state.get(
            "file_results",
            []
        )

        for file_index, result in enumerate(
            file_results
        ):
            st.markdown("---")

            file_name = result.get(
                "file_name",
                "unknown"
            )

            st.header(
                file_name
            )

            extracted_text = result.get(
                "text",
                ""
            )

            structured_data = result.get(
                "structured_data",
                empty_structure()
            )

            entity_rows = result.get(
                "entity_rows",
                []
            )

            relationships = result.get(
                "relationships",
                []
            )

            dataframe = result.get(
                "dataframe"
            )

            with st.expander(
                "View Parsed Content"
            ):
                st.text(
                    extracted_text
                )

            if dataframe is not None:
                st.subheader(
                    "Table Preview"
                )

                st.dataframe(
                    dataframe,
                    width="stretch"
                )

            st.subheader(
                "Extracted Entities"
            )

            if entity_rows:
                st.success(
                    f"{len(entity_rows)} entities extracted."
                )

                st.dataframe(
                    pd.DataFrame(
                        entity_rows
                    ),
                    width="stretch"
                )

            else:
                st.info(
                    "No entities detected."
                )

            st.subheader(
                "Structured Investigation Data"
            )

            st.json(
                structured_data
            )

            relationships = show_relationships(
                relationships,
                "Extracted Relationships",
                f"file_{file_index}",
                session_key="file",
                file_index=file_index,
                allow_review=True
            )

            st.session_state[
                "file_results"
            ][file_index][
                "relationships"
            ] = relationships

            show_entity_resolution(
                structured_data,
                "Entity Resolution"
            )

            st.subheader(
                "Graph-Ready KRONOS JSON"
            )

            latest_relationships = (
                st.session_state[
                    "file_results"
                ][file_index].get(
                    "relationships",
                    []
                )
            )

            graph_ready_file = (
                build_graph_ready_json(
                    structured_data,
                    latest_relationships
                )
            )

            st.json(
                graph_ready_file
            )

        # =================================================
        # COMBINED RESULTS
        # ONLY FOR 2 OR MORE FILES
        # =================================================

        if len(file_results) > 1:
            all_structured_data = []
            all_relationships = []
            all_entity_rows = []

            current_file_results = (
                st.session_state.get(
                    "file_results",
                    []
                )
            )

            for result in current_file_results:
                file_name = result.get(
                    "file_name",
                    "unknown"
                )

                structured_data = result.get(
                    "structured_data",
                    empty_structure()
                )

                relationships = result.get(
                    "relationships",
                    []
                )

                entity_rows = result.get(
                    "entity_rows",
                    []
                )

                all_structured_data.append({
                    "file_name":
                        file_name,

                    "data":
                        structured_data
                })

                all_relationships.extend(
                    relationships
                )

                all_entity_rows.extend(
                    entity_rows
                )

            all_relationships = (
                remove_relationship_duplicates(
                    all_relationships
                )
            )

            st.markdown("---")

            st.header(
                "Combined Investigation Results"
            )

            if all_entity_rows:
                st.subheader(
                    "Combined Extracted Entities"
                )

                st.dataframe(
                    pd.DataFrame(
                        all_entity_rows
                    ),
                    width="stretch"
                )

            else:
                st.info(
                    "No entities extracted across uploaded files."
                )

            show_relationships(
                all_relationships,
                "Combined Relationships",
                "combined",
                allow_review=False
            )

            combined_structure = (
                empty_structure()
            )

            for item in all_structured_data:
                combined_structure = (
                    merge_structured_data(
                        combined_structure,
                        item.get(
                            "data",
                            {}
                        )
                    )
                )

            show_entity_resolution(
                combined_structure,
                "Cross-File Entity Resolution"
            )

            st.markdown("---")

            st.header(
                "Combined Graph-Ready KRONOS JSON"
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
