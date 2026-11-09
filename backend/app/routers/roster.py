from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session as DbSession

from .. import schemas
from ..auth import require_role
from ..db import get_db
from ..models import Member

# Alleen naam + dienstdag van actieve leden, voor editors en admins.
router = APIRouter(prefix="/api/roster", tags=["roster"], dependencies=[Depends(require_role("editor"))])


@router.get("", response_model=list[schemas.RosterDay])
def get_roster(db: DbSession = Depends(get_db)):
    members = db.scalars(
        select(Member).where(Member.active, Member.shift_day.is_not(None)).order_by(Member.name)
    ).all()
    return [
        schemas.RosterDay(day=day, names=[m.name for m in members if m.shift_day == day]) for day in range(7)
    ]
