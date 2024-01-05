import io
from pathlib import Path

from bamboo.database import db
from PIL import Image


def test_upload_media(app, client, mocker):
    db.create_all()
    mocked_function = mocker.patch("bamboo.jobs.gen_small_image.queue", autospec=True)
    mocker.patch(
        "bamboo.blueprints.media.gen_uuid",
        return_value="xxxxxxxx",
        autospec=True,
    )
    content = b"abcdef"
    response = client.post(
        "/media/",
        data={
            "file": (io.BytesIO(content), "test.png"),
        },
    )
    assert response.status_code == 200, response.json
    assert response.json["id"] == 1
    filename = "xxxxxxxx_test.png"
    # check mocked function called
    mocked_function.assert_called_once_with(filename)
    assert response.json["path"] == filename
    file = Path(app.config["BAMBOO_MEDIA_DIR"]) / filename
    # check file exists and content
    assert file.exists()
    assert file.read_bytes() == content
    # delete test file
    file.unlink()


def test_gen_small_image(app):
    # create test image
    media_dir = Path(app.config["BAMBOO_MEDIA_DIR"])
    filename = "test.png"
    image_path = media_dir / filename
    with Image.new("RGB", (100, 100)) as image:
        image.save(image_path)
    # call function
    from bamboo.jobs import gen_small_image

    with app.app_context():
        gen_small_image(filename)
    # check file exists
    small_filename = "test_small.png"
    small_image_path = media_dir / small_filename
    assert small_image_path.exists()
    with Image.open(small_image_path) as small_image:
        # check small image size
        assert small_image.size == (30, 30)
    # delete test file
    image_path.unlink()
    small_image_path.unlink()
