from collections.abc import Callable
from decimal import Decimal

import pytest
from pydantic import ValidationError
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
