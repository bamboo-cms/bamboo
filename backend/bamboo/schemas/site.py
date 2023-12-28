from apiflask import Schema
from apiflask.fields import Dict, String


class SiteIn(Schema):
    name = String(required=True)
    config = Dict()
    template_url = String()
    deploy_target = String()
    deploy_method = String()
    deploy_secret = String()


class SiteOut(Schema):
    id = String()
    name = String()
    config = Dict()
    template_url = String()
    deploy_target = String()
    deploy_method = String()
    deploy_secret = String()
