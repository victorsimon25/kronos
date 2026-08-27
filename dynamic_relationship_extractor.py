import json
import re
import torch

from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig
)

from transformers.cache_utils import DynamicCache

from relation_normalizer import (
    normalize_relation
)


# =========================================================
# CONFIG
# =========================================================

MODEL_NAME = "numind/NuExtract-1.5"


# =========================================================
# PHI / TRANSFORMERS CACHE COMPATIBILITY FIX
# =========================================================

# NuExtract-1.5 uses older Phi-3.5 remote model code.
# Older Phi code expects:
#
# past_key_values.seen_tokens
#
# New Transformers DynamicCache uses:
#
# past_key_values.get_seq_length()
#
# This compatibility property prevents:
#
# AttributeError:
# 'DynamicCache' object has no attribute 'seen_tokens'

if not hasattr(
    DynamicCache,
    "seen_tokens"
):

    DynamicCache.seen_tokens = property(
        lambda self:
            self.get_seq_length()
    )


# =========================================================
# DEVICE INFORMATION
# =========================================================

print("=" * 60)

print(
    "KRONOS Dynamic Relationship Model"
)

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

    gpu_memory = (
        torch.cuda.get_device_properties(
            0
        ).total_memory
        / 1024 ** 3
    )

    print(
        "GPU VRAM:",
        round(
            gpu_memory,
            2
        ),
        "GB"
    )

else:

    print(
        "WARNING: CUDA GPU not detected."
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
# PAD TOKEN SAFETY
# =========================================================

if tokenizer.pad_token_id is None:

    tokenizer.pad_token = (
        tokenizer.eos_token
    )


# =========================================================
# 4-BIT QUANTIZATION
# =========================================================

print(
    "Configuring 4-bit quantization..."
)


quantization_config = (
    BitsAndBytesConfig(

        load_in_4bit=True,

        bnb_4bit_quant_type=
            "nf4",

        bnb_4bit_compute_dtype=
            torch.float16,

        bnb_4bit_use_double_quant=
            True
    )
)


# =========================================================
# LOAD MODEL
# =========================================================

print(
    "Loading NuExtract model..."
)


model = (
    AutoModelForCausalLM.from_pretrained(

        MODEL_NAME,

        trust_remote_code=True,

        quantization_config=
            quantization_config,

        device_map="auto",

        low_cpu_mem_usage=True,

        attn_implementation=
            "eager"
    )
)


model.eval()


# =========================================================
# IMPORTANT CACHE FIX
# =========================================================

# Disable KV cache because old Phi remote code and modern
# Transformers DynamicCache are not fully compatible.

model.config.use_cache = False


if hasattr(
    model,
    "generation_config"
):

    model.generation_config.use_cache = (
        False
    )


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
            "source_entity":
                "verbatim-string",

            "relation":
                "string",

            "target_entity":
                "verbatim-string",

            "evidence":
                "verbatim-string"
        }
    ]
}


# =========================================================
# BUILD NUEXTRACT PROMPT
# =========================================================

