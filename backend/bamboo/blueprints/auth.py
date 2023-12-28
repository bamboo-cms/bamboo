import types
from datetime import timedelta
from typing import Any, List


from apiflask import (
    APIBlueprint,
    HTTPTokenAuth,
    abort,
)
from flask import current_app
from jose.exceptions import JWTError

from bamboo.database import db, models
from bamboo.schemas.auth import LoginSchema, TokenSchema
from bamboo.utils import decode_jwt, encode_jwt

MANAGE_SITE = 0b001
MANAGE_USER = 0b010
MANAGE_CONTENT = 0b100
PERMISSIONS = (MANAGE_SITE, MANAGE_USER, MANAGE_CONTENT)


def auth_required(self, f=None, permissions: int = 0, optional=None) -> Any:
    """A wrapper of `login_required`.

    Examples:
    Only login is required.
    ```python
    from bamboo.blueprints.auth import auth, MANAGE_USER

    @auth.auth_required
    def manage_user_only():
        ...
    ```

    One permission is required.
    ```python
    from bamboo.blueprints.auth import auth, MANAGE_USER

    @auth.auth_required(permissions=MANAGE_USER)
    def manage_user_only():
        ...
    ```

    Multiple permissions are required
    ```python
    from bamboo.blueprints.auth import (
        auth,
        MANAGE_SITE,
        MANAGE_USER,
    )

    @auth.auth_required(permissions=MANAGE_SITE | MANAGE_USER)
    def manage_site_and_user():
        ...
    ```
    """
    required_permissions = []
    for perm in PERMISSIONS:
        if perm & permissions:
            required_permissions.append(perm)

    if f:
        return self.login_required(f=f)
    return self.login_required(f=None, role=[required_permissions], optional=optional)


auth = HTTPTokenAuth(scheme="Bearer", header="Authorization")
auth.auth_required = types.MethodType(auth_required, auth)
auth_bp = APIBlueprint("auth", __name__)


@auth_bp.post("/login")
@auth_bp.input(LoginSchema)
@auth_bp.output(TokenSchema)
def login(json_data):
    user = models.User.query.filter_by(name=json_data["username"]).first()
    if user is None or user.validate_password(json_data["password"]) is False:
        abort(401, "Incorrect username or password.")

    # Only the user with a role and the role's permissions is not 0 are allowed to log in.
    if user.role is None or user.role.permissions == 0:
        abort(403)

    access_token = encode_jwt(
        payload={"user_id": user.id},
        secret_key=current_app.config.get("SECRET_KEY"),
    )

    refresh_token = encode_jwt(
        payload={"user_id": user.id},
        secret_key=current_app.config.get("SECRET_KEY"),
        token_type="refresh",
        expires_delta=timedelta(days=7),
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }


@auth_bp.post("/refresh")
@auth_bp.output(TokenSchema)
@auth.auth_required
def refresh():
    user_id = auth.current_user.get("user_id")
    user = db.session.get(models.User, user_id)

    if user is None:
        abort(401)

    if user.role is None or user.role.permissions == 0:
        abort(403)

    access_token = encode_jwt(
        payload={"user_id": user.id},
        secret_key=current_app.config.get("SECRET_KEY"),
    )

    return {"access_token": access_token}


@auth.verify_token
def verify_token(token: str) -> dict[str, Any] | None:
    try:
        payload = decode_jwt(encoded_token=token, secret_key=current_app.config.get("SECRET_KEY"))
    except JWTError as error:
        abort(401, str(error))

    return {"user_id": payload.get("user_id")}


@auth.get_user_roles
def get_user_permissions(payload: dict[str, Any]) -> List[int]:
    user_permissions = []
    user_id = payload.get("user_id")
    user = db.session.get(models.User, user_id)
    if user is None:
        abort(401)

    if user.role is None:
        abort(403)

    for permission in PERMISSIONS:
        if user.role.permissions & permission:
            user_permissions.append(permission)
    return user_permissions
