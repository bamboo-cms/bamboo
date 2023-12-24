from typing import Generator

import pytest
from apiflask import APIFlask
from bamboo import create_app
from flask.testing import FlaskClient


@pytest.fixture(autouse=True)
def app() -> Generator[APIFlask, None, None]:
    app = create_app("testing")
    with app.app_context():
        yield app


@pytest.fixture
def client(app: APIFlask) -> FlaskClient:
    return app.test_client()
