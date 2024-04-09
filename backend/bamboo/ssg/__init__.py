from flask import Flask

from bamboo.ssg.core import SSG


def init_app(app: Flask, url_prefix: str = "/ssg", sync_interval: int = 5) -> None:
    """
    :param app: The Flask app to initialize with.
    :param url_prefix: The URL prefix for the SSG blueprint.
    :param sync_interval: The interval (in minutes) to sync the templates from GitHub.
    """
    ssg = SSG(app, url_prefix, sync_interval)
    if not hasattr(app, "extensions"):
        app.extensions = {}
    app.extensions["ssg"] = ssg
