from apiflask import APIFlask

from bamboo.blueprints.admin import admin_bp
from bamboo.blueprints.auth import auth_bp
from bamboo.blueprints.blog import blog_bp
from bamboo.blueprints.media import media_bp
from bamboo.blueprints.page import page_bp
from bamboo.blueprints.talk import talk_bp


def init_app(app: APIFlask) -> None:
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(blog_bp, url_prefix="/blog")
    app.register_blueprint(page_bp, url_prefix="/page")
    app.register_blueprint(talk_bp, url_prefix="/talk")
    app.register_blueprint(media_bp, url_prefix="/media")
