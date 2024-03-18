from apiflask import Schema
from apiflask.fields import DateTime, Integer, List, Nested, String
from apiflask.validators import Length

from bamboo.schemas.schedule_item import ScheduleItemOut
from bamboo.schemas.talk import TalkOut


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


class VenueSchedulesOut(Schema):
    venue = Nested(VenueOut)
    schedule_items = List(Nested(ScheduleItemOut))


class VenueTalkOut(Schema):
    venue = Nested(VenueOut)
    talks = List(Nested(TalkOut))
