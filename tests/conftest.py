import os

TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://car_rental:car_rental@localhost:5432/car_rental_test",
)
# Must happen before anything from `app` is imported: tests never touch the dev database.
os.environ["DATABASE_URL"] = TEST_DATABASE_URL

from collections.abc import Callable, Iterator
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session


def _ensure_test_database(url: str) -> None:
    target = make_url(url)
    admin = create_engine(target.set(database="postgres"), isolation_level="AUTOCOMMIT")
    with admin.connect() as conn:
        exists = conn.scalar(
            text("SELECT 1 FROM pg_database WHERE datname = :name"), {"name": target.database}
        )
        if not exists:
            conn.execute(text(f'CREATE DATABASE "{target.database}"'))
    admin.dispose()


_ensure_test_database(TEST_DATABASE_URL)

from app.db import Base, SessionLocal, engine, init_db
from app.main import app
from app.models import Car, User
from app.services import auth

PASSWORD = "secret123"


@pytest.fixture(autouse=True)
def reset_db() -> None:
    Base.metadata.drop_all(engine)
    init_db()


@pytest.fixture
def db() -> Iterator[Session]:
    with SessionLocal() as session:
        yield session


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def make_user(db: Session) -> Callable[..., User]:
    count = 0

    def _make(role: str = "customer", email: str | None = None) -> User:
        nonlocal count
        count += 1
        user = auth.register(
            db,
            email=email or f"user{count}@example.com",
            password=PASSWORD,
            full_name=f"User {count}",
            role=role,
            company_name=f"Company {count}" if role == "company" else None,
        )
        assert user is not None
        return user

    return _make


@pytest.fixture
def make_car(db: Session) -> Callable[..., Car]:
    def _make(owner: User, **overrides) -> Car:
        values = {
            "brand": "Fiat",
            "model": "Egea",
            "year": 2023,
            "category": "sedan",
            "seats": 5,
            "transmission": "manual",
            "fuel": "diesel",
            "daily_price": Decimal("1200.00"),
            "city": "Adana",
            "lat": 37.0,
            "lng": 35.32,
        }
        values.update(overrides)
        car = Car(owner_id=owner.id, **values)
        db.add(car)
        db.commit()
        return car

    return _make


@pytest.fixture
def login(client: TestClient) -> Callable[[User], None]:
    def _login(user: User) -> None:
        response = client.post(
            "/login", data={"email": user.email, "password": PASSWORD}, follow_redirects=False
        )
        assert response.status_code == 303

    return _login
