from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


EventTense = Literal["past", "future"]
EventCategory = Literal["research", "life", "meeting"]


class Event(BaseModel):
    id: str
    title: str
    description: str = ""
    start_at: datetime
    end_at: datetime
    tense: EventTense
    category: EventCategory
    color: str
    source_type: Literal["text", "voice"] = "text"
    raw_input: str
    confidence: float = Field(ge=0.0, le=1.0)

    model_config = {"from_attributes": True}


class EventCreate(BaseModel):
    id: str
    title: str = Field(min_length=1, max_length=255)
    description: str = ""
    start_at: datetime
    end_at: datetime
    tense: EventTense
    category: EventCategory
    color: str
    source_type: Literal["text", "voice"] = "text"
    raw_input: str
    confidence: float = Field(ge=0.0, le=1.0)


class ParseRequest(BaseModel):
    text: str = Field(min_length=1)


class ParseResponse(BaseModel):
    message: str
    event: Event
