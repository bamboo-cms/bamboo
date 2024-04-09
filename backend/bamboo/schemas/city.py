from apiflask import Schema
from apiflask.fields import DateTime, Dict, Float, Integer, Nested, String

from bamboo.schemas.site import SiteOut


class CityIn(Schema):
    name = String(required=True)
    site_id = Integer(required=True)
    address = String()
    latitude = Float()
    longitude = Float()
    start = DateTime()
    end = DateTime()
    registration_url = String()
    live_urls = Dict()


class CityOut(Schema):
    id = Integer()
    name = String()
    address = String()
    latitude = Float()
    longitude = Float()
    start = DateTime()
    end = DateTime()
    registration_url = String()
    live_urls = Dict()
    site = Nested(SiteOut)
