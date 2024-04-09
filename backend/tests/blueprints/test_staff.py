import pytest

from bamboo.blueprints.auth import Permission
from bamboo.database import db, models


def _prepare():
    user_role = models.Role(name="a_user_role", permissions=Permission.USER)
    profile = models.Media.from_file("test.png")
    user = models.User(name="john", profile_image=profile, role=user_role)
    city1 = models.City(name="Shanghai", site=models.Site(name="Somewhere"))
    city2 = models.City(name="Chongqing", site=models.Site(name="SomewhereAnother"))
    staff = models.Staff(city=city1, staff=user, category="sponsor")
    db.session.add_all([staff, city2])
    db.session.commit()
    return city1, city2, user, staff


@pytest.fixture()
def prepare_staff():
    yield _prepare()


def test_get_staffs_permission(client):
    rv = client.get("/api/staff/list?city_id=1")
    assert rv.status_code == 401


@pytest.mark.parametrize("permission", [Permission.STAFF, Permission.USER, Permission.CONTENT])
def test_get_staffs(client, auth):
    response = client.get("api/staff/list", auth=auth)
    assert response.status_code == 200
    assert response.json == []

    city1, city2, user, staff = _prepare()

    response = client.get("api/staff/list", auth=auth)
    assert response.status_code == 200
    assert len(response.json) == 1

    the_staff = response.json[0]
    assert the_staff["category"] == "sponsor"
    assert the_staff["staff"]["name"] == user.name and the_staff["city"]["name"] == city1.name

    response = client.get(f"api/staff/list?city_id={city1.id}", auth=auth)
    assert response.status_code == 200
    assert len(response.json) == 1

    response = client.get(f"api/staff/list?city_id={city2.id}", auth=auth)
    assert response.status_code == 200
    assert len(response.json) == 0

    response = client.get("api/staff/list?city_id=100", auth=auth)
    assert response.status_code == 200
    assert len(response.json) == 0


@pytest.mark.parametrize("permission", [Permission.USER])
def test_get_staff(client, auth, prepare_staff):
    city1, city2, user, staff = prepare_staff

    response = client.get(f"api/staff?city_id={city1.id}", auth=auth)
    assert response.status_code == 422

    response = client.get(f"api/staff?city_id={city1.id}&staff_id={user.id}", auth=auth)
    assert response.status_code == 200
    assert (
        response.json["staff"]["name"] == user.name and response.json["city"]["name"] == city1.name
    )


@pytest.mark.parametrize(
    "permission", [Permission.USER, Permission.CONTENT, Permission.USER | Permission.CONTENT]
)
def test_modify_staff_permission(client, auth, prepare_staff):
    city1, city2, user, staff = prepare_staff
    response = client.post(
        "api/staff",
        json={"city_id": city2.id, "staff_id": user.id, "category": "supporting"},
        auth=auth,
    )
    assert response.status_code == 403

    response = client.patch(
        "api/staff",
        json={"city_id": city1.id, "staff_id": user.id, "category": "sponsor"},
        auth=auth,
    )
    assert response.status_code == 403

    response = client.delete(
        "api/staff", auth=auth, json={"city_id": city1.id, "staff_id": user.id}
    )
    assert response.status_code == 403


@pytest.mark.parametrize("permission", [Permission.STAFF, Permission.STAFF | Permission.CONTENT])
def test_create_staff(client, auth, prepare_staff):
    city1, city2, user, staff = prepare_staff
    response = client.post("api/staff", json={"city_id": city2.id}, auth=auth)
    assert response.status_code == 422
    assert response.json["message"] == "Validation error"
    assert len(response.json["detail"]["json"]) == 2

    payload = {"city_id": city2.id, "staff_id": user.id, "category": "sponsor"}
    response = client.post("api/staff", json=payload, auth=auth)
    assert response.status_code == 201
    assert response.json["staff"]["name"] == user.name
    assert response.json["city"]["name"] == city2.name


@pytest.mark.parametrize("permission", [Permission.STAFF, Permission.STAFF | Permission.CONTENT])
def test_update_staff(client, auth, prepare_staff):
    city1, _, user, staff = prepare_staff
    response = client.patch(
        "api/staff",
        json={"city_id": city1.id, "staff_id": user.id, "category": "supporting"},
        auth=auth,
    )
    assert response.status_code == 200
    assert response.json["category"] == "supporting"


@pytest.mark.parametrize("permission", [Permission.STAFF, Permission.STAFF | Permission.CONTENT])
def test_delete_staff(client, auth, prepare_staff):
    city1, city2, user, staff = prepare_staff
    response = client.delete(
        "api/staff", auth=auth, json={"city_id": city2.id, "staff_id": user.id}
    )
    assert response.status_code == 404

    response = client.delete(
        "api/staff", auth=auth, json={"city_id": city1.id, "staff_id": user.id}
    )
    assert response.status_code == 204

    response = client.get(f"api/staff?city_id={city1.id}&staff_id={user.id}", auth=auth)
    assert response.status_code == 404
