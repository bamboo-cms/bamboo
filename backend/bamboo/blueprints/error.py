from flask import Blueprint

error = Blueprint("error", __name__)


@error.app_errorhandler(400)
def bad_request(eror):
    return {"message": "bad request"}, 400


@error.app_errorhandler(404)
def not_found(error):
    return {"message": "not found"}, 404


@error.app_errorhandler(500)
def internal_server_error(error):
    return {"message": "internal server error"}, 500
