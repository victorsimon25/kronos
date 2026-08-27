import os
from pathlib import Path

from dotenv import load_dotenv
from neo4j import GraphDatabase


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


class Neo4jService:
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI")
        self.username = os.getenv("NEO4J_USERNAME")
        self.password = os.getenv("NEO4J_PASSWORD")

        if not self.uri or not self.username or not self.password:
            raise ValueError(
                "Neo4j environment variables are missing. "
                "Check backend/.env"
            )

        self.driver = GraphDatabase.driver(
            self.uri,
            auth=(self.username, self.password)
        )

    def verify_connection(self):
        self.driver.verify_connectivity()
        return True

    def close(self):
        self.driver.close()

    def create_criminal_record(self, record: dict):
        query = """
        MERGE (p:Person {name: $person_name})

        SET p.alias = $alias

        MERGE (c:Case {id: $case_id})

        SET c.offense = $offense,
            c.date = $date

        MERGE (p)-[:INVOLVED_IN]->(c)

        RETURN p, c
        """

        with self.driver.session() as session:
            result = session.run(
                query,
                person_name=record.get("person_name"),
                alias=record.get("alias"),
                case_id=record.get("case_id"),
                offense=record.get("offense"),
                date=record.get("date")
            )

            return result.single() is not None

    def create_records(self, records: list[dict]):
        count = 0

        for record in records:
            self.create_criminal_record(record)
            count += 1

        return count

    def get_person(self, name: str):
        query = """
        MATCH (p:Person)
        WHERE toLower(p.name) = toLower($name)
        OPTIONAL MATCH (p)-[:INVOLVED_IN]->(c:Case)

        RETURN
            p.name AS name,
            p.alias AS alias,
            collect({
                case_id: c.id,
                offense: c.offense,
                date: c.date
            }) AS cases
        """

        with self.driver.session() as session:
            result = session.run(query, name=name)
            record = result.single()

            if not record:
                return None

            return record.data()


def verify_neo4j_connection():
    graph = Neo4jService()

    try:
        graph.verify_connection()
        return True
    finally:
        graph.close()