from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import EventRecord
from .schemas import Event, EventCreate


def _to_schema(record: EventRecord) -> Event:
    return Event.model_validate(record)


def list_events(db: Session) -> list[Event]:
    records = db.scalars(select(EventRecord).order_by(EventRecord.start_at.desc())).all()
    return [_to_schema(record) for record in records]


def create_event(db: Session, payload: EventCreate) -> Event:
    record = EventRecord(**payload.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return _to_schema(record)


def seed_events(db: Session) -> None:
    has_existing = db.scalar(select(EventRecord.id).limit(1))
    if has_existing:
        return

    now = datetime.now(tz=timezone.utc)
    samples = [
        EventCreate(
            id="evt_seed_1",
            title="Database optimization session",
            description="Review query plans and compare indexing strategies.",
            start_at=now - timedelta(hours=5),
            end_at=now - timedelta(hours=3),
            tense="past",
            category="research",
            color="#E45757",
            raw_input="Today from 2 to 4 PM I worked on database optimization experiments.",
            confidence=0.93,
        ),
        EventCreate(
            id="evt_seed_2",
            title="Weekly lab meeting",
            description="Share progress on model provider integration.",
            start_at=now + timedelta(days=1, hours=1),
            end_at=now + timedelta(days=1, hours=2),
            tense="future",
            category="meeting",
            color="#4B7BE5",
            raw_input="Tomorrow afternoon I have the weekly lab meeting.",
            confidence=0.91,
        ),
        EventCreate(
            id="evt_seed_3",
            title="Evening run",
            description="30-minute cardio block.",
            start_at=now + timedelta(days=1, hours=6),
            end_at=now + timedelta(days=1, hours=6, minutes=30),
            tense="future",
            category="life",
            color="#3FAE6A",
            raw_input="Remind me to go for a run tomorrow evening.",
            confidence=0.88,
        ),
    ]

    for sample in samples:
        db.add(EventRecord(**sample.model_dump()))

    db.commit()
