import tempfile
import time
import zipfile
from pathlib import Path
from typing import Generator

import pytest
from bamboo.database.models import Site
from bamboo.ssg import SSG

files = {
    "index.html": b"hello {{site.name}}",
    "jinja/layout.html": b"hello {% block name %}{% endblock %}",
    "page.html": b'{% extends "jinja/layout.html" %}\n{% block name %}{{site.name}}{% endblock %}',
    "about/index.html": b'{% extends "jinja/layout.html" %}\n{% block name %}{{site.name}}{% endblock %}',
    "static/style.css": b"body { color: red; }",
    "static/index.js": b"console.log('Hello, world!');",
    "static/favicon.ico": b"test",
    "static/logo.jpg": b"test",
}


@pytest.fixture(autouse=True)
def mock_sites(app) -> list[Site]:
    db = app.extensions["sqlalchemy"]
    db.create_all()
    sites = []
    for i in range(3):
        site = Site(
            name=f"test{i}", config={}, template_url=f"https://github.com/bamboo-cms/bamboo{i}"
        )
        sites.append(site)
        db.session.add(site)
    db.session.commit()
    return sites


@pytest.fixture
def zip_file() -> bytes:
    with tempfile.NamedTemporaryFile(suffix=".zip") as f:
        with zipfile.ZipFile(f, "w") as zf:
            for name, content in files.items():
                zf.writestr("tpl/" + name, content)
        f.seek(0)
        return f.read()


@pytest.fixture(autouse=True)
def mock_fetcher_request(httpx_mock, mock_sites, zip_file):
    for site in mock_sites:
        httpx_mock.add_response(
            url=f"https://api.github.com/repos/bamboo-cms/bamboo{site.id - 1}/zipball",
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


@pytest.fixture(autouse=True)
def ssg(app) -> Generator[SSG, None, None]:
    with tempfile.TemporaryDirectory() as tmp_dir:
        ssg = app.extensions["ssg"]
        ssg.tpl_dir = Path(tmp_dir)
        ssg.fetcher.store_dir = Path(tmp_dir)
        app.apscheduler.start()
        time.sleep(3)  # wait for first schedule
        yield ssg


def test_fetcher(ssg, mock_sites):
    for site in mock_sites:
        for file, content in files.items():
            assert (Path(ssg.fetcher.store_dir) / f"{site.id}_{site.name}" / file).exists()
            assert (
                Path(ssg.fetcher.store_dir) / f"{site.id}_{site.name}" / file
            ).read_bytes() == content


def test_ssg_render_page(app, ssg, mock_sites):
    for site in mock_sites:
        for file, content in files.items():
            with app.test_request_context():
                res = ssg.render_page(site, file)
            if file.startswith("static"):
                assert res.status_code == 200
                data = b"".join(res.iter_encoded())
                assert data == content
            elif file.startswith("jinja"):
                assert res.status_code == 403
            else:
                assert res.status_code == 200
                data = b"".join(res.iter_encoded())
                assert data == b"hello " + site.name.encode()


def test_ssg_pack_site(ssg, mock_sites):
    for site in mock_sites:
        with ssg.pack_site(site) as zf:  # type: zipfile.ZipFile
            for file, content in files.items():
                if file.startswith("static"):
                    assert zf.read(file) == content
                elif file.startswith("jinja"):
                    assert file not in zf.namelist()
                else:
                    assert zf.read(file) == b"hello " + site.name.encode()
