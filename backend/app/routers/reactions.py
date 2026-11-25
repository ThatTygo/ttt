"""Likes en reacties op columns, en likes op reacties. Voor alle ingelogde leden."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session as DbSession

from .. import schemas
from ..auth import current_user
from ..db import get_db
from ..models import ROLE_RANK, Column, ColumnLike, Comment, CommentLike, User, now

router = APIRouter(prefix="/api", tags=["reactions"])


def _likes(db: DbSession, model, key, value: int, user: User) -> schemas.LikesOut:
    rows = db.execute(
        select(User.id, User.name).join(model, model.user_id == User.id).where(key == value).order_by(model.created_at)
    ).all()
    return schemas.LikesOut(count=len(rows), liked=any(uid == user.id for uid, _ in rows), names=[n for _, n in rows])


def _column(db: DbSession, column_id: int) -> Column:
    column = db.get(Column, column_id)
    if column is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Column niet gevonden.")
    return column


def _comment(db: DbSession, comment_id: int) -> Comment:
    comment = db.get(Comment, comment_id)
    if comment is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Reactie niet gevonden.")
    return comment


def _can_moderate(user: User) -> bool:
    # Editors en admins beheren de columns, dus ook de reacties eronder.
    return ROLE_RANK[user.role] >= ROLE_RANK["editor"]


def _comment_out(db: DbSession, comment: Comment, user: User) -> schemas.CommentOut:
    return schemas.CommentOut(
        id=comment.id,
        body=comment.body,
        author=schemas.CommentAuthor(id=comment.user.id, name=comment.user.name),
        created_at=comment.created_at,
        edited_at=comment.edited_at,
        likes=_likes(db, CommentLike, CommentLike.comment_id, comment.id, user),
        can_edit=comment.user_id == user.id,
        can_delete=comment.user_id == user.id or _can_moderate(user),
    )


def _set_like(db: DbSession, model, like: bool, **key) -> None:
    existing = db.get(model, tuple(key.values()))
    if like and existing is None:
        db.add(model(**key))
    elif not like and existing is not None:
        db.delete(existing)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()  # tegelijk twee keer geliket: de like bestaat al


# --- Column ---------------------------------------------------------------


@router.get("/columns/{column_id}/reactions", response_model=schemas.ReactionsOut)
def get_reactions(column_id: int, user: User = Depends(current_user), db: DbSession = Depends(get_db)):
    _column(db, column_id)
    comments = db.scalars(select(Comment).where(Comment.column_id == column_id).order_by(Comment.created_at)).all()
    return schemas.ReactionsOut(
        likes=_likes(db, ColumnLike, ColumnLike.column_id, column_id, user),
        comments=[_comment_out(db, c, user) for c in comments],
    )


@router.put("/columns/{column_id}/like", response_model=schemas.LikesOut)
def like_column(column_id: int, user: User = Depends(current_user), db: DbSession = Depends(get_db)):
    _column(db, column_id)
    _set_like(db, ColumnLike, True, column_id=column_id, user_id=user.id)
    return _likes(db, ColumnLike, ColumnLike.column_id, column_id, user)


@router.delete("/columns/{column_id}/like", response_model=schemas.LikesOut)
def unlike_column(column_id: int, user: User = Depends(current_user), db: DbSession = Depends(get_db)):
    _column(db, column_id)
    _set_like(db, ColumnLike, False, column_id=column_id, user_id=user.id)
    return _likes(db, ColumnLike, ColumnLike.column_id, column_id, user)


@router.post("/columns/{column_id}/comments", response_model=schemas.CommentOut, status_code=status.HTTP_201_CREATED)
def add_comment(column_id: int, data: schemas.CommentIn, user: User = Depends(current_user),
                db: DbSession = Depends(get_db)):
    _column(db, column_id)
    if not data.body:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Je reactie is leeg.")
    comment = Comment(column_id=column_id, user_id=user.id, body=data.body)
    db.add(comment)
    db.commit()
    return _comment_out(db, comment, user)


# --- Reactie --------------------------------------------------------------


@router.patch("/comments/{comment_id}", response_model=schemas.CommentOut)
def edit_comment(comment_id: int, data: schemas.CommentIn, user: User = Depends(current_user),
                 db: DbSession = Depends(get_db)):
    comment = _comment(db, comment_id)
    if comment.user_id != user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Je kunt alleen je eigen reacties bewerken.")
    if not data.body:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Je reactie is leeg.")
    if data.body != comment.body:
        comment.body = data.body
        comment.edited_at = now()
        db.commit()
    return _comment_out(db, comment, user)


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(comment_id: int, user: User = Depends(current_user), db: DbSession = Depends(get_db)):
    comment = _comment(db, comment_id)
    if comment.user_id != user.id and not _can_moderate(user):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Je kunt alleen je eigen reacties verwijderen.")
    db.delete(comment)
    db.commit()


@router.put("/comments/{comment_id}/like", response_model=schemas.LikesOut)
def like_comment(comment_id: int, user: User = Depends(current_user), db: DbSession = Depends(get_db)):
    _comment(db, comment_id)
    _set_like(db, CommentLike, True, comment_id=comment_id, user_id=user.id)
    return _likes(db, CommentLike, CommentLike.comment_id, comment_id, user)


@router.delete("/comments/{comment_id}/like", response_model=schemas.LikesOut)
def unlike_comment(comment_id: int, user: User = Depends(current_user), db: DbSession = Depends(get_db)):
    _comment(db, comment_id)
    _set_like(db, CommentLike, False, comment_id=comment_id, user_id=user.id)
    return _likes(db, CommentLike, CommentLike.comment_id, comment_id, user)
