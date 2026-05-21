from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Literal, Optional

PreferredTime = Literal["morning", "afternoon", "evening", "anytime"]


@dataclass
class PlannedTask:
    name: str
    estimated_duration_minutes: int
    priority: int = 0
    preferred_time_of_day: Optional[str] = None
    deadline: Optional[datetime] = None
    earliest_start: Optional[datetime] = None
    splittable: bool = False


@dataclass
class PlannedAvailability:
    day_of_week: int  # 0=Mon .. 6=Sun; -1 means weekdays 0-4
    start_minutes: int
    end_minutes: int
    weekdays_only: bool = False


@dataclass
class PlannedConstraint:
    constraint_type: str
    day_of_week: Optional[int] = None
    start_minutes: Optional[int] = None
    end_minutes: Optional[int] = None
    value: Optional[int] = None
    every_weekday: bool = False


@dataclass
class PlanIntent:
    """Structured planning intent extracted from natural language."""

    raw_prompt: str
    tasks: list[PlannedTask] = field(default_factory=list)
    availability: list[PlannedAvailability] = field(default_factory=list)
    constraints: list[PlannedConstraint] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    parser: str = "deterministic"


def _parseDurationMinutes(text: str) -> Optional[int]:
    lower = text.lower()

    m = re.search(r"(\d+(?:\.\d+)?)\s*hours?", lower)
    if m:
        return int(float(m.group(1)) * 60)

    m = re.search(r"(\d+)\s*hrs?", lower)
    if m:
        return int(m.group(1)) * 60

    m = re.search(r"(\d+)\s*minutes?", lower)
    if m:
        return int(m.group(1))

    m = re.search(r"(\d+)\s*mins?", lower)
    if m:
        return int(m.group(1))

    m = re.search(r"\b(\d+)\s*h\b", lower)
    if m:
        return int(m.group(1)) * 60

    return None


def _parseClockToMinutes(token: str) -> Optional[int]:
    token = token.strip().lower().replace(" ", "")
    m = re.match(r"^(\d{1,2})(?::(\d{2}))?\s*(am|pm)?$", token)
    if not m:
        return None
    hour = int(m.group(1))
    minute = int(m.group(2) or 0)
    ampm = m.group(3)
    if ampm == "pm" and hour < 12:
        hour += 12
    if ampm == "am" and hour == 12:
        hour = 0
    if hour > 23 or minute > 59:
        return None
    return hour * 60 + minute


def _nextWeekday(fromDt: datetime, weekday: int) -> datetime:
    """Next occurrence of weekday (0=Mon) at midnight, not before tomorrow if today matches past."""
    base = fromDt.replace(hour=0, minute=0, second=0, microsecond=0)
    daysAhead = (weekday - base.weekday()) % 7
    if daysAhead == 0:
        daysAhead = 7
    return base + timedelta(days=daysAhead)


def _parseDeadline(text: str, reference: datetime) -> Optional[datetime]:
    lower = text.lower()
    if "tomorrow" in lower:
        d = reference.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        return d.replace(hour=23, minute=59)

    m = re.search(r"\bby\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b", lower)
    if m:
        names = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        weekday = names.index(m.group(1))
        d = _nextWeekday(reference, weekday)
        return d.replace(hour=17, minute=0)

    if "before friday" in lower or "by friday" in lower:
        d = _nextWeekday(reference, 4)
        return d.replace(hour=17, minute=0)

    if "this friday" in lower:
        d = _nextWeekday(reference, 4)
        return d.replace(hour=17, minute=0)

    return None


def _parseEarliest(text: str, reference: datetime) -> Optional[datetime]:
    lower = text.lower()
    if "tomorrow" in lower:
        return reference.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    return None


def _parsePreferred(text: str) -> Optional[str]:
    lower = text.lower()
    if "morning" in lower:
        return "morning"
    if "afternoon" in lower:
        return "afternoon"
    if "evening" in lower or "tonight" in lower:
        return "evening"
    return None


def _parsePriority(text: str) -> int:
    lower = text.lower()
    if "high priority" in lower or "urgent" in lower or "asap" in lower:
        return 8
    if "low priority" in lower:
        return 2
    if "medium priority" in lower:
        return 5
    return 0


