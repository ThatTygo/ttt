import hashlib
import secrets
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone

from argon2 import PasswordHasher
from argon2.exceptions import VerificationError
from fastapi import Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session as DbSession

from .config import settings
from .db import get_db
from .models import ROLE_RANK, Session, User, now

COOKIE_NAME = "ttt_session"
_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    try:
        return _hasher.verify(password_hash, password)
    except VerificationError:
        return False


# Zelfde rekentijd als bij een bestaand account, zodat je niet kunt raden welke e-mails bestaan.
_DUMMY_HASH = hash_password("niet-een-echt-wachtwoord")


def verify_dummy() -> None:
    verify_password(_DUMMY_HASH, "x")


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def start_session(db: DbSession, response: Response, user: User) -> None:
    token = secrets.token_urlsafe(32)
    expires = now() + timedelta(days=settings.session_days)
    db.add(Session(token_hash=_token_hash(token), user_id=user.id, expires_at=expires))
    user.last_login_at = now()
    db.commit()
    response.set_cookie(
        COOKIE_NAME,
        token,
        max_age=settings.session_days * 86400,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        path="/",
    )


def end_session(db: DbSession, request: Request, response: Response) -> None:
    token = request.cookies.get(COOKIE_NAME)
    if token:
        db.query(Session).filter(Session.token_hash == _token_hash(token)).delete()
        db.commit()
    response.delete_cookie(COOKIE_NAME, path="/")


def current_user_optional(request: Request, db: DbSession = Depends(get_db)) -> User | None:
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return None
    session = db.get(Session, _token_hash(token))
    if session is None:
        return None
    if session.expires_at < datetime.now(timezone.utc):
        db.delete(session)
        db.commit()
        return None
    user = session.user
    if user.status != "approved":
        return None
    return user


def current_user(user: User | None = Depends(current_user_optional)) -> User:
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Je bent niet ingelogd.")
    return user


def require_role(minimum: str):
    def dependency(user: User = Depends(current_user)) -> User:
        if ROLE_RANK[user.role] < ROLE_RANK[minimum]:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Daar heb je de rechten niet voor.")
        return user

    return dependency


class RateLimiter:
    """Simpele in-memory limiet per IP, genoeg tegen brute-force op het inlogformulier."""

    def __init__(self, max_hits: int, window_seconds: int):
        self.max_hits = max_hits
        self.window = window_seconds
        self.hits: dict[str, deque[float]] = defaultdict(deque)

    def __call__(self, request: Request) -> None:
        key = request.client.host if request.client else "?"
        stamp = time.monotonic()
        # IP-adressen niet langer bewaren dan het venster (zie privacybeleid).
        for stale in [k for k, v in self.hits.items() if not v or stamp - v[-1] > self.window]:
            del self.hits[stale]
        hits = self.hits[key]
        while hits and stamp - hits[0] > self.window:
            hits.popleft()
        if len(hits) >= self.max_hits:
            raise HTTPException(
                status.HTTP_429_TOO_MANY_REQUESTS, "Te veel pogingen. Probeer het over een paar minuten opnieuw."
            )
        hits.append(stamp)


login_limiter = RateLimiter(max_hits=10, window_seconds=300)
register_limiter = RateLimiter(max_hits=5, window_seconds=3600)
