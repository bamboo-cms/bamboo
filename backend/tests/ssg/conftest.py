from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

import pytest
from pytest_httpx import HTTPXMock

from bamboo import create_app
from bamboo.database import db
from bamboo.database.models import Site


@pytest.fixture
def example_template_path():
    return Path(__file__).parent / "template_example"


@pytest.fixture
def mock_template_download(httpx_mock: HTTPXMock, example_template_path: Path):
    httpx_mock.add_response(
        url="https://api.github.com/repos/PyConChina/templates/zipball",
        status_code=302,
        headers={
            "Location": "https://codeload.github.com/PyConChina/templates/legacy.zip/refs/heads/main"
        },
    )
    buf = BytesIO()
    with ZipFile(buf, "w") as zip_file:
        for file in example_template_path.rglob("*"):
            if file.is_file():
                p = Path("PyConChina-templates-0000000") / file.relative_to(example_template_path)
                zip_file.write(file, p)
    buf.seek(0)
    httpx_mock.add_response(
        url="https://codeload.github.com/PyConChina/templates/legacy.zip/refs/heads/main",
        content=buf.read(),
        headers={"Content-Type": "application/zip"},
    )


@pytest.fixture(autouse=True)
def app():
    app = create_app("testing")
    with app.app_context():
        yield app


@pytest.fixture(autouse=True)
def init_db():
    db.create_all()
    try:
        yield
    finally:
        db.drop_all()


@pytest.fixture(autouse=True)
def site():
    site = Site(id=1000, name="site1000", template_url="https://github.com/PyConChina/templates")
    db.session.add(site)
    db.session.commit()
    yield site
