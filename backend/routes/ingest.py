from fastapi import APIRouter, File, HTTPException, UploadFile

from services.ingestion import parse_file


router = APIRouter(prefix="/ingest", tags=["Ingestion"])


@router.post("/file")
async def ingest_file(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required"
        )

    try:
        file_bytes = await file.read()

        result = parse_file(
            file.filename,
            file_bytes
        )

        return {
            "status": "success",
            "filename": file.filename,
            "data": result
        }

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process file: {str(e)}"
        )