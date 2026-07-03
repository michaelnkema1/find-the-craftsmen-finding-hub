"""Basic auth regression tests."""
from auth import create_access_token, decode_access_token, encrypt_field, decrypt_field


def test_jwt_sub_must_be_string():
    token = create_access_token({"sub": "1"})
    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == "1"


def test_encrypt_decrypt_roundtrip():
    plain = "user@example.com"
    encrypted = encrypt_field(plain)
    assert encrypted != plain
    assert decrypt_field(encrypted) == plain


def test_decrypt_legacy_plaintext_email():
    assert decrypt_field("legacy@demo.com") == "legacy@demo.com"
