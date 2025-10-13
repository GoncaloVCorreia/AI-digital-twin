from datetime import timedelta
from app.utils.security import (
    get_password_hash, verify_password,
    create_access_token, verify_token
)

def test_password_hash_and_verify():
    # Arrange
    pwd = "StrongPass1!"
    # Act
    hashed = get_password_hash(pwd)
    # Assert
    assert verify_password(pwd, hashed)
    assert not verify_password("wrong", hashed)

def test_jwt_valid_roundtrip():

    token = create_access_token({"sub": "alice"}, expires_delta=timedelta(minutes=5))
    assert verify_token(token) == "alice"

def test_jwt_expired_returns_none():
    # Arrange
    token = create_access_token({"sub": "bob"}, expires_delta=timedelta(seconds=-1))
    # Assert
    assert verify_token(token) is None
