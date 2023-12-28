from apiflask import APIFlask
from flask import redirect, url_for

from bamboo import blueprints, database, jobs
from bamboo.settings import config
from bamboo.ssg import SSG

ssg = SSG()


def create_app(config_name: str) -> APIFlask:
    app = APIFlask("bamboo", title="Bamboo", version="0.1.0")
    app.config.from_object(config[config_name])

    # blueprints
    blueprints.init_app(app)
    # database
    database.init_app(app)
    # jobs
    jobs.init_app(app)
    # SSG
    ssg.init_app(app)

    # TODO: direct it to the dashboard when it's ready.
    @app.get("/")
    def index():
        return redirect(url_for("openapi.docs"))

    return app
