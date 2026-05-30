''''''
import pytest
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_roles_defined():
    from auth import ROLES
    assert "admin" in ROLES
    assert "operator" in ROLES
    assert "viewer" in ROLES
    assert ROLES["admin"]["level"] > ROLES["operator"]["level"] > ROLES["viewer"]["level"]

def test_token_create_decode():
    from auth import create_token, _decode_jwt
    token = create_token("testuser", "viewer")
    assert token is not None
    result = _decode_jwt(token)
    assert result["valid"] is True
    assert result["user"] == "testuser"
    assert result["role"] == "viewer"

def test_token_invalid():
    from auth import _decode_jwt
    result = _decode_jwt("invalid.token.here")
    assert result["valid"] is False

def test_permission_check():
    from auth import has_permission
    assert has_permission("admin", "anything") is True  # admin has *
    assert has_permission("viewer", "execute:L1") is False
    assert has_permission("operator", "read:orders") is True  # read:*

def test_password_hash():
    import hashlib
    pw = "test123"
    h1 = hashlib.sha256(pw.encode()).hexdigest()
    h2 = hashlib.sha256(pw.encode()).hexdigest()
    assert h1 == h2
    assert len(h1) == 64