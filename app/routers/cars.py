from typing import Annotated

from fastapi import APIRouter, Query, Request

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
