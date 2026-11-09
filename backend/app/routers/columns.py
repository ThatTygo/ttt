from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session as DbSession

from .. import schemas
from ..auth import require_role
from ..db import get_db
from ..models import Column, User, now

router = APIRouter(prefix="/api/columns", tags=["columns"])


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
            id=c.id, title=c.title, author_name=c.author_name, published_at=c.published_at, excerpt=_excerpt(c.body)
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
    db.commit()
    return column


@router.delete("/{column_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_role("editor"))])
def delete_column(column_id: int, db: DbSession = Depends(get_db)):
    column = db.get(Column, column_id)
    if column is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Column niet gevonden.")
    db.delete(column)
    db.commit()
