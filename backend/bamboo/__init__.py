from apiflask import APIFlask

from bamboo import blueprints, database, jobs
from bamboo.settings import config


def create_app(config_name: str) -> APIFlask:
    app = APIFlask("bamboo", title="Bamboo", version="0.1.0")
    app.config.from_object(config[config_name])

    # blueprints
    blueprints.init_app(app)
    # database
    database.init_app(app)
    # jobs
    jobs.init_app(app)
    return app
