from io import BytesIO
from pathlib import Path
import shutil
import tempfile
from zipfile import ZipFile, BadZipFile

from flask import Flask, current_app
from flask_rq2 import RQ
from PIL import Image
from sqlalchemy import ScalarResult
from bamboo.utils import fetch_github_repo

from bamboo.database.models import db, Site

rq = RQ()


@rq.job
def gen_small_image(image_path: Path) -> None:
    """Generate a small image from the given image."""
    small_suffix = current_app.config["BAMBOO_SMALL_IMAGE_SUFFIX"]
    small_ratio = current_app.config["BAMBOO_SMALL_IMAGE_RATIO"]
    small_image_path = image_path.parent / f"{image_path.stem}{small_suffix}{image_path.suffix}"
    with Image.open(image_path) as image:
        width, height = image.size
        small_width = int(width * small_ratio)
        small_height = int(height * small_ratio)
        with image.resize((small_width, small_height)) as small_image:
            small_image.save(small_image_path)


@rq.job
def sync_templates(store_dir: Path, **kwargs) -> None:
    """
    Sync the templates from the GitHub repository to local.

    :param store_dir: The directory to store the template.
    :param gh_token: The GitHub token to use for the sync. If None, GitHub may be forbid access.
    """
    sites: ScalarResult[Site] = db.session.execute(db.select(Site)).scalars()
    for site in sites:
        if not site.template_url:
            continue
        name = f"{site.id}_{site.name}"
        gh_token: str | None = kwargs.get("gh_token")
        file_bytes = fetch_github_repo(site.template_url, gh_token=gh_token)
        if file_bytes is None:
            continue
        buf = BytesIO(file_bytes)
        try:
            zip_file = ZipFile(buf)
        except BadZipFile:
            continue
        if zip_file.testzip() is not None:
            continue
        if len(zip_file.namelist()) == 0:
            continue
        dir_name = zip_file.namelist()[0].split("/")[0]
        dest = store_dir / name
        if dest.exists():
            shutil.rmtree(dest)
        with tempfile.TemporaryDirectory() as tmp_dir:
            zip_file.extractall(tmp_dir)
            shutil.copytree(Path(tmp_dir) / dir_name, dest)
        zip_file.close()


def init_app(app: Flask) -> None:
    rq.init_app(app)
