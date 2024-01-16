from typing import Generator

import pytest
from apiflask import APIFlask
from bamboo import create_app
from bamboo.database import db
from flask.testing import FlaskClient


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
