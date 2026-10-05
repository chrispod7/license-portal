"""Integration tests run the real app against a real PostgreSQL (DATABASE_URL)."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app import models  # noqa: F401
from app.database import Base, engine
from app.main import app


@pytest.fixture(scope="session", autouse=True)
def schema():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture(autouse=True)
def clean_tables():
    yield
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE licenses, products, users RESTART IDENTITY CASCADE"))


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def user(client):
    r = client.post("/api/users", json={"email": "ada@example.com", "full_name": "Ada Lovelace"})
    assert r.status_code == 201
    return r.json()


@pytest.fixture
def product(client):
    r = client.post("/api/products", json={"sku": "acme", "name": "Acme Studio"})
    assert r.status_code == 201
    return r.json()


@pytest.fixture
def license_(client, user, product):
    r = client.post("/api/licenses", json={"user_id": user["id"], "product_id": product["id"]})
    assert r.status_code == 201
    return r.json()
