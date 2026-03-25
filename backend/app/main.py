from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import models  # noqa: F401
from .db import Base, SessionLocal, engine, get_db
from .parser import infer_event
from .repository import create_event, list_events, seed_events
from .schemas import Event, EventCreate, ParseRequest, ParseResponse


def initialize_database() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_events(db)


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_database()
    yield


app = FastAPI(
    title="AI Calendar API",
    description="MVP backend for an AI-powered memory and planning assistant.",
    version="0.2.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

initialize_database()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/events", response_model=list[Event])
def get_events(db: Session = Depends(get_db)) -> list[Event]:
    return list_events(db)


@app.post("/api/events", response_model=Event)
def post_event(payload: EventCreate, db: Session = Depends(get_db)) -> Event:
    return create_event(db, payload)


@app.post("/api/parse", response_model=ParseResponse)
def parse_event(payload: ParseRequest, db: Session = Depends(get_db)) -> ParseResponse:
    inferred = infer_event(payload.text)
    event = create_event(db, inferred)
    return ParseResponse(
        message="Parsed successfully and saved to the event timeline.",
        event=event,
    )
