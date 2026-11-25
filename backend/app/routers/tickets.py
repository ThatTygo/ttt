"""Meldingen: bugs, ideeën en vragen over de site.

Iedere ingelogde gebruiker kan melden en ziet zijn eigen meldingen.
Admins zien alles, wijzigen status/prioriteit/behandelaar en kunnen interne
notities maken die de melder niet ziet.
"""

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from sqlalchemy import case, func, select
from sqlalchemy.orm import Session as DbSession

from .. import schemas
from ..auth import current_user, require_role
from ..config import settings
from ..db import get_db
from ..mail import mail_enabled, send_mail
from ..models import CLOSED_TICKET_STATUSES, TICKET_PRIORITIES, Ticket, TicketMessage, User, now

router = APIRouter(prefix="/api/tickets", tags=["tickets"])

STATUS_LABELS = {"open": "Nieuw", "in_behandeling": "In behandeling", "opgelost": "Opgelost", "gesloten": "Gesloten"}
KIND_LABELS = {"bug": "Bug", "idee": "Idee", "vraag": "Vraag"}


def _is_admin(user: User) -> bool:
    return user.role == "admin"


def _ref(user: User | None) -> schemas.PersonRef | None:
    return schemas.PersonRef(id=user.id, name=user.name) if user else None


def _get(db: DbSession, ticket_id: int, user: User) -> Ticket:
    ticket = db.get(Ticket, ticket_id)
    if ticket is None or not (_is_admin(user) or ticket.reporter_id == user.id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Melding niet gevonden.")
    return ticket


def _visible_messages(ticket: Ticket, user: User) -> list[TicketMessage]:
    return [m for m in ticket.messages if _is_admin(user) or not m.internal]


def _summary(db: DbSession, ticket: Ticket, user: User) -> dict:
    return dict(
        id=ticket.id,
        kind=ticket.kind,
        title=ticket.title,
        status=ticket.status,
        priority=ticket.priority,
        reporter=_ref(ticket.reporter),
        assignee=_ref(ticket.assignee),
        message_count=sum(1 for m in _visible_messages(ticket, user) if m.kind == "message"),
        created_at=ticket.created_at,
        updated_at=ticket.updated_at,
    )


def _out(db: DbSession, ticket: Ticket, user: User) -> schemas.TicketOut:
    return schemas.TicketOut(
        **_summary(db, ticket, user),
        description=ticket.description,
        page=ticket.page,
        closed_at=ticket.closed_at,
        messages=[
            schemas.TicketMessageOut(
                id=m.id, kind=m.kind, body=m.body, internal=m.internal, author=_ref(m.author),
                from_admin=bool(m.author and m.author.role == "admin"), created_at=m.created_at,
            )
            for m in _visible_messages(ticket, user)
        ],
        can_reply=_is_admin(user) or ticket.status != "gesloten",
    )


def _event(ticket: Ticket, author: User, text: str) -> None:
    ticket.messages.append(TicketMessage(author_id=author.id, body=text, kind="event"))


def _link(ticket: Ticket) -> str:
    return f"{settings.site_url.rstrip('/')}/meldingen/{ticket.id}"


def _send_all(to: list[str], subject: str, body: str) -> None:
    for address in to:
        send_mail(address, subject, body)


def _queue_mail(background: BackgroundTasks, to: list[str], subject: str, body: str) -> None:
    """Verstuurt na het antwoord, zodat een trage mailserver de site niet ophoudt."""
    if mail_enabled() and to:
        background.add_task(_send_all, to, subject, body)


# --- Overzicht en melden ------------------------------------------------


@router.get("", response_model=list[schemas.TicketSummary])
def list_tickets(
    scope: str = Query(default="mine", pattern="^(mine|all)$"),
    status_filter: str | None = Query(default=None, alias="status", pattern="^(open|closed)$"),
    user: User = Depends(current_user),
    db: DbSession = Depends(get_db),
):
    query = select(Ticket)
    if scope == "mine" or not _is_admin(user):
        query = query.where(Ticket.reporter_id == user.id)
    if status_filter == "open":
        query = query.where(Ticket.status.not_in(CLOSED_TICKET_STATUSES))
    elif status_filter == "closed":
        query = query.where(Ticket.status.in_(CLOSED_TICKET_STATUSES))
    # Open meldingen eerst, dan hoogste prioriteit, dan laatst bijgewerkt.
    rank = case({p: i for i, p in enumerate(reversed(TICKET_PRIORITIES))}, value=Ticket.priority)
    query = query.order_by(Ticket.status.in_(CLOSED_TICKET_STATUSES), rank, Ticket.updated_at.desc())
    return [_summary(db, t, user) for t in db.scalars(query)]


@router.get("/open-count", dependencies=[Depends(require_role("admin"))])
def open_count(db: DbSession = Depends(get_db)):
    return {"count": db.scalar(select(func.count()).where(Ticket.status == "open"))}


@router.post("", response_model=schemas.TicketOut, status_code=status.HTTP_201_CREATED)
def create_ticket(data: schemas.TicketIn, background: BackgroundTasks,
                  user: User = Depends(current_user), db: DbSession = Depends(get_db)):
    ticket = Ticket(kind=data.kind, title=data.title, description=data.description,
                    page=data.page or None, reporter_id=user.id)
    db.add(ticket)
    db.commit()
    admins = db.scalars(select(User.email).where(User.role == "admin", User.status == "approved")).all()
    _queue_mail(
        background, list(admins), f"Nieuwe melding: {ticket.title}",
        f"{user.name} heeft een melding gedaan ({KIND_LABELS[ticket.kind].lower()}):\n\n"
        f"{ticket.title}\n\n{ticket.description}\n\n"
        + (f"Pagina: {ticket.page}\n\n" if ticket.page else "")
        + f"Bekijk en behandel hem op {_link(ticket)}\n\nTrauma Tram Tellers",
    )
    return _out(db, ticket, user)


# --- Eén melding ----------------------------------------------------------


@router.get("/{ticket_id}", response_model=schemas.TicketOut)
def get_ticket(ticket_id: int, user: User = Depends(current_user), db: DbSession = Depends(get_db)):
    return _out(db, _get(db, ticket_id, user), user)


@router.post("/{ticket_id}/messages", response_model=schemas.TicketOut, status_code=status.HTTP_201_CREATED)
def add_message(ticket_id: int, data: schemas.TicketMessageIn, background: BackgroundTasks,
                user: User = Depends(current_user), db: DbSession = Depends(get_db)):
    ticket = _get(db, ticket_id, user)
    admin = _is_admin(user)
    if not data.body:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Je bericht is leeg.")
    if not admin and ticket.status == "gesloten":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Deze melding is gesloten. Doe gerust een nieuwe melding.")
    internal = admin and data.internal
    ticket.messages.append(TicketMessage(author_id=user.id, body=data.body, internal=internal))
    # Reageert de melder op een opgeloste melding, dan gaat hij weer open.
    if not admin and ticket.status == "opgelost":
        ticket.status = "in_behandeling"
        ticket.closed_at = None
        _event(ticket, user, "Heropend door de melder.")
    ticket.updated_at = now()
    db.commit()
    reporter = ticket.reporter
    if admin and not internal and reporter and reporter.id != user.id:
        _queue_mail(background, [reporter.email], f"Antwoord op je melding: {ticket.title}",
                    f"Hoi {reporter.name},\n\n{user.name} heeft gereageerd op je melding \"{ticket.title}\":\n\n"
                    f"{data.body}\n\nBekijk of reageer op {_link(ticket)}\n\nTrauma Tram Tellers")
    return _out(db, ticket, user)


@router.patch("/{ticket_id}", response_model=schemas.TicketOut)
def update_ticket(ticket_id: int, data: schemas.TicketUpdate, background: BackgroundTasks,
                  user: User = Depends(require_role("admin")), db: DbSession = Depends(get_db)):
    ticket = _get(db, ticket_id, user)
    old_status = ticket.status
    if data.status and data.status != ticket.status:
        _event(ticket, user, f"Status: {STATUS_LABELS[ticket.status]} → {STATUS_LABELS[data.status]}")
        ticket.status = data.status
        ticket.closed_at = now() if data.status in CLOSED_TICKET_STATUSES else None
    if data.priority and data.priority != ticket.priority:
        _event(ticket, user, f"Prioriteit: {ticket.priority} → {data.priority}")
        ticket.priority = data.priority
    if data.unassign and ticket.assignee_id is not None:
        _event(ticket, user, "Niemand meer toegewezen")
        ticket.assignee_id = None
    elif data.assignee_id is not None and data.assignee_id != ticket.assignee_id:
        assignee = db.get(User, data.assignee_id)
        if assignee is None or assignee.role != "admin" or assignee.status != "approved":
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Alleen admins kunnen een melding behandelen.")
        _event(ticket, user, f"Toegewezen aan {assignee.name}")
        ticket.assignee_id = assignee.id
    ticket.updated_at = now()
    db.commit()
    reporter = ticket.reporter
    if ticket.status != old_status and reporter and reporter.id != user.id:
        _queue_mail(background, [reporter.email], f"Je melding is {STATUS_LABELS[ticket.status].lower()}: {ticket.title}",
                    f"Hoi {reporter.name},\n\nDe status van je melding \"{ticket.title}\" is nu: "
                    f"{STATUS_LABELS[ticket.status]}.\n\nBekijk hem op {_link(ticket)}\n\nTrauma Tram Tellers")
    return _out(db, ticket, user)


@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ticket(ticket_id: int, user: User = Depends(require_role("admin")), db: DbSession = Depends(get_db)):
    db.delete(_get(db, ticket_id, user))
    db.commit()
