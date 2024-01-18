from datetime import datetime

from bamboo.database import db, models


def test_get_venue(client):
    response = client.get("/api/venue/-1")
    assert response.status_code == 404

    site = models.Site(name="Test site", config={})
    city = models.City(name="Test city", site=site)
    talk = models.Talk(title="Test talk", content="Test talk content", site=site)
    db.session.add_all([site, city, talk])
    db.session.commit()

    response = client.post(
        "/api/venue/", json={"name": "Venue 1", "address": "Test Address 1", "city_id": city.id}
    )
    assert response.status_code == 201
    venue_id = response.json["id"]

    response = client.get(f"/api/venue/{venue_id}")
    assert response.status_code == 200
    assert response.json["venue"]["name"] == "Venue 1"

    item = models.ScheduleItem(
        venue_id=venue_id, start=datetime.now(), end=datetime.now(), talk=talk
    )
    db.session.add(item)
    db.session.commit()

    response = client.get(f"/api/venue/{venue_id}")
    assert response.status_code == 200
    assert response.json["venue"]["name"] == "Venue 1"
    assert len(response.json["talks"]) == 1


def test_get_venue_schedules(client):
    response = client.get("/api/venue/-1")
    assert response.status_code == 404

    site = models.Site(name="Test site", config={})
    city = models.City(name="Test city", site=site)
    db.session.add_all([site, city])
    db.session.commit()

    response = client.post(
        "/api/venue/", json={"name": "Venue 1", "address": "Test Address 1", "city_id": city.id}
    )
    assert response.status_code == 201
    venue_id = response.json["id"]

    response = client.get(f"/api/venue/{venue_id}")
    assert response.status_code == 200
    assert response.json["venue"]["name"] == "Venue 1"

    item1 = models.ScheduleItem(venue_id=venue_id, start=datetime.now(), end=datetime.now())
    item2 = models.ScheduleItem(venue_id=venue_id, start=datetime.now(), end=datetime.now())
    db.session.add_all([item1, item2])
    db.session.commit()

    response = client.get(f"/api/venue/{venue_id}/schedules")
    assert response.status_code == 200
    assert response.json["venue"]["name"] == "Venue 1"
    assert len(response.json["schedule_items"]) == 2


def test_creat_venue(client):
    response = client.post("/api/venue/", json={})
    assert response.status_code == 422
    assert response.json["message"] == "Validation error"
    assert len(response.json["detail"]["json"]) == 3

    site = models.Site(name="Test site", config={})
    city = models.City(name="Test city", site=site)
    db.session.add_all([site, city])
    db.session.commit()

    response = client.post(
        "/api/venue/", json={"name": "Venue 2", "address": "Test Address 2", "city_id": city.id}
    )
    assert response.status_code == 201
    assert response.json["name"] == "Venue 2"


def test_update_venue(client):
    site = models.Site(name="Test site", config={})
    city = models.City(name="Test city", site=site)
    db.session.add_all([site, city])
    db.session.commit()

    response = client.post(
        "/api/venue/", json={"name": "Venue 3", "address": "Test Address 3", "city_id": city.id}
    )
    venue_id = response.json["id"]

    response = client.patch(f"/api/venue/{venue_id}", json={"address": ""})
    assert response.json["address"] == ""


def test_delete_venue(client):
    response = client.delete("/api/venue/-1")
    assert response.status_code == 404

    site = models.Site(name="Test site", config={})
    city = models.City(name="Test city", site=site)
    db.session.add_all([site, city])
    db.session.commit()

    response = client.post(
        "/api/venue/", json={"name": "Venue 4", "address": "Test Address 4", "city_id": city.id}
    )
    venue_id = response.json["id"]

    response = client.delete(f"/api/venue/{venue_id}")
    assert response.status_code == 204
