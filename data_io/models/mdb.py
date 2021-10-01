from neomodel import StructuredNode, UniqueIdProperty, StringProperty, RelationshipTo
from data_io.models.faction import Faction
from data_io.models.member_rel import MemberRel


class Mdb(StructuredNode):
    mdb_id = UniqueIdProperty()
    first_name = StringProperty()
    last_name = StringProperty()

    member = RelationshipTo(Faction, 'PART_OF', model=MemberRel)
