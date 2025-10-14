# tests/auth/test_auth_service.py
import pytest
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.services.interviewers_service import AuthService
from app.schemas.interviewers import UserCreate, UserUpdate
from app.models.interviewers import User


def test_create_user_success(db_session: Session):
    """Testa criação de utilizador com sucesso."""
    user_data = UserCreate(
        email="create@test.com",
        username="createuser",
        full_name="Create User",
        password="Abcdefg1!",
    )
    
    user = AuthService.create_user(db_session, user_data)
    
    assert user.id is not None
    assert user.email == "create@test.com"
    assert user.username == "createuser"
    assert user.full_name == "Create User"
    assert user.hashed_password != "Abcdefg1!"  # deve estar hash
    assert len(user.hashed_password) > 20


def test_create_user_hashes_password(db_session: Session):
    """Testa que a password é hash corretamente."""
    user_data = UserCreate(
        email="hash@test.com",
        username="hashuser",
        full_name="Hash User",
        password="SecurePass123!",
    )
    
    user = AuthService.create_user(db_session, user_data)
    
    # Password não deve estar em texto claro
    assert user.hashed_password != "SecurePass123!"
    
    # Deve ser um hash válido (bcrypt tem formato específico)
    assert user.hashed_password.startswith("$2b$")


def test_create_user_duplicate_email_fails(db_session: Session):
    """Testa que criar utilizador com email duplicado falha."""
    user_data1 = UserCreate(
        email="duplicate@test.com",
        username="user1",
        full_name="User One",
        password="Abcdefg1!",
    )
    AuthService.create_user(db_session, user_data1)
    
    # Tenta criar outro com mesmo email
    user_data2 = UserCreate(
        email="duplicate@test.com",
        username="user2",
        full_name="User Two",
        password="Abcdefg1!",
    )
    
    with pytest.raises(Exception):  # IntegrityError da SQLAlchemy
        AuthService.create_user(db_session, user_data2)


def test_create_user_duplicate_username_fails(db_session: Session):
    """Testa que criar utilizador com username duplicado falha."""
    user_data1 = UserCreate(
        email="user1@test.com",
        username="sameusername",
        full_name="User One",
        password="Abcdefg1!",
    )
    AuthService.create_user(db_session, user_data1)
    
    # Tenta criar outro com mesmo username
    user_data2 = UserCreate(
        email="user2@test.com",
        username="sameusername",
        full_name="User Two",
        password="Abcdefg1!",
    )
    
    with pytest.raises(Exception):
        AuthService.create_user(db_session, user_data2)


def test_create_user_password_too_short_fails():
    """Testa que password curta falha na validação."""
    with pytest.raises(ValidationError):
        UserCreate(
            email="short@test.com",
            username="shortpass",
            full_name="Short Pass",
            password="Short1!",  # menos de 8 caracteres
        )


def test_create_user_password_no_uppercase_fails():
    """Testa que password sem maiúsculas falha."""
    with pytest.raises(ValidationError):
        UserCreate(
            email="nouppercase@test.com",
            username="nouppercase",
            full_name="No Upper",
            password="abcdefg1!",
        )


def test_create_user_password_no_digit_fails():
    """Testa que password sem números falha."""
    with pytest.raises(ValidationError):
        UserCreate(
            email="nodigit@test.com",
            username="nodigit",
            full_name="No Digit",
            password="Abcdefgh!",
        )


def test_get_user_by_id(db_session: Session):
    """Testa obter utilizador por ID."""
    user_data = UserCreate(
        email="getid@test.com",
        username="getiduser",
        full_name="Get ID User",
        password="Abcdefg1!",
    )
    created = AuthService.create_user(db_session, user_data)
    
    fetched = AuthService.get_user(db_session, created.id)
    
    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.username == "getiduser"


def test_get_user_by_id_not_found(db_session: Session):
    """Testa obter utilizador inexistente por ID."""
    result = AuthService.get_user(db_session, 99999)
    assert result is None


