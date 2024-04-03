from apiflask import Schema
from apiflask.fields import DateTime, Integer, Nested, String

from bamboo.schemas.city import CityOut
from bamboo.schemas.media import MediaOut


class StaffIn(Schema):
    city_id = Integer(required=True)
    staff_id = Integer(required=True)
    category = String(required=True)


class StaffByCityIn(Schema):
    city_id = Integer()


class StaffByPrimaryIn(Schema):
    city_id = Integer(required=True)
    staff_id = Integer(required=True)


class StaffInfo(Schema):
    id = Integer()
    name = String()
    email = String()
    profile_image = Nested(MediaOut)


class StaffOut(Schema):
    city = Nested(CityOut)
    staff = Nested(StaffInfo)
    category = String()
    created_at = DateTime()
    updated_at = DateTime()
