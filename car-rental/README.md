# Car Rental System

CEN317 Engineering Design project.

## Setup

```bash
git clone <repo-url>
cd car-rental
cp .env.example .env
docker compose up -d
uv sync
uv run uvicorn app.main:app --reload
```

Open http://localhost:8000/health

## Team

- Metin
