"""Pimpy: notulen, taken en agenda per groep. Alleen voor editors en admins;
editors zien alleen de groepen waar ze lid van zijn."""

from datetime import timedelta

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session as DbSession

from .. import schemas
from ..auth import require_role
from ..config import settings
from ..db import get_db
from ..mail import mail_enabled, send_mail
from ..models import (
    OPEN_STATUSES,
    ROLE_RANK,
    TASK_STATUSES,
    Group,
    Meeting,
    Minute,
    Task,
    User,
    group_members,
    now,
)
from ..pimpy import ParseResult, parse_minutes, task_code

router = APIRouter(prefix="/api/pimpy", tags=["pimpy"], dependencies=[Depends(require_role("editor"))])


def _is_admin(user: User) -> bool:
    return user.role == "admin"


def _visible_group_ids(db: DbSession, user: User) -> list[int] | None:
    """None = alle groepen (admin)."""
    if _is_admin(user):
        return None
    return list(db.scalars(select(group_members.c.group_id).where(group_members.c.user_id == user.id)))


def _get_group(db: DbSession, user: User, group_id: int) -> Group:
    group = db.get(Group, group_id)
    if group is None or not (_is_admin(user) or user in group.members):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Groep niet gevonden.")
    return group


def _users_in_group(db: DbSession, group: Group, user_ids: list[int]) -> list[User]:
    members = {u.id: u for u in group.members}
    missing = [i for i in user_ids if i not in members]
    if missing:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Taken kunnen alleen aan leden van de groep worden gegeven.")
    return [members[i] for i in dict.fromkeys(user_ids)]


def _ref(obj) -> schemas.UserRef:
    return schemas.UserRef(id=obj.id, name=obj.name)


def _task_out(task: Task) -> schemas.TaskOut:
    return schemas.TaskOut(
        id=task.id,
        code=task_code(task.id),
        title=task.title,
        content=task.content,
        status=TASK_STATUSES[task.status],
        group=_ref(task.group),
        users=[_ref(u) for u in task.users],
        minute_id=task.minute_id,
        minute_date=task.minute.minute_date if task.minute else None,
        line=task.line,
        created_at=task.created_at,
        updated_at=task.updated_at,
    )


def _meeting_out(meeting: Meeting) -> schemas.MeetingOut:
    return schemas.MeetingOut(
        id=meeting.id,
        title=meeting.title,
        start_at=meeting.start_at,
        end_at=meeting.end_at,
        group=_ref(meeting.group),
        minute_id=meeting.minute_id,
    )


def _send_task_mails(mails: list[tuple[str, str, str]]) -> None:
    for to, subject, body in mails:
        send_mail(to, subject, body)


def _queue_mails(background: BackgroundTasks, tasks: list[Task]) -> None:
    """Eén mail per persoon met al zijn/haar nieuwe taken, verstuurd na het antwoord."""
    if not mail_enabled() or not tasks:
        return
    per_user: dict[int, tuple[User, list[Task]]] = {}
    for task in tasks:
        for user in task.users:
            if user.email_tasks:
                per_user.setdefault(user.id, (user, []))[1].append(task)
    mails = []
    for user, user_tasks in per_user.values():
        lines = "\n".join(f"  [{task_code(t.id)}] {t.title}" for t in user_tasks)
        group = user_tasks[0].group.name
        body = (
            f"Hoi {user.name},\n\n"
            f"Je hebt {len(user_tasks)} nieuwe {'taak' if len(user_tasks) == 1 else 'taken'} bij {group}:\n\n"
            f"{lines}\n\n"
            f"Bekijk en werk ze bij op {settings.site_url.rstrip('/')}/pimpy/taken\n\n"
            "Geen mails meer ontvangen? Zet het uit onder 'Mijn account'.\n\n"
            "Trauma Tram Tellers"
        )
        mails.append((user.email, f"Nieuwe taak bij {group}", body))
    background.add_task(_send_task_mails, mails)


# --- Groepen ------------------------------------------------------------


@router.get("/groups", response_model=list[schemas.GroupOut])
def list_groups(user: User = Depends(require_role("editor")), db: DbSession = Depends(get_db)):
    query = select(Group).order_by(Group.name)
    ids = _visible_group_ids(db, user)
    if ids is not None:
        query = query.where(Group.id.in_(ids))
    return db.scalars(query).all()


def _group_members(db: DbSession, member_ids: list[int]) -> list[User]:
    users = db.scalars(select(User).where(User.id.in_(member_ids))).all() if member_ids else []
    if len(users) != len(set(member_ids)):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Onbekend account in de ledenlijst.")
    if any(u.status != "approved" or ROLE_RANK[u.role] < ROLE_RANK["editor"] for u in users):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Alleen goedgekeurde editors en admins kunnen in een groep.")
    return list(users)


