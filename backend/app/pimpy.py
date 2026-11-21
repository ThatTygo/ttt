"""Notulen lezen en omzetten naar taken en vergaderingen (naar het voorbeeld van Pimpy in viaduct).

Syntax, één opdracht per regel:

    ACTIE Robin, Gijs: stickers bestellen        één taak voor Robin én Gijs samen
    ACTIES Robin, Gijs: notulen lezen            een aparte taak voor Robin en voor Gijs
    ACTIE: stickers bestellen                    zonder namen: de hele groep
    DONE 1A, 2B                                  taken met deze codes zijn afgerond
    REMOVE 3C                                    taken met deze codes vervallen
    MEETING 12-11-2026 13:30(2) Vergadering      vergadering op de agenda (duur in uren, standaard 1)

Nederlandse varianten: TAAK/TAKEN, KLAAR, VERVALT, VERGADERING.
"""

import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from difflib import SequenceMatcher
from zoneinfo import ZoneInfo

from .config import settings
from .models import Group, Task, User

TASK_RE = re.compile(r"^\s*(?:ACTIE|TASK|TAAK)(?P<names>\s[^:]*)?:\s*(?P<title>.+?)\s*$")
TASKS_RE = re.compile(r"^\s*(?:ACTIES|TASKS|TAKEN)(?P<names>\s[^:]*)?:\s*(?P<title>.+?)\s*$")
DONE_RE = re.compile(r"^\s*(?:DONE|KLAAR)\s+(?P<codes>\S.*?)\s*$")
REMOVE_RE = re.compile(r"^\s*(?:REMOVE|VERVALT)\s+(?P<codes>\S.*?)\s*$")
MISSING_COLON_RE = re.compile(r"^\s*(?:ACTIES?|TASKS?|TAAK|TAKEN)\s+\w[^:]*$")
MEETING_RE = re.compile(
    r"^\s*(?:MEETING|VERGADERING)\s+"
    r"(?P<date>\d{1,2}-\d{1,2}-\d{4})?\s*"
    r"(?P<time>\d{1,2}:\d{2})?\s*"
    r"(?:\((?P<hours>\d{1,2}(?:[.,]\d)?)\))?\s*"
    r"(?P<title>.*?)\s*$"
)

# Hoe zeker een naam moet lijken op een groepslid (0..1).
NAME_MATCH_THRESHOLD = 0.6

# Crockford base32: korte, goed leesbare taakcodes zonder I, L, O en U.
_ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
_DECODE_ALIASES = str.maketrans({"O": "0", "I": "1", "L": "1"})


def task_code(task_id: int) -> str:
    code = ""
    while True:
        task_id, rest = divmod(task_id, 32)
        code = _ALPHABET[rest] + code
        if task_id == 0:
            return code


def decode_task_code(code: str) -> int | None:
    value = 0
    for char in code.strip().upper().translate(_DECODE_ALIASES):
        if char not in _ALPHABET:
            return None
        value = value * 32 + _ALPHABET.index(char)
    return value if code.strip() else None


class UnknownNameError(ValueError):
    pass


def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def match_user(name: str, members: list[User]) -> User:
    """Het groepslid waarvan de (voor- of achter)naam het meest op `name` lijkt."""
    wanted = name.strip().lower()
    best, best_score = None, 0.0
    for user in members:
        parts = user.name.lower().split()
        candidates = [user.name.lower(), *parts[:1], *parts[-1:]]
        score = max(_similarity(wanted, c) for c in candidates)
        if score > best_score:
            best, best_score = user, score
    if best is None or best_score < NAME_MATCH_THRESHOLD:
        raise UnknownNameError(f"'{name.strip()}' is geen lid van deze groep")
    return best


def users_from_names(names: str | None, group: Group) -> list[User]:
    names = (names or "").strip()
    if not names:
        return list(group.members)
    found: list[User] = []
    for name in filter(None, (n.strip() for n in names.split(","))):
        user = match_user(name, group.members)
        if user not in found:
            found.append(user)
    return found


@dataclass
class NewTask:
    line: int
    title: str
    users: list[User]


@dataclass
class NewMeeting:
    line: int
    title: str
    start: datetime
    end: datetime


@dataclass
class ParseError:
    line: int
    text: str
    reason: str


@dataclass
class ParseResult:
    tasks: list[NewTask] = field(default_factory=list)
    done: list[Task] = field(default_factory=list)
    removed: list[Task] = field(default_factory=list)
    meetings: list[NewMeeting] = field(default_factory=list)
    errors: list[ParseError] = field(default_factory=list)


def _tasks_from_codes(codes: str, find_task, line_no: int, line: str, result: ParseResult) -> list[Task]:
    tasks = []
    for code in filter(None, (c.strip() for c in codes.split(","))):
        task_id = decode_task_code(code)
        task = find_task(task_id) if task_id is not None else None
        if task is None:
            result.errors.append(ParseError(line_no, line, f"Onbekende taakcode '{code}'"))
        else:
            tasks.append(task)
    return tasks


def _parse_meeting(match: re.Match, line_no: int, line: str, result: ParseResult) -> None:
    if not match["date"] or not match["time"]:
        result.errors.append(ParseError(line_no, line, "Vergadering mist een datum (dd-mm-jjjj) en tijd (uu:mm)"))
        return
    if not match["title"]:
        result.errors.append(ParseError(line_no, line, "Vergadering mist een titel"))
        return
    try:
        start = datetime.strptime(f"{match['date']} {match['time']}", "%d-%m-%Y %H:%M")
    except ValueError:
        result.errors.append(ParseError(line_no, line, "Ongeldige datum of tijd"))
        return
    start = start.replace(tzinfo=ZoneInfo(settings.timezone))
    hours = float(match["hours"].replace(",", ".")) if match["hours"] else 1.0
    result.meetings.append(NewMeeting(line_no, match["title"][:200], start, start + timedelta(hours=hours)))


def parse_minutes(content: str, group: Group, find_task) -> ParseResult:
    """`find_task(id)` geeft een taak uit deze groep terug, of None."""
    result = ParseResult()
    for line_no, line in enumerate(content.splitlines(), start=1):
        try:
            if MISSING_COLON_RE.match(line):
                result.errors.append(ParseError(line_no, line, "Dubbele punt ontbreekt na de namen"))
            elif m := TASKS_RE.match(line):
                for user in users_from_names(m["names"], group):
                    result.tasks.append(NewTask(line_no, m["title"][:500], [user]))
            elif m := TASK_RE.match(line):
                result.tasks.append(NewTask(line_no, m["title"][:500], users_from_names(m["names"], group)))
            elif m := DONE_RE.match(line):
                result.done += _tasks_from_codes(m["codes"], find_task, line_no, line, result)
            elif m := REMOVE_RE.match(line):
                result.removed += _tasks_from_codes(m["codes"], find_task, line_no, line, result)
            elif m := MEETING_RE.match(line):
                _parse_meeting(m, line_no, line, result)
        except UnknownNameError as e:
            result.errors.append(ParseError(line_no, line, str(e)))
    for task in result.tasks:
        if not task.users:
            result.errors.append(ParseError(task.line, task.title, "Deze groep heeft nog geen leden"))
    return result
