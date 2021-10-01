from data_processing.mdb_processing import MdbProcessing
from data_io.mongo import Mongo
from data_io import neo4j
from data_processing import graph_processing, comment_processing, protocol_processing

# Setup mdb processing
mdbs = MdbProcessing()

# Get raw protocols from db
protocols = Mongo().get_collection_documents()

# Extract raw comments
raw_comments = protocol_processing.get_comments_from_protocols(protocols)

# Process comments
comments = []
for (session_id, speaker_id, comment, commenter_name) in raw_comments:
    speaker = mdbs.get_mdb_by_id(speaker_id)
    commenter = mdbs.get_mdb_by_name(commenter_name)
    if speaker and commenter:
        polarity = comment_processing.get_comment_polarity(comment)
        comments.append((session_id, speaker, commenter, comment, polarity))

# Insert mdbs and comments into db
neo4j.clear_db()
neo4j.setup_factions()
neo4j.insert_mdbs(mdbs.mdbs)
neo4j.insert_comments(comments)

# Graph analysis
graph_processing.apply_pagerank()
graph_processing.apply_eigenvector()
