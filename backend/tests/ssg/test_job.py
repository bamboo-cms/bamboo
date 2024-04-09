from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from bamboo.database.models import Site
from bamboo.jobs import sync_templates


@pytest.mark.usefixtures("mock_template_download")
def test_job(site: Site, example_template_path: Path):
    with TemporaryDirectory() as tmp_dir:
        sync_templates(Path(tmp_dir))
        path = Path(tmp_dir) / f"{site.id}_{site.name}"
        assert path.exists(), "Templates not synced"
        for file in example_template_path.rglob("*"):
            if file.is_file():
                p = path / file.relative_to(example_template_path)
                assert p.exists(), f"File {p} not synced"
                assert p.read_text() == file.read_text(), f"File {p} content not synced"
