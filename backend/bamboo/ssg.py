import logging
import tempfile
import threading
import zipfile
from contextlib import contextmanager
from datetime import timedelta
from pathlib import Path
from typing import Generator, Optional

import jinja2
from flask import Flask, Response, send_from_directory
from flask_rq2 import RQ

from bamboo.database.models import Site
from bamboo.jobs import sync_templates

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
        if hasattr(app, "extensions") and "rq2" in app.extensions:
            rq2: RQ = app.extensions["rq2"]
        else:
            raise RuntimeError("RQ is not initialized.")
        gh_token = app.config.get("SSG_GH_TOKEN")
        config = {}
        if gh_token:
            config["GH_TOKEN"] = gh_token
        self.fetcher = Fetcher(minutes, rq2, self.tpl_dir, config)
        if not app.config.get("TESTING"):
            self.fetcher.schedule()

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


class Fetcher:
    """
    Fetches templates from remote source and stores them locally.

    :param sync_interval: Interval between syncs with remote source.
    :param config: Configuration of the fetcher. For example, GH-TOKEN.
    """

    def __init__(
        self,
        sync_interval: timedelta,
        rq: RQ,
        store_dir: Path,
        config: Optional[dict] = None,
    ):
        self.sync_interval = sync_interval
        self.store_dir = store_dir
        self.rq = rq
        self.config = config or {}
        self._jinja_envs: dict[str, jinja2.Environment] = {}
        self._jinja_envs_lock = threading.Lock()

    def schedule(self):
        """
        Schedules the fetcher.
        """
        logger.info(f"Scheduling sync with interval {self.sync_interval}")
        sync_templates(self.store_dir, self.sync_interval, self.config.get("GH_TOKEN", None))

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
