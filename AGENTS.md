# AGENTS.md: Car Rental System (CEN317 Engineering Design)

This file is the shared instruction set for every AI assistant used on this project
(ChatGPT, Claude, Gemini, Copilot, Cursor or any other). Three students use different
tools; this file is what keeps their code identical in style and structure.

Read the whole file before writing anything. Then read the task card the user gives you.

---

## 0. Ground rules for the assistant

1. **The task card is the scope.** Do exactly what the card asks. Create or change only the
   files listed under "Files" in the card. Do not refactor, rename, reformat or "improve"
   anything else, even if you think it is better.
2. **This file wins over your habits.** If something here differs from how you usually write
   FastAPI or SQLAlchemy code, follow this file.
3. **Never guess missing context.** If you need the content of a file you were not given
   (for example `app/models.py`), ask the user to paste it. Do not invent field names,
   function names, routes, fixtures or template blocks.
4. **Stop on conflicts.** If the card contradicts this file, or the card cannot be done
   without touching a file it does not list, stop and explain the conflict in Turkish.
   Do not work around it.
5. **No new dependencies.** If the task seems to need a package that is not in section 2,
   say so and stop. Only Metin (team lead) adds packages.
6. **The user is learning.** Two of the three students are beginners. Prefer the simplest
   correct code over clever code. Every line must be explainable by the student.

## 1. The project

A web platform where customers filter and rent cars, choose a date range and go through a
simulated payment, and rental companies manage their own fleet. It is a school MVP, not a
production system: correct and simple beats complete.

Required features (all seven must work at the end):

| # | Feature | How it is built |
| --- | --- | --- |
| 1 | Filter cars | `/cars` page; brand, category, transmission, fuel, min seats, price range |
| 2 | Pick a date range | Pick-up and return dates; only available cars are listed |
| 3 | Payment simulation | Fake card form; only the last 4 digits are stored |
| 4 | Fleet management | Users with role `company` add, edit, deactivate their own cars |
| 5 | Map-based filtering | Leaflet map; "Search this area" filters by the visible map bounds |
| 6 | Concurrency control | PostgreSQL exclusion constraint; a car cannot be double-booked |
| 7 | LLM recommendation | Budget, passengers, purpose; SQL pre-filter, Claude ranks, ids validated |

Team: **Metin** (team lead; owns the core and reviews every PR), **Gizem** (fleet screens, map),
**Enes** (seed data, payment and reservation pages, recommendation page, report).

## 2. Stack (fixed)

| Area | Choice | Notes |
| --- | --- | --- |
| Language | Python 3.13 | Type hints on every function signature |
| Web | FastAPI 0.142 | Sync `def` endpoints only |
| ORM | SQLAlchemy 2.1 | Sync, 2.0-style API (`select()`, `Mapped`, `mapped_column`) |
| Database | PostgreSQL 16 via Docker Compose | Driver: psycopg 3 (`postgresql+psycopg://`) |
| Validation | Pydantic 2 | Form and query models live in `app/services/` |
| HTML | Jinja2 templates, server-rendered | Every page extends `base.html` |
| CSS | Bootstrap 5.3 from CDN | Bootstrap classes only; no custom CSS framework |
| Map | Leaflet 1.x (stable) from CDN + OpenStreetMap tiles | Vanilla JS in `app/static/map.js` |
| Sessions | Starlette `SessionMiddleware` (signed cookie) | No JWT |
| Passwords | `pwdlib[argon2]` | Only through `app/services/auth.py` |
| Settings | `pydantic-settings` reading `.env` | Only through `app/config.py` |
| LLM (Milestone 3) | Official `anthropic` Python SDK | Only inside `app/services/recommendation.py` |
| Tooling | `uv`, `pytest`, `ruff`, `httpx2` (for `TestClient`) | |

Not used, on purpose: async SQLAlchemy, Alembic, React or any JS framework or build step,
HTMX, WTForms, fastapi-users, passlib, JWT, Redis, Celery, PostGIS, Google Maps.

## 3. Layout and layers

