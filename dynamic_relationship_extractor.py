import json
import re
import torch

from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig
)

from relation_normalizer import normalize_relation


# =========================================================
# MODEL CONFIGURATION
# =========================================================

MODEL_NAME = "numind/NuExtract-1.5"


# =========================================================
# GPU INFORMATION
# =========================================================

print("=" * 60)
print("KRONOS Dynamic Relationship Model")
print("=" * 60)

print(
    "CUDA available:",
    torch.cuda.is_available()
)

if torch.cuda.is_available():

    print(
        "GPU:",
        torch.cuda.get_device_name(0)
    )

    total_vram = (
        torch.cuda.get_device_properties(
            0
        ).total_memory
        / 1024**3
    )

    print(
        "GPU VRAM:",
        round(total_vram, 2),
        "GB"
    )

else:

    print(
        "GPU: CPU mode"
    )


# =========================================================
# TOKENIZER
# =========================================================

print(
    "Loading tokenizer..."
)

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME,
    trust_remote_code=True
)


# =========================================================
# 4-BIT QUANTIZATION
# =========================================================

print(
    "Configuring 4-bit quantization..."
)

quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True
)


# =========================================================
# MODEL LOADING
# =========================================================

print(
    "Loading NuExtract model..."
)

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    trust_remote_code=True,
    quantization_config=quantization_config,
    device_map="auto",
    low_cpu_mem_usage=True,
    attn_implementation="eager"
)

model.eval()


print(
    "Model device:",
    model.device
)

print(
    "NuExtract model loaded successfully."
)

print("=" * 60)


# =========================================================
# EXTRACTION TEMPLATE
# =========================================================

TEMPLATE = {
    "relationships": [
        {
            "source_entity": "verbatim-string",
            "relation": "string",
            "target_entity": "verbatim-string",
            "evidence": "verbatim-string"
        }
    ]
}


# =========================================================
# MAIN EXTRACTION FUNCTION
# =========================================================

def extract_dynamic_relationships(
    text,
    source_file="manual_input"
):

    if not text:
        return []

    if not text.strip():
        return []

    # =====================================================
    # BUILD PROMPT
    # =====================================================

    prompt = build_prompt(
        text
    )


    # =====================================================
    # TOKENIZE
    # =====================================================

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=2048
    )


    # =====================================================
    # MOVE INPUT TO MODEL DEVICE
    # =====================================================

    inputs = {
        key: value.to(
            model.device
        )
        for key, value
        in inputs.items()
    }


    input_length = (
        inputs[
            "input_ids"
        ].shape[1]
    )


    print(
        "\nKRONOS: Starting relationship extraction..."
    )

    print(
        "Input tokens:",
        input_length
    )


    # =====================================================
    # GENERATE
    # =====================================================

    with torch.inference_mode():

        outputs = model.generate(
            **inputs,

            max_new_tokens=700,

            do_sample=False,

            use_cache=True,

            pad_token_id=
                tokenizer.eos_token_id,

            eos_token_id=
                tokenizer.eos_token_id
        )


    # =====================================================
    # DECODE ONLY GENERATED TOKENS
    # =====================================================

    generated_tokens = outputs[0][
        input_length:
    ]


    generated = tokenizer.decode(
        generated_tokens,
        skip_special_tokens=True,
        clean_up_tokenization_spaces=False
    )


    print(
        "\n===== NuExtract RAW OUTPUT ====="
    )

    print(
        generated
    )

    print(
        "================================\n"
    )


    # =====================================================
    # PARSE OUTPUT
    # =====================================================

    data = parse_json_output(
        generated
    )


    relationships = data.get(
        "relationships",
        []
    )


    if not isinstance(
        relationships,
        list
    ):

        print(
            "Invalid relationship output format."
        )

        return []


    final_relationships = []

    seen = set()


    # =====================================================
    # PROCESS EACH RELATIONSHIP
    # =====================================================

    for relation in relationships:

        if not isinstance(
            relation,
            dict
        ):
            continue


        source = clean_value(
            relation.get(
                "source_entity"
            )
        )


        raw_relation = clean_value(
            relation.get(
                "relation"
            )
        )


        target = clean_value(
            relation.get(
                "target_entity"
            )
        )


        evidence = clean_value(
            relation.get(
                "evidence"
            )
        )


        # =================================================
        # BASIC VALIDATION
        # =================================================

        if not source:
            continue

        if not raw_relation:
            continue

        if not target:
            continue


        # =================================================
        # VERIFY SOURCE ENTITY EXISTS
        # =================================================

        if (
            source.lower()
            not in text.lower()
        ):

            print(
                "Rejected source not found:",
                source
            )

            continue


        # =================================================
        # VERIFY TARGET
        # =================================================

        # Some targets may be concepts such as:
        # "motorcycle"
        # so do not reject aggressively

        if (
            target.lower()
            not in text.lower()
        ):

            print(
                "Target not found exactly:",
                target
            )


        # =================================================
        # NORMALIZE RELATION
        # =================================================

        normalized = normalize_relation(
            raw_relation
        )


        relationship = (
            normalized[
                "relationship"
            ]
        )


        relation_status = (
            normalized[
                "status"
            ]
        )


        # =================================================
        # EVIDENCE FALLBACK
        # =================================================

        if not evidence:

            evidence = find_sentence(
                text,
                source,
                target
            )


        # =================================================
        # TIMESTAMP
        # =================================================

        timestamp = extract_timestamp(
            evidence
        )


        if timestamp is None:

            supporting_sentence = (
                find_sentence(
                    text,
                    source,
                    target
                )
            )

            timestamp = (
                extract_timestamp(
                    supporting_sentence
                )
            )


        # =================================================
        # CONFIDENCE
        # =================================================

        confidence = (
            calculate_confidence(
                source,
                target,
                evidence,
                text
            )
        )


        # =================================================
        # DECISION
        # =================================================

        decision = classify_relation(
            confidence,
            relation_status
        )


        # =================================================
        # DUPLICATE CHECK
        # =================================================

        key = (
            source.lower(),
            relationship,
            target.lower()
        )


        if key in seen:
            continue


        seen.add(
            key
        )


        # =================================================
        # FINAL RELATIONSHIP OBJECT
        # =================================================

        final_relationships.append({

            "source_entity":
                source,

            "raw_relation":
                raw_relation,

            "relationship":
                relationship,

            "target_entity":
                target,

            "timestamp":
                timestamp,

            "confidence":
                confidence,

            "source_file":
                source_file,

            "evidence":
                evidence,

            "relation_status":
                relation_status,

            "decision":
                decision,

            "method":
                "NuExtract-1.5-4bit"
        })


    print(
        "KRONOS extracted",
        len(final_relationships),
        "relationships."
    )


    return final_relationships


