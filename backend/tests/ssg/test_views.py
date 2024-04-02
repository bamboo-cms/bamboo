from pathlib import Path
import shutil
import pytest

from bamboo.database.models import Site


@pytest.fixture(autouse=True)
def ssg(site: Site, example_template_path: Path):
    dest = Path(".") / "data" / "templates" / f"{site.id}_{site.name}"
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(example_template_path, dest)
    yield
    shutil.rmtree(dest)


def test_views(client, site, example_template_path):
    res = client.get(f"/ssg/?site_id={site.id}")
    assert res.status_code == 200
    content = res.get_data(as_text=True)
    assert content.find(f"{site.name} | PyCon China") != -1
    assert content.find(f'<link rel="stylesheet" href="static/style.css?site_id={site.id}" />') != -1
    assert content.find(f'<a href="test.html?a=1&site_id={site.id}">Go</a>') != -1
    assert content.find(f'<script src="static/script.js?site_id={site.id}"></script>') != -1

    res = client.get(f"/ssg/static/style.css?site_id={site.id}")
    assert res.status_code == 200
    assert res.get_data() == (example_template_path / "static" / "style.css").read_bytes()

    res = client.get(f"/ssg/static/script.js?site_id={site.id}")
    assert res.status_code == 200
    assert res.get_data() == (example_template_path / "static" / "script.js").read_bytes()
