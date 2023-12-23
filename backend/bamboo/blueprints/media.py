import uuid
from pathlib import Path

from apiflask import APIBlueprint
from flask import current_app

from bamboo.core.extensions import db
from bamboo.forms.media import MediaContentType, MediaForm
from bamboo.jobs import gen_small_image
from bamboo.models import Media

media_bp = APIBlueprint("media", __name__)


def gen_uuid() -> str:
    """Generate a uuid hex string."""
    return str(uuid.uuid4().hex)


# upload media
@media_bp.post("/")
def upload_media():
    media_dir = Path(current_app.config["BAMBOO_MEDIA_DIR"])
    form = MediaForm()
    if not form.validate_on_submit():
        return form.errors, 400
    media = Media(content_type=form.content_type.data)
    db.session.add(media)
    # flush to get id
    db.session.flush()
    # generate unique filename
    filename = f"{media.id}_{gen_uuid()[:8]}{Path(form.file.data.filename).suffix}"
    # save filename to db
    media.path = filename
    # save file to disk
    form.file.data.save(media_dir / filename)
    if MediaContentType(media.content_type) is MediaContentType.image:
        # async generate small image
        gen_small_image.queue(filename)
    # commit to db
    db.session.commit()
    return {
        "id": media.id,
        "path": media.path,
    }
