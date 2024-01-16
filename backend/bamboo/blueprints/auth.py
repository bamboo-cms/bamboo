from datetime import timedelta
from typing import Any, Callable, TypeVar, overload

from apiflask import APIBlueprint, HTTPTokenAuth, abort
from flask import current_app
from flask_httpauth import Authorization
from jose.exceptions import JWTError

from bamboo.database import db, models
from bamboo.schemas.auth import LoginSchema, TokenSchema
from bamboo.utils import decode_jwt, encode_jwt

F = TypeVar("F", bound=Callable)

MANAGE_SITE = 0b001
MANAGE_USER = 0b010
MANAGE_CONTENT = 0b100
PERMISSIONS = (MANAGE_SITE, MANAGE_USER, MANAGE_CONTENT)


class TokenAuth(HTTPTokenAuth):
    def authorize(
        self, permissions: int | None, user: models.User, _: Authorization | None
    ) -> bool:
        """Overriding authorize() to improve efficiency."""
        if permissions is None:
            return True

        if self.get_user_roles_callback is None:
            raise ValueError("get_user_roles callback is not defined")

        user_permissions = self.ensure_sync(self.get_user_roles_callback)(user)

        return permissions & user_permissions == permissions

    @property
    def current_user(self) -> models.User | None:
        """Overriding current_user to offer type information."""
        return super().current_user

    @overload
    def auth_required(self, f: F) -> F:
        ...

    @overload
    def auth_required(
        self, *, permissions: int | None = None, optional: Any = None
    ) -> Callable[[F], F]:
        ...

    def auth_required(
        self, f: F | None = None, *, permissions: int | None = None, optional: Any = None
    ) -> F | Callable[[F], F]:
        """A wrapper of login_required() supporting bitwise permission check.

        Examples:
            Only login is required.
            ```python
            from bamboo.blueprints.auth import token_auth, MANAGE_USER

            @token_auth.auth_required
            def manage_user_only():
                ...
            ```

            One permission is required.
            ```python
            from bamboo.blueprints.auth import token_auth, MANAGE_USER

            @token_auth.auth_required(permissions=MANAGE_USER)
            def manage_user_only():
                ...
            ```

            Multiple permissions are required
            ```python
            from bamboo.blueprints.auth import (
                token_auth,
                MANAGE_SITE,
                MANAGE_USER,
            )

            @token_auth.auth_required(permissions=MANAGE_SITE | MANAGE_USER)
            def manage_site_and_user():
                ...
            ```
        """
        return self.login_required(f, role=permissions, optional=optional)


token_auth = TokenAuth()
auth = APIBlueprint("auth", __name__)


@auth.post("/login")
@auth.input(LoginSchema)
@auth.output(TokenSchema)
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


@auth.post("/refresh")
@auth.output(TokenSchema)
@token_auth.login_required
def refresh():
    user = token_auth.current_user

    if user.role is None or user.role.permissions == 0:
        abort(403)

    access_token = encode_jwt(
        payload={"user_id": user.id},
        secret_key=current_app.config.get("SECRET_KEY"),
    )

    return {"access_token": access_token}


@token_auth.verify_token
def verify_token(token: str) -> models.User:
    try:
        payload = decode_jwt(encoded_token=token, secret_key=current_app.config.get("SECRET_KEY"))
    except JWTError as error:
        abort(401, str(error))
    user = db.session.get(models.User, payload.get("user_id"))
    if user is None:
        abort(401)
    return user


@token_auth.get_user_roles
def get_user_permissions(user: models.User) -> int:
    if user.role is None:
        abort(403)

    return user.role.permissions  # type: ignore[union-attr]
