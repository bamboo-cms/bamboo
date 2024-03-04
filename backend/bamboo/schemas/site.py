from apiflask import Schema
from apiflask.fields import Dict, Integer, String


class SiteIn(Schema):
    name = String(required=True)
    config = Dict()
    template_url = String()
    deploy_target = String()
    deploy_method = String()
    deploy_secret = String()


class SiteOut(Schema):
    id = Integer()
    name = String()
    config = Dict()
    template_url = String()
    deploy_target = String()
    deploy_method = String()
    deploy_secret = String()
