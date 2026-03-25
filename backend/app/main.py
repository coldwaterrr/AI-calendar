from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect
from sqlalchemy.orm import Session

from . import models  # noqa: F401
from .db import SessionLocal, engine, get_db
from .llm import infer_event_with_llm, run_model_config_test
from .parser import infer_event_rule_based
from .repository import (
    create_event,
    get_model_config,
    get_model_config_secret,
    list_events,
    seed_events,
    upsert_model_config,
)
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
    version='0.6.1',
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
    config_secret = get_model_config_secret(db)

    if config_secret is None:
        inferred = infer_event_rule_based(payload.text)
        parser_mode = 'rule_based'
        message = 'No active model config was found, so fallback rules were used.'
    else:
        try:
            inferred = infer_event_with_llm(
                provider=config_secret['provider'],
                model=config_secret['model'],
                api_key=config_secret['api_key'],
                base_url=config_secret['base_url'],
                text=payload.text,
            )
            parser_mode = 'llm'
            message = 'Parsed with the configured model and saved to the event timeline.'
        except Exception:
            inferred = infer_event_rule_based(payload.text)
            parser_mode = 'rule_based'
            message = 'Model parsing failed, so fallback rules were used and the event was saved.'

    event = create_event(db, inferred)
    return ParseResponse(
        message=message,
        event=event,
        parser_mode=parser_mode,
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
