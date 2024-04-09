import pytest

from bamboo.blueprints.auth import Permission
from bamboo.database import db, models


def test_get_cities_permission(client):
    rv = client.get("/api/city/all")
    assert rv.status_code == 401


@pytest.mark.parametrize("permission", [Permission.CITY, Permission.USER, Permission.CONTENT])
def test_get_cities(client, auth):
    response = client.get("api/city/all", auth=auth)
    assert response.status_code == 200
    assert response.json == []

    site = models.Site(name="Somewhere")
    city = models.City(name="Shanghai", site=site)
    db.session.add(city)
    db.session.commit()

    response = client.get("api/city/all", auth=auth)
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]["name"] == city.name


@pytest.mark.parametrize("permission", [Permission.USER])
def test_get_city(client, auth):
    response = client.get("api/city/999", auth=auth)
    assert response.status_code == 404

    site = models.Site(name="Somewhere")
    city = models.City(name="Chengdu", site=site)
    db.session.add(city)
    db.session.commit()

    response = client.get(f"api/city/{city.id}", auth=auth)
    assert response.status_code == 200
    assert response.json["name"] == city.name


@pytest.mark.parametrize(
    "permission", [Permission.USER, Permission.CONTENT, Permission.USER | Permission.CONTENT]
)
def test_modify_city_permission(client, auth):
    response = client.post("api/city", json={"name": "Hangzhou", "site_id": 0}, auth=auth)
    assert response.status_code == 403

    site = models.Site(name="Somewhere")
    city = models.City(name="Beijing", site=site)
    db.session.add(city)
    db.session.commit()

    response = client.patch(f"api/city/{city.id}", json={"name": "Guangzhou"}, auth=auth)
    assert response.status_code == 403

    response = client.delete(f"api/city/{city.id}", auth=auth)
    assert response.status_code == 403


@pytest.mark.parametrize("permission", [Permission.CITY, Permission.CITY | Permission.CONTENT])
def test_create_city(client, auth):
    response = client.post("api/city", json={}, auth=auth)
    assert response.status_code == 422
    assert response.json["message"] == "Validation error"
    assert len(response.json["detail"]["json"]) == 2

    site = models.Site(name="Somewhere")
    db.session.add(site)
    db.session.commit()

    payload = {"name": "Chongqing", "site_id": site.id}
    response = client.post("api/city", json=payload, auth=auth)
    assert response.status_code == 201
    assert response.json["name"] == payload["name"]
    city_id = response.json["id"]

    response = client.get(f"api/city/{city_id}", auth=auth)
    assert response.json["name"] == payload["name"]


@pytest.mark.parametrize("permission", [Permission.CITY, Permission.CITY | Permission.CONTENT])
def test_update_city(client, auth):
    site = models.Site(name="Somewhere")
    db.session.add(site)
    db.session.commit()

    response = client.post(
        "api/city",
        json={"name": "Shenzhen", "registration_url": "https://foo.bar", "site_id": site.id},
        auth=auth,
    )
    city_id = response.json["id"]
    assert response.status_code == 201
    assert response.json["registration_url"] == "https://foo.bar"

    payload_update = {"registration_url": "https://baz.qux"}
    response = client.patch(f"api/city/{city_id}", json=payload_update, auth=auth)
    assert response.json["registration_url"] == payload_update["registration_url"]

    response = client.get(f"api/city/{city_id}", auth=auth)
    assert response.json["registration_url"] == payload_update["registration_url"]


@pytest.mark.parametrize("permission", [Permission.CITY, Permission.CITY | Permission.CONTENT])
def test_delete_city(client, auth):
    response = client.delete("api/city/999", auth=auth)
    assert response.status_code == 404

    site = models.Site(name="Somewhere")
    city = models.City(name="Xuzhou", site=site)
    db.session.add(city)
    db.session.commit()

    response = client.delete(f"api/city/{city.id}", auth=auth)
    assert response.status_code == 204

    response = client.get(f"api/city/{city.id}", auth=auth)
    assert response.status_code == 404
