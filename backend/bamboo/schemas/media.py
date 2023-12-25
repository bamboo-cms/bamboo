from enum import Enum

from apiflask import Schema
from apiflask.fields import Enum as EnumField
from apiflask.fields import File as FileField
from apiflask.validators import FileSize, FileType


class MediaContentType(Enum):
    image = "image"
    slides = "slides"


class MediaSchema(Schema):
    content_type = EnumField(MediaContentType, required=True)
    file = FileField(
        validate=[
            FileType([".png", ".jpg", ".jpeg", ".ppt", ".pptx", ".pdf"]),
            FileSize(max="50 MB"),
        ]
    )
