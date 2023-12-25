from pathlib import Path

from apiflask import APIBlueprint
from flask import current_app
from werkzeug.datastructures import FileStorage

from bamboo.database import db
from bamboo.database.models import Media
from bamboo.jobs import gen_small_image
from bamboo.schemas.media import MediaContentType, MediaSchema
from bamboo.utils import gen_uuid

media_bp = APIBlueprint("media", __name__)


@media_bp.post("/")
@media_bp.input(MediaSchema, location="form_and_files")
def upload_media(form_and_files_data: dict) -> dict:
    content_type: MediaContentType = form_and_files_data["content_type"]
    file: FileStorage = form_and_files_data["file"]
    media_dir = Path(current_app.config["BAMBOO_MEDIA_DIR"])
    media = Media(content_type=content_type.value, path="")
    db.session.add(media)
    # flush to get id
    db.session.flush()
    # generate unique filename
    filename = f"{media.id}_{gen_uuid()[:8]}{Path(file.filename).suffix}"
    # save filename to db
    media.path = filename
    # save file to disk
    file.save(media_dir / filename)
    if content_type is MediaContentType.image:
        # async generate small image
        gen_small_image.queue(filename)
    # commit to db
    db.session.commit()
    return {
        "id": media.id,
        "path": media.path,
    }
