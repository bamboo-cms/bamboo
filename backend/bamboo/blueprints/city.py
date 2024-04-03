from apiflask import APIBlueprint

from bamboo.blueprints.auth import Permission, token_auth
from bamboo.database import db
from bamboo.database.models import City, Site
from bamboo.schemas.city import CityIn, CityOut

city = APIBlueprint("city", __name__)


@city.get("/<int:city_id>")
@city.output(CityOut)
@token_auth.auth_required
def get_city(city_id):
    return db.get_or_404(City, city_id)


@city.get("/all")
@city.output(CityOut(many=True))
@token_auth.auth_required
def list_cities():
    return db.session.scalars(db.select(City).order_by(City.created_at.desc())).all()


@city.post("")
@city.input(CityIn, location="json")
@city.output(CityOut, status_code=201)
@token_auth.auth_required(permissions=Permission.CITY)
def create_city(json_data):
    city = City(**json_data)
    db.session.add(city)
    db.session.commit()
    return city


@city.patch("/<int:city_id>")
@city.input(CityIn(partial=True), location="json")
@city.output(CityOut)
@token_auth.auth_required(permissions=Permission.CITY)
def update_city(city_id, json_data):
    city = db.get_or_404(City, city_id)
    for attr, value in json_data.items():
        if attr == "site_id":
            site = db.get_or_404(Site, value)
            city.site = site
        else:
            setattr(city, attr, value)
    db.session.commit()
    return city


@city.delete("/<int:city_id>")
@city.output({}, status_code=204)
@token_auth.auth_required(permissions=Permission.CITY)
def delete_city(city_id):
    city = db.get_or_404(City, city_id)
    db.session.delete(city)
    db.session.commit()
    return ""
