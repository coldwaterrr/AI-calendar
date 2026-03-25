from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect
from sqlalchemy.orm import Session

from . import models  # noqa: F401
from .db import SessionLocal, engine, get_db
from .llm import run_model_config_test
from .parser import infer_event
from .repository import create_event, get_model_config, list_events, seed_events, upsert_model_config
from .schemas import (
    Event,
    EventCreate,
    ModelConfig,
    ModelConfigTestRequest,
    ModelConfigTestResponse,
    ModelConfigUpdate,
    ParseRequest,
    ParseResponse,
)


def initialize_database() -> None:
    inspector = inspect(engine)
    if not inspector.has_table('events') or not inspector.has_table('model_configs'):
        return

    with SessionLocal() as db:
        seed_events(db)


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_database()
    yield


app = FastAPI(
    title='AI Calendar API',
    description='MVP backend for an AI-powered memory and planning assistant.',
    version='0.5.0',
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

initialize_database()


@app.get('/health')
def health() -> dict[str, str]:
    return {'status': 'ok'}


@app.get('/api/events', response_model=list[Event])
def get_events(db: Session = Depends(get_db)) -> list[Event]:
    return list_events(db)


@app.post('/api/events', response_model=Event)
def post_event(payload: EventCreate, db: Session = Depends(get_db)) -> Event:
    return create_event(db, payload)


@app.post('/api/parse', response_model=ParseResponse)
def parse_event(payload: ParseRequest, db: Session = Depends(get_db)) -> ParseResponse:
    inferred = infer_event(payload.text)
    event = create_event(db, inferred)
    return ParseResponse(
        message='Parsed successfully and saved to the event timeline.',
        event=event,
    )


@app.get('/api/model-config', response_model=ModelConfig)
def get_active_model_config(db: Session = Depends(get_db)) -> ModelConfig:
    config = get_model_config(db)
    if config is None:
        raise HTTPException(status_code=404, detail='Model config has not been set yet.')
    return config


@app.put('/api/model-config', response_model=ModelConfig)
def put_model_config(payload: ModelConfigUpdate, db: Session = Depends(get_db)) -> ModelConfig:
    return upsert_model_config(db, payload)


@app.post('/api/model-config/test', response_model=ModelConfigTestResponse)
def test_model_config(payload: ModelConfigTestRequest) -> ModelConfigTestResponse:
    success, latency_ms, message = run_model_config_test(payload)
    return ModelConfigTestResponse(
        success=success,
        latency_ms=latency_ms,
        message=message,
    )
