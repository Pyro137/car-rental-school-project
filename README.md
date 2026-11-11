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
