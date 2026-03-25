from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .mock_data import MOCK_EVENTS
from .schemas import Event, ParseRequest, ParseResponse


app = FastAPI(
    title="AI Calendar API",
    description="MVP backend for an AI-powered memory and planning assistant.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def infer_event(text: str) -> Event:
    now = datetime.now(tz=timezone.utc)
    lowered = text.lower()

    if "昨天" in text or "刚刚" in text or "today" in lowered:
        tense = "past"
        start_at = now - timedelta(hours=2)
        end_at = now - timedelta(hours=1)
    else:
        tense = "future"
        start_at = now + timedelta(days=1, hours=1)
        end_at = start_at + timedelta(hours=1)

    if "组会" in text or "会议" in text or "meeting" in lowered:
        category = "meeting"
        color = "#4B7BE5"
    elif "运动" in text or "吃饭" in text or "跑步" in text:
        category = "life"
        color = "#3FAE6A"
    else:
        category = "research"
        color = "#E45757"

    return Event(
        id=f"evt_{uuid4().hex[:8]}",
        title=text[:18],
        description="MVP 版本使用规则引擎生成，后续可替换为 LLM 结构化解析。",
        start_at=start_at,
        end_at=end_at,
        tense=tense,
        category=category,
        color=color,
        raw_input=text,
        confidence=0.72,
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/events", response_model=list[Event])
def list_events() -> list[Event]:
    return MOCK_EVENTS


@app.post("/api/parse", response_model=ParseResponse)
def parse_event(payload: ParseRequest) -> ParseResponse:
    event = infer_event(payload.text)
    return ParseResponse(
        message="解析完成，MVP 已生成结构化事件。",
        event=event,
    )
