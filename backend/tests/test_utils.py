from datetime import timedelta

import pytest
from bamboo.utils import decode_jwt, encode_jwt
from jose.exceptions import ExpiredSignatureError, JWTClaimsError, JWTError


def test_simple_jwt():
    encoded_token = encode_jwt(
        extra_claims={"username": "bamboo"},
        secret_key="bamboo",
    )

    decoded_token = decode_jwt(encoded_token=encoded_token, secret_key="bamboo")

    assert decoded_token["username"] == "bamboo"
    assert decoded_token["type"] == "access"
    assert decoded_token["iat"] is not None
    assert decoded_token["exp"] == (decoded_token["iat"] + timedelta(minutes=30).total_seconds())
    assert decoded_token.get("iss") is None
    assert decoded_token.get("sub") is None
    assert decoded_token.get("aud") is None
    assert decoded_token.get("nbf") is None


def test_jwt():
    encoded_token = encode_jwt(
        extra_claims={"username": "bamboo"},
        secret_key="bamboo",
        issuer="issuer",
        subject="subject",
        audience="audience",
        nbf=True,
        jti=True,
    )

    decoded_token = decode_jwt(
        encoded_token=encoded_token, secret_key="bamboo", audience="audience"
    )

    assert decoded_token["username"] == "bamboo"
    assert decoded_token["type"] == "access"
    assert decoded_token["iat"] is not None
    assert decoded_token["exp"] == (decoded_token["iat"] + timedelta(minutes=30).total_seconds())
    assert decoded_token["iss"] == "issuer"
    assert decoded_token["sub"] == "subject"
    assert decoded_token["aud"] == "audience"
    assert decoded_token["nbf"] == decoded_token["iat"]
    assert decoded_token["jti"] is not None

    with pytest.raises(JWTClaimsError, match="Invalid audience"):
        decode_jwt(
            encoded_token=encoded_token,
            secret_key="bamboo",
        )


def test_expired_jwt():
    encoded_token = encode_jwt(
        extra_claims={"username": "bamboo"},
        secret_key="bamboo",
        expires_delta=timedelta(seconds=-1),
    )

    with pytest.raises(ExpiredSignatureError):
        decode_jwt(encoded_token=encoded_token, secret_key="bamboo")


def test_invalid_jwt():
    encoded_token = encode_jwt(
        extra_claims={"username": "bamboo"},
        secret_key="bamboo",
    )

    with pytest.raises(JWTError):
        decode_jwt(encoded_token=encoded_token + "wrong suffix", secret_key="bamboo")
