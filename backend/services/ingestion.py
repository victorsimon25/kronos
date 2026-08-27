import io

import pandas as pd
from PyPDF2 import PdfReader


def parse_csv(file_bytes: bytes) -> dict:
    df = pd.read_csv(io.BytesIO(file_bytes))

    # Convert Pandas NaN values to None for valid JSON.
    df = df.astype(object).where(pd.notna(df), None)

    rows = df.to_dict(orient="records")

    return {
        "type": "csv",
        "columns": df.columns.tolist(),
        "row_count": len(rows),
        "rows": rows
    }


def parse_pdf(file_bytes: bytes) -> dict:
    pdf_file = io.BytesIO(file_bytes)
    reader = PdfReader(pdf_file)

    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""

        pages.append({
            "page": page_number,
            "text": text
        })

    full_text = "\n".join(page["text"] for page in pages)

    return {
        "type": "pdf",
        "page_count": len(reader.pages),
        "text": full_text,
        "pages": pages
    }


def parse_txt(file_bytes: bytes) -> dict:
    text = file_bytes.decode("utf-8")

    return {
        "type": "txt",
        "text": text
    }


def parse_file(filename: str, file_bytes: bytes) -> dict:
    filename = filename.lower()

    if filename.endswith(".csv"):
        return parse_csv(file_bytes)

    if filename.endswith(".pdf"):
        return parse_pdf(file_bytes)

    if filename.endswith(".txt"):
        return parse_txt(file_bytes)

    raise ValueError("Only CSV, PDF, and TXT files are supported")