def _extractTaskName(text: str) -> str:
    """Heuristic: strip scheduling verbs and duration/time phrases."""
    cleaned = text.strip()
    cleaned = re.sub(
        r"^(schedule|block|plan|add|create)\s+",
        "",
        cleaned,
        flags=re.IGNORECASE
    )
    cleaned = re.sub(
        r"\b\d+(?:\.\d+)?\s*(?:hours?|hrs?|h|minutes?|mins?)\s*(?:of\s+)?",
        "",
        cleaned,
        flags=re.IGNORECASE
    )
    cleaned = re.sub(
        r"\b(high|low|medium)\s+priority\b",
        "",
        cleaned,
        flags=re.IGNORECASE
    )
    cleaned = re.sub(
        r"\b(tomorrow|tonight|morning|afternoon|evening|can split|splittable)\b",
        "",
        cleaned,
        flags=re.IGNORECASE
    )
    cleaned = re.sub(
        r"\b(before|by)\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b",
        "",
        cleaned,
        flags=re.IGNORECASE
    )
    cleaned = re.sub(r"\bon\s+the\s+", " ", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" ,.-")
    if not cleaned:
        return "Untitled task"
    # Capitalize first letter
    return cleaned[0].upper() + cleaned[1:]


def _weekdayNameToIndex(name: str) -> int:
    names = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    return names.index(name.lower())


def _parseClockFlexible(token: str, preferPm: bool = False) -> Optional[int]:
    """Parse clock; if no am/pm and preferPm, treat 1–11 as PM (exams/classes)."""
    token = token.strip().lower().replace(" ", "")
    m = re.match(r"^(\d{1,2})(?::(\d{2}))?\s*(am|pm)?$", token)
    if not m:
        return None
    hour = int(m.group(1))
    minute = int(m.group(2) or 0)
    ampm = m.group(3)
    if ampm is None and preferPm and 1 <= hour <= 11:
        hour += 12
    elif ampm == "pm" and hour < 12:
        hour += 12
    elif ampm == "am" and hour == 12:
        hour = 0
    if hour > 23 or minute > 59:
        return None
    return hour * 60 + minute


