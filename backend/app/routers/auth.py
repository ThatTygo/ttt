from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session as DbSession

from .. import schemas
from ..auth import (
    current_user,
    end_session,
    hash_password,
    login_limiter,
    register_limiter,
    start_session,
    verify_dummy,
    verify_password,
)
from ..db import get_db
from ..models import User

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _find_by_email(db: DbSession, email: str) -> User | None:
    return db.scalar(select(User).where(func.lower(User.email) == email.lower()))


@router.post("/register", status_code=status.HTTP_201_CREATED, dependencies=[Depends(register_limiter)])
def register(data: schemas.RegisterIn, db: DbSession = Depends(get_db)):
    if _find_by_email(db, data.email):
        raise HTTPException(status.HTTP_409_CONFLICT, "Er bestaat al een account met dit e-mailadres.")
    db.add(User(name=data.name, email=data.email.lower(), password_hash=hash_password(data.password)))
    db.commit()
    return {"message": "Account aangemaakt. Een admin moet je account nog goedkeuren voordat je kunt inloggen."}


@router.post("/login", response_model=schemas.UserOut, dependencies=[Depends(login_limiter)])
def login(data: schemas.LoginIn, response: Response, db: DbSession = Depends(get_db)):
    user = _find_by_email(db, data.email)
    if user is None:
        verify_dummy()
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "E-mailadres of wachtwoord klopt niet.")
    if not verify_password(user.password_hash, data.password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "E-mailadres of wachtwoord klopt niet.")
    if user.status != "approved":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Je account wacht nog op goedkeuring door een admin.")
    start_session(db, response, user)
    return user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(request: Request, response: Response, db: DbSession = Depends(get_db)):
    end_session(db, request, response)


@router.get("/me", response_model=schemas.UserOut)
def me(user: User = Depends(current_user)):
    return user
