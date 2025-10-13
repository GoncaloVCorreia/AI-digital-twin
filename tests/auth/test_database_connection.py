from sqlalchemy import inspect
from app.database import engine
from app.models.interviewers import User

def test_database_schema_is_valid():
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    assert "interviewers" in tables, "Tabela 'interviewers' não encontrada na BD."

def test_can_create_and_query_user(db_session):
    user = User(
        email="dbcheck@company.com",
        username="dbcheck",
        full_name="DB Check User",
        hashed_password="hash"
    )
    db_session.add(user)
    db_session.commit()

    fetched = db_session.query(User).filter_by(email="dbcheck@company.com").first()
    assert fetched is not None
    assert fetched.username == "dbcheck"
