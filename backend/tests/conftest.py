import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base, get_db
from app.core.security import create_access_token
from app import models as _models  # noqa: F401
from app.main import app
from app.models.user import User, UserProfile

TEST_DB_URL = "sqlite:///./test_foodverse.db"

test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)
    if os.path.exists("./test_foodverse.db"):
        try:
            os.remove("./test_foodverse.db")
        except Exception:
            pass


@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client):
    # Register and login a primary test user
    email = "chef@foodverse.ai"
    password = "SecurePassword123!"
    client.post("/api/v1/auth/register", json={
        "email": email,
        "password": password,
        "full_name": "Head Chef"
    })
    resp = client.post("/api/v1/auth/login", json={
        "email": email,
        "password": password
    })
    token = resp.json().get("access_token")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def secondary_auth_headers(client):
    # Register and login a second user to test ownership isolation
    email = "user2@foodverse.ai"
    password = "SecurePassword456!"
    client.post("/api/v1/auth/register", json={
        "email": email,
        "password": password,
        "full_name": "Second User"
    })
    resp = client.post("/api/v1/auth/login", json={
        "email": email,
        "password": password
    })
    token = resp.json().get("access_token")
    return {"Authorization": f"Bearer {token}"}
