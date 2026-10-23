from collections.abc import Sequence
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, field_validator
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Car


class CarForm(BaseModel):
    brand: str = Field(min_length=1)
    model: str = Field(min_length=1)
    city: str = Field(min_length=1)
    year: int = Field(ge=1990, le=2030)
    category: Literal["economy", "sedan", "suv", "van", "luxury"]
    transmission: Literal["manual", "automatic"]
    fuel: Literal["gasoline", "diesel", "hybrid", "electric"]
    seats: int = Field(ge=1, le=9)
    daily_price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    lat: float = Field(ge=-90, le=90)
    lng: float = Field(ge=-180, le=180)
    image_url: str | None = None

    @field_validator("image_url", mode="before")
    @classmethod
    def empty_to_none(cls, value: str | None) -> str | None:
        return None if value == "" else value


def list_for_owner(db: Session, owner_id: int) -> Sequence[Car]:
    return db.scalars(
        select(Car).where(Car.owner_id == owner_id).order_by(Car.brand, Car.model)
    ).all()


def create(db: Session, owner_id: int, form: CarForm) -> Car:
    car = Car(owner_id=owner_id, **form.model_dump())
    db.add(car)
    db.commit()
    return car


def get_owned(db: Session, owner_id: int, car_id: int) -> Car | None:
    car = db.get(Car, car_id)
    return car if car and car.owner_id == owner_id else None


def update(db: Session, car: Car, form: CarForm) -> None:
    for field, value in form.model_dump().items():
        setattr(car, field, value)
    db.commit()


def toggle_active(db: Session, car: Car) -> None:
    car.is_active = not car.is_active
    db.commit()
