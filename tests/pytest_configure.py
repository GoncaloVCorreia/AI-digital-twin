import os

def pytest_configure(config):
    """Configura ambiente ANTES de qualquer import."""
    os.environ["ENV"] = "test"
    os.environ["DATABASE_URL"] = "sqlite:///./test.db"  
    os.environ["GROQ_API_KEY"] = "dummy-key"
    os.environ["JWT_SECRET_KEY"] = "dummy-secret"