"""Reset the database and load demo data.

Run from the project root:  uv run python -m scripts.seed
"""

from decimal import Decimal

from app.db import Base, SessionLocal, engine, init_db
from app.models import Car
from app.services import auth

PASSWORD = "demo1234"

CITIES = {
    "Adana": (37.0000, 35.3213),
    "Ankara": (39.9334, 32.8597),
    "Istanbul": (41.0082, 28.9784),
    "Izmir": (38.4237, 27.1428),
    "Antalya": (36.8969, 30.7133),
}

# brand, model, year, category, seats, transmission, fuel, daily_price, city, lat_offset, lng_offset
COMPANIES = {
    ("acme@example.com", "Acme Rent"): [
        ("Fiat", "Egea", 2023, "sedan", 5, "manual", "diesel", "1200", "Adana", 0.010, -0.015),
        (
            "Renault",
            "Clio",
            2022,
            "economy",
            5,
            "automatic",
            "gasoline",
            "1100",
            "Adana",
            -0.020,
            0.012,
        ),
    ],
}


def main() -> None:
    Base.metadata.drop_all(engine)
    init_db()
    with SessionLocal() as db:
        auth.register(
            db,
            email="customer@example.com",
            password=PASSWORD,
            full_name="Demo Customer",
            role="customer",
            company_name=None,
        )
        for (email, name), cars in COMPANIES.items():
            company = auth.register(
                db,
                email=email,
                password=PASSWORD,
                full_name=f"{name} Admin",
                role="company",
                company_name=name,
            )
            for (
                brand,
                model,
                year,
                category,
                seats,
                transmission,
                fuel,
                price,
                city,
                dlat,
                dlng,
            ) in cars:
                lat, lng = CITIES[city]
                db.add(
                    Car(
                        owner_id=company.id,
                        brand=brand,
                        model=model,
                        year=year,
                        category=category,
                        seats=seats,
                        transmission=transmission,
                        fuel=fuel,
                        daily_price=Decimal(price),
                        city=city,
                        lat=lat + dlat,
                        lng=lng + dlng,
                    )
                )
        db.commit()
    print("Seed complete.")


if __name__ == "__main__":
    main()
