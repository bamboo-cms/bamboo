import logging
import re
import shutil
import tempfile
import zipfile
from datetime import timedelta
from pathlib import Path
from typing import Optional

import httpx
from flask import Flask
from flask_rq2 import RQ

from bamboo.database.models import Site

rq = RQ()
logger = logging.getLogger(__name__)

gh_pattern = re.compile(r"https://github\.com/(?P<owner>\S+)/(?P<repo>\S+)")


@rq.job
def sync_templates(store_dir: Path, sync_interval: timedelta, gh_token: Optional[str] = None):
    logger.info("Syncing templates")
    for site in Site.query.all():
        if not site.config.get("sync") or not site.template_url:
            continue
        elif site.template_url.startswith("https://github.com"):
            name = f"{site.id}_{site.name}"
            fetch_template(name, site.template_url, store_dir, gh_token)
        else:
            logger.warning(f"Unsupported template URL: {site.template_url}, skipping.")
    sync_templates.schedule(sync_interval)


@rq.job
def fetch_template(name: str, url: str, store_dir: Path, gh_token: Optional[str] = None):
    logger.info(f"Fetching {name} from {url}")
    match = gh_pattern.match(url)
    if match is None or "owner" not in match.groupdict() or "repo" not in match.groupdict():
        logger.warning(f"Invalid GitHub URL: {url}, skipping.")
        return
    owner = match.group("owner")
    repo = match.group("repo")
    file_url = f"https://api.github.com/repos/{owner}/{repo}/zipball"
    headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    if gh_token:
        headers["Authorization"] = f"Bearer {gh_token}"
    with httpx.Client() as client:
        try:
            res = client.get(file_url, headers=headers, follow_redirects=True, timeout=30)
            res.raise_for_status()
        except httpx.HTTPError:
            logger.warning(f"Failed to fetch {file_url}, skipping.")
            return
    with tempfile.NamedTemporaryFile(suffix=".zip") as tmp:
        chunk_size = 128 * 1024  # 128 KB
        for chunk in res.iter_bytes(chunk_size):
            tmp.write(chunk)
        tmp.seek(0)
        try:
            zip_file = zipfile.ZipFile(tmp)
        except zipfile.BadZipFile:
            logger.warning(f"Bad zip file: {file_url}, skipping.")
            return
        if zip_file.testzip() is not None:
            logger.warning(f"Can not read zip file: {file_url}, skipping.")
            return
        if len(zip_file.namelist()) == 0:
            logger.warning(f"Empty zip file: {file_url}, skipping.")
            return
        dir_name = zip_file.namelist()[0].split("/")[0]
        dest = store_dir / name
        if dest.exists():
            shutil.rmtree(dest)
        with tempfile.TemporaryDirectory() as tmp_dir:
            zip_file.extractall(tmp_dir)
            shutil.copytree(Path(tmp_dir) / dir_name, dest)
        zip_file.close()
        logger.info(f"Stored {name} at {dest.absolute()}")


def init_app(app: Flask) -> None:
    rq.init_app(app)
