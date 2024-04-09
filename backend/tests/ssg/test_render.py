import shutil
from pathlib import Path

import pytest
from apiflask import APIFlask

from bamboo.database.models import Site
from bamboo.ssg.core import SSG


@pytest.fixture
def ssg(app: APIFlask, site: Site, example_template_path: Path):
    dest = Path(".") / "data" / "templates" / f"{site.id}_{site.name}"
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(example_template_path, dest)
    yield app.extensions["ssg"]
    shutil.rmtree(dest)


def test_render(ssg: SSG, site: Site, example_template_path: Path):
    content = ssg.render(site, "static/style.css")
    assert content == (example_template_path / "static" / "style.css").read_bytes()

    content = ssg.render(site, "static/script.js")
    assert content == (example_template_path / "static" / "script.js").read_bytes()

    content = str(ssg.render(site, "index.html"))
    assert content.find(f"{site.name} | PyCon China") != -1
    assert (
        content.find(f'<link rel="stylesheet" href="static/style.css?site_id={site.id}" />') != -1
    )
    assert content.find(f'<a href="test.html?a=1&site_id={site.id}">Go</a>') != -1
    assert content.find(f'<script src="static/script.js?site_id={site.id}"></script>') != -1
