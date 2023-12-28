import tempfile
import zipfile
from datetime import timedelta
from pathlib import Path

import pytest
from bamboo.database import db
from bamboo.database.models import Site
from bamboo.ssg import Fetcher
from flask_apscheduler import APScheduler


@pytest.fixture
def zip_file():
    with tempfile.NamedTemporaryFile(suffix=".zip") as f:
        with zipfile.ZipFile(f, "w") as zf:
            zf.writestr("tpl/index.html", b"Hello, world!")
            zf.writestr("tpl/about.html", b"Hello, world!")
        f.seek(0)
        return f.read()


@pytest.fixture(autouse=True)
def mock_site(httpx_mock, zip_file):
    db.create_all()
    for i in range(3):
        db.session.add(
            Site(
                name=f"test{i}", config={}, template_url=f"https://github.com/bamboo-cms/bamboo{i}"
            )
        )
        httpx_mock.add_response(
            url=f"https://api.github.com/repos/bamboo-cms/bamboo{i}/zipball",
            headers={"Location": "https://exapmle.com"},
            method="GET",
            status_code=302,
        )
    httpx_mock.add_response(
        url="https://exapmle.com",
        content=zip_file,
        method="GET",
        status_code=200,
    )
    db.session.commit()


@pytest.fixture(autouse=True)
def apscheduler(app):
    scheduler = APScheduler()
    scheduler.init_app(app)
    yield scheduler


def test_fetcher_sync(apscheduler):
    with tempfile.TemporaryDirectory() as tmp_dir:
        fetcher = Fetcher(timedelta(seconds=1), apscheduler, Path(tmp_dir))
        fetcher.sync()
        fetcher.stop()
        for site in Site.query.all():
            for file in ["index.html", "about.html"]:
                assert (Path(tmp_dir) / f"{site.id}_{site.name}" / file).exists()
                assert (
                    Path(tmp_dir) / f"{site.id}_{site.name}" / file
                ).read_text() == "Hello, world!"
