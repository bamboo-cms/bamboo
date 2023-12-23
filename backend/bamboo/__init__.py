from apiflask import APIFlask

from bamboo.blueprints.admin import admin_bp
from bamboo.blueprints.auth import auth_bp
from bamboo.blueprints.blog import blog_bp
from bamboo.blueprints.media import media_bp
from bamboo.blueprints.page import page_bp
from bamboo.blueprints.talk import talk_bp
from bamboo.core.commands import register_commands
from bamboo.core.extensions import db, migrate, rq
from bamboo.settings import config


def create_app(config_name: str) -> APIFlask:
    app = APIFlask(
        "bamboo",
        title="Bamboo",
        version="0.1.0",
    )
    app.config.from_object(config[config_name])

    # blueprints
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(blog_bp, url_prefix="/blog")
    app.register_blueprint(media_bp, url_prefix="/media")
    app.register_blueprint(page_bp, url_prefix="/page")
    app.register_blueprint(talk_bp, url_prefix="/talk")

    # extensions
    db.init_app(app)
    migrate.init_app(app, db)
    rq.init_app(app)

    register_commands(app)
    return app
