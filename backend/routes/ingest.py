from fastapi import APIRouter, File, UploadFile, HTTPException

from services.ingestion import parse_file
from services.graph import Neo4jService


router = APIRouter(prefix="/ingest", tags=["Ingestion"])


@router.post("/file")
async def ingest_file(file: UploadFile = File(...)):
    try:
        file_bytes = await file.read()

        data = parse_file(
            file.filename,
            file_bytes
        )

        # CSV records can be inserted directly into Neo4j.
        if data["type"] == "csv":
            graph = Neo4jService()

            try:
                graph.verify_connection()

                inserted = graph.create_records(
                    data["rows"]
                )
            finally:
                graph.close()

            return {
                "status": "success",
                "filename": file.filename,
                "type": "csv",
                "row_count": data["row_count"],
                "inserted_into_neo4j": inserted
            }

        # PDF/TXT are parsed for now.
        # Their text will go through NLP/LLM extraction next.
        return {
            "status": "success",
            "filename": file.filename,
            "data": data
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )