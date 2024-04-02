import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

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


def test_pack(ssg: SSG, site: Site, example_template_path):
    with ssg.pack(site) as path:
        with TemporaryDirectory() as tmp:
            ZipFile(path, "r").extractall(tmp)
            assert (Path(tmp) / "static" / "style.css").read_bytes() == (
                example_template_path / "static" / "style.css"
            ).read_bytes()
            assert (Path(tmp) / "static" / "script.js").read_bytes() == (
                example_template_path / "static" / "script.js"
            ).read_bytes()

            content = (Path(tmp) / "index.html").read_text()
            assert content.find(f"{site.name} | PyCon China") != -1
            assert content.find('<link rel="stylesheet" href="static/style.css" />') != -1
            assert content.find('<a href="test.html?a=1">Go</a>') != -1
            assert content.find('<script src="static/script.js"></script>') != -1
