from apiflask import APIBlueprint, abort

from bamboo.database import db
from bamboo.database.models import Media, Organization
from bamboo.schemas.organization import OrganizationIn, OrganizationOut

organization = APIBlueprint("organization ", __name__)


@organization.get("/<int:organization_id>")
@organization.output(OrganizationOut)
def get_organization(organization_id):
    return db.get_or_404(Organization, organization_id)


@organization.post("/")
@organization.input(OrganizationIn, location="json")
@organization.output(OrganizationOut)
def create_organization(json_data):
    image = db.session.get(Media, json_data.pop("profile_image_id"))
    if not image:
        abort(404, message="Image not found")
    json_data["profile_image"] = image

    payload = Organization(**json_data)
    db.session.add(payload)
    db.session.commit()
    return payload


@organization.patch("/<int:organization_id>")
@organization.input(OrganizationIn(partial=True), location="json")
@organization.output(OrganizationOut)
def update_organization(organization_id, json_data):
    payload = db.get_or_404(Organization, organization_id)

    if "profile_image_id" in json_data:
        image = db.session.get(Media, json_data.pop("profile_image_id"))
        if not image:
            abort(404, message="Image not found")
        json_data["profile_image"] = image

    for attr, value in json_data.items():
        setattr(payload, attr, value)
    db.session.commit()
    return payload


@organization.delete("/<int:organization_id>")
@organization.output({}, status_code=204)
def delete_organization(organization_id):
    payload = db.get_or_404(Organization, organization_id)
    db.session.delete(payload)
    db.session.commit()
    return ""
