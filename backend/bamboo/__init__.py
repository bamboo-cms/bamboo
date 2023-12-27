from apiflask import APIFlask
from flask import redirect, url_for

from bamboo import blueprints, database
from bamboo.settings import config


def create_app(config_name: str) -> APIFlask:
    app = APIFlask("bamboo", title="Bamboo", version="0.1.0")
    app.config.from_object(config[config_name])

    # blueprints
    blueprints.init_app(app)
    # database
    database.init_app(app)
    # TODO: direct it to the dashboard when it's ready.
    @app.get("/")
    def index():
        return redirect(url_for("openapi.docs"))

    return app
