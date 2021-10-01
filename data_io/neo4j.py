from neomodel import DoesNotExist, db
from datetime import datetime
from data_io.models.comment import Comment
from data_io.models.faction import Faction
from data_io.models.mdb import Mdb

db.set_connection('bolt://user:pw@127.0.0.1:7687')


def clear_db():
    db.cypher_query('MATCH (n) DETACH DELETE n')


def setup_factions():
    Faction(name='DIE LINKE.', color='#BE3075', period='19').save()
    Faction(name='SPD', color='#E3000F', period='19').save()
    Faction(name='BÜNDNIS 90/DIE GRÜNEN', color='#46962B', period='19').save()
    Faction(name='CDU/CSU', color='#32302E', period='19').save()
    Faction(name='FDP', color='#FFED00', period='19').save()
    Faction(name='AFD', color='#0099FF', period='19').save()
    Faction(name='Fraktionslos', color='#ABABAB', period='19').save()


def insert_mdbs(mdbs):
    for mdb in mdbs:
        mdb_id, aliases, periods = mdb

        current_alias = None
        for alias in aliases:
            first_name, last_name, to_date = alias
            # Not the current name
            if to_date:
                continue
            current_alias = alias

        for period in periods:
            period_id, faction_name, part_of_faction_from, part_of_faction_to = period

            if period_id not in ['16', '17', '18', '19']:
                continue

            try:
                faction = Faction.nodes.get(name=faction_name, period=period_id)
            except DoesNotExist:
                faction = Faction(name=faction_name, period=period_id, color='#000000').save()

            mdb = Mdb.nodes.get_or_none(mdb_id=mdb_id,
                                        first_name=current_alias[0],
                                        last_name=current_alias[1])

            if not mdb:
                mdb = Mdb(mdb_id=mdb_id,
                          first_name=current_alias[0],
                          last_name=current_alias[1]).save()

            start_member = datetime.strptime(part_of_faction_from, '%d.%m.%Y').date()
            end_member = datetime.strptime(part_of_faction_to, '%d.%m.%Y').date() if part_of_faction_to else None

            if not end_member:
                mdb.member.connect(faction, {'start': start_member})
            else:
                mdb.member.connect(faction, {'start': start_member, 'end': end_member})


def insert_comments(comments):
    for comment in comments:
        session_id, speaker, commenter, comment, polarity = comment

        try:
            speaker_neo4j = Mdb.nodes.get(mdb_id=speaker[0])
            commenter_neo4j = Mdb.nodes.get(mdb_id=commenter[0])
        except DoesNotExist:
            # Probably formal mdbs (see e.g. Zypries in 19. WP)
            continue

        comment_neo4j = Comment(text=comment, polarity=polarity).save()

        comment_neo4j.sender.connect(commenter_neo4j)
        comment_neo4j.receiver.connect(speaker_neo4j)