# =========================================================
# NUEXTRACT PROMPT
# =========================================================

def build_prompt(
    text
):

    template_string = json.dumps(
        TEMPLATE,
        indent=4,
        ensure_ascii=False
    )


    prompt = (
        "<|input|>\n"
        "### Template:\n"
        f"{template_string}\n"
        "### Text:\n"
        f"{text}\n\n"
        "<|output|>"
    )


    return prompt


# =========================================================
# CLEAN VALUES
# =========================================================

def clean_value(
    value
):

    if value is None:
        return ""

    return str(
        value
    ).strip()


# =========================================================
# JSON PARSER
# =========================================================

def parse_json_output(
    output
):

    if not output:

        return {
            "relationships": []
        }


    cleaned = (
        output
        .replace(
            "```json",
            ""
        )
        .replace(
            "```JSON",
            ""
        )
        .replace(
            "```",
            ""
        )
        .strip()
    )


    # =====================================================
    # ATTEMPT 1:
    # VALID COMPLETE JSON
    # =====================================================

    try:

        data = json.loads(
            cleaned
        )


        # -----------------------------------------
        # {
        #   "relationships": [...]
        # }
        # -----------------------------------------

        if isinstance(
            data,
            dict
        ):

            if (
                "relationships"
                in data
            ):

                return data


        # -----------------------------------------
        # [
        #   {...},
        #   {...}
        # ]
        # -----------------------------------------

        if isinstance(
            data,
            list
        ):

            return {
                "relationships":
                    data
            }


    except json.JSONDecodeError:

        pass


    # =====================================================
    # ATTEMPT 2:
    # FIND COMPLETE JSON ARRAY
    # =====================================================

    array_start = cleaned.find(
        "["
    )

    array_end = cleaned.rfind(
        "]"
    )


    if (
        array_start != -1
        and
        array_end != -1
        and
        array_end > array_start
    ):

        try:

            array_text = cleaned[
                array_start:
                array_end + 1
            ]


            array_data = json.loads(
                array_text
            )


            if isinstance(
                array_data,
                list
            ):

                return {
                    "relationships":
                        array_data
                }


        except json.JSONDecodeError:

            pass


    # =====================================================
    # ATTEMPT 3:
    # RECOVER INDIVIDUAL COMPLETE OBJECTS
    # FROM PARTIAL OUTPUT
    # =====================================================

    relationships = []


    object_pattern = re.compile(

        r'\{\s*'

        r'"source_entity"\s*:\s*'
        r'"((?:\\.|[^"\\])*)"\s*,\s*'

        r'"relation"\s*:\s*'
        r'"((?:\\.|[^"\\])*)"\s*,\s*'

        r'"target_entity"\s*:\s*'
        r'"((?:\\.|[^"\\])*)"\s*,\s*'

        r'"evidence"\s*:\s*'
        r'"((?:\\.|[^"\\])*)"\s*'

        r'\}',

        re.DOTALL
    )


    matches = object_pattern.findall(
        cleaned
    )


    for match in matches:

        (
            source,
            relation,
            target,
            evidence
        ) = match


        relationships.append({

            "source_entity":
                decode_json_string(
                    source
                ),

            "relation":
                decode_json_string(
                    relation
                ),

            "target_entity":
                decode_json_string(
                    target
                ),

            "evidence":
                decode_json_string(
                    evidence
                )
        })


    print(
        "Recovered",
        len(relationships),
        "relationships from partial output."
    )


    return {
        "relationships":
            relationships
    }