def test_get_user_by_email(db_session: Session):
    """Testa obter utilizador por email."""
    user_data = UserCreate(
        email="getemail@test.com",
        username="getemailuser",
        full_name="Get Email User",
        password="Abcdefg1!",
    )
    AuthService.create_user(db_session, user_data)
    
    fetched = AuthService.get_user_by_email(db_session, "getemail@test.com")
    
    assert fetched is not None
    assert fetched.email == "getemail@test.com"
    assert fetched.username == "getemailuser"


def test_get_user_by_email_not_found(db_session: Session):
    """Testa obter utilizador inexistente por email."""
    result = AuthService.get_user_by_email(db_session, "nonexistent@test.com")
    assert result is None


def test_get_user_by_username(db_session: Session):
    """Testa obter utilizador por username."""
    user_data = UserCreate(
        email="getuser@test.com",
        username="getusername",
        full_name="Get Username User",
        password="Abcdefg1!",
    )
    AuthService.create_user(db_session, user_data)
    
    fetched = AuthService.get_user_by_username(db_session, "getusername")
    
    assert fetched is not None
    assert fetched.username == "getusername"
    assert fetched.email == "getuser@test.com"


def test_get_user_by_username_not_found(db_session: Session):
    """Testa obter utilizador inexistente por username."""
    result = AuthService.get_user_by_username(db_session, "nonexistent")
    assert result is None


def test_authenticate_user_valid_credentials(db_session: Session):
    """Testa autenticação com credenciais válidas."""
    user_data = UserCreate(
        email="auth@test.com",
        username="authuser",
        full_name="Auth User",
        password="ValidPass123!",
    )
    AuthService.create_user(db_session, user_data)
    
    authenticated = AuthService.authenticate_user(db_session, "authuser", "ValidPass123!")
    
    assert authenticated is not None
    assert authenticated.username == "authuser"


def test_authenticate_user_invalid_password(db_session: Session):
    """Testa autenticação com password errada."""
    user_data = UserCreate(
        email="wrongpass@test.com",
        username="wrongpassuser",
        full_name="Wrong Pass User",
        password="CorrectPass123!",
    )
    AuthService.create_user(db_session, user_data)
    
    result = AuthService.authenticate_user(db_session, "wrongpassuser", "WrongPass123!")
    
    assert result is None


def test_authenticate_user_nonexistent_username(db_session: Session):
    """Testa autenticação com username inexistente."""
    result = AuthService.authenticate_user(db_session, "ghost", "AnyPass123!")
    assert result is None


def test_update_user_success(db_session: Session):
    """Testa atualização de utilizador."""
    user_data = UserCreate(
        email="update@test.com",
        username="updateuser",
        full_name="Original Name",
        password="Abcdefg1!",
    )
    created = AuthService.create_user(db_session, user_data)
    
    update_data = UserUpdate(full_name="Updated Name")
    updated = AuthService.update_user(db_session, created.id, update_data)
    
    assert updated is not None
    assert updated.full_name == "Updated Name"
    assert updated.username == "updateuser"  # não mudou


def test_update_user_not_found(db_session: Session):
    """Testa atualização de utilizador inexistente."""
    update_data = UserUpdate(full_name="New Name")
    result = AuthService.update_user(db_session, 99999, update_data)
    
    assert result is None


def test_username_is_lowercased(db_session: Session):
    """Testa que username é convertido para minúsculas."""
    user_data = UserCreate(
        email="lowercase@test.com",
        username="UpperCaseUser",
        full_name="Lowercase Test",
        password="Abcdefg1!",
    )
    user = AuthService.create_user(db_session, user_data)
    
    assert user.username == "uppercaseuser"


def test_user_timestamps_are_set(db_session: Session):
    """Testa que timestamps são criados automaticamente."""
    user_data = UserCreate(
        email="timestamp@test.com",
        username="timestampuser",
        full_name="Timestamp User",
        password="Abcdefg1!",
    )
    user = AuthService.create_user(db_session, user_data)
    
    assert user.created_at is not None
    assert user.updated_at is not None


def test_user_is_not_superuser_by_default(db_session: Session):
    """Testa que utilizador não é superuser por padrão."""
    user_data = UserCreate(
        email="normal@test.com",
        username="normaluser",
        full_name="Normal User",
        password="Abcdefg1!",
    )
    user = AuthService.create_user(db_session, user_data)
    
    assert user.is_superuser is False