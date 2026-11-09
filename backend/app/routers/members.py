from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session as DbSession

from .. import schemas
from ..auth import require_role
from ..db import get_db
from ..models import Member, User

# De ledenadministratie is in zijn geheel alleen voor admins (AVG).
router = APIRouter(prefix="/api/members", tags=["members"], dependencies=[Depends(require_role("admin"))])


@router.get("", response_model=list[schemas.MemberOut])
def list_members(db: DbSession = Depends(get_db)):
    return db.scalars(select(Member).order_by(Member.active.desc(), Member.name)).all()


def _check_user(db: DbSession, user_id: int | None) -> None:
    if user_id is not None and db.get(User, user_id) is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Gekoppeld account bestaat niet.")


@router.post("", response_model=schemas.MemberOut, status_code=status.HTTP_201_CREATED)
def create_member(data: schemas.MemberIn, db: DbSession = Depends(get_db)):
    _check_user(db, data.user_id)
    member = Member(**data.model_dump())
    db.add(member)
    db.commit()
    return member


@router.put("/{member_id}", response_model=schemas.MemberOut)
def update_member(member_id: int, data: schemas.MemberIn, db: DbSession = Depends(get_db)):
    member = db.get(Member, member_id)
    if member is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Lid niet gevonden.")
    _check_user(db, data.user_id)
    for key, value in data.model_dump().items():
        setattr(member, key, value)
    db.commit()
    return member


@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_member(member_id: int, db: DbSession = Depends(get_db)):
    member = db.get(Member, member_id)
    if member is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Lid niet gevonden.")
    db.delete(member)
    db.commit()
