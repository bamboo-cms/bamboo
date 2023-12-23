from enum import Enum

from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired, FileSize
from wtforms import SelectField
from wtforms.validators import DataRequired


class MediaContentType(Enum):
    image = "image"
    slides = "slides"


class MediaForm(FlaskForm):
    content_type = SelectField(
        "Content Type",
        choices=[(e.name, e.value) for e in MediaContentType],
        validators=[DataRequired()],
    )
    file = FileField(
        "File",
        validators=[
            FileRequired(),
            FileAllowed(["jpg", "jpeg", "png", "pdf", "ppt", "pptx"]),
            FileSize(max_size=50 * 1024 * 1024),
        ],
    )
