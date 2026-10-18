from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import models  # noqa: F401  (registers the tables on Base.metadata)
from app.db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Car Rental", lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "ok"}
