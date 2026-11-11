# Car Rental System

CEN317 Engineering Design project. Customers filter and rent cars; rental companies manage
their own fleet. Built with FastAPI, PostgreSQL and server-rendered Jinja templates.

## Requirements

Git, Docker Desktop and [uv](https://docs.astral.sh/uv/). uv installs the right Python version.

## Setup

```bash
git clone https://github.com/Pyro137/car-rental-school-project.git
cd car-rental-school-project
cp .env.example .env
docker compose up -d
uv sync
uv run python -m scripts.seed
```

The seed command resets the database and loads demo data. Run it again whenever the models
change.

## Run

```bash
uv run uvicorn app.main:app --reload
```

Open http://localhost:8000. Demo accounts (password `demo1234`):

- Customer: `customer@example.com`
- Companies: `acme@example.com`, `speedcar@example.com`, `luxeride@example.com`

## Try it end to end

Start from a fresh database (`uv run python -m scripts.seed`), then:

1. **Company:** click "Sign up", choose "Rental company" and enter a company name.
   "My fleet" appears in the menu.
2. Open "My fleet", click "Add car", fill in the form and save. "Car added." is shown once.
3. Click "Edit" on the new car, change the price and save. Then click "Deactivate" and
   "Activate" again; the status badge follows.
4. Click "Log out". **Customer:** sign up as "Customer".
5. On "Cars", filter by the new car's brand and a price range around it, then click "Details".
6. **Access rules:** as the customer, open http://localhost:8000/fleet and get 403. Log out
   and log in with a wrong password; it is rejected.

While the car is inactive in step 3, it is missing from "Cars" and its details page returns
404. After running the seed again, log out and back in.

## Checks

```bash
uv run ruff format .
uv run ruff check --fix .
uv run pytest
```

Tests use a separate `car_rental_test` database and never touch the demo data. CI runs the
same checks on every pull request. Coding rules for people and AI tools are in `AGENTS.md`.

## Team

- Metin 2022556033
- Gizem
- Enes
