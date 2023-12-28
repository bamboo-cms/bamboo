from pathlib import Path

from flask import Flask
from flask_migrate import Migrate

from bamboo.database.models import db

migrate = Migrate(db=db, directory=Path(__file__).with_name("migrations"))


def init_app(app: Flask) -> None:
    db.init_app(app)
    migrate.init_app(app)