def build_prompt(text):

    template_string = (
        json.dumps(
            TEMPLATE,
            indent=4,
            ensure_ascii=False
        )
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
# JSON STRING DECODER
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
# PARSE NUEXTRACT OUTPUT
# =========================================================

def parse_json_output(
    generated
):

    if not generated:

        return {
            "relationships": []
        }


    cleaned = (
        generated
        .strip()
    )


    # =====================================================
    # REMOVE MARKDOWN CODE FENCES
    # =====================================================

    cleaned = re.sub(
        r'^```(?:json)?',
        '',
        cleaned,
        flags=re.IGNORECASE
    )

    cleaned = re.sub(
        r'```$',
        '',
        cleaned
    )

    cleaned = (
        cleaned.strip()
    )


    # =====================================================
    # DIRECT JSON
    # =====================================================

    try:

        data = json.loads(
            cleaned
        )


        if isinstance(
            data,
            dict
        ):

            relationships = (
                data.get(
                    "relationships",
                    []
                )
            )


            if isinstance(
                relationships,
                list
            ):

                return {
                    "relationships":
                        relationships
                }


        if isinstance(
            data,
            list
        ):

            return {
                "relationships":
                    data
            }


    except Exception:

        pass


    # =====================================================
    # TRY JSON ARRAY
    # =====================================================

    array_start = (
        cleaned.find(
            "["
        )
    )

    array_end = (
        cleaned.rfind(
            "]"
        )
    )


    if (
        array_start != -1
        and
        array_end != -1
        and
        array_end > array_start
    ):

        possible_array = (
            cleaned[
                array_start:
                array_end + 1
            ]
        )


        try:

            data = json.loads(
                possible_array
            )


            if isinstance(
                data,
                list
            ):

                return {
                    "relationships":
                        data
                }


        except Exception:

            pass


    # =====================================================
    # TRY JSON OBJECT
    # =====================================================

    object_start = (
        cleaned.find(
            "{"
        )
    )

    object_end = (
        cleaned.rfind(
            "}"
        )
    )


    if (
        object_start != -1
        and
        object_end != -1
        and
        object_end > object_start
    ):

        possible_object = (
            cleaned[
                object_start:
                object_end + 1
            ]
        )


        try:

            data = json.loads(
                possible_object
            )


            if isinstance(
                data,
                dict
            ):

                relationships = (
                    data.get(
                        "relationships",
                        []
                    )
                )


                if isinstance(
                    relationships,
                    list
                ):

                    return {
                        "relationships":
                            relationships
                    }


        except Exception:

            pass


    # =====================================================
    # PARTIAL OUTPUT RECOVERY
    # =====================================================

    recovered = []


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


    matches = (
        object_pattern.findall(
            cleaned
        )
    )


    for match in matches:

        source = (
            decode_json_string(
                match[0]
            )
        )

        relation = (
            decode_json_string(
                match[1]
            )
        )

        target = (
            decode_json_string(
                match[2]
            )
        )

        evidence = (
            decode_json_string(
                match[3]
            )
        )


        recovered.append({

            "source_entity":
                source,

            "relation":
                relation,

            "target_entity":
                target,

            "evidence":
                evidence
        })


    return {

        "relationships":
            recovered
    }


# =========================================================
# FIND DATE INSIDE EVIDENCE
# =========================================================

def extract_timestamp(
    evidence
):

    if not evidence:

        return None


    # Example:
    # 24 August 2026

    date_match = re.search(

        r'\b'
        r'\d{1,2}\s+'
        r'(?:January|February|March|April|May|June|'
        r'July|August|September|October|November|December)'
        r'\s+\d{4}'
        r'\b',

        evidence,

        re.IGNORECASE
    )


    if date_match:

        return (
            date_match.group(
                0
            )
        )


    # Example:
    # 2026-08-24

    iso_match = re.search(

        r'\b'
        r'\d{4}-\d{2}-\d{2}'
        r'\b',

        evidence
    )


    if iso_match:

        return (
            iso_match.group(
                0
            )
        )


    # Example:
    # 24/08/2026

    slash_match = re.search(

        r'\b'
        r'\d{1,2}/'
        r'\d{1,2}/'
        r'\d{4}'
        r'\b',

        evidence
    )


    if slash_match:

        return (
            slash_match.group(
                0
            )
        )


    return None


# =========================================================
# RELATION CONFIDENCE
# =========================================================

def calculate_confidence(
    source,
    target,
    raw_relation,
    evidence,
    full_text
):

    score = 0.40


    source_lower = (
        str(source)
        .strip()
        .lower()
    )

    target_lower = (
        str(target)
        .strip()
        .lower()
    )

    relation_lower = (
        str(raw_relation)
        .strip()
        .lower()
    )

    evidence_lower = (
        str(evidence)
        .strip()
        .lower()
    )

    text_lower = (
        str(full_text)
        .strip()
        .lower()
    )


    if (
        source_lower
        and
        source_lower in text_lower
    ):

        score += 0.15


    if (
        target_lower
        and
        target_lower in text_lower
    ):

        score += 0.15


    if (
        source_lower
        and
        source_lower in evidence_lower
    ):

        score += 0.10


    if (
        target_lower
        and
        target_lower in evidence_lower
    ):

        score += 0.10


    relation_words = [

        word

        for word
        in re.findall(
            r'[a-zA-Z]+',
            relation_lower
        )

        if len(word) > 2
    ]


    if relation_words:

        matched_words = sum(

            1

            for word
            in relation_words

            if word
            in evidence_lower
        )


        if matched_words > 0:

            score += 0.05


    if (
        evidence_lower
        and
        evidence_lower in text_lower
    ):

        score += 0.05


    # This is a heuristic extraction score,
    # not a calibrated probability.

    return round(
        min(
            score,
            0.95
        ),
        2
    )


# =========================================================
# CHECK ENTITY IN ORIGINAL DOCUMENT
# =========================================================

def entity_exists_in_text(
    entity,
    text
):

    if not entity:

        return False


    return (
        str(entity)
        .strip()
        .lower()

        in

        str(text)
        .lower()
    )


# =========================================================
# NORMALIZE RELATION SAFELY
# =========================================================

def normalize_relationship(
    raw_relation
):

    try:

        result = normalize_relation(
            raw_relation
        )


        # Expected format:
        #
        # {
        #   "relationship": "...",
        #   "status": "KNOWN/REVIEW"
        # }

        if isinstance(
            result,
            dict
        ):

            relationship = (
                result.get(
                    "relationship"
                )
                or
                result.get(
                    "relation"
                )
                or
                str(
                    raw_relation
                )
                .upper()
                .replace(
                    " ",
                    "_"
                )
            )


            status = (
                result.get(
                    "status",
                    "REVIEW"
                )
            )


            return (
                relationship,
                status
            )


        # If normalizer returns only string

        if isinstance(
            result,
            str
        ):

            return (
                result,
                "KNOWN"
            )


    except Exception as error:

        print(
            "Relation normalization error:",
            error
        )


    relationship = (
        str(
            raw_relation
        )
        .strip()
        .upper()
        .replace(
            " ",
            "_"
        )
    )


    return (
        relationship,
        "REVIEW"
    )


# =========================================================
# REMOVE DUPLICATE RELATIONS
# =========================================================

def remove_duplicates(
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
            ).lower(),

            str(
                relation.get(
                    "relationship",
                    ""
                )
            ).upper(),

            str(
                relation.get(
                    "target_entity",
                    ""
                )
            ).lower(),

            str(
                relation.get(
                    "source_file",
                    ""
                )
            ).lower()
        )


        if key in seen:

            continue


        seen.add(
            key
        )


        result.append(
            relation
        )


    return result


