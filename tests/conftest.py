import os
from types import SimpleNamespace
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

os.environ.setdefault("ENV", "test")
os.environ.setdefault("GROQ_API_KEY", "dummy-key")
os.environ.setdefault("JWT_SECRET_KEY", "dummy-secret")
os.environ.setdefault("SECRET_API_KEY", "test-secret-api-key")
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from app.database import Base, get_db
from app import models  
from app.main import app
from app.utils import dependencies  

# --- SQLite in-memory isolado para testes ---
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Cria e destrói as tabelas no SQLite de teste (uma vez por sessão)."""
    print("\n✅ creating test tables (SQLite in-memory)...")
    Base.metadata.create_all(bind=engine)
    yield
    print("\n🧹 cleaning up test tables...")
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session():
    """Sessão de BD isolada com rollback automático."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    try:
        yield session
    finally:
        transaction.rollback()
        session.close()
        connection.close()


@pytest.fixture()
def client(db_session: Session):
    """Cliente FastAPI com override do get_db para usar a sessão de teste."""
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as c:
            yield c
    finally:
        app.dependency_overrides.pop(get_db, None)


# --- Fixtures de autenticação ---
def _mock_superuser():
    """Utilizador fictício autenticado com permissões totais."""
    return SimpleNamespace(id=1, username="testadmin", is_superuser=True)


@pytest.fixture()
def mock_auth():
    """
    Fixture que faz override da autenticação para testes unitários.
    NÃO é autouse - apenas testes que precisam podem usá-la.
    """
    app.dependency_overrides[dependencies.get_current_user] = _mock_superuser
    yield
    app.dependency_overrides.pop(dependencies.get_current_user, None)


@pytest.fixture()
def authenticated_client(client: TestClient):
    """
    Cliente com um utilizador real registado e autenticado via token JWT.
    Usa para testes de integração de API.
    """
    from uuid import uuid4
    
    unique_id = uuid4().hex[:8]
    user_data = {
        "email": f"test_{unique_id}@example.com",
        "username": f"testuser_{unique_id}",
        "full_name": "Test User",
        "password": "TestPass123!"
    }
    
    register_response = client.post("/auth/register", json=user_data)
    assert register_response.status_code in (200, 201), f"Registration failed: {register_response.text}"
    
    # Faz login para obter token
    login_response = client.post(
        "/auth/login",
        data={"username": user_data["username"], "password": user_data["password"]}
    )
    assert login_response.status_code == 200, f"Login failed: {login_response.text}"
    
    token = login_response.json()["access_token"]
    
    # Retorna cliente com headers de autenticação
    class AuthenticatedClient:
        def __init__(self, client, token):
            self._client = client
            self.headers = {"Authorization": f"Bearer {token}"}
        
        def get(self, *args, **kwargs):
            kwargs.setdefault("headers", {}).update(self.headers)
            return self._client.get(*args, **kwargs)
        
        def post(self, *args, **kwargs):
            kwargs.setdefault("headers", {}).update(self.headers)
            return self._client.post(*args, **kwargs)
        
        def put(self, *args, **kwargs):
            kwargs.setdefault("headers", {}).update(self.headers)
            return self._client.put(*args, **kwargs)
        
        def patch(self, *args, **kwargs):
            kwargs.setdefault("headers", {}).update(self.headers)
            return self._client.patch(*args, **kwargs)
        
        def delete(self, *args, **kwargs):
            kwargs.setdefault("headers", {}).update(self.headers)
            return self._client.delete(*args, **kwargs)
    
    return AuthenticatedClient(client, token)