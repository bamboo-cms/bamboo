from bamboo.database import db, models


def test_create_organization(client):
    response = client.post("/api/organization/", json={})

    assert response.status_code == 422

    assert response.json["detail"]["json"]["name"][0] == "Missing data for required field."
    assert (
        response.json["detail"]["json"]["profile_image_id"][0] == "Missing data for required field."
    )

    db.session.add(models.Media.from_file("test.png"))
    db.session.commit()
    response = client.post(
        "/api/organization/",
        json={
            "name": "code-kitchen",
            "url": "https://codekitchen.community",
            "profile_image_id": 1,
        },
    )
    assert response.status_code == 200
    assert response.json["name"] == "code-kitchen"
    assert response.json["url"] == "https://codekitchen.community"
    assert response.json["profile_image_id"] == 1


def test_update_organization(client):
    test_create_organization(client)
    response = client.patch("/api/organization/1", json={"name": "test"})
    assert response.status_code == 200
    assert response.json["name"] == "test"

    response = client.patch("/api/organization/1", json={"profile_image_id": 2})
    assert response.status_code == 404

    image1 = models.Media.from_file("test.png")
    db.session.add_all([image1])

    response = client.patch("/api/organization/1", json={"profile_image_id": 2})
    assert response.status_code == 200


def test_delete_organization(client):
    response = client.delete("/api/organization/999")
    assert response.status_code == 404

    test_create_organization(client)
    response = client.delete("/api/organization/1")
    assert response.status_code == 204


def test_get_organization(client):
    response = client.get("/api/organization/1")
    assert response.status_code == 404

    test_create_organization(client)
    response = client.get("/api/organization/1")
    assert response.status_code == 200
    assert response.json["name"] == "code-kitchen"
    assert response.json["url"] == "https://codekitchen.community"
    assert response.json["profile_image_id"] == 1
