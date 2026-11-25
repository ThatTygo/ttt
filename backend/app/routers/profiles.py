"""Profielen: profielfoto en bio. Alleen zichtbaar voor ingelogde leden."""

import io

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from PIL import Image, ImageOps, UnidentifiedImageError
from sqlalchemy import select
from starlette.concurrency import run_in_threadpool
from sqlalchemy.orm import Session as DbSession, object_session

from .. import schemas
from ..auth import current_user
from ..db import get_db
from ..models import Avatar, User, now

router = APIRouter(prefix="/api", tags=["profiles"])

MAX_UPLOAD_BYTES = 8 * 1024 * 1024
AVATAR_SIZE = 400  # pixels, vierkant
# Bescherming tegen "decompression bombs": kleine bestanden die enorm uitpakken.
Image.MAX_IMAGE_PIXELS = 40_000_000


def user_avatar(user: User) -> bytes | None:
    avatar = object_session(user).get(Avatar, user.id)
    return avatar.image if avatar else None


def _to_avatar(data: bytes) -> bytes:
    """Draait de foto goed, knipt het midden vierkant uit en verkleint naar WebP.

    Opnieuw opslaan haalt ook metadata zoals GPS-locatie uit de foto.
    """
    try:
        with Image.open(io.BytesIO(data)) as img:
            img = ImageOps.exif_transpose(img)
            img = ImageOps.fit(img.convert("RGB"), (AVATAR_SIZE, AVATAR_SIZE), Image.Resampling.LANCZOS)
            out = io.BytesIO()
            img.save(out, "WEBP", quality=85)
            return out.getvalue()
    except (UnidentifiedImageError, Image.DecompressionBombError, OSError, ValueError):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Dit bestand is geen (bruikbare) afbeelding.")


@router.get("/profiles", response_model=list[schemas.ProfileOut])
def list_profiles(_: User = Depends(current_user), db: DbSession = Depends(get_db)):
    return db.scalars(select(User).where(User.status == "approved").order_by(User.name)).all()


@router.get("/profiles/{user_id}", response_model=schemas.ProfileOut)
def get_profile(user_id: int, _: User = Depends(current_user), db: DbSession = Depends(get_db)):
    user = db.get(User, user_id)
    if user is None or user.status != "approved":
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Profiel niet gevonden.")
    return user


@router.get("/users/{user_id}/avatar", include_in_schema=False)
def get_avatar(user_id: int, _: User = Depends(current_user), db: DbSession = Depends(get_db)):
    avatar = db.get(Avatar, user_id)
    if avatar is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Geen profielfoto.")
    # De URL bevat ?v=<tijdstip>, dus een nieuwe foto krijgt een nieuwe URL.
    return Response(avatar.image, media_type="image/webp",
                    headers={"Cache-Control": "private, max-age=31536000, immutable"})


@router.put("/account/avatar", response_model=schemas.UserOut)
async def upload_avatar(request: Request, user: User = Depends(current_user), db: DbSession = Depends(get_db)):
    if not request.headers.get("content-type", "").startswith("image/"):
        raise HTTPException(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "Upload een afbeelding (JPG, PNG, WebP of GIF).")
    data = bytearray()
    async for chunk in request.stream():
        data += chunk
        if len(data) > MAX_UPLOAD_BYTES:
            raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "De foto is te groot (maximaal 8 MB).")
    image = await run_in_threadpool(_to_avatar, bytes(data))
    avatar = db.get(Avatar, user.id)
    if avatar is None:
        db.add(Avatar(user_id=user.id, image=image))
    else:
        avatar.image = image
    user.avatar_updated_at = now()
    db.commit()
    return user


@router.delete("/account/avatar", response_model=schemas.UserOut)
def delete_avatar(user: User = Depends(current_user), db: DbSession = Depends(get_db)):
    avatar = db.get(Avatar, user.id)
    if avatar is not None:
        db.delete(avatar)
    user.avatar_updated_at = None
    db.commit()
    return user
