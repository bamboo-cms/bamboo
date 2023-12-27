from apiflask import APIFlask

from bamboo.blueprints.admin import admin
from bamboo.blueprints.auth import auth
from bamboo.blueprints.blog import blog
from bamboo.blueprints.command import command
from bamboo.blueprints.error import error
from bamboo.blueprints.media import media
from bamboo.blueprints.page import page
from bamboo.blueprints.talk import talk


def init_app(app: APIFlask) -> None:
    app.register_blueprint(command)
    app.register_blueprint(error)
    app.register_blueprint(admin, url_prefix="/admin")
    app.register_blueprint(auth, url_prefix="/auth")
    app.register_blueprint(blog, url_prefix="/blog")
    app.register_blueprint(media, url_prefix="/media")
    app.register_blueprint(page, url_prefix="/page")
    app.register_blueprint(talk, url_prefix="/talk")
