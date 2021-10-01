from neomodel import StructuredRel, DateProperty, StringProperty


class MemberRel(StructuredRel):
    start = DateProperty()
    end = DateProperty()
    period = StringProperty()
