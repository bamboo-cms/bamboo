from typing import Generator

import pytest
from apiflask import APIFlask
from flask.testing import FlaskClient
from werkzeug.datastructures import Authorization

from bamboo import create_app
from bamboo.blueprints.auth import Permission
from bamboo.database import db, models
from bamboo.utils import encode_jwt


@pytest.fixture(autouse=True)
def app() -> Generator[APIFlask, None, None]:
    app = create_app("testing")
    with app.app_context():
        yield app


@pytest.fixture
def client(app: APIFlask) -> FlaskClient:
    return app.test_client()


@pytest.fixture(autouse=True)
def init_db():
    db.create_all()
    try:
        yield
    finally:
        db.drop_all()


@pytest.fixture
def auth(permission: Permission, app: APIFlask) -> Authorization:
    profile = models.Media.from_file("test.png")
    user = models.User(
        name="test",
        username="test",
        profile_image=profile,
        role=models.Role(name="test-role", permissions=permission),
    )
    user.password = "123456"
    db.session.add(user)
    db.session.commit()
    access_token = encode_jwt(
        payload={"user_id": user.id},
        secret_key=app.config.get("SECRET_KEY"),
    )
    return Authorization("bearer", token=access_token)
