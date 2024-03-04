import pytest

from bamboo.blueprints.auth import Permission
from bamboo.database import db, models


def test_get_sites_permission(client):
    rv = client.get("/api/site/all")
    assert rv.status_code == 401


@pytest.mark.parametrize("permission", [Permission.SITE, Permission.USER, Permission.CONTENT])
def test_get_sites(client, auth):
    response = client.get("api/site/all", auth=auth)
    assert response.status_code == 200
    assert response.json == []

    site = models.Site(name="Site 1")
    db.session.add(site)
    db.session.commit()

    response = client.get("api/site/all", auth=auth)
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]["name"] == "Site 1"


@pytest.mark.parametrize("permission", [Permission.USER])
def test_get_site(client, auth):
    response = client.get("api/site/999", auth=auth)
    assert response.status_code == 404

    site = models.Site(name="Site 1")
    db.session.add(site)
    db.session.commit()

    response = client.get(f"api/site/{site.id}", auth=auth)
    assert response.status_code == 200
    assert response.json["name"] == "Site 1"


@pytest.mark.parametrize(
    "permission", [Permission.USER, Permission.CONTENT, Permission.USER | Permission.CONTENT]
)
def test_modify_site_permission(client, auth):
    response = client.post("api/site", json={"name": "Site 3"}, auth=auth)
    assert response.status_code == 403

    site = models.Site(name="Site 1")
    db.session.add(site)
    db.session.commit()

    response = client.patch(f"api/site/{site.id}", json={"config": {"foo": "bar"}}, auth=auth)
    assert response.status_code == 403

    response = client.delete(f"api/site/{site.id}", auth=auth)
    assert response.status_code == 403


@pytest.mark.parametrize("permission", [Permission.SITE, Permission.SITE | Permission.CONTENT])
def test_creat_site(client, auth):
    response = client.post("api/site", json={}, auth=auth)
    assert response.status_code == 422
    assert response.json["message"] == "Validation error"
    assert len(response.json["detail"]["json"]) == 1

    response = client.post("api/site", json={"name": "Site 3"}, auth=auth)
    assert response.status_code == 201
    assert response.json["name"] == "Site 3"
    site_id = response.json["id"]

    response = client.get(f"api/site/{site_id}", auth=auth)
    assert response.json["name"] == "Site 3"


@pytest.mark.parametrize("permission", [Permission.SITE, Permission.SITE | Permission.CONTENT])
def test_update_site(client, auth):
    response = client.post("api/site", json={"name": "Site 4", "config": {}}, auth=auth)
    site_id = response.json["id"]
    assert response.json["config"] == {}

    response = client.patch(f"api/site/{site_id}", json={"config": {"foo": "bar"}}, auth=auth)
    assert response.json["config"] == {"foo": "bar"}

    response = client.get(f"api/site/{site_id}", auth=auth)
    assert response.json["config"] == {"foo": "bar"}


@pytest.mark.parametrize("permission", [Permission.SITE, Permission.SITE | Permission.CONTENT])
def test_delete_site(client, auth):
    response = client.delete("api/site/999", auth=auth)
    assert response.status_code == 404

    site = models.Site(name="Site 1")
    db.session.add(site)
    db.session.commit()

    response = client.delete(f"api/site/{site.id}", auth=auth)
    assert response.status_code == 204

    response = client.get(f"api/site/{site.id}", auth=auth)
    assert response.status_code == 404
