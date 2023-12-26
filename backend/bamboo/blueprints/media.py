import mimetypes
from pathlib import Path

from apiflask import APIBlueprint
from flask import current_app
from werkzeug.datastructures import FileStorage

from bamboo.database import db
from bamboo.database.models import Media
from bamboo.jobs import gen_small_image
from bamboo.schemas.media import IMAGE_SUFFIXES, MediaSchema
from bamboo.utils import gen_uuid

media_bp = APIBlueprint("media", __name__)


@media_bp.post("/")
@media_bp.input(MediaSchema, location="files")
def upload_media(files_data: dict) -> dict | tuple[dict, int]:
    file: FileStorage = files_data["file"]
    if not isinstance(file.filename, str):
        return {"message": "Invalid filename"}, 400
    content_type = mimetypes.guess_type(file.filename)[0]
    media_dir = Path(current_app.config["BAMBOO_MEDIA_DIR"])
    media = Media(content_type=content_type, path="")
    db.session.add(media)
    # flush to get id
    db.session.flush()
    file_suffix = Path(file.filename).suffix.lower()
    # generate unique filename
    filename = f"{media.id}_{gen_uuid()[:8]}{file_suffix}"
    # save filename to db
    media.path = filename
    # save file to disk
    file.save(media_dir / filename)
    if file_suffix in IMAGE_SUFFIXES:
        # async generate small image
        gen_small_image.queue(filename)  # pyright: ignore reportFunctionMemberAccess
    # commit to db
    db.session.commit()
    return {
        "id": media.id,
        "path": media.path,
    }
