from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app import models  # noqa: F401  (registers the tables on Base.metadata)
from app.config import settings
from app.db import init_db
from app.deps import LoginRequired, templates
from app.routers import auth, cars, fleet, recommend, reservations


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Car Rental", lifespan=lifespan)
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key, same_site="lax")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(auth.router)
app.include_router(cars.router)
app.include_router(fleet.router)
app.include_router(reservations.router)
app.include_router(recommend.router)


@app.exception_handler(RequestValidationError)
def invalid_input(request: Request, exc: RequestValidationError):
    messages = [f"{error['loc'][-1]}: {error['msg']}" for error in exc.errors()]
    return templates.TemplateResponse(
        request,
        "error.html",
        {"title": "Invalid input", "messages": messages},
        status_code=422,
    )


@app.exception_handler(LoginRequired)
def redirect_to_login(request: Request, exc: LoginRequired):
    return RedirectResponse("/login", status_code=303)


@app.get("/")
def home():
    return RedirectResponse("/cars")


@app.get("/health")
def health():
    return {"status": "ok"}
