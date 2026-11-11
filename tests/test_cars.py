from decimal import Decimal

import pytest

from app.models import User
from app.services import cars
from app.services.cars import CarFilters


def add_three_cars(make_user, make_car) -> User:
    owner = make_user("company")
    make_car(owner)  # Fiat Egea: sedan, 5 seats, manual, diesel, 1200.00
    make_car(
        owner,
        brand="Renault",
        model="Clio",
        category="economy",
        transmission="automatic",
        fuel="gasoline",
        daily_price=Decimal("900.00"),
    )
    make_car(
        owner,
        brand="Hyundai",
        model="Tucson",
        category="suv",
        seats=7,
        transmission="automatic",
        fuel="hybrid",
        daily_price=Decimal("2500.00"),
    )
    return owner


def model_names(result) -> list[str]:
    return [car.model for car in result]


# Values are strings because that is how they arrive from the query string.
@pytest.mark.parametrize(
    ("field", "value", "expected"),
    [
        ("brand", "Renault", ["Clio"]),
        ("category", "suv", ["Tucson"]),
        ("transmission", "manual", ["Egea"]),
        ("fuel", "hybrid", ["Tucson"]),
        ("min_seats", "7", ["Tucson"]),
        ("min_price", "1200", ["Egea", "Tucson"]),
        ("max_price", "1200", ["Clio", "Egea"]),
    ],
)
def test_single_filter(db, make_user, make_car, field, value, expected):
    add_three_cars(make_user, make_car)
    filters = CarFilters.model_validate({field: value})
    assert model_names(cars.list_cars(db, filters)) == expected


def test_three_filters_together(db, make_user, make_car):
    add_three_cars(make_user, make_car)
    filters = CarFilters.model_validate(
        {"transmission": "automatic", "min_seats": "5", "max_price": "2000"}
    )
    assert model_names(cars.list_cars(db, filters)) == ["Clio"]


def test_blank_fields_list_all_active_cars(db, make_user, make_car):
    add_three_cars(make_user, make_car)
    filters = CarFilters.model_validate(
        {
            "brand": "",
            "category": "",
            "transmission": "",
            "fuel": "",
            "min_seats": "",
            "min_price": "",
            "max_price": "",
        }
    )
    assert model_names(cars.list_cars(db, filters)) == ["Clio", "Egea", "Tucson"]


def test_inactive_car_is_never_listed(db, make_user, make_car):
    owner = add_three_cars(make_user, make_car)
    make_car(owner, brand="Tesla", model="Model 3", fuel="electric", is_active=False)
    assert "Model 3" not in model_names(cars.list_cars(db, CarFilters()))
    assert cars.list_cars(db, CarFilters(brand="Tesla")) == []
    assert cars.list_cars(db, CarFilters(fuel="electric")) == []
    assert "Tesla" not in cars.list_brands(db)


def test_list_brands(db, make_user, make_car):
    owner = add_three_cars(make_user, make_car)
    make_car(owner, model="Doblo")
    assert cars.list_brands(db) == ["Fiat", "Hyundai", "Renault"]


def test_get_active_car(db, make_user, make_car):
    car = make_car(make_user("company"))
    assert cars.get_active_car(db, car.id) is car


def test_get_active_car_missing_or_inactive(db, make_user, make_car):
    inactive = make_car(make_user("company"), is_active=False)
    assert cars.get_active_car(db, inactive.id) is None
    assert cars.get_active_car(db, 99999) is None


def test_detail_page(client, make_user, make_car):
    car = make_car(make_user("company"), image_url="https://example.com/egea.jpg")

    response = client.get(f"/cars/{car.id}")

    assert response.status_code == 200
    assert "Fiat Egea (2023)" in response.text
    assert "Offered by Company 1 · Adana" in response.text
    assert 'src="https://example.com/egea.jpg"' in response.text
    assert "1200.00 ₺" in response.text
    assert f'href="/cars/{car.id}"' in client.get("/cars").text


def test_detail_page_not_found(client, make_user, make_car):
    inactive = make_car(make_user("company"), is_active=False)

    assert client.get("/cars/99999").status_code == 404
    assert client.get(f"/cars/{inactive.id}").status_code == 404
