from pathlib import Path

from flask import current_app, g
import jinja2

from bamboo.database.models import Site
            

def loader_func(base_dir: Path):
    def loader(tpl_name: str) -> str:
        return (base_dir / tpl_name).read_text()
    return loader
            

class Environment(jinja2.Environment):
    def join_path(self, template: str, parent: str) -> str:
        # if parent is not None, it is the name of the template that is including or importing the template.
        if parent:
            ps = parent.split("/", 1)
            if len(ps) == 1:
                return template
            prefix = ps[0]
            return f"{prefix}/{template}"
        return template
    

def url_filter_func(url: str, site: Site) -> str:
    # if it packing site currently, do not add site_id
    if current_app.config.get("SSG_PACKING"):
        return url
    if "?" in url:
        return f"{url}&site_id={site.id}"
    return f"{url}?site_id={site.id}"
