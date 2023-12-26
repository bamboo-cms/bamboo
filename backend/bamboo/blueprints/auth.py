import types
from typing import Any, List

from apiflask import (
    APIBlueprint,
    HTTPTokenAuth,
    abort,
)
from flask import current_app
from jose.exceptions import JWTError

from bamboo.database import models
from bamboo.utils import decode_jwt

MANAGE_SITE = 0b001
MANAGE_USER = 0b010
MANAGE_CONTENT = 0b100
PERMISSIONS = (MANAGE_SITE, MANAGE_USER, MANAGE_CONTENT)


def auth_required(self, f=None, permissions: int | None = None, optional=None) -> Any:
    """A wrapper of `login_required`.

    Examples:
    Only one permission is required.
    ```python
    from bamboo.blueprints.auth import auth, MANAGE_USER

    @auth.auth_required(permissions=MANAGE_USER)
    def manage_user_only():
        ...
    ```

    Multiple permissions is required
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
    return self.login_required(f, [required_permissions], optional)


auth = HTTPTokenAuth(scheme="Bearer")
auth.auth_required = types.MethodType(auth_required, auth)
auth_bp = APIBlueprint("auth", __name__)


@auth.verify_token
def verify_token(token: str) -> models.User | None:
    try:
        payload = decode_jwt(encoded_token=token, secret_key=current_app.config.get("SECRET_KEY"))
    except JWTError as error:
        abort(401, str(error))

    user_id = payload["user_id"]
    return models.User.query.get(user_id)


@auth.get_user_roles
def get_user_permissions(user: models.User) -> List[int]:
    user_permissions = []
    for permission in PERMISSIONS:
        if user.role.permissions & permission:
            user_permissions.append(permission)
    return user_permissions
