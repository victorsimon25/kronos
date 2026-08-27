import os

import certifi
from dotenv import load_dotenv
from neo4j import GraphDatabase


load_dotenv()


NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")


if not NEO4J_URI or not NEO4J_USERNAME or not NEO4J_PASSWORD:
    raise RuntimeError("Neo4j environment variables are not configured")


driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
)


def verify_neo4j_connection():
    driver.verify_connectivity()
    return True


def close_neo4j_connection():
    driver.close()