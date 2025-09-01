import enum
from datetime import timedelta
from typing import Any, Callable, TypeVar, overload

from apiflask import APIBlueprint, HTTPTokenAuth, abort
from flask import current_app
from flask_httpauth import Authorization
from jose.exceptions import JWTError

from bamboo.database import db, models
from bamboo.schemas.auth import CurrentUserSchema, LoginSchema, TokenSchema
from bamboo.utils import decode_jwt, encode_jwt

F = TypeVar("F", bound=Callable)


class Permission(enum.IntFlag):
    CONTENT = enum.auto()
    USER = enum.auto()
    SITE = enum.auto()
    CITY = enum.auto()
    STAFF = enum.auto()


class TokenAuth(HTTPTokenAuth):
    def authorize(
        self, permissions: Permission | None, user: models.User, _: Authorization | None
    ) -> bool:
        """Overriding authorize() to improve efficiency."""
        if permissions is None or user.is_superuser:
            return True

        if self.get_user_roles_callback is None:
            raise ValueError("get_user_roles callback is not defined")

        user_permissions: Permission = self.ensure_sync(self.get_user_roles_callback)(user)

        return permissions & user_permissions == permissions

    @property
    def current_user(self) -> models.User | None:
        """Overriding current_user to offer type information."""
        return super().current_user

    @overload
    def auth_required(self, f: F) -> F: ...

    @overload
    def auth_required(
        self, *, permissions: Permission | None = None, optional: Any = None
    ) -> Callable[[F], F]: ...

    def auth_required(
        self, f: F | None = None, *, permissions: Permission | None = None, optional: Any = None
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
            from bamboo.blueprints.auth import token_auth, Permission

            @token_auth.auth_required(permissions=Permission.USER)
            def manage_user_only():
                ...
            ```

            Multiple permissions are required
            ```python
            from bamboo.blueprints.auth import token_auth, Permission

            @token_auth.auth_required(permissions=Permission.SITE | Permission.USER)
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
    user: models.User | None = db.session.scalars(
        db.select(models.User).filter_by(username=json_data["username"])
    ).one_or_none()
    if user is None or user.validate_password(json_data["password"]) is False:
        abort(401, "Incorrect username or password.")

    # Only the user with a role and the role's permissions is not 0 are allowed to log in.
    if not user.allow_login():
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
@token_auth.auth_required
def refresh():
    user = token_auth.current_user

    if not user.allow_login():
        abort(403)

    access_token = encode_jwt(
        payload={"user_id": user.id},
        secret_key=current_app.config.get("SECRET_KEY"),
    )

    return {"access_token": access_token}


@auth.get("/current")
@auth.output(CurrentUserSchema)
@token_auth.auth_required
def current_user():
    return {
        "name": token_auth.current_user.name,
        "username": token_auth.current_user.username,
        "email": token_auth.current_user.email,
        "profile": token_auth.current_user.profile_image.url_small,
        "is_superuser": token_auth.current_user.is_superuser,
        "role": token_auth.current_user.role.name if token_auth.current_user.role else None,
    }


@token_auth.verify_token
def verify_token(token: str) -> models.User | None:
    if not token:
        return None
    try:
        payload = decode_jwt(encoded_token=token, secret_key=current_app.config.get("SECRET_KEY"))
    except JWTError as error:
        abort(401, str(error))
    user = db.session.get(models.User, payload.get("user_id"))
    return user


@token_auth.get_user_roles
def get_user_permissions(user: models.User) -> Permission:
    if user.role is None:
        abort(403)

    return Permission(user.role.permissions)  # type: ignore[union-attr]
