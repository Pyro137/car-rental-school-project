from typing import Annotated

from fastapi import Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import User

templates = Jinja2Templates(directory="app/templates")

Db = Annotated[Session, Depends(get_db)]


class LoginRequired(Exception):
    pass


def current_user(request: Request, db: Db) -> User | None:
    user_id = request.session.get("user_id")
    return db.get(User, user_id) if user_id else None


def require_role(role: str):
    def dependency(user: Annotated[User | None, Depends(current_user)]) -> User:
        if user is None:
            raise LoginRequired
        if user.role != role:
            raise HTTPException(status_code=403)
        return user

    return dependency


Customer = Annotated[User, Depends(require_role("customer"))]
Company = Annotated[User, Depends(require_role("company"))]
