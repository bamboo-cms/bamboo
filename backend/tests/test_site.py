def test_get_sites(client):
    response = client.get("/site/all")
    assert response.status_code == 200
    assert response.json == []

    response = client.post("/site", json={"name": "Site 1", "config": {}})
    assert response.status_code == 201

    response = client.get("/site/all")
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]["name"] == "Site 1"


def test_get_site(client):
    response = client.get("/site/999")
    assert response.status_code == 404

    response = client.post("/site", json={"name": "Site 2", "config": {}})
    assert response.status_code == 201
    site_id = response.json["id"]

    response = client.get(f"/site/{site_id}")
    assert response.status_code == 200
    assert response.json["name"] == "Site 2"


def test_creat_site(client):
    response = client.post("/site", json={})
    assert response.status_code == 422
    assert response.json["message"] == "Validation error"
    assert len(response.json["detail"]["json"]) == 2

    response = client.post("/site", json={"name": "Site 3", "config": {}})
    assert response.status_code == 201
    assert response.json["name"] == "Site 3"


def test_update_site(client):
    response = client.post("/site", json={"name": "Site 4", "config": {}})
    site_id = response.json["id"]
    assert response.json["config"] == {}

    response = client.patch(f"/site/{site_id}", json={"config": {"foo": "bar"}})
    assert response.json["config"] == {"foo": "bar"}


def test_delete_site(client):
    response = client.delete("/site/999")
    assert response.status_code == 404

    response = client.post("/site", json={"name": "Site 5", "config": {}})
    site_id = response.json["id"]

    response = client.delete(f"/site/{site_id}")
    assert response.status_code == 204
