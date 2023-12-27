from apiflask import Schema
from apiflask.fields import DateTime, Integer, String
from apiflask.validators import Length


class ScheduleItemIn(Schema):
    venue_id = Integer(required=True)
    talk_id = Integer(required=False)
    content = String(required=False, validate=Length(0, 10**5))
    start = DateTime(required=True)
    end = DateTime(required=True)


class ScheduleItemOut(Schema):
    id = Integer()
    venue_id = Integer()
    talk_id = Integer()
    content = String()
    start = DateTime()
    end = DateTime()
