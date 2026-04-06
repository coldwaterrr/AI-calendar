export type EventTense = "past" | "future";
export type EventCategory = "research" | "life" | "meeting";
export type Provider = "openai" | "anthropic" | "gemini" | "ollama" | "openrouter" | "custom";
export type ParserMode = "rule_based" | "llm";

export type EventItem = {
  id: string;
  title: string;
  description: string;
  start_at: string;
  end_at: string;
  tense: EventTense;
  category: EventCategory;
  color: string;
  raw_input: string;
  confidence: number;
};

export type ModelConfig = {
  provider: Provider;
  model: string;
  base_url: string;
  api_key_masked: string;
  is_active: boolean;
  has_api_key: boolean;
  updated_at: string;
};

export type TestResult = {
  success: boolean;
  latency_ms: number;
  message: string;
};

export type ParseResult = {
  event: EventItem;
  message: string;
  parser_mode: ParserMode;
};

export type Summary = {
  summary_text: string;
  event_count: number;
  period_start: string;
  period_end: string;
  parser_mode: "llm" | "fallback";
};

export type ApiError = {
  detail?: unknown;
  message?: string;
};
