from datetime import datetime

from bamboo.database import db, models


def test_get_schedule_item(client):
    response = client.get("/api/schedule_item/1")
    assert response.status_code == 404

    site = models.Site(name="Test site", config={})
    city = models.City(name="Test city", site=site)
    venue = models.Venue(name="Test venue", address="Test address", city=city)
    talk = models.Talk(title="Sample Talk", site=site)
    db.session.add_all([site, city, venue, talk])
    db.session.commit()

    response = client.post(
        "/api/schedule_item/",
        json={
            "venue_id": venue.id,
            "talk_id": talk.id,
            "content": "Test content 1",
            "start": str(datetime.now()),
            "end": str(datetime.now()),
        },
    )
    assert response.status_code == 201
    schedule_item_id = response.json["id"]

    response = client.get(f"/api/schedule_item/{schedule_item_id}")
    assert response.status_code == 200
    assert response.json["venue_id"] == 1


def test_creat_schedule_item(client):
    response = client.post("/api/schedule_item/", json={})
    assert response.status_code == 422
    assert response.json["message"] == "Validation error"
    assert len(response.json["detail"]["json"]) == 3

    site = models.Site(name="Test site", config={})
    city = models.City(name="Test city", site=site)
    venue = models.Venue(name="Test venue", address="Test address", city=city)
    talk = models.Talk(title="Sample Talk", site=site)
    db.session.add_all([site, city, venue, talk])
    db.session.commit()

    response = client.post(
        "/api/schedule_item/",
        json={
            "venue_id": venue.id,
            "talk_id": talk.id,
            "content": "Test content 2",
            "start": str(datetime.now()),
            "end": str(datetime.now()),
        },
    )
    assert response.status_code == 201
    assert response.json["venue_id"] == venue.id


def test_update_schedule_item(client):
    site = models.Site(name="Test site", config={})
    city = models.City(name="Test city", site=site)
    venue = models.Venue(name="Test venue", address="Test address", city=city)
    talk = models.Talk(title="Sample Talk", site=site)
    db.session.add_all([site, city, venue, talk])
    db.session.commit()

    response = client.post(
        "/api/schedule_item/",
        json={
            "venue_id": venue.id,
            "talk_id": talk.id,
            "content": "Test content 3",
            "start": str(datetime.now()),
            "end": str(datetime.now()),
        },
    )
    schedule_item_id = response.json["id"]

    response = client.patch(f"/api/schedule_item/{schedule_item_id}", json={"content": ""})
    assert response.json["content"] == ""


def test_delete_schedule_item(client):
    site = models.Site(name="Test site", config={})
    city = models.City(name="Test city", site=site)
    venue = models.Venue(name="Test venue", address="Test address", city=city)
    talk = models.Talk(title="Sample Talk", site=site)
    db.session.add_all([site, city, venue, talk])
    db.session.commit()

    response = client.delete("/api/schedule_item/1")
    assert response.status_code == 404

    response = client.post(
        "/api/schedule_item/",
        json={
            "venue_id": venue.id,
            "talk_id": talk.id,
            "content": "Test content 4",
            "start": str(datetime.now()),
            "end": str(datetime.now()),
        },
    )
    schedule_item_id = response.json["id"]

    response = client.delete(f"/api/schedule_item/{schedule_item_id}")
    assert response.status_code == 204
