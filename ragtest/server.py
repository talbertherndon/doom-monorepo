from neo4j import GraphDatabase

uri = "neo4j://localhost:7687"  # Try "bolt://" if "neo4j://" fails
auth = ("neo4j", "securepassword123")

driver = GraphDatabase.driver(uri, auth=auth)

with driver.session() as session:
    result = session.run("RETURN 'Hello, Neo4j!' AS message")
    for record in result:
        print(record["message"])

#http://192.168.4.250:7687