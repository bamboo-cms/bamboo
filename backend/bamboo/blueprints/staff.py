from apiflask import APIBlueprint, abort

from bamboo.blueprints.auth import Permission, token_auth
from bamboo.database import db
from bamboo.database.models import City, Staff, User
from bamboo.schemas.staff import StaffByCityIn, StaffByPrimaryIn, StaffIn, StaffOut

staff = APIBlueprint("staff", __name__)


@staff.get("")
@staff.input(StaffByPrimaryIn, location="query")
@staff.output(StaffOut)
@token_auth.auth_required
def get_staff(query_data):
    return db.get_or_404(Staff, query_data)


@staff.get("/list")
@staff.input(StaffByCityIn, location="query")
@staff.output(StaffOut(many=True))
@token_auth.auth_required
def list_staffs(query_data):
    query = db.select(Staff)
    if "city_id" in query_data:
        city = db.session.get(City, query_data.pop("city_id"))
        if not city:
            return []
        query = query.filter_by(city=city)
    return db.session.scalars(
        query.join(User, Staff.staff)
        .filter(User.active.is_(True))
        .order_by(Staff.created_at.desc())
    ).all()


@staff.post("")
@staff.input(StaffIn, location="json")
@staff.output(StaffOut, status_code=201)
@token_auth.auth_required(permissions=Permission.STAFF)
def create_staff(json_data):
    city = db.session.get(City, json_data.pop("city_id"))
    if not city:
        abort(404, message="City not found")

    user = db.session.get(User, json_data.pop("staff_id"))
    if not user:
        abort(404, message="User not found")

    payload = Staff(city=city, staff=user, category=json_data["category"])
    db.session.add(payload)
    db.session.commit()
    return payload


@staff.patch("")
@staff.input(StaffIn(partial=True), location="json")
@staff.output(StaffOut)
@token_auth.auth_required(permissions=Permission.STAFF)
def update_staff(json_data):
    if "city_id" not in json_data or "staff_id" not in json_data:
        abort(422, message="Missing city_id or staff_id")
    the_staff = db.get_or_404(
        Staff,
        {
            "city_id": json_data["city_id"],
            "staff_id": json_data["staff_id"],
        },
    )

    if "category" in json_data:
        the_staff.category = json_data["category"]
    db.session.commit()
    return the_staff


@staff.delete("")
@staff.input(StaffByPrimaryIn, location="json")
@staff.output({}, status_code=204)
@token_auth.auth_required(permissions=Permission.STAFF)
def delete_staff(json_data):
    the_staff = db.get_or_404(
        Staff,
        {
            "city_id": json_data["city_id"],
            "staff_id": json_data["staff_id"],
        },
    )
    db.session.delete(the_staff)
    db.session.commit()
    return ""
