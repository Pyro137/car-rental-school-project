from collections.abc import Sequence
from decimal import Decimal

from pydantic import BaseModel, field_validator
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Car


class CarFilters(BaseModel):
    brand: str | None = None
    category: str | None = None
    transmission: str | None = None
    fuel: str | None = None
    min_seats: int | None = None
    min_price: Decimal | None = None
    max_price: Decimal | None = None

    @field_validator("*", mode="before")
    @classmethod
    def empty_to_none(cls, value):
        # A blank form field arrives as "", which must mean "no filter".
        return None if value == "" else value


def list_cars(db: Session, filters: CarFilters) -> Sequence[Car]:
    stmt = select(Car).where(Car.is_active).order_by(Car.daily_price)
    if filters.brand:
        stmt = stmt.where(Car.brand == filters.brand)
    if filters.category:
        stmt = stmt.where(Car.category == filters.category)
    if filters.transmission:
        stmt = stmt.where(Car.transmission == filters.transmission)
    if filters.fuel:
        stmt = stmt.where(Car.fuel == filters.fuel)
    if filters.min_seats is not None:
        stmt = stmt.where(Car.seats >= filters.min_seats)
    if filters.min_price is not None:
        stmt = stmt.where(Car.daily_price >= filters.min_price)
    if filters.max_price is not None:
        stmt = stmt.where(Car.daily_price <= filters.max_price)
    return db.scalars(stmt).all()


def list_brands(db: Session) -> Sequence[str]:
    return db.scalars(select(Car.brand).where(Car.is_active).distinct().order_by(Car.brand)).all()
