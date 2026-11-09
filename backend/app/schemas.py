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


class AccountUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=80)
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


# --- Columns ------------------------------------------------------------


class ColumnIn(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    body: str = Field(min_length=1, max_length=20000)
    author_name: str = Field(min_length=1, max_length=120)
    published_at: datetime | None = None

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
    published_at: datetime
    updated_at: datetime


class ColumnSummary(Orm):
    id: int
    title: str
    author_name: str
    published_at: datetime
    excerpt: str


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
