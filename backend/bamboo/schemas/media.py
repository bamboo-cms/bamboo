from apiflask import Schema
from apiflask.fields import File as FileField
from apiflask.validators import FileSize, FileType

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg"}
SLIDES_SUFFIXES = {".ppt", ".pptx", ".pdf"}


class MediaSchema(Schema):
    file = FileField(
        required=True,
        validate=[
            FileType(IMAGE_SUFFIXES | SLIDES_SUFFIXES),
            FileSize(max="50 MB"),
        ]
    )