def _parseExamAndStudy(text: str, reference: datetime) -> tuple[list[PlannedConstraint], list[PlannedTask], list[str]]:
    """Parse exam/test + per-day study blocking."""
    lower = text.lower()
    constraints: list[PlannedConstraint] = []
    tasks: list[PlannedTask] = []
    notes: list[str] = []

    isExam = any(k in lower for k in ("test", "exam", "midterm", "final"))
    if not isExam:
        return constraints, tasks, notes

    dayMatch = re.search(
        r"\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b",
        lower
    )
    timeMatch = re.search(
        r"(?:at|from)\s+(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)\s*(?:-|–|to)\s*(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)",
        lower
    )
    if not timeMatch:
        timeMatch = re.search(
            r"\b(\d{1,2}(?::\d{2})?)\s*(?:-|–)\s*(\d{1,2}(?::\d{2})?)\b",
            lower
        )

    if not dayMatch or not timeMatch:
        return constraints, tasks, notes

    weekday = _weekdayNameToIndex(dayMatch.group(1))
    startM = _parseClockFlexible(timeMatch.group(1), preferPm=True)
    endM = _parseClockFlexible(timeMatch.group(2), preferPm=True)
    if startM is None or endM is None or endM <= startM:
        return constraints, tasks, notes

    examDay = _nextWeekday(reference, weekday)
    # If reference is before that weekday later this week, prefer this week
    thisWeek = reference.replace(hour=0, minute=0, second=0, microsecond=0)
    daysAhead = (weekday - thisWeek.weekday()) % 7
    if daysAhead == 0 and (reference.hour * 60 + reference.minute) < startM:
        examDay = thisWeek
    elif daysAhead > 0:
        examDay = thisWeek + timedelta(days=daysAhead)

    constraints.append(
        PlannedConstraint(
            constraint_type="protected_block",
            day_of_week=weekday,
            start_minutes=startM,
            end_minutes=endM,
            every_weekday=False
        )
    )
    notes.append(
        f"Protected exam block on {dayMatch.group(1).title()} "
        f"{startM // 60}:{startM % 60:02d}–{endM // 60}:{endM % 60:02d}."
    )

    course = None
    courseMatch = re.search(r"\b([A-Z]{2,6}\s*\d{2,4}[A-Z]?)\b", text, re.IGNORECASE)
    if courseMatch:
        course = re.sub(r"\s+", " ", courseMatch.group(1).upper().replace("  ", " "))

    wantsDailyStudy = any(
        phrase in lower
        for phrase in (
            "per day",
            "each day",
            "every day",
            "block out",
            "study for",
            "study session",
        )
    )
    if not wantsDailyStudy:
        return constraints, tasks, notes

    studyMinutes = _parseDurationMinutes(text) or 90
    subject = f"Study {course}" if course else "Exam study"
    examDeadline = examDay.replace(hour=startM // 60, minute=startM % 60)
    # Study only on remaining days from "now" up to (not including) exam day
    cursor = reference.replace(hour=0, minute=0, second=0, microsecond=0)
    examMidnight = examDay.replace(hour=0, minute=0, second=0, microsecond=0)
    if cursor >= examMidnight:
        tasks.append(
            PlannedTask(
                name=f"{subject} (pre-exam)",
                estimated_duration_minutes=min(studyMinutes, max(30, startM - 8 * 60)),
                priority=8,
                preferred_time_of_day="morning",
                deadline=examDeadline,
                earliest_start=cursor.replace(hour=8, minute=0),
                splittable=True
            )
        )
        notes.append("Exam is today — scheduled a pre-exam study block.")
        return constraints, tasks, notes

    dayIndex = 0
    while cursor < examMidnight and dayIndex < 7:
        if cursor.weekday() < 5:
            earliest = cursor.replace(hour=8, minute=0)
            if cursor.date() == reference.date() and reference.hour >= 8:
                earliest = reference.replace(minute=0, second=0, microsecond=0)
            tasks.append(
                PlannedTask(
                    name=f"{subject} ({cursor.strftime('%a')})",
                    estimated_duration_minutes=studyMinutes,
                    priority=7,
                    preferred_time_of_day="afternoon",
                    deadline=examDeadline,
                    earliest_start=earliest,
                    splittable=True
                )
            )
        cursor = cursor + timedelta(days=1)
        dayIndex += 1

    if tasks:
        notes.append(f"Blocked {len(tasks)} study session(s) leading up to the exam.")

    return constraints, tasks, notes


def _parseProtectLunch(text: str) -> list[PlannedConstraint]:
    lower = text.lower()
    if "protect lunch" not in lower and "block lunch" not in lower:
        return []

    startM = 12 * 60
    endM = 13 * 60
    m = re.search(r"from\s+(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)\s+to\s+(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)", lower)
    if m:
        s = _parseClockToMinutes(m.group(1))
        e = _parseClockToMinutes(m.group(2))
        if s is not None and e is not None and e > s:
            startM, endM = s, e

    everyDay = "every day" in lower or "everyday" in lower or "weekdays" in lower or "each day" in lower
    if everyDay:
        return [
            PlannedConstraint(
                constraint_type="protected_block",
                start_minutes=startM,
                end_minutes=endM,
                every_weekday=True
            )
        ]
    return [
        PlannedConstraint(
            constraint_type="protected_block",
            day_of_week=datetime.utcnow().weekday(),
            start_minutes=startM,
            end_minutes=endM
        )
    ]


def _parseAvailability(text: str) -> list[PlannedAvailability]:
    lower = text.lower()
    if "free" not in lower and "available" not in lower and "availability" not in lower:
        return []

    m = re.search(
        r"(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)\s*(?:to|-)\s*(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)",
        lower
    )
    if not m:
        return []

    startM = _parseClockToMinutes(m.group(1))
    endM = _parseClockToMinutes(m.group(2))
    if startM is None or endM is None or endM <= startM:
        return []

    weekdays = "weekday" in lower or "week day" in lower
    if weekdays:
        return [
            PlannedAvailability(
                day_of_week=-1,
                start_minutes=startM,
                end_minutes=endM,
                weekdays_only=True
            )
        ]

    return [PlannedAvailability(day_of_week=datetime.utcnow().weekday(), start_minutes=startM, end_minutes=endM)]


def _parseEachDurationMinutes(text: str) -> Optional[int]:
    """Parse 'each 2 hours', '2 hours each', 'of 90 minutes', '2h each', 'two-hour'."""
    lower = text.lower()
    wordNums = {
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
        "six": 6,
    }
    for word, num in wordNums.items():
        if re.search(rf"\b{word}\s*-?\s*hours?\b", lower):
            return num * 60
        if re.search(rf"\b{word}\s*-?\s*hour\b", lower):
            return num * 60

    patterns = [
        r"each\s+(\d+(?:\.\d+)?)\s*(hours?|hrs?|h|minutes?|mins?)",
        r"(\d+(?:\.\d+)?)\s*(hours?|hrs?|h|minutes?|mins?)\s*(?:each|apiece|long)",
        r"(?:spots?|blocks?|sessions?|slots?)\s+(?:of\s+)?(\d+(?:\.\d+)?)\s*(hours?|hrs?|h|minutes?|mins?)",
        r"(\d+(?:\.\d+)?)\s*(?:-|\s)?\s*(hour|hr|h|minute|min)(?:s)?(?:-|\s)+(?:long\s+)?(?:spots?|blocks?|sessions?|slots?)",
        r"(\d+(?:\.\d+)?)\s*-\s*(hour|hr|minute|min)",
    ]
    for pat in patterns:
        m = re.search(pat, lower)
        if not m:
            continue
        amount = float(m.group(1))
        unit = m.group(2)
        if unit.startswith("h"):
            return max(15, int(amount * 60))
        return max(15, int(amount))
    # Fallback: first duration in the prompt when multi-spot language is present
    if any(w in lower for w in ("spots", "spot", "sessions", "slots", "chunks", "each", "find me", "give me")):
        return _parseDurationMinutes(text)
    return None


def _parseCount(text: str) -> Optional[int]:
    """Parse an explicit count of spots/blocks/sessions."""
    lower = text.lower()
    wordNums = {
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
        "six": 6,
    }
    # "three spots", "three two-hour sessions", "three 2-hour spots"
    for word, num in wordNums.items():
        if re.search(
            rf"\b{word}\s+(?:[\w.-]+\s+){{0,3}}(?:spots?|blocks?|sessions?|slots?|chunks?)\b",
            lower,
        ):
            return num

    patterns = [
        # "give me 3 two-hour sessions", "find me 3 spots"
        r"(?:find(?:\s+me)?|give(?:\s+me)?|get(?:\s+me)?|schedule|block|book|add|need|want)\s+(\d+)\s+(?:[\w.-]+\s+){0,3}(?:spots?|blocks?|sessions?|slots?|chunks?|windows?)",
        # "3 two-hour sessions", "4 blocks"
        r"(\d+)\s+(?:[\w.-]+\s+){0,2}(?:spots?|blocks?|sessions?|slots?|chunks?|windows?)",
        r"(\d+)\s*(?:spots?|blocks?|sessions?|slots?|chunks?|windows?)",
        r"(\d+)\s*x\s*\d",
        r"(?:times?)\s*[:=]?\s*(\d+)\b",
    ]
    for pat in patterns:
        m = re.search(pat, lower)
        if m:
            n = int(m.group(1))
            if 1 <= n <= 14:
                return n
    return None


def _multiSpotLabel(text: str) -> str:
    """Best-effort label for repeated focus blocks."""
    lower = text.lower()
    topic = re.search(
        r"\b(?:for|on|to)\s+([a-z0-9][\w\s\-]{1,40}?)(?:\.|,|$| each| before| tomorrow| morning| afternoon| evening)",
        lower
    )
    if topic:
        raw = topic.group(1).strip(" .,")
        raw = re.sub(r"\b(spots?|blocks?|sessions?|slots?|hours?|minutes?|each|long)\b", "", raw).strip()
        if raw and len(raw) > 1:
            return raw[0].upper() + raw[1:]
    if "deep work" in lower:
        return "Deep work"
    if "study" in lower:
        return "Study"
    if "focus" in lower:
        return "Focus"
    return "Focus block"


def _nextWeekdayFrom(cursor: datetime) -> datetime:
    day = cursor.replace(hour=8, minute=0, second=0, microsecond=0)
    if day < cursor:
        day = day + timedelta(days=1)
        day = day.replace(hour=8, minute=0, second=0, microsecond=0)
    while day.weekday() >= 5:
        day = day + timedelta(days=1)
    return day


def _parseMultiSpots(text: str, reference: datetime) -> tuple[list[PlannedTask], list[str]]:
    """
    Parse requests like:
    - find me 3 spots, each 2 hours long
    - schedule 4 blocks of 90 minutes for deep work
    - 3 two-hour sessions this week
    """
    lower = text.lower()
    multiHints = any(
        w in lower
        for w in (
            "spots",
            "spot",
            "sessions",
            "session",
            "slots",
            "chunks",
            "each",
            "find me",
            "give me",
            "get me",
            "blocks of",
            "two-hour",
            "one-hour",
            "three-hour",
        )
    ) or bool(re.search(r"\b\d+\s*-\s*hours?\b", lower))
    count = _parseCount(text)
    eachDuration = _parseEachDurationMinutes(text)
    if not multiHints or count is None or eachDuration is None:
        return [], []
    if count < 2:
        # Single spot — still useful, but leave to generic parser unless "find me 1 spot"
        if "find" not in lower and "give me" not in lower and "spot" not in lower:
            return [], []

    label = _multiSpotLabel(text)
    preferred = _parsePreferred(text)
    priority = _parsePriority(text) or 6
    deadline = _parseDeadline(text, reference)
    if deadline is None:
        # End of the current week Friday 6pm CST-ish from reference
        d = reference.replace(hour=0, minute=0, second=0, microsecond=0)
        while d.weekday() != 4:
            d = d + timedelta(days=1)
        deadline = d.replace(hour=18, minute=0)

    tasks: list[PlannedTask] = []
    cursor = reference
    for i in range(count):
        earliest = _nextWeekdayFrom(cursor)
        # Prefer spreading across days so the engine finds distinct spots
        cursor = earliest + timedelta(hours=10)
        tasks.append(
            PlannedTask(
                name=f"{label} ({i + 1}/{count})",
                estimated_duration_minutes=eachDuration,
                priority=priority,
                preferred_time_of_day=preferred,
                deadline=deadline,
                earliest_start=earliest,
                splittable=False
            )
        )

    notes = [
        f"Parsed {count} separate {eachDuration}-minute spots labeled “{label}” (contiguous, not split)."
    ]
    return tasks, notes


def parseDeterministic(prompt: str, reference: Optional[datetime] = None) -> PlanIntent:
    """Always-on regex/heuristic parser — works without API keys."""
    from app.core.timeutil import nowCst

    ref = reference or nowCst()
    text = prompt.strip()
    intent = PlanIntent(raw_prompt=text, parser="deterministic")

    examConstraints, examTasks, examNotes = _parseExamAndStudy(text, ref)
    if examConstraints:
        intent.constraints.extend(examConstraints)
    if examTasks:
        intent.tasks.extend(examTasks)
    intent.notes.extend(examNotes)

    protect = _parseProtectLunch(text)
    if protect:
        intent.constraints.extend(protect)
        intent.notes.append("Parsed protected lunch block.")

    avail = _parseAvailability(text)
    if avail:
        intent.availability.extend(avail)
        intent.notes.append("Parsed availability windows.")

    multiTasks, multiNotes = _parseMultiSpots(text, ref)
    if multiTasks:
        intent.tasks.extend(multiTasks)
        intent.notes.extend(multiNotes)

    duration = _parseDurationMinutes(text)
    lower = text.lower()
    isFreePhrase = "i'm free" in lower or "i am free" in lower or "free weekdays" in lower or "available weekdays" in lower
    isProtectOnly = bool(protect) and duration is None and not examTasks
    isExamPlan = bool(examTasks)
    isMultiSpot = bool(multiTasks)

    looksLikeTask = any(
        kw in lower
        for kw in (
            "schedule",
            "block",
            "study",
            "work",
            "prep",
            "write",
            "deep work",
            "minutes",
            "hour",
            "hours",
            "find me",
            "give me",
            "spots",
            "sessions",
        )
    )

    # Skip generic single-task parse when we already built exam/multi plans
    if (
        duration
        and looksLikeTask
        and not isProtectOnly
        and not isFreePhrase
        and not isExamPlan
        and not isMultiSpot
    ):
        name = _extractTaskName(text)
        preferred = _parsePreferred(text)
        deadline = _parseDeadline(text, ref)
        earliest = _parseEarliest(text, ref)
        priority = _parsePriority(text)
        splittable = "split" in lower or "can split" in lower
        intent.tasks.append(
            PlannedTask(
                name=name,
                estimated_duration_minutes=duration,
                priority=priority,
                preferred_time_of_day=preferred,
                deadline=deadline,
                earliest_start=earliest,
                splittable=splittable
            )
        )
        intent.notes.append(f"Parsed task '{name}' ({duration} min).")

    if not intent.tasks and not intent.availability and not intent.constraints:
        intent.notes.append(
            "Could not extract structured intent; try “find me 3 spots, each 2 hours” or a deadline."
        )

    return intent
