from datetime import date, datetime, timezone

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, LargeBinary, String, Table, Text, false, true
from sqlalchemy import Column as SqlColumn
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base

ROLES = ("user", "editor", "admin")
ROLE_RANK = {role: rank for rank, role in enumerate(ROLES)}
STATUSES = ("pending", "approved")


def now() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80))
    email: Mapped[str] = mapped_column(String(254), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(16), default="user")
    status: Mapped[str] = mapped_column(String(16), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    # Mail ontvangen bij een nieuwe Pimpy-taak.
    email_tasks: Mapped[bool] = mapped_column(Boolean, default=True, server_default=true())
    # Profiel: korte tekst over jezelf; tijdstip van de laatste profielfoto (ook voor cache).
    bio: Mapped[str | None] = mapped_column(Text)
    avatar_updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    sessions: Mapped[list["Session"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", passive_deletes=True
    )

    @property
    def avatar_url(self) -> str | None:
        if self.avatar_updated_at is None:
            return None
        return f"/api/users/{self.id}/avatar?v={int(self.avatar_updated_at.timestamp())}"


class Avatar(Base):
    """Profielfoto, al verkleind tot een vierkante WebP."""

    __tablename__ = "avatars"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    image: Mapped[bytes] = mapped_column(LargeBinary)


class Session(Base):
    __tablename__ = "sessions"

    # SHA-256 van het token; het token zelf staat alleen in de cookie.
    token_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    user: Mapped[User] = relationship(back_populates="sessions")


class Member(Base):
    __tablename__ = "members"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80))
    nickname: Mapped[str | None] = mapped_column(String(80))
    function: Mapped[str | None] = mapped_column(String(80))
    # 0 = maandag ... 6 = zondag; dag waarop dit lid de column schrijft.
    shift_day: Mapped[int | None] = mapped_column(Integer)
    member_since: Mapped[date | None] = mapped_column(Date)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    notes: Mapped[str | None] = mapped_column(Text)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)


class Column(Base):
    __tablename__ = "columns"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(160))
    body: Mapped[str] = mapped_column(Text)
    author_name: Mapped[str] = mapped_column(String(120))
    # Deze column meldde een stickerwaardig tramincident (en heeft de teller bijgewerkt).
    has_incident: Mapped[bool] = mapped_column(Boolean, default=False, server_default=false())
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, index=True)
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    updated_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)


class Counter(Base):
    """Eén rij met de stand van de teller op de homepage."""

    __tablename__ = "counter"

    id: Mapped[int] = mapped_column(primary_key=True, default=1)
    last_incident_date: Mapped[date | None] = mapped_column(Date)
    last_incident_text: Mapped[str | None] = mapped_column(String(300))
    sticker_count: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)


# --- Pimpy: groepen, notulen, taken en vergaderingen ---------------------

group_members = Table(
    "group_members",
    Base.metadata,
    SqlColumn("group_id", ForeignKey("groups.id", ondelete="CASCADE"), primary_key=True),
    SqlColumn("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
)

task_users = Table(
    "task_users",
    Base.metadata,
    SqlColumn("task_id", ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True),
    SqlColumn("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
)


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True)
    description: Mapped[str | None] = mapped_column(String(300))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

    members: Mapped[list[User]] = relationship(secondary=group_members, order_by=User.name)


class Minute(Base):
    __tablename__ = "minutes"

    id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id", ondelete="CASCADE"), index=True)
    minute_date: Mapped[date] = mapped_column(Date)
    content: Mapped[str] = mapped_column(Text)
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

    group: Mapped[Group] = relationship()
    created_by: Mapped[User | None] = relationship()


# Volgorde = waarde in de database (zelfde als viaduct).
TASK_STATUSES = ("new", "started", "done", "not_done", "finished", "deleted")
OPEN_STATUSES = (0, 1, 2, 3)


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id", ondelete="CASCADE"), index=True)
    minute_id: Mapped[int | None] = mapped_column(ForeignKey("minutes.id", ondelete="CASCADE"), index=True)
    # Regelnummer in de notulen waar de taak uit komt.
    line: Mapped[int | None] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(String(500))
    content: Mapped[str | None] = mapped_column(Text)
    status: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)

    group: Mapped[Group] = relationship()
    minute: Mapped[Minute | None] = relationship()
    users: Mapped[list[User]] = relationship(secondary=task_users, order_by=User.name)


class Meeting(Base):
    __tablename__ = "meetings"

    id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id", ondelete="CASCADE"), index=True)
    minute_id: Mapped[int | None] = mapped_column(ForeignKey("minutes.id", ondelete="SET NULL"))
    title: Mapped[str] = mapped_column(String(200))
    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

    group: Mapped[Group] = relationship()
    minute: Mapped[Minute | None] = relationship()


# --- Meldingen (bugs, ideeën, vragen) ------------------------------------

TICKET_KINDS = ("bug", "idee", "vraag")
TICKET_STATUSES = ("open", "in_behandeling", "opgelost", "gesloten")
TICKET_PRIORITIES = ("laag", "normaal", "hoog", "urgent")
CLOSED_TICKET_STATUSES = ("opgelost", "gesloten")


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True)
    kind: Mapped[str] = mapped_column(String(16), default="bug")
    title: Mapped[str] = mapped_column(String(160))
    description: Mapped[str] = mapped_column(Text)
    # Pagina waarop de melding is gedaan, bijv. /columns/12.
    page: Mapped[str | None] = mapped_column(String(300))
    status: Mapped[str] = mapped_column(String(20), default="open", index=True)
    priority: Mapped[str] = mapped_column(String(16), default="normaal")
    # Verwijdert de melder zijn account, dan blijft de melding staan zonder naam.
    reporter_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    assignee_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    reporter: Mapped[User | None] = relationship(foreign_keys=[reporter_id])
    assignee: Mapped[User | None] = relationship(foreign_keys=[assignee_id])
    messages: Mapped[list["TicketMessage"]] = relationship(
        back_populates="ticket", cascade="all, delete-orphan", passive_deletes=True,
        order_by="TicketMessage.created_at",
    )


class TicketMessage(Base):
    __tablename__ = "ticket_messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id", ondelete="CASCADE"), index=True)
    author_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    body: Mapped[str] = mapped_column(Text)
    # "message" = reactie, "event" = automatische regel (status gewijzigd e.d.)
    kind: Mapped[str] = mapped_column(String(16), default="message")
    # Interne notitie: alleen zichtbaar voor admins.
    internal: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

    ticket: Mapped[Ticket] = relationship(back_populates="messages")
    author: Mapped[User | None] = relationship()
