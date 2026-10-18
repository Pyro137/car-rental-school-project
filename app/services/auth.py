from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import User

_hasher = PasswordHash.recommended()


def register(
    db: Session,
    *,
    email: str,
    password: str,
    full_name: str,
    role: str,
    company_name: str | None,
) -> User | None:
    """Create a user. Returns None if the email is already registered."""
    user = User(
        email=email.strip().lower(),
        password_hash=_hasher.hash(password),
        full_name=full_name.strip(),
        role=role,
        company_name=company_name.strip() if role == "company" and company_name else None,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return None
    return user


def authenticate(db: Session, email: str, password: str) -> User | None:
    user = db.scalar(select(User).where(User.email == email.strip().lower()))
    if user is None or not _hasher.verify(password, user.password_hash):
        return None
    return user
