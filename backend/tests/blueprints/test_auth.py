from flask import current_app

from bamboo.blueprints.auth import Permission, token_auth
from bamboo.database import db, models
from bamboo.utils import encode_jwt


def test_auth_required(app, client):
    user_only = models.Role(name="manage_user", permissions=Permission.USER)
    user_and_site = models.Role(
        name="manage_user_and_site", permissions=Permission.SITE | Permission.USER
    )
    profile = models.Media.from_file("test.png")
    user1 = models.User(name="test", profile_image=profile, role=user_only)
    user2 = models.User(name="test2", profile_image=profile, role=user_and_site)
    admin = models.User(name="admin", profile_image=profile, is_superuser=True)
    db.session.add_all([user1, user2, profile, user_only, user_and_site, admin])
    db.session.commit()

    @app.get("/login-only")
    @token_auth.auth_required
    def loginr_only():
        return {"message": "Success"}

    @app.get("/user-only")
    @token_auth.auth_required(permissions=Permission.USER)
    def manage_user_only():
        return {"message": "Success"}

    @app.get("/site-and-user")
    @token_auth.auth_required(permissions=Permission.SITE | Permission.USER)
    def manage_site_and_user():
        return {"message": "Success"}

    token = encode_jwt(
        payload={"user_id": user1.id}, secret_key=current_app.config.get("SECRET_KEY")
    )

    rv = client.get("/login-only", headers={"Authorization": f"Bearer {token}"})
    assert rv.status_code == 200
    assert rv.json["message"] == "Success"

    rv = client.get("/user-only", headers={"Authorization": f"Bearer {token}"})
    assert rv.status_code == 200
    assert rv.json["message"] == "Success"

    rv = client.get("/site-and-user", headers={"Authorization": f"Bearer {token}"})
    assert rv.status_code == 403
    assert rv.json["message"] == "Forbidden"

    token = encode_jwt(
        payload={"user_id": user2.id}, secret_key=current_app.config.get("SECRET_KEY")
    )

    rv = client.get("/site-and-user", headers={"Authorization": f"Bearer {token}"})
    assert rv.status_code == 200
    assert rv.json["message"] == "Success"

    rv = client.get("/site-and-user", headers={"Authorization": f"Bearer {token}invalid suffix"})
    assert rv.status_code == 401
    assert rv.json["message"] == "Signature verification failed."

    token = encode_jwt(payload={"user_id": 1024}, secret_key=current_app.config.get("SECRET_KEY"))

    rv = client.get("/site-and-user", headers={"Authorization": f"Bearer {token}"})
    assert rv.status_code == 401
    assert rv.json["message"] == "Unauthorized"

    token = encode_jwt(
        payload={"user_id": admin.id}, secret_key=current_app.config.get("SECRET_KEY")
    )

    rv = client.get("/site-and-user", headers={"Authorization": f"Bearer {token}"})
    assert rv.status_code == 200
    assert rv.json["message"] == "Success"


def test_login(client):
    user_only = models.Role(name="manage_user", permissions=Permission.USER)
    profile = models.Media.from_file("test.png")
    user1 = models.User(name="test", username="test", profile_image=profile, role=user_only)
    user1.password = "123456"
    user2 = models.User(name="test2", username="test2", profile_image=profile)
    user2.password = "123456"
    admin = models.User(name="admin", username="admin", profile_image=profile, is_superuser=True)
    admin.password = "123456"
    db.session.add_all([user1, user2, profile, user_only, admin])
    db.session.commit()

    rv = client.post(
        "/api/auth/login",
        json={
            "username": "test",
            "password": "123456",
        },
    )
    assert rv.status_code == 200
    assert rv.json["access_token"] is not None
    assert rv.json["refresh_token"] is not None

    rv = client.post(
        "/api/auth/login",
        json={
            "username": "admin",
            "password": "123456",
        },
    )
    assert rv.status_code == 200
    assert rv.json["access_token"] is not None
    assert rv.json["refresh_token"] is not None

    rv = client.post(
        "/api/auth/login",
        json={
            "username": "test1",
            "password": "123456",
        },
    )
    assert rv.status_code == 401
    assert rv.json["message"] == "Incorrect username or password."

    rv = client.post(
        "/api/auth/login",
        json={
            "username": "test",
            "password": "12345",
        },
    )
    assert rv.status_code == 401
    assert rv.json["message"] == "Incorrect username or password."

    rv = client.post(
        "/api/auth/login",
        json={
            "username": "test2",
            "password": "123456",
        },
    )
    assert rv.status_code == 403
    assert rv.json["message"] == "Forbidden"


def test_refresh(client):
    user_only = models.Role(name="manage_user", permissions=Permission.USER)
    profile = models.Media.from_file("test.png")
    user1 = models.User(name="test", profile_image=profile, role=user_only)
    user2 = models.User(name="test2", profile_image=profile)
    admin = models.User(name="admin", profile_image=profile, is_superuser=True)
    db.session.add_all([user1, user2, profile, user_only, admin])
    db.session.commit()

    token = encode_jwt(
        payload={"user_id": user1.id},
        secret_key=current_app.config.get("SECRET_KEY"),
        token_type="refresh",
    )

    rv = client.post("/api/auth/refresh", headers={"Authorization": f"Bearer {token}"})
    assert rv.status_code == 200
    assert rv.json["access_token"] is not None

    token = encode_jwt(
        payload={"user_id": user2.id},
        secret_key=current_app.config.get("SECRET_KEY"),
        token_type="refresh",
    )

    rv = client.post("/api/auth/refresh", headers={"Authorization": f"Bearer {token}"})
    assert rv.status_code == 403
    assert rv.json["message"] == "Forbidden"

    token = encode_jwt(
        payload={"user_id": 1024},
        secret_key=current_app.config.get("SECRET_KEY"),
        token_type="refresh",
    )

    rv = client.post("/api/auth/refresh", headers={"Authorization": f"Bearer {token}"})
    assert rv.status_code == 401
    assert rv.json["message"] == "Unauthorized"

    token = encode_jwt(
        payload={"user_id": admin.id},
        secret_key=current_app.config.get("SECRET_KEY"),
        token_type="refresh",
    )

    rv = client.post("/api/auth/refresh", headers={"Authorization": f"Bearer {token}"})
    assert rv.status_code == 200
    assert rv.json["access_token"] is not None
