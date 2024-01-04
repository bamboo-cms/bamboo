from apiflask import APIBlueprint, abort

from bamboo.database import db
from bamboo.database.models import City, Organization, Partnership
from bamboo.schemas.partnership import (
    PartnershipByCityIn,
    PartnershipByPrimaryIn,
    PartnershipIn,
    PartnershipOut,
)

partnership = APIBlueprint("partnership ", __name__)


@partnership.get("/")
@partnership.input(PartnershipByPrimaryIn, location="query")
@partnership.output(PartnershipOut)
def get_partnership(query_data):
    return db.get_or_404(Partnership, query_data)


@partnership.get("/list")
@partnership.input(PartnershipByCityIn, location="query")
@partnership.output(PartnershipOut(many=True))
def get_partnership_query(query_data):
    query = db.select(Partnership)
    if "city_id" in query_data:
        city = db.session.get(City, query_data.pop("city_id"))
        if not city:
            return []
        query = query.filter_by(city=city)
    return db.session.execute(query).scalars()


@partnership.post("/")
@partnership.input(PartnershipIn, location="json")
@partnership.output(PartnershipOut)
def create_partnership(json_data):
    city = db.session.get(City, json_data.pop("city_id"))
    if not city:
        abort(404, message="City not found")
    json_data["city"] = city

    organization = db.session.get(Organization, json_data.pop("organization_id"))
    if not organization:
        abort(404, message="Organization not found")
    json_data["organization"] = organization

    payload = Partnership(**json_data)
    db.session.add(payload)
    db.session.commit()
    return payload


@partnership.patch("/")
@partnership.input(PartnershipIn(partial=True), location="json")
@partnership.output(PartnershipOut)
def update_partnership(json_data):
    if "city_id" not in json_data or "organization_id" not in json_data:
        abort(422, message="Missing city_id or organization_id")
    payload = db.get_or_404(
        Partnership,
        {
            "city_id": json_data["city_id"],
            "organization_id": json_data["organization_id"],
        },
    )

    if "category" in json_data:
        payload.category = json_data["category"]
    db.session.commit()
    return payload


@partnership.delete("/")
@partnership.input(PartnershipIn, location="query")
@partnership.output({}, status_code=204)
def delete_partnership(query_data):
    payload = db.get_or_404(
        Partnership,
        {
            "city_id": query_data["city_id"],
            "organization_id": query_data["organization_id"],
        },
    )
    db.session.delete(payload)
    db.session.commit()
    return ""