```text
car-rental/
├── AGENTS.md                 # this file
├── app/
│   ├── main.py               # app, middleware, routers, error handlers      (Metin only)
│   ├── config.py             # settings from .env                            (Metin only)
│   ├── db.py                 # engine, SessionLocal, Base, init_db, get_db   (Metin only)
│   ├── models.py             # User, Car, Reservation                        (Metin only)
│   ├── deps.py               # templates, Db, Customer, Company              (Metin only)
│   ├── routers/              # HTTP layer: one file per area
│   │   ├── auth.py  cars.py  fleet.py  reservations.py  recommend.py
│   ├── services/             # business logic + Pydantic form/query models
│   │   ├── auth.py  cars.py  fleet.py  booking.py  recommendation.py
│   ├── templates/            # base.html (Metin only), error.html, one folder per area
│   └── static/               # style.css, map.js
├── scripts/seed.py           # resets the dev database and loads demo data
├── tests/                    # conftest.py (Metin only) + test_<area>.py files
├── docker-compose.yml  pyproject.toml  uv.lock  .env.example  README.md
```

"Metin only" files change only when a card explicitly lists them.

Three layers, always in this direction: **router → service → model**.

- **Router** (`app/routers/`): knows HTTP. Reads query/form data, checks the role with a
  dependency, calls one service function, returns a template or a redirect. It never builds
  a SQL query and never contains business rules.
- **Service** (`app/services/`): knows the rules. Queries with SQLAlchemy, computes prices,
  checks availability, raises domain exceptions. It never imports `Request`, never returns
  HTML, never raises `HTTPException`.
- **Model** (`app/models.py`): tables and relationships only.

## 4. Domain rules

- **Roles:** `customer` and `company`. A company is a user with `role="company"` and a
  `company_name`. There is no separate company table.
- **Ownership:** a company sees and changes only cars where `car.owner_id == user.id`.
  Accessing someone else's car or reservation returns **404**, not 403, so existence is
  not leaked.
- **Money:** `Decimal`, stored as `Numeric(10, 2)`, currency TL. Never `float` for money.
- **Dates:** reservations use `date` (no time, no time zone). The period is a half-open
  range `[start, end)` stored as `DATERANGE` and written as `Range(start, end)`.
  Rental days = `(end - start).days`. A car returned on the 13th can be picked up again on
  the 13th.
- **Reservation status:** `confirmed` or `cancelled`. Nothing is ever deleted: cars become
  `is_active = False`, reservations become `cancelled`.
- **Cancellation:** only the customer's own `confirmed` reservation, and only before the
  pick-up day.
- **Payment:** card number, expiry and CVV are validated for format only and never stored.
  Only `card_last4` is saved.
- **Availability:** use `booking.is_available(start, end)` as the SQL condition.
  Double booking is prevented by the database constraint `no_double_booking`.
  **Never** add a "check first, then insert" availability check as protection; the service
  catches the constraint error (SQLSTATE `23P01`) and raises `CarUnavailable`.
- **Fixed value lists:**
  `category`: economy, sedan, suv, van, luxury · `transmission`: manual, automatic ·
  `fuel`: gasoline, diesel, hybrid, electric.
- **Language:** UI text, code, comments, commit messages: English.
  Explanations to the student: Turkish.

## 5. Code patterns (copy these shapes)

### 5.1 Router

```python
from typing import Annotated

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import RedirectResponse

from app.deps import Company, Db, templates
from app.services import fleet
from app.services.fleet import CarForm

router = APIRouter(prefix="/fleet")


@router.get("")
def fleet_list(request: Request, db: Db, user: Company):
    return templates.TemplateResponse(
        request, "fleet/list.html", {"cars": fleet.list_for_owner(db, user.id)}
    )


@router.post("/new")
def create(request: Request, db: Db, user: Company, form: Annotated[CarForm, Form()]):
    fleet.create(db, user.id, form)
    request.session["flash"] = "Car added."
    return RedirectResponse("/fleet", status_code=303)


@router.get("/{car_id}/edit")
def edit_form(request: Request, db: Db, user: Company, car_id: int):
    car = fleet.get_owned(db, user.id, car_id)
    if car is None:
        raise HTTPException(status_code=404)
    return templates.TemplateResponse(request, "fleet/form.html", {"car": car})
```

Rules shown above:

- `templates.TemplateResponse(request, "name.html", {...})`: request first, as its own
  argument. Never put `"request"` inside the context dict.
