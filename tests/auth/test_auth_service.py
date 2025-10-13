import pytest
from pydantic import ValidationError

from app.services.interviewers_service import AuthService
from app.schemas.interviewers import UserCreate
from app.models.interviewers import User


def test_create_user_persists_and_hashes(db_session):
    # cria com password válida (>= 8 chars)
    AuthService.create_user(
        db_session,
        UserCreate(
            email="hash@demo.com",
            username="hashuser",
            full_name="Hash User",
            password="Abcdefg1!",
        ),
    )
    fetched = db_session.query(User).filter_by(email="hash@demo.com").first()
    assert fetched is not None
    assert fetched.hashed_password != "Abcdefg1!"
    assert len(fetched.hashed_password) > 20


def test_create_user_rejects_short_password(db_session):
    # garantir que uma password curta falha na validação do schema
    with pytest.raises(ValidationError):
        AuthService.create_user(
            db_session,
            UserCreate(
                email="short@demo.com",
                username="shorty",
                full_name="Short Pass",
                password="1234",  # curto demais
            ),
        )


def test_duplicate_email_or_username(db_session):
    AuthService.create_user(
        db_session,
        UserCreate(
            email="dup@x.com",
            username="user1",
            full_name="Dup One",
            password="Abcdefg1!",
        ),
    )

    # mesmo email, username diferente -> deve falhar
    with pytest.raises(Exception):
        AuthService.create_user(
            db_session,
            UserCreate(
                email="dup@x.com",
                username="user2",
                full_name="Dup Two",
                password="Abcdefg1!",
            ),
        )

    # mesmo username, email diferente -> deve falhar
    with pytest.raises(Exception):
        AuthService.create_user(
            db_session,
            UserCreate(
                email="other@x.com",
                username="user1",
                full_name="Dup Three",
                password="Abcdefg1!",
            ),
        )


def test_authenticate_user_valid_and_invalid(db_session):
    AuthService.create_user(
        db_session,
        UserCreate(
            email="c@d.com",
            username="carol",
            full_name="Carol",
            password="Abcdefg1!",
        ),
    )

    assert AuthService.authenticate_user(db_session, "carol", "Abcdefg1!")
    assert AuthService.authenticate_user(db_session, "carol", "WRONG") is None
    assert AuthService.authenticate_user(db_session, "ghost", "Abcdefg1!") is None


def test_get_user_by_email_and_username(db_session):
    AuthService.create_user(
        db_session,
        UserCreate(
            email="find@demo.com",
            username="finduser",
            full_name="Find User",
            password="Abcdefg1!",
        ),
    )
    assert AuthService.get_user_by_email(db_session, "find@demo.com") is not None
    assert AuthService.get_user_by_username(db_session, "finduser") is not None
