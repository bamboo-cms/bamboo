from apiflask import Schema
from apiflask.fields import DateTime, Integer, String
from apiflask.validators import Length


class VenueIn(Schema):
    name = String(required=True, validate=Length(0, 100))
    address = String(required=True, validate=Length(0, 100))
    city_id = Integer(required=True)


class VenueOut(Schema):
    id = Integer()
    name = String()
    address = String()
    city_id = Integer()
    updated_at = DateTime()
    created_at = DateTime()
