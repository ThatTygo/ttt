from datetime import date, datetime
from typing import Literal
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from .config import settings

Role = Literal["user", "editor", "admin"]
Status = Literal["pending", "approved"]


class Orm(BaseModel):
    model_config = ConfigDict(from_attributes=True)


def _strip(value):
    return value.strip() if isinstance(value, str) else value


# --- Auth ---------------------------------------------------------------


class RegisterIn(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    email: EmailStr
    password: str = Field(min_length=10, max_length=200)

    _s = field_validator("name")(_strip)


class LoginIn(BaseModel):
    email: EmailStr
    password: str = Field(max_length=200)


class UserOut(Orm):
    id: int
    name: str
    email: str
    role: Role
    status: Status
    created_at: datetime
    last_login_at: datetime | None = None
    email_tasks: bool = True


class AccountUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=80)
    email_tasks: bool | None = None
    current_password: str | None = None
    new_password: str | None = Field(default=None, min_length=10, max_length=200)


class PasswordConfirm(BaseModel):
    password: str


class UserAdminUpdate(BaseModel):
    role: Role | None = None
    status: Status | None = None


# --- Leden --------------------------------------------------------------


class MemberIn(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    nickname: str | None = Field(default=None, max_length=80)
    function: str | None = Field(default=None, max_length=80)
    shift_day: int | None = Field(default=None, ge=0, le=6)
    member_since: date | None = None
    active: bool = True
    notes: str | None = Field(default=None, max_length=2000)
    user_id: int | None = None

    _s = field_validator("name", "nickname", "function", "notes")(_strip)


class MemberOut(Orm):
    id: int
    name: str
    nickname: str | None
    function: str | None
    shift_day: int | None
    member_since: date | None
    active: bool
    notes: str | None
    user_id: int | None


class RosterDay(BaseModel):
    day: int
    names: list[str]


# --- Columns ------------------------------------------------------------


class IncidentIn(BaseModel):
    """Optioneel bij het opslaan van een column: er was een stickerwaardig incident."""

    day: date | None = None  # standaard de publicatiedatum van de column
    text: str | None = Field(default=None, max_length=300)

    _s = field_validator("text")(_strip)


class ColumnIn(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    body: str = Field(min_length=1, max_length=20000)
    author_name: str = Field(min_length=1, max_length=120)
    published_at: datetime | None = None
    incident: IncidentIn | None = None

    _s = field_validator("title", "author_name")(_strip)

    @field_validator("published_at")
    @classmethod
    def _amsterdam(cls, value: datetime | None) -> datetime | None:
        # Het formulier stuurt een tijd zonder tijdzone: dat is Amsterdamse tijd.
        if value is not None and value.tzinfo is None:
            value = value.replace(tzinfo=ZoneInfo(settings.timezone))
        return value


class ColumnOut(Orm):
    id: int
    title: str
    body: str
    author_name: str
    has_incident: bool
    published_at: datetime
    updated_at: datetime


class ColumnSummary(Orm):
    id: int
    title: str
    author_name: str
    has_incident: bool
    published_at: datetime
    excerpt: str
    like_count: int = 0
    comment_count: int = 0


class ColumnPage(BaseModel):
    items: list[ColumnSummary]
    total: int
    authors: list[str]


# --- Teller -------------------------------------------------------------


class CounterIn(BaseModel):
    last_incident_date: date | None = None
    last_incident_text: str | None = Field(default=None, max_length=300)
    sticker_count: int = Field(ge=0, le=100000)


class CounterOut(Orm):
    last_incident_date: date | None
    last_incident_text: str | None
    sticker_count: int
    updated_at: datetime


# --- Pimpy --------------------------------------------------------------

TaskStatus = Literal["new", "started", "done", "not_done", "finished", "deleted"]


class UserRef(Orm):
    id: int
    name: str


class GroupIn(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    description: str | None = Field(default=None, max_length=300)
    member_ids: list[int] = []

    _s = field_validator("name", "description")(_strip)


class GroupOut(Orm):
    id: int
    name: str
    description: str | None
    members: list[UserRef]


class MinuteIn(BaseModel):
    group_id: int
    minute_date: date
    content: str = Field(min_length=1, max_length=100000)


class MinutePreviewIn(BaseModel):
    group_id: int
    content: str = Field(max_length=100000)


class TaskOut(BaseModel):
    id: int
    code: str
    title: str
    content: str | None
    status: TaskStatus
    group: UserRef  # id + naam van de groep
    users: list[UserRef]
    minute_id: int | None
    minute_date: date | None
    line: int | None
    created_at: datetime
    updated_at: datetime


class TaskIn(BaseModel):
    group_id: int
    title: str = Field(min_length=1, max_length=500)
    content: str | None = Field(default=None, max_length=5000)
    user_ids: list[int] = Field(min_length=1)

    _s = field_validator("title", "content")(_strip)


class TaskUpdate(BaseModel):
    status: TaskStatus | None = None
    title: str | None = Field(default=None, min_length=1, max_length=500)
    content: str | None = Field(default=None, max_length=5000)
    user_ids: list[int] | None = Field(default=None, min_length=1)

    _s = field_validator("title", "content")(_strip)


class MeetingIn(BaseModel):
    group_id: int
    title: str = Field(min_length=1, max_length=200)
    start_at: datetime
    hours: float = Field(default=1, gt=0, le=99)

    _s = field_validator("title")(_strip)

    @field_validator("start_at")
    @classmethod
    def _amsterdam(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            value = value.replace(tzinfo=ZoneInfo(settings.timezone))
        return value


class MeetingOut(BaseModel):
    id: int
    title: str
    start_at: datetime
    end_at: datetime
    group: UserRef
    minute_id: int | None


class MinuteSummary(BaseModel):
    id: int
    group: UserRef
    minute_date: date
    created_by: str | None
    created_at: datetime
    task_count: int
    excerpt: str


class MinuteOut(MinuteSummary):
    content: str
    tasks: list[TaskOut]
    meetings: list[MeetingOut]


class ParseErrorOut(BaseModel):
    line: int
    text: str
    reason: str


class PreviewTask(BaseModel):
    line: int
    title: str
    users: list[str]


class PreviewTaskRef(BaseModel):
    code: str
    title: str


class PreviewMeeting(BaseModel):
    line: int
    title: str
    start_at: datetime
    end_at: datetime


class MinutePreview(BaseModel):
    tasks: list[PreviewTask]
    done: list[PreviewTaskRef]
    removed: list[PreviewTaskRef]
    meetings: list[PreviewMeeting]
    errors: list[ParseErrorOut]


# --- Reacties op columns -------------------------------------------------


class LikesOut(BaseModel):
    count: int
    liked: bool
    names: list[str]  # wie er geliket heeft


class CommentIn(BaseModel):
    body: str = Field(min_length=1, max_length=2000)

    _s = field_validator("body")(_strip)


class CommentAuthor(BaseModel):
    id: int
    name: str


class CommentOut(BaseModel):
    id: int
    body: str
    author: CommentAuthor
    created_at: datetime
    edited_at: datetime | None
    likes: LikesOut
    can_edit: bool
    can_delete: bool


class ReactionsOut(BaseModel):
    likes: LikesOut
    comments: list[CommentOut]