- Protection is a typed parameter: `user: Company` or `user: Customer`. Public pages have no
  user parameter. Never check `request.session` for roles inside a route.
- Database access is the `db: Db` parameter. Never create sessions in routers.
- Every successful `POST` ends with `RedirectResponse(url, status_code=303)`, usually after
  setting `request.session["flash"]`. Never return a template from a successful `POST`.
- A missing or foreign record raises `HTTPException(status_code=404)`.
- Service exceptions (`InvalidDates`, `CarUnavailable`) are caught in the router and shown
  with `error.html` and status 400 or 409.

### 5.2 Service

```python
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Car


def list_for_owner(db: Session, owner_id: int) -> Sequence[Car]:
    return db.scalars(
        select(Car).where(Car.owner_id == owner_id).order_by(Car.brand, Car.model)
    ).all()


def get_owned(db: Session, owner_id: int, car_id: int) -> Car | None:
    car = db.get(Car, car_id)
    return car if car and car.owner_id == owner_id else None


def create(db: Session, owner_id: int, form: CarForm) -> Car:
    car = Car(owner_id=owner_id, **form.model_dump())
    db.add(car)
    db.commit()
    return car
```

- First parameter is always `db: Session`. Return models or `None`; never dicts unless the
  card says so.
- Queries: `select(...)` with `db.scalars(...).all()`, `db.scalar(...)` or `db.get(...)`.
  Never `db.query(...)`. Never raw SQL strings.
- The service that changes data calls `db.commit()` itself.

### 5.3 Form and query models

```python
class CarForm(BaseModel):
    brand: str = Field(min_length=1)
    year: int = Field(ge=1990, le=2030)
    category: Literal["economy", "sedan", "suv", "van", "luxury"]
    daily_price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    image_url: str | None = None

    @field_validator("image_url", mode="before")
    @classmethod
    def empty_to_none(cls, value):
        return None if value == "" else value
```

- Forms: `form: Annotated[CarForm, Form()]`. Query filters:
  `filters: Annotated[CarFilters, Query()]`.
- An empty HTML field arrives as `""`. Optional fields convert `""` to `None` with a
  `mode="before"` validator, as above.
- Invalid input raises Pydantic errors; the global handler in `main.py` renders
  `error.html` with status 422. Do not add your own try/except around form parsing.
- Pydantic 2 only: `field_validator`, `model_validator`, `model_dump`, `model_config`.
  Never `@validator`, `class Config`, `orm_mode` or `.dict()`.

### 5.4 Templates

```html
{% extends "base.html" %}
{% block title %}My fleet{% endblock %}
{% block content %}
<h1 class="h3 mb-3">My fleet</h1>
<form method="post" class="row g-3 col-md-8">
  <div class="col-md-6">
    <label class="form-label" for="brand">Brand</label>
    <input class="form-control" id="brand" name="brand" value="{{ car.brand if car }}" required>
  </div>
  <div class="col-12">
    <button class="btn btn-primary">Save</button>
  </div>
</form>
{% endblock %}
```

- Every page: `{% extends "base.html" %}`, blocks `title` and `content` only.
- Each input's `name` equals the field name in the Pydantic model.
- Repeat the server rules as HTML attributes (`required`, `min`, `max`, `step`), but the
  Pydantic model stays the real check.
- Actions that change data are `<form method="post">` buttons, never links.
- Empty lists show a sentence (`No cars match these filters.`), never a blank page.
- Inline `<script>` is allowed only to pass data, e.g.
  `<script>const MAP_POINTS = {{ map_points|tojson }};</script>`. Logic goes in
  `app/static/map.js`.

### 5.5 Style

- Formatting and import order come from ruff (line length 100). Run it; do not hand-format.
- Names: `snake_case` functions and variables, `PascalCase` classes, verbs for functions
  (`list_for_owner`, `create_reservation`), routes in lowercase with hyphens or plain words.
- Comments explain **why**, not what. No commented-out code, no `print` debugging.
- No bare `except:` and no `except Exception:` except the single LLM fallback in
  `recommendation.recommend`.
- Secrets only from settings (`app/config.py` and `.env`). Never hard-code keys.

## 6. Common mistakes: never do these