def _check_unique_name(db: DbSession, name: str, exclude_id: int | None = None) -> None:
    query = select(Group.id).where(func.lower(Group.name) == name.lower())
    if exclude_id:
        query = query.where(Group.id != exclude_id)
    if db.scalar(query):
        raise HTTPException(status.HTTP_409_CONFLICT, "Er bestaat al een groep met deze naam.")


@router.post("/groups", response_model=schemas.GroupOut, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_role("admin"))])
def create_group(data: schemas.GroupIn, db: DbSession = Depends(get_db)):
    _check_unique_name(db, data.name)
    group = Group(name=data.name, description=data.description or None, members=_group_members(db, data.member_ids))
    db.add(group)
    db.commit()
    return group


@router.put("/groups/{group_id}", response_model=schemas.GroupOut, dependencies=[Depends(require_role("admin"))])
def update_group(group_id: int, data: schemas.GroupIn, db: DbSession = Depends(get_db)):
    group = db.get(Group, group_id)
    if group is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Groep niet gevonden.")
    _check_unique_name(db, data.name, exclude_id=group.id)
    group.name = data.name
    group.description = data.description or None
    group.members = _group_members(db, data.member_ids)
    db.commit()
    return group


@router.delete("/groups/{group_id}", status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(require_role("admin"))])
def delete_group(group_id: int, db: DbSession = Depends(get_db)):
    group = db.get(Group, group_id)
    if group is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Groep niet gevonden.")
    db.delete(group)
    db.commit()


# --- Notulen ------------------------------------------------------------


def _parse(db: DbSession, group: Group, content: str) -> ParseResult:
    def find_task(task_id: int) -> Task | None:
        task = db.get(Task, task_id)
        return task if task is not None and task.group_id == group.id else None

    return parse_minutes(content, group, find_task)


def _excerpt(text: str, length: int = 180) -> str:
    flat = " ".join(text.split())
    return flat if len(flat) <= length else flat[:length].rsplit(" ", 1)[0] + "…"


def _minute_summary(db: DbSession, minute: Minute) -> dict:
    return dict(
        id=minute.id,
        group=_ref(minute.group),
        minute_date=minute.minute_date,
        created_by=minute.created_by.name if minute.created_by else None,
        created_at=minute.created_at,
        task_count=db.scalar(select(func.count()).where(Task.minute_id == minute.id)),
        excerpt=_excerpt(minute.content),
    )


@router.get("/minutes", response_model=list[schemas.MinuteSummary])
def list_minutes(
    group_id: int | None = None, user: User = Depends(require_role("editor")), db: DbSession = Depends(get_db)
):
    query = select(Minute).order_by(Minute.minute_date.desc(), Minute.id.desc())
    ids = _visible_group_ids(db, user)
    if ids is not None:
        query = query.where(Minute.group_id.in_(ids))
    if group_id is not None:
        query = query.where(Minute.group_id == group_id)
    return [_minute_summary(db, m) for m in db.scalars(query)]


@router.get("/minutes/{minute_id}", response_model=schemas.MinuteOut)
def get_minute(minute_id: int, user: User = Depends(require_role("editor")), db: DbSession = Depends(get_db)):
    minute = db.get(Minute, minute_id)
    if minute is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Notulen niet gevonden.")
    _get_group(db, user, minute.group_id)
    tasks = db.scalars(select(Task).where(Task.minute_id == minute.id).order_by(Task.line, Task.id)).all()
    meetings = db.scalars(select(Meeting).where(Meeting.minute_id == minute.id).order_by(Meeting.start_at)).all()
    return schemas.MinuteOut(
        **_minute_summary(db, minute),
        content=minute.content,
        tasks=[_task_out(t) for t in tasks],
        meetings=[_meeting_out(m) for m in meetings],
    )


@router.post("/minutes/preview", response_model=schemas.MinutePreview)
def preview_minute(data: schemas.MinutePreviewIn, user: User = Depends(require_role("editor")),
                   db: DbSession = Depends(get_db)):
    """Laat zien wat de notulen zouden doen, zonder iets op te slaan."""
    group = _get_group(db, user, data.group_id)
    result = _parse(db, group, data.content)
    ref = lambda t: schemas.PreviewTaskRef(code=task_code(t.id), title=t.title)  # noqa: E731
    return schemas.MinutePreview(
        tasks=[schemas.PreviewTask(line=t.line, title=t.title, users=[u.name for u in t.users]) for t in result.tasks],
        done=[ref(t) for t in result.done],
        removed=[ref(t) for t in result.removed],
        meetings=[schemas.PreviewMeeting(line=m.line, title=m.title, start_at=m.start, end_at=m.end)
                  for m in result.meetings],
        errors=[schemas.ParseErrorOut(line=e.line, text=e.text, reason=e.reason) for e in result.errors],
    )


