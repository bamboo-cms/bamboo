from pathlib import Path

from flask import Flask, current_app
from flask_rq2 import RQ
from PIL import Image

rq = RQ()


@rq.job
def gen_small_image(filename: str) -> None:
    """Generate a small image from the given image."""
    media_dir = Path(current_app.config["BAMBOO_MEDIA_DIR"])
    small_suffix = current_app.config["BAMBOO_SMALL_IMAGE_SUFFIX"]
    small_ratio = current_app.config["BAMBOO_SMALL_IMAGE_RATIO"]
    image_path = media_dir / filename
    small_image_path = media_dir / f"{image_path.stem}{small_suffix}{image_path.suffix}"
    with Image.open(image_path) as image:
        width, height = image.size
        small_width = int(width * small_ratio)
        small_height = int(height * small_ratio)
        with image.resize((small_width, small_height)) as small_image:
            small_image.save(small_image_path)


def init_app(app: Flask) -> None:
    rq.init_app(app)
