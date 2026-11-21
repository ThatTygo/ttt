from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session as DbSession

from .. import schemas
from ..auth import current_user, require_role
from ..config import settings
from ..db import get_db
from ..models import Column, Counter, User, now

# Columns zijn alleen voor ingelogde (goedgekeurde) leden.
router = APIRouter(prefix="/api/columns", tags=["columns"], dependencies=[Depends(current_user)])


def _log_incident(db: DbSession, column: Column, incident: schemas.IncidentIn) -> None:
    """Een gemeld incident plakt een sticker en zet zo nodig de teller terug."""
    counter = db.get(Counter, 1)
    if counter is None:
        counter = Counter(id=1, sticker_count=0)
        db.add(counter)
    day = incident.day or column.published_at.astimezone(ZoneInfo(settings.timezone)).date()
    counter.sticker_count = (counter.sticker_count or 0) + 1
    # Een column over een ouder incident zet de teller niet terug in de tijd.
    if counter.last_incident_date is None or day >= counter.last_incident_date:
        counter.last_incident_date = day
        counter.last_incident_text = incident.text or column.title
    column.has_incident = True


def _excerpt(body: str, length: int = 220) -> str:
    text = " ".join(body.split())
    return text if len(text) <= length else text[:length].rsplit(" ", 1)[0] + "…"


@router.get("", response_model=schemas.ColumnPage)
def list_columns(
    q: str | None = Query(default=None, max_length=100),
    author: str | None = Query(default=None, max_length=120),
    limit: int = Query(default=12, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: DbSession = Depends(get_db),
):
    query = select(Column)
    if q:
        pattern = f"%{q}%"
        query = query.where(or_(Column.title.ilike(pattern), Column.body.ilike(pattern)))
    if author:
        query = query.where(Column.author_name == author)
    total = db.scalar(select(func.count()).select_from(query.subquery()))
    rows = db.scalars(query.order_by(Column.published_at.desc()).limit(limit).offset(offset)).all()
    authors = db.scalars(select(Column.author_name).distinct().order_by(Column.author_name)).all()
    items = [
        schemas.ColumnSummary(
            id=c.id,
            title=c.title,
            author_name=c.author_name,
            has_incident=c.has_incident,
            published_at=c.published_at,
            excerpt=_excerpt(c.body),
        )
        for c in rows
    ]
    return schemas.ColumnPage(items=items, total=total, authors=authors)


@router.get("/{column_id}", response_model=schemas.ColumnOut)
def get_column(column_id: int, db: DbSession = Depends(get_db)):
    column = db.get(Column, column_id)
    if column is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Column niet gevonden.")
    return column


@router.post("", response_model=schemas.ColumnOut, status_code=status.HTTP_201_CREATED)
def create_column(data: schemas.ColumnIn, user: User = Depends(require_role("editor")), db: DbSession = Depends(get_db)):
    column = Column(
        title=data.title,
        body=data.body,
        author_name=data.author_name,
        published_at=data.published_at or now(),
        created_by_id=user.id,
        updated_by_id=user.id,
    )
    db.add(column)
    if data.incident:
        _log_incident(db, column, data.incident)
    db.commit()
    return column


@router.put("/{column_id}", response_model=schemas.ColumnOut)
def update_column(
    column_id: int, data: schemas.ColumnIn, user: User = Depends(require_role("editor")), db: DbSession = Depends(get_db)
):
    column = db.get(Column, column_id)
    if column is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Column niet gevonden.")
    column.title = data.title
    column.body = data.body
    column.author_name = data.author_name
    if data.published_at:
        column.published_at = data.published_at
    column.updated_by_id = user.id
    # Per column hooguit één sticker, ook als hij vaker wordt opgeslagen.
    if data.incident and not column.has_incident:
        _log_incident(db, column, data.incident)
    db.commit()
    return column


@router.delete("/{column_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_role("editor"))])
def delete_column(column_id: int, db: DbSession = Depends(get_db)):
    column = db.get(Column, column_id)
    if column is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Column niet gevonden.")
    db.delete(column)
    db.commit()
