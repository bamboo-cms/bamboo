from apiflask import Schema
from apiflask.fields import Boolean, String


class LoginSchema(Schema):
    username = String(required=True)
    password = String(required=True)


class TokenSchema(Schema):
    access_token = String()
    refresh_token = String()


class CurrentUserSchema(Schema):
    name = String()
    username = String()
    email = String()
    profile = String()
    is_superuser = Boolean()
    role = String()