@router.post("/minutes", response_model=schemas.MinuteSummary, status_code=status.HTTP_201_CREATED)
def create_minute(data: schemas.MinuteIn, background: BackgroundTasks,
                  user: User = Depends(require_role("editor")), db: DbSession = Depends(get_db)):
    group = _get_group(db, user, data.group_id)
    result = _parse(db, group, data.content)
    if result.errors:
        lines = ", ".join(str(e.line) for e in result.errors)
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY,
                            f"De notulen bevatten fouten (regel {lines}). Controleer ze eerst.")
    minute = Minute(group=group, minute_date=data.minute_date, content=data.content, created_by_id=user.id)
    db.add(minute)
    new_tasks = [Task(group=group, minute=minute, line=t.line, title=t.title, users=t.users) for t in result.tasks]
    db.add_all(new_tasks)
    for task in result.done:
        task.status = TASK_STATUSES.index("finished")
    for task in result.removed:
        task.status = TASK_STATUSES.index("deleted")
    for m in result.meetings:
        db.add(Meeting(group=group, minute=minute, title=m.title, start_at=m.start, end_at=m.end))
    db.commit()
    _queue_mails(background, new_tasks)
    return _minute_summary(db, minute)


@router.delete("/minutes/{minute_id}", status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(require_role("admin"))])
def delete_minute(minute_id: int, db: DbSession = Depends(get_db)):
    minute = db.get(Minute, minute_id)
    if minute is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Notulen niet gevonden.")
    db.delete(minute)  # taken uit deze notulen gaan mee (cascade)
    db.commit()


# --- Taken --------------------------------------------------------------


@router.get("/tasks", response_model=list[schemas.TaskOut])
def list_tasks(
    scope: str = Query(default="mine", pattern="^(mine|all)$"),
    group_id: int | None = None,
    include_closed: bool = False,
    user: User = Depends(require_role("editor")),
    db: DbSession = Depends(get_db),
):
    query = select(Task).order_by(Task.status, Task.created_at.desc())
    if scope == "mine":
        query = query.where(Task.users.any(User.id == user.id))
    ids = _visible_group_ids(db, user)
    if ids is not None:
        query = query.where(Task.group_id.in_(ids))
    if group_id is not None:
        query = query.where(Task.group_id == group_id)
    if not include_closed:
        query = query.where(Task.status.in_(OPEN_STATUSES))
    return [_task_out(t) for t in db.scalars(query)]


@router.post("/tasks", response_model=schemas.TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(data: schemas.TaskIn, background: BackgroundTasks,
                user: User = Depends(require_role("editor")), db: DbSession = Depends(get_db)):
    group = _get_group(db, user, data.group_id)
    task = Task(group=group, title=data.title, content=data.content or None,
                users=_users_in_group(db, group, data.user_ids))
    db.add(task)
    db.commit()
    _queue_mails(background, [task])
    return _task_out(task)


@router.patch("/tasks/{task_id}", response_model=schemas.TaskOut)
def update_task(task_id: int, data: schemas.TaskUpdate,
                user: User = Depends(require_role("editor")), db: DbSession = Depends(get_db)):
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Taak niet gevonden.")
    group = _get_group(db, user, task.group_id)
    if data.status is not None:
        task.status = TASK_STATUSES.index(data.status)
    if data.title is not None:
        task.title = data.title
    if data.content is not None:
        task.content = data.content or None
    if data.user_ids is not None:
        task.users = _users_in_group(db, group, data.user_ids)
    db.commit()
    return _task_out(task)


# --- Agenda -------------------------------------------------------------


@router.get("/meetings", response_model=list[schemas.MeetingOut])
def list_meetings(past: bool = False, user: User = Depends(require_role("editor")), db: DbSession = Depends(get_db)):
    # Vergaderingen van vandaag blijven de hele dag zichtbaar onder "komend".
    cutoff = now() - timedelta(hours=12)
    query = select(Meeting)
    query = query.where(Meeting.end_at < cutoff).order_by(Meeting.start_at.desc()) if past \
        else query.where(Meeting.end_at >= cutoff).order_by(Meeting.start_at)
    ids = _visible_group_ids(db, user)
    if ids is not None:
        query = query.where(Meeting.group_id.in_(ids))
    return [_meeting_out(m) for m in db.scalars(query.limit(200))]


@router.post("/meetings", response_model=schemas.MeetingOut, status_code=status.HTTP_201_CREATED)
def create_meeting(data: schemas.MeetingIn, user: User = Depends(require_role("editor")),
                   db: DbSession = Depends(get_db)):
    group = _get_group(db, user, data.group_id)
    meeting = Meeting(group=group, title=data.title, start_at=data.start_at,
                      end_at=data.start_at + timedelta(hours=data.hours))
    db.add(meeting)
    db.commit()
    return _meeting_out(meeting)


@router.delete("/meetings/{meeting_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_meeting(meeting_id: int, user: User = Depends(require_role("editor")), db: DbSession = Depends(get_db)):
    meeting = db.get(Meeting, meeting_id)
    if meeting is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Vergadering niet gevonden.")
    _get_group(db, user, meeting.group_id)
    db.delete(meeting)
    db.commit()
