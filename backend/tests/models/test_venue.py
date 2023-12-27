def test_get_venue(client):
    response = client.get("/venue/-1")
    assert response.status_code == 404

    response = client.post("/venue/", json={"name": "Venue 1", "address": "Test Address 1", "city_id": 1})
    assert response.status_code == 201
    venue_id = response.json["id"]

    response = client.get(f"/venue/{venue_id}")
    assert response.status_code == 200
    assert response.json["name"] == "Venue 1"


def test_creat_venue(client):
    response = client.post("/venue/", json={})
    assert response.status_code == 422
    assert response.json["message"] == "Validation error"
    assert len(response.json["detail"]["json"]) == 3

    response = client.post("/venue/", json={"name": "Venue 2", "address": "Test Address 2", "city_id": 2})
    assert response.status_code == 201
    assert response.json["name"] == "Venue 2"


def test_update_venue(client):
    response = client.post("/venue/", json={"name": "Venue 3", "address": "Test Address 3", "city_id": 3})
    venue_id = response.json["id"]

    response = client.patch(f"/venue/{venue_id}", json={"address": ""})
    assert response.json["address"] == ""


def test_delete_venue(client):
    response = client.delete("/venue/-1")
    assert response.status_code == 404

    response = client.post("/venue/", json={"name": "Venue 4", "address": "Test Address 4", "city_id": 4})
    venue_id = response.json["id"]

    response = client.delete(f"/venue/{venue_id}")
    assert response.status_code == 204