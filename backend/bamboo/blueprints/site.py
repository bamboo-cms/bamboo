from apiflask import APIBlueprint

from bamboo.database import db
from bamboo.database.models import Site
from bamboo.schemas.site import SiteIn, SiteOut

site = APIBlueprint("site", __name__)


@site.get("/<int:site_id>")
@site.output(SiteOut)
def get_site(site_id):
    return Site.query.get_or_404(site_id)


@site.get("/all")
@site.output(SiteOut(many=True))
def get_sites():
    return Site.query.all()


@site.post("")
@site.input(SiteIn, location="json")
@site.output(SiteOut, status_code=201)
def create_site(json_data):
    site = Site(**json_data)
    db.session.add(site)
    db.session.commit()
    return site


@site.patch("/<int:site_id>")
@site.input(SiteIn(partial=True), location="json")
@site.output(SiteOut)
def update_site(site_id, json_data):
    site = Site.query.get_or_404(site_id)
    for attr, value in json_data.items():
        setattr(site, attr, value)
    db.session.commit()
    return site


@site.delete("/<int:site_id>")
@site.output({}, status_code=204)
def delete_site(site_id):
    site = Site.query.get_or_404(site_id)
    db.session.delete(site)
    db.session.commit()
    return ""
