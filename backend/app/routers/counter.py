from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DbSession

from .. import schemas
from ..auth import require_role
from ..db import get_db
from ..models import Counter

router = APIRouter(prefix="/api/counter", tags=["counter"])


def _get(db: DbSession) -> Counter:
    counter = db.get(Counter, 1)
    if counter is None:
        counter = Counter(id=1)
        db.add(counter)
        db.commit()
    return counter


@router.get("", response_model=schemas.CounterOut)
def get_counter(db: DbSession = Depends(get_db)):
    return _get(db)


@router.put("", response_model=schemas.CounterOut, dependencies=[Depends(require_role("editor"))])
def update_counter(data: schemas.CounterIn, db: DbSession = Depends(get_db)):
    counter = _get(db)
    for key, value in data.model_dump().items():
        setattr(counter, key, value)
    db.commit()
    return counter
