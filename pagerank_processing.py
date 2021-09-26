from neomodel import db


def write_pagerank():
    # Delete named graph (just in case)
    try:
        db.cypher_query('CALL gds.graph.drop("pagerank")')
    except:
        pass

    # Create named graph
    db.cypher_query('CALL gds.graph.create.cypher("pagerank", "MATCH (m:Mdb) RETURN id(m) as id",'
                    '"MATCH (s:Mdb)<-[:FROM]-(:Comment)-[:TO]->(t:Mdb) RETURN id(s) as source, id(t) as target")')

    # Run pagerank on named graph and write result on each node
    db.cypher_query('CALL gds.pageRank.write("pagerank", {maxIterations: 100, writeProperty: "pagerank"})')

    # Run pagerank on named graph and write result on each node
    db.cypher_query('CALL gds.eigenvector.write("pagerank", {maxIterations: 100, writeProperty: "eigenvector"})')
