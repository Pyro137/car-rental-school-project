from typing import Annotated

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.deps import Company, Db, templates
from app.services import fleet
from app.services.fleet import CarForm

router = APIRouter(prefix="/fleet")


@router.get("")
def fleet_list(request: Request, db: Db, user: Company):
    return templates.TemplateResponse(
        request,
        "fleet/list.html",
        {
            "cars": fleet.list_for_owner(db, user.id),
        },
    )


@router.get("/new")
def create_form(request: Request, user: Company) -> HTMLResponse:
    return templates.TemplateResponse(request, "fleet/form.html", {"car": None})


@router.post("/new")
def create(
    request: Request, db: Db, user: Company, form: Annotated[CarForm, Form()]
) -> RedirectResponse:
    fleet.create(db, user.id, form)
    request.session["flash"] = "Car added."
    return RedirectResponse("/fleet", status_code=303)


@router.get("/{car_id}/edit")
def edit_form(request: Request, db: Db, user: Company, car_id: int) -> HTMLResponse:
    car = fleet.get_owned(db, user.id, car_id)
    if car is None:
        raise HTTPException(status_code=404)
    return templates.TemplateResponse(request, "fleet/form.html", {"car": car})


@router.post("/{car_id}/edit")
def edit(
    request: Request, db: Db, user: Company, car_id: int, form: Annotated[CarForm, Form()]
) -> RedirectResponse:
    car = fleet.get_owned(db, user.id, car_id)
    if car is None:
        raise HTTPException(status_code=404)
    fleet.update(db, car, form)
    request.session["flash"] = "Car updated."
    return RedirectResponse("/fleet", status_code=303)


@router.post("/{car_id}/toggle")
def toggle(db: Db, user: Company, car_id: int) -> RedirectResponse:
    car = fleet.get_owned(db, user.id, car_id)
    if car is None:
        raise HTTPException(status_code=404)
    fleet.toggle_active(db, car)
    return RedirectResponse("/fleet", status_code=303)
