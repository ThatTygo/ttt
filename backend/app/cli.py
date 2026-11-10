"""Beheercommando's.

    python -m app.cli init-db                       tabellen aanmaken (bestaande data blijft staan)
    python -m app.cli create-admin EMAIL NAAM       admin aanmaken of bestaand account admin maken
"""

import getpass
import sys

from sqlalchemy import func, select

from . import models
from .auth import hash_password
from .db import Base, SessionLocal, engine


def init_db() -> None:
    Base.metadata.create_all(engine)


def create_admin(email: str, name: str) -> None:
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        user = db.scalar(select(models.User).where(func.lower(models.User.email) == email.lower()))
        if user is None:
            password = getpass.getpass("Wachtwoord (min. 10 tekens): ")
            if len(password) < 10:
                sys.exit("Wachtwoord te kort.")
            if password != getpass.getpass("Nogmaals: "):
                sys.exit("Wachtwoorden komen niet overeen.")
            user = models.User(name=name, email=email.lower(), password_hash=hash_password(password))
            db.add(user)
        user.role = "admin"
        user.status = "approved"
        user.approved_at = user.approved_at or models.now()
        db.commit()
        print(f"{user.email} is nu admin.")


if __name__ == "__main__":
    match sys.argv[1:]:
        case ["init-db"]:
            init_db()
        case ["create-admin", email, *name]:
            create_admin(email, " ".join(name) or email.split("@")[0])
        case _:
            sys.exit(__doc__)
