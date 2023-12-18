from apiflask import APIFlask

from bamboo.views.admin import admin_bp
from bamboo.views.auth import auth_bp
from bamboo.views.blog import blog_bp
from bamboo.views.page import page_bp
from bamboo.views.talk import talk_bp
from bamboo.core.extensions import db, migrate
from bamboo.settings import config


def create_app(config_name: str) -> APIFlask:
    app = APIFlask(
        'bamboo',
        title='Bamboo',
        version='0.1.0',
    )
    app.config.from_object(config[config_name])

    # blueprints
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(blog_bp, url_prefix='/blog')
    app.register_blueprint(page_bp, url_prefix='/page')
    app.register_blueprint(talk_bp, url_prefix='/talk')

    # extensions
    db.init_app(app)
    migrate.init_app(app, db)

    return app
