from collections.abc import Callable
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Car, User
from app.services import fleet
from app.services.fleet import CarForm


@pytest.fixture
def form_data() -> dict[str, str | int | float]:
    return {
        "brand": "Fiat",
        "model": "Egea",
        "city": "Adana",
        "year": 2023,
        "category": "sedan",
        "transmission": "manual",
        "fuel": "diesel",
        "seats": 5,
        "daily_price": "1200.50",
        "lat": 37.0,
        "lng": 35.32,
        "image_url": "",
    }


def test_list_for_owner(
    db: Session, make_user: Callable[..., User], make_car: Callable[..., Car]
) -> None:
    owner = make_user("company")
    other_owner = make_user("company")
    last = make_car(owner, brand="Toyota", model="Corolla")
    second = make_car(owner, brand="Fiat", model="Panda", is_active=False)
    first = make_car(owner, brand="Fiat", model="Egea")
    make_car(other_owner)

    assert list(fleet.list_for_owner(db, owner.id)) == [first, second, last]


def test_list_for_owner_without_cars(db: Session, make_user: Callable[..., User]) -> None:
    owner = make_user("company")

    assert list(fleet.list_for_owner(db, owner.id)) == []


def test_create(
    db: Session, make_user: Callable[..., User], form_data: dict[str, str | int | float]
) -> None:
    owner = make_user("company")
    owner_id = owner.id
    car = fleet.create(db, owner_id, CarForm(**form_data))
    car_id = car.id
    db.expunge_all()
    saved = db.get(Car, car_id)

    assert saved is not None
    assert saved.owner_id == owner_id
    assert saved.brand == "Fiat"
    assert saved.model == "Egea"
    assert saved.daily_price == Decimal("1200.50")
    assert isinstance(saved.daily_price, Decimal)
    assert saved.image_url is None
    assert saved.is_active is True


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("brand", ""),
        ("model", ""),
        ("city", ""),
        ("year", 1980),
        ("year", 2031),
        ("category", "truck"),
        ("transmission", "semi-automatic"),
        ("fuel", "lpg"),
        ("seats", 0),
        ("seats", 10),
        ("daily_price", "0"),
        ("daily_price", "100000000.00"),
        ("daily_price", "1200.501"),
        ("lat", -91),
        ("lat", 91),
        ("lng", -181),
        ("lng", 181),
    ],
)
def test_car_form_rejects_invalid_values(
    form_data: dict[str, str | int | float], field: str, value: str | int
) -> None:
    form_data[field] = value

    with pytest.raises(ValidationError):
        CarForm(**form_data)


def test_car_form_optional_image(form_data: dict[str, str | int | float]) -> None:
    del form_data["image_url"]

    assert CarForm(**form_data).image_url is None


def test_car_form_preserves_image_url(form_data: dict[str, str | int | float]) -> None:
    form_data["image_url"] = "https://example.com/car.jpg"

    assert CarForm(**form_data).image_url == "https://example.com/car.jpg"


def test_fleet_page_shows_own_cars(client, make_user, make_car, login):
    owner = make_user("company")
    other_owner = make_user("company")

    make_car(owner, brand="Toyota", model="Corolla")
    make_car(owner, brand="Renault", model="Clio", is_active=False)
    make_car(other_owner, brand="Hyundai", model="Tucson")

    login(owner)
    response = client.get("/fleet")

    assert response.status_code == 200
    assert "My Fleet" in response.text
    assert "Toyota" in response.text
    assert "Renault" in response.text
    assert "Inactive" in response.text
    assert "Hyundai" not in response.text


def test_fleet_page_empty(client, make_user, login):
    owner = make_user("company")
    login(owner)

    response = client.get("/fleet")

    assert response.status_code == 200
    assert "You have no cars yet." in response.text
    assert "Add car" in response.text


def test_fleet_page_forbidden_for_customer(client, make_user, login):
    customer = make_user("customer")
    login(customer)

    response = client.get("/fleet")

    assert response.status_code == 403


def test_fleet_page_requires_login(client):
    response = client.get("/fleet", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"].startswith("/login")


def test_new_car_form(
    client: TestClient, make_user: Callable[..., User], login: Callable[[User], None]
) -> None:
    login(make_user("company"))

    response = client.get("/fleet/new")

    assert response.status_code == 200
    assert response.context["car"] is None
    assert "Add car" in response.text
    assert 'name="daily_price"' in response.text
    assert "Save" in response.text
    assert 'href="/fleet">Cancel' in response.text


def test_create_car_from_form(
    client: TestClient,
    db: Session,
    make_user: Callable[..., User],
    login: Callable[[User], None],
    form_data: dict[str, str | int | float],
) -> None:
    owner = make_user("company")
    make_user("company")
    owner_id = owner.id
    customer = make_user("customer")
    login(owner)

    response = client.post("/fleet/new", data=form_data, follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/fleet"
    db.expire_all()
    car = db.scalar(select(Car))
    assert car is not None
    assert car.owner_id == owner_id
    for field, value in form_data.items():
        expected = Decimal(value) if field == "daily_price" else value
        if field == "image_url":
            expected = None
        assert getattr(car, field) == expected
    assert car.is_active is True

    fleet_page = client.get("/fleet")
    assert fleet_page.status_code == 200
    assert "Fiat Egea" in fleet_page.text
    assert "Car added." in fleet_page.text
    assert "Car added." not in client.get("/fleet").text

    login(customer)
    cars_page = client.get("/cars")
    assert cars_page.status_code == 200
    assert "Fiat Egea" in cars_page.text


def test_create_car_rejects_invalid_seats(
    client: TestClient,
    db: Session,
    make_user: Callable[..., User],
    login: Callable[[User], None],
    form_data: dict[str, str | int | float],
) -> None:
    login(make_user("company"))
    form_data["seats"] = 0

    response = client.post("/fleet/new", data=form_data, follow_redirects=False)

    assert response.status_code == 422
    assert "Invalid input" in response.text
    db.expire_all()
    assert db.scalar(select(Car)) is None


def test_create_car_forbidden_for_customer(
    client: TestClient,
    db: Session,
    make_user: Callable[..., User],
    login: Callable[[User], None],
    form_data: dict[str, str | int | float],
) -> None:
    login(make_user("customer"))

    response = client.post("/fleet/new", data=form_data, follow_redirects=False)

    assert response.status_code == 403
    db.expire_all()
    assert db.scalar(select(Car)) is None
