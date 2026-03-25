from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import EventRecord, ModelConfigRecord
from .schemas import Event, EventCreate, ModelConfig, ModelConfigUpdate
from .security import decrypt_value, encrypt_value, mask_secret


def _to_event_schema(record: EventRecord) -> Event:
    return Event.model_validate(record)


def list_events(db: Session) -> list[Event]:
    records = db.scalars(select(EventRecord).order_by(EventRecord.start_at.desc())).all()
    return [_to_event_schema(record) for record in records]


def create_event(db: Session, payload: EventCreate) -> Event:
    record = EventRecord(**payload.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return _to_event_schema(record)


def seed_events(db: Session) -> None:
    has_existing = db.scalar(select(EventRecord.id).limit(1))
    if has_existing:
        return

    now = datetime.now(tz=timezone.utc)
    samples = [
        EventCreate(
            id='evt_seed_1',
            title='Database optimization session',
            description='Review query plans and compare indexing strategies.',
            start_at=now - timedelta(hours=5),
            end_at=now - timedelta(hours=3),
            tense='past',
            category='research',
            color='#E45757',
            raw_input='Today from 2 to 4 PM I worked on database optimization experiments.',
            confidence=0.93,
        ),
        EventCreate(
            id='evt_seed_2',
            title='Weekly lab meeting',
            description='Share progress on model provider integration.',
            start_at=now + timedelta(days=1, hours=1),
            end_at=now + timedelta(days=1, hours=2),
            tense='future',
            category='meeting',
            color='#4B7BE5',
            raw_input='Tomorrow afternoon I have the weekly lab meeting.',
            confidence=0.91,
        ),
        EventCreate(
            id='evt_seed_3',
            title='Evening run',
            description='30-minute cardio block.',
            start_at=now + timedelta(days=1, hours=6),
            end_at=now + timedelta(days=1, hours=6, minutes=30),
            tense='future',
            category='life',
            color='#3FAE6A',
            raw_input='Remind me to go for a run tomorrow evening.',
            confidence=0.88,
        ),
    ]

    for sample in samples:
        db.add(EventRecord(**sample.model_dump()))

    db.commit()


def get_model_config(db: Session) -> ModelConfig | None:
    record = db.scalar(select(ModelConfigRecord).order_by(ModelConfigRecord.updated_at.desc()))
    if record is None:
        return None

    api_key = decrypt_value(record.encrypted_api_key)
    return ModelConfig(
        provider=record.provider,
        model=record.model,
        base_url=record.base_url,
        api_key_masked=mask_secret(api_key),
        is_active=record.is_active,
        has_api_key=bool(api_key),
        updated_at=record.updated_at,
    )


def upsert_model_config(db: Session, payload: ModelConfigUpdate) -> ModelConfig:
    now = datetime.now(tz=timezone.utc)
    record = db.scalar(select(ModelConfigRecord).order_by(ModelConfigRecord.updated_at.desc()))
    encrypted_api_key = encrypt_value(payload.api_key)

    if record is None:
        record = ModelConfigRecord(
            provider=payload.provider,
            model=payload.model,
            base_url=payload.base_url,
            encrypted_api_key=encrypted_api_key,
            is_active=payload.is_active,
            created_at=now,
            updated_at=now,
        )
        db.add(record)
    else:
        record.provider = payload.provider
        record.model = payload.model
        record.base_url = payload.base_url
        record.encrypted_api_key = encrypted_api_key
        record.is_active = payload.is_active
        record.updated_at = now

    db.commit()
    db.refresh(record)

    return ModelConfig(
        provider=record.provider,
        model=record.model,
        base_url=record.base_url,
        api_key_masked=mask_secret(payload.api_key),
        is_active=record.is_active,
        has_api_key=True,
        updated_at=record.updated_at,
    )
