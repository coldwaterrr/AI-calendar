from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


EventTense = Literal['past', 'future']
EventCategory = Literal['research', 'life', 'meeting']
ModelProvider = Literal['openai', 'anthropic', 'gemini', 'ollama', 'custom']


class Event(BaseModel):
    id: str
    title: str
    description: str = ''
    start_at: datetime
    end_at: datetime
    tense: EventTense
    category: EventCategory
    color: str
    source_type: Literal['text', 'voice'] = 'text'
    raw_input: str
    confidence: float = Field(ge=0.0, le=1.0)

    model_config = {'from_attributes': True}


class EventCreate(BaseModel):
    id: str
    title: str = Field(min_length=1, max_length=255)
    description: str = ''
    start_at: datetime
    end_at: datetime
    tense: EventTense
    category: EventCategory
    color: str
    source_type: Literal['text', 'voice'] = 'text'
    raw_input: str
    confidence: float = Field(ge=0.0, le=1.0)


class ParseRequest(BaseModel):
    text: str = Field(min_length=1)


class ParseResponse(BaseModel):
    message: str
    event: Event


class ModelConfigUpdate(BaseModel):
    provider: ModelProvider
    model: str = Field(min_length=1, max_length=128)
    base_url: str = ''
    api_key: str = Field(min_length=1)
    is_active: bool = True


class ModelConfig(BaseModel):
    provider: ModelProvider
    model: str
    base_url: str = ''
    api_key_masked: str
    is_active: bool
    has_api_key: bool
    updated_at: datetime


class ModelConfigTestRequest(BaseModel):
    provider: ModelProvider
    model: str = Field(min_length=1, max_length=128)
    base_url: str = ''
    api_key: str = Field(min_length=1)


class ModelConfigTestResponse(BaseModel):
    success: bool
    latency_ms: int
    message: str
