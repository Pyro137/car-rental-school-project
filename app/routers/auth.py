from typing import Annotated, Literal

from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse

from app.deps import Db, templates
from app.models import User
from app.services import auth

router = APIRouter()


def _login(request: Request, user: User) -> None:
    request.session.update(user_id=user.id, role=user.role, name=user.full_name)


@router.get("/register")
def register_form(request: Request):
    return templates.TemplateResponse(request, "auth/register.html")


@router.post("/register")
def register(
    request: Request,
    db: Db,
    email: Annotated[str, Form()],
    password: Annotated[str, Form(min_length=8)],
    full_name: Annotated[str, Form(min_length=1)],
    role: Annotated[Literal["customer", "company"], Form()],
    company_name: Annotated[str, Form()] = "",
):
    error = None
    if role == "company" and not company_name.strip():
        error = "Company name is required."
    else:
        user = auth.register(
            db,
            email=email,
            password=password,
            full_name=full_name,
            role=role,
            company_name=company_name,
        )
        if user is None:
            error = "This email is already registered."
    if error:
        return templates.TemplateResponse(
            request, "auth/register.html", {"error": error}, status_code=400
        )
    _login(request, user)
    return RedirectResponse("/cars", status_code=303)


@router.get("/login")
def login_form(request: Request):
    return templates.TemplateResponse(request, "auth/login.html")


@router.post("/login")
def login(
    request: Request,
    db: Db,
    email: Annotated[str, Form()],
    password: Annotated[str, Form()],
):
    user = auth.authenticate(db, email, password)
    if user is None:
        return templates.TemplateResponse(
            request,
            "auth/login.html",
            {"error": "Wrong email or password."},
            status_code=400,
        )
    _login(request, user)
    return RedirectResponse("/cars", status_code=303)


@router.post("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)
