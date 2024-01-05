from apiflask import Schema
from apiflask.fields import String


class LoginSchema(Schema):
    username = String(required=True)
    password = String(required=True)


class TokenSchema(Schema):
    access_token = String()
    refresh_token = String()