# =========================================================
# MAIN DYNAMIC EXTRACTION FUNCTION
# =========================================================

def extract_dynamic_relationships(
    text,
    source_file="unknown"
):

    if not text:

        return []


    text = str(
        text
    ).strip()


    if not text:

        return []


    print()

    print(
        "KRONOS: Starting relationship extraction..."
    )


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


    inputs = {

        key:
            value.to(
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
        "Input tokens:",
        input_length
    )


    # =====================================================
    # GENERATE
    # =====================================================

    try:

        with torch.inference_mode():

            outputs = model.generate(

                **inputs,

                max_new_tokens=700,

                do_sample=False,

                # =================================================
                # IMPORTANT FIX
                # =================================================
                #
                # Disable DynamicCache.
                #
                # NuExtract remote Phi code expects old
                # past_key_values.seen_tokens.
                #
                # Modern Transformers removed that API.
                #

                use_cache=False,

                pad_token_id=
                    tokenizer.eos_token_id,

                eos_token_id=
                    tokenizer.eos_token_id
            )


    except AttributeError as error:

        # =====================================================
        # SECONDARY CACHE COMPATIBILITY FALLBACK
        # =====================================================

        if (
            "seen_tokens"
            in str(error)
        ):

            print(
                "KRONOS: DynamicCache compatibility issue detected."
            )

            print(
                "Retrying generation without cache..."
            )


            model.config.use_cache = (
                False
            )


            if hasattr(
                model,
                "generation_config"
            ):

                model.generation_config.use_cache = (
                    False
                )


            with torch.inference_mode():

                outputs = model.generate(

                    **inputs,

                    max_new_tokens=700,

                    do_sample=False,

                    use_cache=False,

                    pad_token_id=
                        tokenizer.eos_token_id,

                    eos_token_id=
                        tokenizer.eos_token_id
                )

        else:

            raise


    # =====================================================
    # DECODE ONLY GENERATED TOKENS
    # =====================================================

    generated_tokens = (

        outputs[0][
            input_length:
        ]
    )


    generated = tokenizer.decode(

        generated_tokens,

        skip_special_tokens=True,

        clean_up_tokenization_spaces=False
    )


    print(
        "KRONOS: Raw NuExtract output:"
    )

    print(
        generated
    )


    # =====================================================
    # PARSE OUTPUT
    # =====================================================

    parsed = parse_json_output(
        generated
    )


    raw_relationships = (
        parsed.get(
            "relationships",
            []
        )
    )


    print(
        "KRONOS: Parsed relationships:",
        len(
            raw_relationships
        )
    )


    # =====================================================
    # FINAL RELATIONSHIP OBJECTS
    # =====================================================

    final_relationships = []


    for item in raw_relationships:

        if not isinstance(
            item,
            dict
        ):

            continue


        source = (
            item.get(
                "source_entity"
            )
            or
            item.get(
                "source"
            )
            or
            ""
        )


        raw_relation = (
            item.get(
                "relation"
            )
            or
            item.get(
                "relationship"
            )
            or
            ""
        )


        target = (
            item.get(
                "target_entity"
            )
            or
            item.get(
                "target"
            )
            or
            ""
        )


        evidence = (
            item.get(
                "evidence"
            )
            or
            ""
        )


        source = str(
            source
        ).strip()

        target = str(
            target
        ).strip()

        raw_relation = str(
            raw_relation
        ).strip()

        evidence = str(
            evidence
        ).strip()


        # =================================================
        # MINIMUM VALIDITY
        # =================================================

        if not source:

            continue


        if not target:

            continue


        if not raw_relation:

            continue


        # =================================================
        # SOURCE MUST EXIST
        # =================================================

        if not entity_exists_in_text(
            source,
            text
        ):

            print(
                "Skipping hallucinated source:",
                source
            )

            continue


        # =================================================
        # TARGET WARNING
        # =================================================

        if not entity_exists_in_text(
            target,
            text
        ):

            print(
                "Warning: target not found exactly in text:",
                target
            )


        # =================================================
        # EVIDENCE FALLBACK
        # =================================================

        if not evidence:

            evidence = (
                find_best_evidence(
                    source,
                    target,
                    text
                )
            )


        # =================================================
        # NORMALIZE RELATION
        # =================================================

        (
            normalized_relation,
            relation_status
        ) = normalize_relationship(
            raw_relation
        )


        # =================================================
        # TIMESTAMP
        # =================================================

        # IMPORTANT:
        # Only use date found inside this evidence.
        #
        # Do not use first global document date.

        timestamp = (
            extract_timestamp(
                evidence
            )
        )


        # =================================================
        # CONFIDENCE
        # =================================================

        confidence = (
            calculate_confidence(

                source,

                target,

                raw_relation,

                evidence,

                text
            )
        )


        # =================================================
        # INITIAL DECISION
        # =================================================

        if relation_status == "KNOWN":

            decision = "ACCEPT"

        else:

            decision = "REVIEW"


        # =================================================
        # FINAL OBJECT
        # =================================================

        relationship_object = {

            "source_entity":
                source,

            "raw_relation":
                raw_relation,

            "relationship":
                normalized_relation,

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
        }


        final_relationships.append(
            relationship_object
        )


    # =====================================================
    # REMOVE DUPLICATES
    # =====================================================

    final_relationships = (
        remove_duplicates(
            final_relationships
        )
    )


    print(
        "KRONOS: Final relationships:",
        len(
            final_relationships
        )
    )


    return final_relationships


# =========================================================
# FIND BEST EVIDENCE
# =========================================================

def find_best_evidence(
    source,
    target,
    text
):

    sentences = re.split(

        r'(?<=[.!?])\s+',

        text
    )


    source_lower = (
        str(source)
        .lower()
    )

    target_lower = (
        str(target)
        .lower()
    )


    # =====================================================
    # BOTH SOURCE + TARGET
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

            return (
                sentence.strip()
            )


    # =====================================================
    # SOURCE ONLY
    # =====================================================

    for sentence in sentences:

        if (
            source_lower
            in sentence.lower()
        ):

            return (
                sentence.strip()
            )


    return ""