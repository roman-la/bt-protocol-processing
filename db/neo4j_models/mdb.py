from neomodel import StructuredNode, UniqueIdProperty, StringProperty, RelationshipTo
from db.neo4j_models.faction import Faction
from db.neo4j_models.member_rel import MemberRel


class Mdb(StructuredNode):
    mdb_id = UniqueIdProperty()
    first_name = StringProperty()
    last_name = StringProperty()

    member = RelationshipTo(Faction, 'PART_OF', model=MemberRel)
