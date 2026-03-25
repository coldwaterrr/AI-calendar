from datetime import datetime, timedelta, timezone
from uuid import uuid4

from .schemas import EventCreate


CATEGORY_COLORS = {
    "research": "#E45757",
    "meeting": "#4B7BE5",
    "life": "#3FAE6A",
}


def infer_event(text: str) -> EventCreate:
    now = datetime.now(tz=timezone.utc)
    lowered = text.lower()

    if any(token in text for token in ("昨天", "刚刚", "之前")) or "yesterday" in lowered:
        tense = "past"
        start_at = now - timedelta(hours=2)
        end_at = now - timedelta(hours=1)
    else:
        tense = "future"
        start_at = now + timedelta(days=1, hours=1)
        end_at = start_at + timedelta(hours=1)

    if any(token in text for token in ("组会", "会议", "讨论")) or "meeting" in lowered:
        category = "meeting"
    elif any(token in text for token in ("运动", "吃饭", "跑步", "通勤")):
        category = "life"
    else:
        category = "research"

    return EventCreate(
        id=f"evt_{uuid4().hex[:8]}",
        title=text[:18] or "Untitled event",
        description="Rule-based MVP parsing result. Replace this layer with structured LLM output later.",
        start_at=start_at,
        end_at=end_at,
        tense=tense,
        category=category,
        color=CATEGORY_COLORS[category],
        source_type="text",
        raw_input=text,
        confidence=0.72,
    )
