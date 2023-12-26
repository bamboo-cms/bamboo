from bamboo.blueprints.auth import (
    MANAGE_SITE,
    MANAGE_USER,
    auth,
)
from bamboo.database import db, models
from bamboo.utils import encode_jwt
from flask import current_app


def test_auth_required(app, client):
    user_only = models.Role(name="manage_site", permissions=MANAGE_USER)
    user_and_site = models.Role(name="manage_user", permissions=MANAGE_SITE | MANAGE_USER)
    profile = models.Media(path="test.png", content_type="image/png")
    user1 = models.User(name="test", profile_image=profile, role=user_only)
    user2 = models.User(name="test2", profile_image=profile, role=user_and_site)
    db.session.add_all([user1, user2, profile, user_only, user_and_site])
    db.session.commit()

    @app.get("/user-only")
    @auth.auth_required(permissions=MANAGE_USER)
    def manage_user_only():
        return {"message": "Success"}

    @app.get("/site-and-user")
    @auth.auth_required(permissions=MANAGE_SITE | MANAGE_USER)
    def manage_site_and_user():
        return {"message": "Success"}

    token = encode_jwt(
        payload={"user_id": user1.id}, secret_key=current_app.config.get("SECRET_KEY")
    )

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
