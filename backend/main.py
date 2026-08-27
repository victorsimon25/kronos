from fastapi import FastAPI

from routes.ingest import router as ingest_router
from services.graph import verify_neo4j_connection


app = FastAPI(
    title="Criminal Network Analysis API",
    version="1.0.0"
)


app.include_router(ingest_router)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "message": "Backend is running"
    }


@app.get("/health/neo4j")
def neo4j_health_check():
    verify_neo4j_connection()

    return {
        "status": "ok",
        "message": "Neo4j connection is working"
    }