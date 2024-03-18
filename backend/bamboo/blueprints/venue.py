from apiflask import APIBlueprint

from bamboo.database import db
from bamboo.database.models import ScheduleItem, Talk, Venue
from bamboo.schemas.venue import VenueIn, VenueOut, VenueSchedulesOut, VenueTalkOut

venue = APIBlueprint("venue", __name__)


@venue.get("/<int:venue_id>")
@venue.output(VenueTalkOut)
def get_venue(venue_id):
    venue = Venue.query.get_or_404(venue_id)
    schedule_items = ScheduleItem.query.filter_by(venue_id=venue_id).all()
    talk_ids = list({item.talk_id for item in schedule_items if item.talk_id is not None})
    if talk_ids is not None:
        talks = Talk.query.filter(Talk.id.in_(talk_ids)).all()
    return {
        "venue": venue,
        "talks": talks,
    }


@venue.get("/<int:venue_id>/schedules")
@venue.output(VenueSchedulesOut)
def get_venue_schedules(venue_id):
    venue = Venue.query.get_or_404(venue_id)
    schedule_items = ScheduleItem.query.filter_by(venue_id=venue_id).all()
    return {
        "venue": venue,
        "schedule_items": schedule_items,
    }


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
