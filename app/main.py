from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles

from app import models  # noqa: F401  (registers the tables on Base.metadata)
from app.db import init_db
from app.deps import templates


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Car Rental", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.exception_handler(RequestValidationError)
def invalid_input(request: Request, exc: RequestValidationError):
    messages = [f"{error['loc'][-1]}: {error['msg']}" for error in exc.errors()]
    return templates.TemplateResponse(
        request,
        "error.html",
        {"title": "Invalid input", "messages": messages},
        status_code=422,
    )


@app.get("/health")
def health():
    return {"status": "ok"}
