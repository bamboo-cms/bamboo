from apiflask import Schema
from apiflask.fields import DateTime, Integer, String


class OrganizationIn(Schema):
    name = String(required=True)
    url = String()
    profile_image_id = Integer(required=True)


class OrganizationOut(Schema):
    name = String()
    url = String()
    profile_image_id = Integer()
    id = Integer()
    created_at = DateTime()
    updated_at = DateTime()
