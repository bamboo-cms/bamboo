from apiflask import APIBlueprint
from flask import current_app

from bamboo.database.models import Site
from bamboo.ssg import SSG

ssg = APIBlueprint("ssg", __name__)


@ssg.get("/<int:site_id>/<path:file>")
def render(site_id: int, file: str):
    site = Site.query.get(site_id)
    if not site:
        return "Site not found.", 404
    generator: SSG = current_app.extensions["ssg"]
    return generator.render_page(site, file)
