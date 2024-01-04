from bamboo.database import db, models


def test_create_partnership(client):
    response = client.post("/partnership/", json={})
    assert response.status_code == 422
    assert response.json["detail"]["json"]["city_id"][0] == "Missing data for required field."
    assert (
        response.json["detail"]["json"]["organization_id"][0] == "Missing data for required field."
    )

    site = models.Site(name="Test site", config={})
    city = models.City(name="Test city", site=site)
    profile = models.Media(path="test.png", content_type="image/png")
    user = models.User(name="staff", profile_image=profile)
    city.staffs.add(models.Staff(staff=user, category="supporter"))

    media = models.Media(path="test.png", content_type="image/png")
    organization = models.Organization(profile_image=media, name="test", url="test")

    db.session.add_all([city, organization])
    db.session.commit()

    response = client.post(
        "/partnership/",
        json={
            "city_id": 1,
            "organization_id": 1,
            "category": "test",
        },
    )
    assert response.status_code == 200
    assert response.json["city_id"] == 1
    assert response.json["organization_id"] == 1
    assert response.json["category"] == "test"


def test_update_partnership(client):
    response = client.patch("/partnership/", json={"category": "update"})
    assert response.status_code == 422

    test_create_partnership(client)
    response = client.patch(
        "/partnership/",
        json={"category": "update", "city_id": 1, "organization_id": 1},
    )
    assert response.status_code == 200
    assert response.json["category"] == "update"

    response = client.patch(
        "/partnership/",
        json={"category": "update", "city_id": 1, "organization_id": 2},
    )
    assert response.status_code == 404


def test_get_partnership(client):
    response = client.get("/partnership/", query_string={"city_id": 1, "organization_id": 1})
    assert response.status_code == 404


def test_get_partnership_list(client):
    response = client.get(
        "/partnership/list",
        query_string={
            "city_id": 1,
        },
    )
    assert response.status_code == 200
    assert len(response.json) == 0

    test_create_partnership(client)
    response = client.get(
        "/partnership/list",
        query_string={
            "city_id": 1,
        },
    )
    assert len(response.json) == 1


def test_delete_partnership(client):
    response = client.delete("/partnership/", query_string={"city_id": 999, "organization_id": 999})
    assert response.status_code == 404
    test_create_partnership(client)
    response = client.delete("/partnership/", query_string={"city_id": 1, "organization_id": 1})
    assert response.status_code == 204
