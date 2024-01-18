from apiflask import Schema
from apiflask.fields import DateTime, Integer, String


class TalkOut(Schema):
    id = Integer()
    title = String()
    content = String()
    video_url = String()
    slides_url = String()
    slides_id = Integer()
    site_id = Integer()
    updated_at = DateTime()
    created_at = DateTime()
