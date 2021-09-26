import protocol_processing
from mdb_processing import MdbProcessing
from db.mongodb import MongoDB
import comment_processing
from db import neo4jdb
import pagerank_processing

mdbs = MdbProcessing()

protocols = MongoDB().get_collection_documents()

raw_comments = protocol_processing.process(protocols)

comments = []
for (session_id, speaker_id, comment, commenter_name) in raw_comments:
    speaker = mdbs.get_mdb_by_id(speaker_id)
    commenter = mdbs.get_mdb_by_name(commenter_name)
    if speaker and commenter:
        polarity = comment_processing.get_comment_polarity(comment)
        comments.append((session_id, speaker, commenter, comment, polarity))

neo4jdb.clear_db()
neo4jdb.setup_factions()
neo4jdb.insert_mdbs(mdbs.mdbs)
neo4jdb.insert_comments(comments)
pagerank_processing.write_pagerank()