| Do not | Do instead |
| --- | --- |
| `async def` endpoints | `def` endpoints |
| `db.query(Car).filter(...)` | `db.scalars(select(Car).where(...)).all()` |
| `Column(Integer)` style models | `Mapped[int] = mapped_column(...)` (Metin only) |
| `TemplateResponse("x.html", {"request": request})` | `TemplateResponse(request, "x.html", {...})` |
| `@app.on_event("startup")` | Already handled by `lifespan` in `main.py` |
| `RedirectResponse(url)` after `POST` (307) or 302 | `RedirectResponse(url, status_code=303)` |
| `float` for prices | `Decimal` |
| `datetime` for reservation dates | `date` and `Range(start, end)` |
| Checking availability with a SELECT before inserting, as protection | Rely on the constraint; catch `CarUnavailable` |
| JSON API + JavaScript that renders the page | Server-rendered Jinja templates |
| New packages, new folders, new config files | Ask Metin |
| Editing files not listed in the card | Stop and ask |
| Turkish UI text | English UI text |
| Returning 403 for another company's car | 404 |

## 7. Tests

- Tests live in `tests/test_<area>.py` as plain `pytest` functions. No classes.
- `tests/conftest.py` points the app at a separate database `car_rental_test` and resets
  it before every test. Tests never touch the dev database.
- Fixtures available in every test:

| Fixture | Gives you |
| --- | --- |
| `db` | A SQLAlchemy `Session` |
| `client` | A FastAPI `TestClient` |
| `make_user(role="customer", email=None)` | A saved `User`; password is `secret123` |
| `make_car(owner, **overrides)` | A saved active `Car` (Fiat Egea, Adana, 1200.00 TL) |
| `login(user)` | Logs `client` in as that user |

- Every new service function gets at least one test for the normal case and one for each
  rule it enforces (wrong owner, inactive car, bad dates...).
- After requests made through `client`, call `db.expire_all()` before reading with `db`.
- Use dates relative to `date.today()`, never fixed calendar dates.

Example:

```python
from datetime import date, timedelta
from decimal import Decimal

import pytest

from app.services import booking
from app.services.booking import InvalidDates


def days(n: int) -> date:
    return date.today() + timedelta(days=n)


def test_validate_dates():
    booking.validate_dates(days(1), days(3))
    with pytest.raises(InvalidDates):
        booking.validate_dates(days(3), days(3))


def test_quote(make_user, make_car):
    car = make_car(make_user("company"), daily_price=Decimal("1200.50"))
    assert booking.quote(car, days(10), days(13)) == Decimal("3601.50")
```

## 8. Commands

```bash
docker compose up -d                    # start PostgreSQL
uv sync                                 # install dependencies
uv run python -m scripts.seed           # reset dev database with demo data
uv run uvicorn app.main:app --reload    # run the app on http://localhost:8000
uv run ruff format .                    # format
uv run ruff check --fix .               # lint
uv run pytest                           # tests
```

All commands run from the project root. Before every commit: format, lint, tests.
CI runs the same three checks on every pull request; a red CI is not merged.

## 9. Git

- One card = one branch = one pull request. Branch name: `<card-id>-<short-name>`,
  e.g. `1.8a-fleet-service`.
- Commit message: `<card-id>: <imperative sentence>`, e.g. `1.8a: Add fleet service`.
- Never push to `main`. Never commit `.env`.
- Fill in the pull request template, including the understanding questions in your own words.

## 10. How to answer

Answer in this order:

1. **Plan** (Turkish, 2 to 4 sentences): what you will build and the exact list of files you
   will create or change. The list must match the card's "Files".
2. **Code:** the complete content of every file you create or change, each under a heading
   with its path. Complete files, not diffs or fragments, so a beginner can copy them
   safely. If a listed file is large and you change one function only, show the complete
   function and say exactly where it goes.
3. **Run:** the commands to run and what the student should see (page, test output).
4. **Explanation** (Turkish, for a beginner): what each new function or template part does
   and why it is written this way. Mention any rule from this file that shaped the code.
5. **Open points:** anything you assumed or could not do. If nothing, say so.

Do not answer the card's "Anlama soruları" for the student. If asked, give hints and point
to the relevant lines; the student writes the answers in their own words.
