from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Request

from app.deps import Db, templates
from app.services import cars
from app.services.cars import CarFilters

router = APIRouter()


@router.get("/cars")
def car_list(request: Request, db: Db, filters: Annotated[CarFilters, Query()]):
    return templates.TemplateResponse(
        request,
        "cars/list.html",
        {
            "cars": cars.list_cars(db, filters),
            "brands": cars.list_brands(db),
            "filters": filters,
        },
    )


@router.get("/cars/{car_id}")
def car_detail(request: Request, db: Db, car_id: int):
    car = cars.get_active_car(db, car_id)
    if car is None:
        raise HTTPException(status_code=404)
    return templates.TemplateResponse(request, "cars/detail.html", {"car": car})
