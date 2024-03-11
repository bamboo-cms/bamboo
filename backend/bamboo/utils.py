import re
import uuid
from datetime import UTC, datetime, timedelta
from typing import (
    Any,
    Container,
    Iterable,
    MutableMapping,
)

import httpx
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
        issuer: The principal that issued JWT.
        others: For details about other args, see [the JWT RFC](https://datatracker.ietf.org/doc/html/rfc7519)

    Returns:
        dict[str, Any]: The data of JWT.
    """
    return jwt.decode(
        token=encoded_token,
        key=secret_key,
        algorithms=algorithms,
        issuer=issuer,
        audience=audience,
    )


def gen_uuid() -> str:
    """Generate a uuid hex string."""
    return str(uuid.uuid4().hex)


gh_pattern = re.compile(r"github\.com/(?P<owner>\S+)/(?P<repo>\S+)")


def fetch_github_repo(url: str, gh_token: str | None = None) -> bytes | None:
    match = gh_pattern.match(url)
    if match is None or "owner" not in match.groupdict() or "repo" not in match.groupdict():
        return None
    owner = match.group("owner")
    repo = match.group("repo")
    file_url = f"https://api.github.com/repos/{owner}/{repo}/zipball"
    headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    if gh_token:
        headers["Authorization"] = f"Bearer {gh_token}"
    with httpx.Client() as client:
        try:
            res = client.get(file_url, headers=headers, follow_redirects=True, timeout=30)
            res.raise_for_status()
        except httpx.HTTPError:
            return None
        return res.content
