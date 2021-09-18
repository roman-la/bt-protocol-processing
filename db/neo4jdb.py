from neomodel import DoesNotExist, db, StructuredNode, StringProperty, UniqueIdProperty, RelationshipTo, DateProperty, \
    FloatProperty, StructuredRel
from datetime import datetime

db.set_connection('bolt://user:pw@127.0.0.1:7687')


def clear_db():
    db.cypher_query('MATCH (n) DETACH DELETE n')


def setup_factions():
    Faction(name='SPD', color='#E50051').save()
    Faction(name='DIE LINKE.', color='#C7017F').save()
    Faction(name='BÜNDNIS 90/DIE GRÜNEN', color='#009879').save()
    Faction(name='AFD', color='#0085CC').save()
    Faction(name='CDU/CSU', color='#706F6F').save()
    Faction(name='FDP', color='#FFED00').save()
    Faction(name='Fraktionslos', color='#ABABAB').save()


def insert_mdbs(mdbs):
    for mdb in mdbs:
        mdb_id = mdb['id']
        faction = mdb['faction']
        part_of_from = datetime.strptime(mdb['from'], '%d.%m.%Y').date
        part_of_to = datetime.strptime(mdb['to'], '%d.%m.%Y').date if mdb['to'] else None

        for name in mdb['names']:
            first_name, last_name, from_date, to_date = name
            if to_date:
                continue  # Not the current name

            try:
                faction = Faction.nodes.get(name=faction)
            except DoesNotExist:
                continue

            try:
                mdb = Mdb.nodes.get(mdb_id=mdb_id, first_name=first_name, last_name=last_name)
            except DoesNotExist:
                mdb = Mdb(mdb_id=mdb_id, first_name=first_name, last_name=last_name).save()

            mdb.member.connect(faction, {'from_': part_of_from, 'to_': part_of_to})


def insert_comments(comments):
    for comment in comments:
        session_id, speaker, commenter, comment, polarity = comment

        # TODO: Investigate
        try:
            speaker_neo4j = Mdb.nodes.get(mdb_id=speaker['id'])
            commenter_neo4j = Mdb.nodes.get(mdb_id=commenter['id'])
        except DoesNotExist:
            continue

        comment_neo4j = Comment(text=comment, polarity=polarity).save()

        comment_neo4j.sender.connect(commenter_neo4j)
        comment_neo4j.receiver.connect(speaker_neo4j)


class Faction(StructuredNode):
    name = StringProperty()
    color = StringProperty()


class MemberRel(StructuredRel):
    from_ = DateProperty()
    to_ = DateProperty()


class Mdb(StructuredNode):
    mdb_id = UniqueIdProperty()
    first_name = StringProperty()
    last_name = StringProperty()

    member = RelationshipTo(Faction, 'PART_OF', model=MemberRel)


class Comment(StructuredNode):
    text = StringProperty()
    polarity = FloatProperty()

    sender = RelationshipTo(Mdb, 'FROM')
    receiver = RelationshipTo(Mdb, 'TO')
