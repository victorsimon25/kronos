import os
from neo4j import GraphDatabase

# Load credentials from environment variables (with fallback for development)
NEO4J_URI = os.getenv("NEO4J_URI", "neo4j+s://f3d09a64.databases.neo4j.io")
NEO4J_USER = os.getenv("NEO4J_USER", "f3d09a64")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "tXNOIPxX9P7V3NGewbTVjWM4L3L-_snuYIGBno8PKy0")

driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(NEO4J_USER, NEO4J_PASSWORD)
)

ALLOWED_ENTITY_TYPES = {
    "PERSON",
    "PHONE",
    "VEHICLE",
    "LOCATION",
    "ORGANIZATION",
    "BANK_ACCOUNT",
    "EVENT"
}


def create_entity(driver, entity):

    entity_id = entity["id"]
    entity_type = entity["type"]

    if entity_type not in ALLOWED_ENTITY_TYPES:
        raise ValueError(f"Invalid entity type: {entity_type}")

    properties = {
        key: value
        for key, value in entity.items()
        if key not in ["id", "type"]
    }

    query = f"""
    CREATE (n:{entity_type})
    SET n.id = $id
    SET n += $properties
    RETURN n
    """

    with driver.session() as session:
        result = session.run(
            query,
            id=entity_id,
            properties=properties
        )

        record = result.single()

        return record["n"]



def find_entity(driver, entity_type, properties):

    if entity_type not in ALLOWED_ENTITY_TYPES:
        raise ValueError(f"Invalid entity type: {entity_type}")

    query = f"""
    MATCH (n:{entity_type})
    WHERE all(key IN keys($properties)
              WHERE n[key] = $properties[key])
    RETURN n
    """

    with driver.session() as session:
        result = session.run(
            query,
            properties=properties
        )

        return [record["n"] for record in result]


def create_relationship(driver, relationship):

    source_id = relationship["source_id"]
    target_id = relationship["target_id"]
    relationship_type = relationship["type"]

    # if relationship_type not in ALLOWED_RELATIONSHIPS:
    #     raise ValueError(
    #         f"Invalid relationship type: {relationship_type}"
    #     )

    query = f"""
    MATCH (source {{id: $source_id}})
    MATCH (target {{id: $target_id}})
    CREATE (source)-[r:{relationship_type}]->(target)
    SET r.confidence = $confidence
    SET r.evidence_id = $evidence_id
    RETURN source, r, target
    """

    with driver.session() as session:
        result = session.run(
            query,
            source_id=source_id,
            target_id=target_id,
            confidence=relationship.get("confidence"),
            evidence_id=relationship.get("evidence_id")
        )

        record = result.single()

        if record is None:
            raise ValueError(
                f"Source '{source_id}' or target '{target_id}' not found"
            )

        return record

def find_network(driver, entity_id, hop_count=1):
    """
    Find all entities within a specified number of hops from the source entity.

    Args:
        driver: Neo4j driver instance
        entity_id: ID of the source entity
        hop_count: Number of hops/degrees of separation (default: 1)
                  1 = direct connections only
                  2 = connections and their connections
                  etc.

    Returns:
        List of paths with connected entities and hop distance
    """

    query = f"""
    MATCH path = (start {{id: $entity_id}})-[*1..{hop_count}]-(connected)
    WITH start, connected, relationships(path) as rels, length(path) as hops
    RETURN DISTINCT start, connected, hops, rels
    ORDER BY hops, connected.id
    """

    with driver.session() as session:
        result = session.run(
            query,
            entity_id=entity_id
        )

        return [
            {
                "start": dict(record["start"]),
                "connected": dict(record["connected"]),
                "hop_distance": record["hops"],
                "relationships": [
                    {
                        "type": rel.type,
                        "properties": dict(rel)
                    }
                    for rel in record["rels"]
                ]
            }
            for record in result
        ]
    
def find_shortest_path(driver, source_id, target_id):

    query = """
    MATCH (source {id: $source_id})
    MATCH (target {id: $target_id}) 
    MATCH path = shortestPath((source)-[*]-(target))
    RETURN path
    """

    with driver.session() as session:
        result = session.run(
            query,
            source_id=source_id,
            target_id=target_id
        )

        record = result.single()

        if record is None:
            return "Not found"

        path = record["path"]

        nodes = [
            {
                "id": node["id"],
                "type": list(node.labels)[0],
                "properties": dict(node)
            }
            for node in path.nodes
        ]

        relationships = [
            {
                "type": relationship.type,
                "source": relationship.start_node["id"],
                "target": relationship.end_node["id"]
            }
            for relationship in path.relationships
        ]

        return {
            "nodes": nodes,
            "relationships": relationships
        }

def find_most_connected_person(driver, limit=1):
    """
    Find the most connected person(s) in the database.
    Returns distinct persons by ID, aggregating connections across duplicate nodes.
    """

    query = """
    MATCH (p:PERSON)
    OPTIONAL MATCH (p)-[r]-()
    WITH p.id as person_id,
         collect(DISTINCT p)[0] as person_node,
         count(DISTINCT r) as connection_count
    WHERE connection_count > 0
    RETURN person_node as p, connection_count
    ORDER BY connection_count DESC, person_id
    LIMIT $limit
    """

    with driver.session() as session:
        result = session.run(
            query,
            limit=limit
        )

        return [
            {
                "person": dict(record["p"]),
                "connection_count": record["connection_count"]
            }
            for record in result
        ]

def close_connection():
    """Close the Neo4j database connection. Call this when shutting down the application."""
    if driver:
        driver.close()
        print("Neo4j connection closed")

# # ---------------- TEST ----------------
 

# test_relationships = [
#     {
#         "source_id": "P001",
#         "target_id": "P002",
#         "type": "ASSOCIATED_WITH",
#         "confidence": 0.9,
#         "evidence_id": "EV001"
#     },
#     {
#         "source_id": "P001",
#         "target_id": "P003",
#         "type": "CALLED",
#         "confidence": 0.8,
#         "evidence_id": "EV002"
#     },
#     {
#         "source_id": "P001",
#         "target_id": "V001",
#         "type": "OWNS",
#         "confidence": 0.95,
#         "evidence_id": "EV003"
#     },
#     {
#         "source_id": "P001",
#         "target_id": "PH001",
#         "type": "CALLED",
#         "confidence": 0.85,
#         "evidence_id": "EV004"
#     },
#     {
#         "source_id": "P001",
#         "target_id": "L001",
#         "type": "LOCATED_AT",
#         "confidence": 0.9,
#         "evidence_id": "EV005"
#     }
# ]