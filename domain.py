"""Pure time rules. Persist instants in UTC; display and interpret wall times in Zurich."""
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

UTC = timezone.utc
ZURICH = ZoneInfo("Europe/Zurich")
REFERENCE_NOW = datetime(2026, 11, 9, 8, tzinfo=ZURICH)


class RuleViolation(ValueError):
    """A request must return to a human without mutating an assignment."""


def instant(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise RuleViolation("Date sans fuseau horaire : contrôle humain requis.")
    # Reject imaginary local times, even when a caller directly attaches ZoneInfo.
    check = value.astimezone(UTC).astimezone(value.tzinfo)
    if check.replace(tzinfo=None) != value.replace(tzinfo=None) or check.fold != value.fold:
        raise RuleViolation("Heure locale inexistante ou indicateur fold invalide.")
    return value.astimezone(UTC)


def local_time(value: str) -> datetime:
    """Parse an offset-free Zurich wall time; ambiguity needs an explicit UTC offset."""
    try:
        wall = datetime.fromisoformat(value)
    except ValueError as exc:
        raise RuleViolation("Date invalide. Format attendu : AAAA-MM-JJ HH:MM.") from exc
    if wall.tzinfo is not None:
        raise RuleViolation("Saisir une heure locale sans décalage UTC.")
    candidates = []
    for fold in (0, 1):
        candidate = wall.replace(tzinfo=ZURICH, fold=fold)
        if candidate.astimezone(UTC).astimezone(ZURICH).replace(tzinfo=None) == wall:
            candidates.append(candidate)
    if not candidates:
        raise RuleViolation("Heure inexistante au passage à l’heure d’été : revue humaine.")
    if len({c.utcoffset() for c in candidates}) > 1:
        raise RuleViolation("Heure ambiguë au passage à l’heure d’hiver : revue humaine.")
    return candidates[0]


def stamp(value: datetime) -> str:
    return instant(value).isoformat(timespec="seconds")


def parse(value: str) -> datetime:
    return instant(datetime.fromisoformat(value))


def window(start: datetime, end: datetime) -> tuple[datetime, datetime]:
    a, b = instant(start), instant(end)
    if b <= a:
        raise RuleViolation("La fin doit être strictement après le début.")
    return a, b


def overlaps(a: datetime, b: datetime, c: datetime, d: datetime) -> bool:
    a, b = window(a, b)
    c, d = window(c, d)
    return a < d and c < b  # Half-open intervals: touching boundaries are allowed.


def cancellation_review(start: datetime, requested_at: datetime) -> bool:
    """Exactly 48 elapsed hours is outside the late-review flag. No fee decision."""
    return instant(start) - instant(requested_at) < timedelta(hours=48)


def display(value: str | datetime) -> str:
    dt = parse(value) if isinstance(value, str) else instant(value)
    return dt.astimezone(ZURICH).strftime("%d/%m/%Y %H:%M %Z")


@dataclass(frozen=True)
class Candidate:
    cleaner_id: str
    label: str
    eligible: bool
    reasons: tuple[str, ...]
    continuity: bool
    day_load: int

    @property
    def rank_key(self):
        return (not self.continuity, self.day_load, self.cleaner_id)
