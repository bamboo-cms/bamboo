from apiflask import APIBlueprint

from bamboo.database import db
from bamboo.database.models import ScheduleItem
from bamboo.schemas.schedule_item import ScheduleItemIn, ScheduleItemOut

schedule_item = APIBlueprint("schedule_item", __name__)


@schedule_item.get("/<int:schedule_item_id>")
@schedule_item.output(ScheduleItemOut)
def get_schedule_item(schedule_item_id):
    return ScheduleItem.query.get_or_404(schedule_item_id)


@schedule_item.post("/")
@schedule_item.input(ScheduleItemIn, location="json")
@schedule_item.output(ScheduleItemOut, status_code=201)
def create_schedule_item(json_data):
    schedule_item = ScheduleItem(**json_data)
    db.session.add(schedule_item)
    db.session.commit()
    return schedule_item


@schedule_item.patch("/<int:schedule_item_id>")
@schedule_item.input(ScheduleItemIn(partial=True), location="json")
@schedule_item.output(ScheduleItemOut)
def update_schedule_item(schedule_item_id, json_data):
    schedule_item = ScheduleItem.query.get_or_404(schedule_item_id)
    for attr, value in json_data.items():
        setattr(schedule_item, attr, value)
    db.session.commit()
    return schedule_item


@schedule_item.delete("/<int:schedule_item_id>")
@schedule_item.output({}, status_code=204)
def delete_schedule_item(schedule_item_id):
    schedule_item = ScheduleItem.query.get_or_404(schedule_item_id)
    db.session.delete(schedule_item)
    db.session.commit()
    return ""
