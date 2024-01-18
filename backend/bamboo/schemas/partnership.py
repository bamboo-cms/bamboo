from apiflask import Schema
from apiflask.fields import DateTime, Integer, String


class PartnershipIn(Schema):
    city_id = Integer(required=True)
    organization_id = Integer(required=True)
    category = String()


class PartnershipByCityIn(Schema):
    city_id = Integer()


class PartnershipByPrimaryIn(Schema):
    city_id = Integer(required=True)
    organization_id = Integer(required=True)


class PartnershipOut(Schema):
    city_id = Integer()
    organization_id = Integer()
    category = String()
    created_at = DateTime()
    updated_at = DateTime()
