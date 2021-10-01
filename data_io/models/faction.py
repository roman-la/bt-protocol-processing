from neomodel import StructuredNode, StringProperty


class Faction(StructuredNode):
    name = StringProperty()
    color = StringProperty()
    period = StringProperty()