# =========================================================
# DECODE JSON STRING
# =========================================================

def decode_json_string(
    value
):

    try:

        return json.loads(
            f'"{value}"'
        )

    except Exception:

        return value


# =========================================================
# FIND SUPPORTING SENTENCE
# =========================================================

def find_sentence(
    text,
    source,
    target
):

    if not text:
        return ""


    sentences = re.split(
        r'(?<=[.!?])\s+',
        text
    )


    source_lower = (
        source.lower()
    )


    target_lower = (
        target.lower()
    )


    # =====================================================
    # BOTH SOURCE AND TARGET
    # =====================================================

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


    # =====================================================
    # SOURCE ONLY FALLBACK
    # =====================================================

    for sentence in sentences:

        if (
            source_lower
            in sentence.lower()
        ):

            return sentence.strip()


    return ""


# =========================================================
# TIMESTAMP EXTRACTION
# =========================================================

def extract_timestamp(
    text
):

    if not text:

        return None


    patterns = [

        # 21 August 2026
        (
            r'\b\d{1,2}\s+'
            r'(?:January|February|March|April|'
            r'May|June|July|August|September|'
            r'October|November|December)'
            r'\s+\d{4}\b'
        ),

        # August 21, 2026
        (
            r'\b(?:January|February|March|April|'
            r'May|June|July|August|September|'
            r'October|November|December)'
            r'\s+\d{1,2},?\s+\d{4}\b'
        ),

        # 2026-08-21
        r'\b\d{4}-\d{2}-\d{2}\b',

        # 21/08/2026
        r'\b\d{1,2}/\d{1,2}/\d{4}\b',

        # 21-08-2026
        r'\b\d{1,2}-\d{1,2}-\d{4}\b'
    ]


    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )


        if match:

            return match.group(
                0
            )


    return None


# =========================================================
# CONFIDENCE
# =========================================================

def calculate_confidence(
    source,
    target,
    evidence,
    full_text
):

    score = 0.40


    source_lower = (
        source
        .lower()
        .strip()
    )


    target_lower = (
        target
        .lower()
        .strip()
    )


    evidence_lower = (
        evidence
        .lower()
        .strip()
    )


    full_text_lower = (
        full_text
        .lower()
        .strip()
    )


    # =====================================================
    # SOURCE IN DOCUMENT
    # =====================================================

    if (
        source_lower
        and
        source_lower
        in full_text_lower
    ):

        score += 0.15


    # =====================================================
    # TARGET IN DOCUMENT
    # =====================================================

    if (
        target_lower
        and
        target_lower
        in full_text_lower
    ):

        score += 0.15


    # =====================================================
    # SOURCE IN EVIDENCE
    # =====================================================

    if (
        source_lower
        and
        source_lower
        in evidence_lower
    ):

        score += 0.10


    # =====================================================
    # TARGET IN EVIDENCE
    # =====================================================

    if (
        target_lower
        and
        target_lower
        in evidence_lower
    ):

        score += 0.10


    # =====================================================
    # EVIDENCE ACTUALLY EXISTS
    # =====================================================

    if (
        evidence_lower
        and
        evidence_lower
        in full_text_lower
    ):

        score += 0.10


    return min(
        round(
            score,
            2
        ),
        1.0
    )


# =========================================================
# DECISION CLASSIFIER
# =========================================================

def classify_relation(
    confidence,
    relation_status
):

    # Newly discovered relation
    if (
        relation_status
        == "REVIEW"
    ):

        return "REVIEW"


    # Known relation
    if confidence >= 0.85:

        return "ACCEPT"


    if confidence >= 0.60:

        return "REVIEW"


    return "REJECT"