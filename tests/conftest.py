import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app import models  


SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Cria e destrói as tabelas no SQLite de teste."""
    print("\n✅ Criando tabelas de teste (SQLite in-memory)...")
    Base.metadata.create_all(bind=engine)
    yield
    print("\n🧹 Limpando tabelas de teste...")
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session():
    """Cria uma sessão de BD nova para cada teste."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db_session):
    """Cria um cliente de teste FastAPI com BD mockada."""
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
