def test_get_sites(client):
    response = client.get("api/site/all")
    assert response.status_code == 200
    assert response.json == []

    response = client.post("api/site", json={"name": "Site 1"})
    assert response.status_code == 201

    response = client.get("api/site/all")
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]["name"] == "Site 1"


def test_get_site(client):
    response = client.get("api/site/999")
    assert response.status_code == 404

    response = client.post("api/site", json={"name": "Site 2"})
    assert response.status_code == 201
    site_id = response.json["id"]

    response = client.get(f"api/site/{site_id}")
    assert response.status_code == 200
    assert response.json["name"] == "Site 2"


def test_creat_site(client):
    response = client.post("api/site", json={})
    assert response.status_code == 422
    assert response.json["message"] == "Validation error"
    assert len(response.json["detail"]["json"]) == 1

    response = client.post("api/site", json={"name": "Site 3"})
    assert response.status_code == 201
    assert response.json["name"] == "Site 3"


def test_update_site(client):
    response = client.post("api/site", json={"name": "Site 4", "config": {}})
    site_id = response.json["id"]
    assert response.json["config"] == {}

    response = client.patch(f"api/site/{site_id}", json={"config": {"foo": "bar"}})
    assert response.json["config"] == {"foo": "bar"}


def test_delete_site(client):
    response = client.delete("api/site/999")
    assert response.status_code == 404

    response = client.post("api/site", json={"name": "Site 5"})
    site_id = response.json["id"]

    response = client.delete(f"api/site/{site_id}")
    assert response.status_code == 204
