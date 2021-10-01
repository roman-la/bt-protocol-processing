from neomodel import StructuredNode, StringProperty, FloatProperty, RelationshipTo, StructuredRel
from data_io.models.mdb import Mdb


class Comment(StructuredNode):
    text = StringProperty()
    polarity = FloatProperty()
    from_faction = StringProperty()
    to_faction = StringProperty()

    sender = RelationshipTo(Mdb, 'FROM')
    receiver = RelationshipTo(Mdb, 'TO')
