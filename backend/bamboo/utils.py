import uuid
from datetime import UTC, datetime, timedelta
from typing import (
    Any,
    Container,
    Iterable,
    MutableMapping,
)

from jose import jwt


def utc_now() -> datetime:
    """Get the current time in UTC."""
    return datetime.now(UTC)


def encode_jwt(
    payload: MutableMapping[str, Any],
    secret_key: str,
    token_type: str = "access",
    expires_delta: timedelta = timedelta(minutes=30),
    algorithm: str = "HS256",
    issuer: str | None = None,
    subject: str | None = None,
    audience: str | Iterable[str] | None = None,
    nbf: bool = False,
    jti: bool = False,
) -> str:
    """Create a JWT.

    Args:
        payload: The custom claims to include in JWT.
        secret_key: The secret key for JWT.
        token_type: The type of JWT.("access" or "refresh")
        expires_delta: The duration of JWT.
        algorithm: The signing algorithm being used.
        others: For details about other args, see [the JWT RFC](https://datatracker.ietf.org/doc/html/rfc7519)

    Returns:
        str: Encoded token
    """
    now = utc_now()

    claims = {
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
    }

    if issuer:
        claims["iss"] = issuer

    if subject:
        claims["sub"] = subject

    if audience:
        claims["aud"] = audience

    if nbf:
        claims["nbf"] = now

    if jti:
        claims["jti"] = str(uuid.uuid4())

    if payload:
        claims.update(payload)

    return jwt.encode(
        claims=claims,
        key=secret_key,
        algorithm=algorithm,
    )


def decode_jwt(
    encoded_token: str,
    secret_key: str,
    algorithms: str | Container[str] = "HS256",
    issuer: str | None = None,
    audience: str | Iterable[str] | None = None,
) -> dict[str, Any]:
    """Verify and decode JWT.

    Args:
        encoded_token: The JWT to verify and decode.
        secret_key: The secret key for JWT.
        algorithm: The signing algorithm being used.
        issuer (str | None, optional): _description_. Defaults to None.
        others: For details about other args, see [the JWT RFC](https://datatracker.ietf.org/doc/html/rfc7519)

    Returns:
        dict[str, Any]: _description_
    """
    return jwt.decode(
        token=encoded_token,
        key=secret_key,
        algorithms=algorithms,
        issuer=issuer,
        audience=audience,
    )
