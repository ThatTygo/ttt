from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session as DbSession

from .. import schemas
from ..auth import current_user, end_session, hash_password, require_role, verify_password
from ..db import get_db
from ..models import User, now

router = APIRouter(prefix="/api", tags=["users"])


def _admin_count(db: DbSession) -> int:
    return db.scalar(select(func.count()).where(User.role == "admin", User.status == "approved"))


# --- Eigen account ------------------------------------------------------


@router.patch("/account", response_model=schemas.UserOut)
def update_account(data: schemas.AccountUpdate, user: User = Depends(current_user), db: DbSession = Depends(get_db)):
    if data.name:
        user.name = data.name.strip()
    if data.new_password:
        if not data.current_password or not verify_password(user.password_hash, data.current_password):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Je huidige wachtwoord klopt niet.")
        user.password_hash = hash_password(data.new_password)
    db.commit()
    return user


@router.get("/account/export")
def export_account(user: User = Depends(current_user)):
    """Inzagerecht (AVG art. 15): alles wat we over het account opslaan."""
    return {
        "account": schemas.UserOut.model_validate(user).model_dump(mode="json"),
        "actieve_sessies": len(user.sessions),
    }


@router.delete("/account", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(
    data: schemas.PasswordConfirm,
    request: Request,
    response: Response,
    user: User = Depends(current_user),
    db: DbSession = Depends(get_db),
):
    if not verify_password(user.password_hash, data.password):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Wachtwoord klopt niet.")
    if user.role == "admin" and _admin_count(db) <= 1:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Je bent de laatste admin. Maak eerst iemand anders admin.")
    end_session(db, request, response)
    db.delete(user)
    db.commit()


# --- Gebruikersbeheer (admin) ------------------------------------------


@router.get("/users", response_model=list[schemas.UserOut], dependencies=[Depends(require_role("admin"))])
def list_users(db: DbSession = Depends(get_db)):
    return db.scalars(select(User).order_by(User.status.desc(), User.name)).all()


@router.patch("/users/{user_id}", response_model=schemas.UserOut)
def update_user(
    user_id: int,
    data: schemas.UserAdminUpdate,
    admin: User = Depends(require_role("admin")),
    db: DbSession = Depends(get_db),
):
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Gebruiker niet gevonden.")
    losing_admin = user.role == "admin" and user.status == "approved" and (
        (data.role and data.role != "admin") or data.status == "pending"
    )
    if losing_admin and _admin_count(db) <= 1:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Er moet minstens één admin overblijven.")
    if data.role:
        user.role = data.role
    if data.status and data.status != user.status:
        user.status = data.status
        user.approved_at = now() if data.status == "approved" else None
        if data.status == "pending":
            user.sessions.clear()
    db.commit()
    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, admin: User = Depends(require_role("admin")), db: DbSession = Depends(get_db)):
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Gebruiker niet gevonden.")
    if user.id == admin.id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Verwijder je eigen account via 'Mijn account'.")
    if user.role == "admin" and _admin_count(db) <= 1:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Er moet minstens één admin overblijven.")
    db.delete(user)
    db.commit()
