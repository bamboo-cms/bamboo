from apiflask import APIBlueprint
from bamboo.database import db
from bamboo.database.models import Venue
from bamboo.schemas.venue import VenueIn, VenueOut

venue = APIBlueprint("venue", __name__)


@venue.get("/<int:venue_id>")
@venue.output(VenueOut)
def get_venue(venue_id):
    return Venue.query.get_or_404(venue_id)


@venue.post("/")
@venue.input(VenueIn, location="json")
@venue.output(VenueOut, status_code=201)
def create_venue(json_data):
    venue = Venue(**json_data)
    db.session.add(venue)
    db.session.commit()
    return venue


@venue.patch("/<int:venue_id>")
@venue.input(VenueIn(partial=True), location="json")
@venue.output(VenueOut)
def update_venue(venue_id, json_data):
    venue = Venue.query.get_or_404(venue_id)
    for attr, value in json_data.items():
        setattr(venue, attr, value)
    db.session.commit()
    return venue


@venue.delete("/<int:venue_id>")
@venue.output({}, status_code=204)
def delete_venue(venue_id):
    venue = Venue.query.get_or_404(venue_id)
    db.session.delete(venue)
    db.session.commit()
    return ""
