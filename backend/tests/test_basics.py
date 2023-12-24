def test_app_exist(app):
    assert app is not None


def test_app_config(app):
    assert app.config["TESTING"]


def test_route(client):
    response = client.get("/foo")
    assert response.status_code, 404


def test_openapi(client):
    response = client.get("/docs")
    assert response.status_code, 200
