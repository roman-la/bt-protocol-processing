from neomodel import db


def apply_pagerank():
    graph_name = 'pagerank'

    __delete_graph(graph_name)

    # Create named graph
    db.cypher_query(f'CALL gds.graph.create.cypher("{graph_name}", "MATCH (m:Mdb) RETURN id(m) as id",'
                    '"MATCH (s:Mdb)<-[:FROM]-(:Comment)-[:TO]->(t:Mdb) RETURN id(s) as target, id(t) as source")')

    # Run pagerank on named graph and write result on each node
    db.cypher_query(f'CALL gds.pageRank.write("{graph_name}", '
                    '{maxIterations: 100, writeProperty: "pagerank"})')

    __delete_graph(graph_name)


def apply_eigenvector():
    graph_name = 'eigenvector'

    __delete_graph(graph_name)

    # Create named graph
    db.cypher_query(f'CALL gds.graph.create.cypher("{graph_name}", "MATCH (m:Mdb) RETURN id(m) as id",'
                    '"MATCH (s:Mdb)<-[:FROM]-(:Comment)-[:TO]->(t:Mdb) RETURN id(s) as target, id(t) as source")')

    # Run eigenvector on named graph and write result on each node
    db.cypher_query(f'CALL gds.eigenvector.write("{graph_name}",'
                    '{maxIterations: 100, writeProperty: "eigenvector"})')

    __delete_graph(graph_name)


def __delete_graph(graph_name):
    try:
        db.cypher_query(f'CALL gds.graph.drop("{graph_name}")')
    except:
        pass
