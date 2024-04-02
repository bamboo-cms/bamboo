from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory, NamedTemporaryFile
from typing import Generator
from zipfile import ZipFile
from flask import Flask, abort
import jinja2

from bamboo.database.models import Site
from bamboo.jobs import sync_templates
from bamboo.ssg.template import loader_func, Environment, url_filter_func
from bamboo.ssg.views import site_bp, freezer


static_dir = "static"  # JS, CSS, Image, etc. Send to browser directly.



class SSG:
    def __init__(self, app: Flask, url_prefix: str, sync_interval: int):
        self.tpl_dir = Path(".") / "data" / "templates"  # 'data' in work dir
        self.tpl_dir.mkdir(parents=True, exist_ok=True)
        app.register_blueprint(site_bp, url_prefix=url_prefix)
        gh_token = app.config.get("SSG_GH_TOKEN")
        sync_templates.cron(f"*/{sync_interval} * * * *", args=(self.tpl_dir,), kwargs={"gh_token": gh_token}, name="ssg")

        self.jinja_env = Environment(loader=jinja2.FunctionLoader(loader_func(self.tpl_dir)))
        self.jinja_env.filters["url"] = url_filter_func

    def render(self, site: Site, tpl_file: str, **kwargs) -> bytes | str:
        """
        Render a template file for a site.

        :param site: Site object, used for context data
        :param tpl_file: Template file name
        :param kwargs: Extra context data
        """
        if tpl_file.startswith(static_dir):
            return self._send_static(site, tpl_file)
        return self._render_template(site, tpl_file, **kwargs)
    
    def _send_static(self, site: Site, file: str):
        path = self.tpl_dir / f"{site.id}_{site.name}" / file
        if not path.exists():
            abort(404)
        return path.read_bytes()
    
    def _render_template(self, site: Site, tpl_file: str, **kwargs):
        tpl_name = f"{site.id}_{site.name}/{tpl_file}"
        try:
            tpl = self.jinja_env.get_template(tpl_name)
        except jinja2.TemplateNotFound:
            abort(404)
        return tpl.render(site=site, **kwargs)
    
    @contextmanager
    def pack(self, site: Site) -> Generator[Path, None, None]:
        """
        Pack all templates for a site into a zip file.
        """
        app = Flask("dummy", static_folder=None)
        app.register_blueprint(site_bp)
        app.config["SSG_PACKING"] = True
        app.config["SSG_SITE"] = site
        if not hasattr(app, "extensions"):
            app.extensions = {}
        app.extensions["ssg"] = self
        with TemporaryDirectory() as tmpdir:
            app.config["FREEZER_DESTINATION"] = str(tmpdir)
            freezer.init_app(app)
            freezer.freeze()
            with NamedTemporaryFile("w+b", suffix=".zip") as tmpfile:
                with ZipFile(tmpfile, "w") as zfile:
                    for file in Path(tmpdir).rglob("*"):
                        if file.is_file():
                            zfile.write(file, file.relative_to(tmpdir))
                yield Path(tmpfile.name)

