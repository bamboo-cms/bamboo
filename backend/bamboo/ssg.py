import logging
import re
import shutil
import tempfile
import threading
import zipfile
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from datetime import timedelta
from pathlib import Path
from typing import Generator, Optional

import httpx
import jinja2
from flask import Flask, Response, send_from_directory
from flask_apscheduler import APScheduler

from bamboo.database.models import Site

logger = logging.getLogger(__name__)


reserved_dir = "jinja"  # Reserved for Jinja2, can not be accessed from web.
static_dir = "static"  # JS, CSS, Image, etc. Send to browser directly.


class SSG:
    """
    Static site generator.
    """

    fetcher: "Fetcher"

    def __init__(self, app: Optional[Flask] = None):
        if app is not None:
            self.init_app(app)
        self.tpl_dir = (
            Path(__file__).parent.parent.parent / "data" / "templates"
        )  # 'data' in root of project

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
        self.fetcher = Fetcher(minutes, scheduler, self.tpl_dir)
        self.fetcher.schedule()
        app.teardown_appcontext(lambda e: self.fetcher.stop())

    def render_page(self, site: Site, path: str) -> Response:
        """
        Renders a page.

        :param site: Site to render.
        :param path: Path to render, it **must be not** startswith "/".
        """
        if path.startswith(reserved_dir):
            return Response(f"Reserved path: {path}", status=403, mimetype="text/plain")
        elif path.startswith(static_dir):
            asset_path = Path(f"{site.id}_{site.name}") / path
            return send_from_directory(self.tpl_dir, asset_path)
        try:
            jinja_env = self.fetcher.get_jinja_env(site)
            template = jinja_env.get_template(path)
            page = template.render(site=site)
        except (jinja2.TemplateNotFound, FileNotFoundError) as e:
            logger.warning(f"Template not found: {e}")
            return Response(f"Template not found: {e}", status=404, mimetype="text/plain")
        return Response(page, mimetype="text/html")

    @contextmanager
    def pack_site(self, site: Site) -> Generator[zipfile.ZipFile, None, None]:
        """
        Packs a site into a zip file.

        :param site: Site to pack.
        :raises jinja2.TemplateNotFound: If template not found.
        """
        site_dir = self.tpl_dir / f"{site.id}_{site.name}"
        if not site_dir.exists():
            raise FileNotFoundError(f"Site not found: {site.id}_{site.name}")
        with tempfile.NamedTemporaryFile(suffix=".zip") as tmp:
            with zipfile.ZipFile(tmp, "w") as zip_file:
                # render page
                for tpl_path in site_dir.glob("**/*.html"):
                    if tpl_path.is_dir():
                        continue
                    # ignore reserved dir and static dir
                    if tpl_path.relative_to(site_dir).parts[0] in (reserved_dir, static_dir):
                        continue
                    tpl_rel_path = tpl_path.relative_to(site_dir)
                    try:
                        jinja_env = self.fetcher.get_jinja_env(site)
                        tpl = jinja_env.get_template(str(tpl_rel_path))
                        page = tpl.render(site=site)
                    except (jinja2.TemplateNotFound, FileNotFoundError) as e:
                        logger.error(f"Template not found: {e}")
                        raise
                    p = tpl_path.relative_to(site_dir)
                    zip_file.writestr(str(p), page)
                # copy static files
                for static_path in site_dir.glob(f"{static_dir}/**/*"):
                    if static_path.is_dir():
                        continue
                    p = static_path.relative_to(site_dir)
                    zip_file.write(static_path, str(p))
                yield zip_file


gh_pattern = re.compile(r"https://github\.com/(?P<owner>\S+)/(?P<repo>\S+)")


class Fetcher:
    """
    Fetches templates from remote source and stores them locally.

    :param sync_interval: Interval between syncs with remote source.
    :param config: Configuration of the fetcher. For example, GH-TOKEN.
    """

    def __init__(
        self,
        sync_interval: timedelta,
        scheduler: APScheduler,
        store_dir: Path,
        config: Optional[dict] = None,
    ):
        self.sync_interval = sync_interval
        self.store_dir = store_dir
        self.client = httpx.Client()
        self.scheduler = scheduler
        self.config = config or {}
        self._jinja_envs: dict[str, jinja2.Environment] = {}
        self._jinja_envs_lock = threading.Lock()

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

    def get_jinja_env(self, site: Site) -> jinja2.Environment:
        name = f"{site.id}_{site.name}"
        path = self.store_dir / name
        with self._jinja_envs_lock:
            if not path.exists():
                if name in self._jinja_envs:
                    del self._jinja_envs[name]
                raise FileNotFoundError(f"Site {site.id} not found.")
            if name not in self._jinja_envs:
                self._jinja_envs[name] = jinja2.Environment(
                    loader=jinja2.FileSystemLoader(str(path))
                )
            return self._jinja_envs[name]

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
            dest = self.store_dir / name
            if dest.exists():
                shutil.rmtree(dest)
            with tempfile.TemporaryDirectory() as tmp_dir:
                zip_file.extractall(tmp_dir)
                shutil.copytree(Path(tmp_dir) / dir_name, dest)
            zip_file.close()
            logger.info(f"Stored {name} at {dest.absolute()}")
