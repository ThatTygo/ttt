from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session as DbSession

from .. import schemas
from ..auth import (
    current_user,
    current_user_optional,
    end_session,
    hash_password,
    login_limiter,
    register_limiter,
    start_session,
    verify_dummy,
    verify_password,
)
from ..config import settings
from ..db import get_db
from ..models import ROLE_RANK, User

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


_WIKI_FORBIDDEN = """<!doctype html><html lang="nl"><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>Geen toegang · TTT Wiki</title>
<body style="font:16px/1.5 system-ui,sans-serif;max-width:32rem;margin:15vh auto;padding:0 16px">
<h1>Geen toegang</h1><p>De wiki is alleen voor editors en admins. Vraag een admin om je de rol editor te geven.</p>
<p><a href="{site}">Terug naar de site</a></p></body></html>"""


@router.get("/wiki", include_in_schema=False)
def wiki_check(request: Request, user: User | None = Depends(current_user_optional)):
    """Toegangscontrole voor de wiki (Caddy forward_auth).

    200 + X-Ttt-*-headers: doorlaten; DokuWiki neemt naam en groepen over.
    Niet ingelogd: door naar het inlogscherm, daarna terug naar de wikipagina.
    """
    site = settings.site_url.rstrip("/")
    if user is None:
        wiki = (settings.wiki_url or "").rstrip("/")
        back = wiki + request.headers.get("x-forwarded-uri", "/") if wiki else ""
        return RedirectResponse(f"{site}/inloggen" + (f"?terug={quote(back, safe='')}" if back else ""), 302)
    if ROLE_RANK[user.role] < ROLE_RANK["editor"]:
        return HTMLResponse(_WIKI_FORBIDDEN.format(site=site), status_code=403)
    groups = ["user", "editor"] + (["admin"] if user.role == "admin" else [])
    return Response(
        status_code=200,
        headers={
            "X-Ttt-User": f"ttt{user.id}",
            # Headers zijn ASCII; DokuWiki decodeert de naam weer.
            "X-Ttt-Name": quote(user.name, safe=" "),
            "X-Ttt-Email": user.email,
            "X-Ttt-Groups": ",".join(groups),
            "Cache-Control": "no-store",
        },
    )
