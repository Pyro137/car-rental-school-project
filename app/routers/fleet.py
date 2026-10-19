from fastapi import APIRouter, Request

from app.deps import Company, Db, templates
from app.services import fleet

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
