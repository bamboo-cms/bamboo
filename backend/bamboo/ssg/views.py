from typing import TYPE_CHECKING

from flask import Blueprint, current_app, g, request
from flask_frozen import Freezer

from bamboo.database import db
from bamboo.database.models import Site

if TYPE_CHECKING:
    from bamboo.ssg.core import SSG


# TODO: How to implement auth for this blueprint?
# These pages canot not use token based auth.
# Session / Cookies?
site_bp = Blueprint("ssg", __name__)

freezer = Freezer()


@site_bp.before_request
def validate_site_id():
    if current_app.config.get("SSG_PACKING") and current_app.config.get("SSG_SITE"):
        g.ssg_site = current_app.config.get("SSG_SITE")
        return

    site_id = request.args.get("site_id")
    if not site_id:
        return "site_id is required", 400
    elif not site_id.isdigit():
        return "invalid site_id", 400
    site = db.get_or_404(Site, int(site_id))
    g.ssg_site = site


@site_bp.errorhandler(404)
def page_not_found(error: Exception):
    if g.ssg_site:
        ssg: "SSG" = current_app.extensions["ssg"]
        return ssg.render(g.ssg_site, "404.html")
    return "resource not found", 404


@site_bp.get("/static/<path:filename>")
def static(filename: str):
    ssg: "SSG" = current_app.extensions["ssg"]
    return ssg.render(g.ssg_site, f"static/{filename}")


@freezer.register_generator
def static_gen():
    if g.ssg_site:
        ssg: "SSG" = current_app.extensions["ssg"]
        path = ssg.tpl_dir / f"{g.ssg_site.id}_{g.ssg_site.name}" / "static"
        for file in path.rglob("*"):
            if file.is_file():
                yield "ssg.static", {"filename": file.name}


@site_bp.get("/")
def index():
    ssg: "SSG" = current_app.extensions["ssg"]
    return ssg.render(g.ssg_site, "index.html")
