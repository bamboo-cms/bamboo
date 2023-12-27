from apiflask import Schema
from apiflask.fields import Dict, String


class SiteIn(Schema):
    name = String(required=True)
    config = Dict(required=True)


class SiteOut(Schema):
    id = String()
    name = String()
    config = Dict()
