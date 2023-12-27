import logging
import re
import shutil
import tempfile
import zipfile
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from pathlib import Path
from typing import Optional

import httpx
from flask import Flask
from flask_apscheduler import APScheduler

from bamboo.database.models import Site

logger = logging.getLogger(__name__)


class SSG:
    def __init__(self, app: Optional[Flask] = None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask):
        if not hasattr(app, "extensions"):
            app.extensions = {}
        app.extensions["ssg"] = self
        sync_interval = app.config.get("SSG_SYNC_INTERVAL", "3")
        minutes = timedelta(minutes=float(sync_interval))
        if hasattr(app, "apscheduler"):
            scheduler: APScheduler = app.apscheduler
        else:
            raise RuntimeError("APScheduler is not initialized.")
        fetcher = Fetcher(minutes, scheduler)
        fetcher.schedule()
        app.teardown_appcontext(lambda e: fetcher.stop())


gh_pattern = re.compile(r"https://github\.com/(?P<owner>\S+)/(?P<repo>\S+)")


class Fetcher:
    """
    Fetches templates from remote source and stores them locally.

    :param sync_interval: Interval between syncs with remote source.
    :param config: Configuration of the fetcher. For example, GH-TOKEN.
    """

    def __init__(
        self, sync_interval: timedelta, scheduler: APScheduler, config: Optional[dict] = None
    ):
        self.sync_interval = sync_interval
        self.store_dir = (
            Path(__file__).parent.parent.parent / "data" / "templates"  # 'data' in root of project
        )
        self.client = httpx.Client()
        self.scheduler = scheduler
        self.config = config or {}

    def sync(self):
        """
        Syncs with remote source.
        """
        logger.info("Syncing templates")
        with ThreadPoolExecutor(max_workers=5) as executor:
            with self.scheduler.app.app_context():
                for site in Site.query.all():
                    if site.template_url.startswith("https://github.com"):
                        name = f"{site.id}_{site.name}"
                        executor.submit(self._fetch_gh, name, site.template_url, site.config)
                    else:
                        logger.warning(f"Unsupported template URL: {site.template_url}, skipping.")

    def schedule(self):
        """
        Schedules the fetcher.
        """
        logger.info(f"Scheduling sync with interval {self.sync_interval}")
        self.scheduler.add_job(
            "SSG", self.sync, trigger="interval", seconds=self.sync_interval.total_seconds()
        )

    def stop(self):
        """
        Stops the fetcher.
        """
        self.client.close()

    @property
    def _gh_headers(self):
        headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
        if "GH-TOKEN" in self.config:
            headers["Authorization"] = f'Bearer {self.config.get("GH-TOKEN")}'
        return headers

    def _fetch_gh(self, name: str, url: str, config: Optional[dict] = None):
        """
        Fetches a template from GitHub.

        TODO: Check if repo is updated.

        :param name: Name of the template, it must be able to use as folder name.
        :param url: URL of the template.
        :param config: Configuration of the template.
        """
        logger.info(f"Fetching {name} from {url}")
        match = gh_pattern.match(url)
        if match is None or "owner" not in match.groupdict() or "repo" not in match.groupdict():
            logger.warning(f"Invalid GitHub URL: {url}, skipping.")
            return
        owner = match.group("owner")
        repo = match.group("repo")
        file_url = f"https://api.github.com/repos/{owner}/{repo}/zipball"
        try:
            res = self.client.get(
                file_url, headers=self._gh_headers, follow_redirects=True, timeout=30
            )
            res.raise_for_status()
        except httpx.HTTPError:
            logger.warning(f"Failed to fetch {file_url}, skipping.")
            return
        tmp = tempfile.NamedTemporaryFile(suffix=".zip")
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
        dest = self.store_dir / name
        if dest.exists():
            shutil.rmtree(dest)
        with tempfile.TemporaryDirectory() as tmp_dir:
            zip_file.extractall(tmp_dir)
            shutil.copytree(Path(tmp_dir) / dir_name, dest)
        logger.info(f"Stored {name} at {dest.absolute()}")
