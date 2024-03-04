from pathlib import Path

from flask import Blueprint, send_from_directory

FRONTEND_DIR = Path(__file__).parent.parent.parent.parent / "frontend" / "dist"
root = Blueprint("root", __name__)


@root.app_errorhandler(400)
def bad_request(eror):
    return {"message": "bad request"}, 400


@root.app_errorhandler(500)
def internal_server_error(error):
    return {"message": "internal server error"}, 500


@root.route("/", defaults={"filename": "index.html"})
@root.route("/<path:filename>")
def dashboard(filename: str):
    return send_from_directory(FRONTEND_DIR, filename)


@root.errorhandler(404)
def fallback_index(error: Exception):
    return send_from_directory(FRONTEND_DIR, "index.html")


@root.app_errorhandler(404)
def not_found(error):
    return {"message": "not found"}, 404
