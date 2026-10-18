from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, func, text
from sqlalchemy.dialects.postgresql import DATERANGE, ExcludeConstraint, Range
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    password_hash: Mapped[str]
    full_name: Mapped[str]
    role: Mapped[str]  # "customer" | "company"
    company_name: Mapped[str | None]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Car(Base):
    __tablename__ = "cars"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    brand: Mapped[str]
    model: Mapped[str]
    year: Mapped[int]
    category: Mapped[str]  # economy | sedan | suv | van | luxury
    seats: Mapped[int]
    transmission: Mapped[str]  # manual | automatic
    fuel: Mapped[str]  # gasoline | diesel | hybrid | electric
    daily_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    city: Mapped[str]
    lat: Mapped[float]
    lng: Mapped[float]
    image_url: Mapped[str | None]
    is_active: Mapped[bool] = mapped_column(default=True)

    owner: Mapped[User] = relationship()


class Reservation(Base):
    __tablename__ = "reservations"
    __table_args__ = (
        ExcludeConstraint(
            ("car_id", "="),
            ("period", "&&"),
            where=text("status = 'confirmed'"),
            using="gist",
            name="no_double_booking",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    car_id: Mapped[int] = mapped_column(ForeignKey("cars.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    period: Mapped[Range[date]] = mapped_column(DATERANGE)
    status: Mapped[str] = mapped_column(default="confirmed")  # confirmed | cancelled
    total_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    card_last4: Mapped[str] = mapped_column(String(4))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    car: Mapped[Car] = relationship()
    user: Mapped[User] = relationship()
