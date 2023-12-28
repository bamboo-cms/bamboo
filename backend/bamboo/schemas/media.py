from apiflask import Schema
from apiflask.fields import File, Integer, String
from apiflask.validators import FileSize, FileType

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg"}
SLIDES_SUFFIXES = {".ppt", ".pptx", ".pdf"}


class MediaIn(Schema):
    file = File(
        required=True,
        validate=[
            FileType(IMAGE_SUFFIXES | SLIDES_SUFFIXES),
            FileSize(max="50 MB"),
        ],
    )


class MediaOut(Schema):
    id = Integer()
    path = String()
