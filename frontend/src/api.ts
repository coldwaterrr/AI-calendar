import type {
  ApiError,
  EventItem,
  ModelConfig,
  ParseResult,
  Summary,
  TestResult,
} from "./types";

const API_BASE = "http://127.0.0.1:8000";

async function parseError(response: Response): Promise<string> {
  try {
    const data = (await response.json()) as ApiError;
    if (typeof data.message === "string") return data.message;
    if (typeof data.detail === "string") return data.detail;
    if (Array.isArray(data.detail)) {
      return data.detail.map((item) => JSON.stringify(item)).join("; ");
    }
  } catch { /* empty */ }
  return `请求失败：HTTP ${response.status}`;
}

export async function fetchEvents(): Promise<EventItem[]> {
  const res = await fetch(`${API_BASE}/api/events`);
  if (!res.ok) throw new Error(await parseError(res));
  return res.json();
}

export async function parseText(text: string): Promise<ParseResult> {
  const res = await fetch(`${API_BASE}/api/parse`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
  if (!res.ok) throw new Error(await parseError(res));
  return res.json();
}

export async function fetchModelConfig(): Promise<ModelConfig> {
  const res = await fetch(`${API_BASE}/api/model-config`);
  if (!res.ok) throw new Error("missing");
  return res.json();
}

export async function saveModelConfig(payload: {
  provider: string;
  model: string;
  base_url: string;
  api_key: string;
  is_active: boolean;
}): Promise<ModelConfig> {
  const res = await fetch(`${API_BASE}/api/model-config`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(await parseError(res));
  return res.json();
}

export async function testModelConfig(payload: {
  provider: string;
  model: string;
  base_url: string;
  api_key: string;
}): Promise<TestResult> {
  const res = await fetch(`${API_BASE}/api/model-config/test`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(await parseError(res));
  return res.json();
}

export async function generateSummary(days: number): Promise<Summary> {
  const res = await fetch(`${API_BASE}/api/summary`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ days }),
  });
  if (!res.ok) throw new Error(await parseError(res));
  return res.json();
}

export async function updateEvent(
  eventId: string,
  payload: Partial<Omit<EventItem, "id" | "raw_input" | "confidence">>
): Promise<EventItem> {
  const res = await fetch(`${API_BASE}/api/events/${eventId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(await parseError(res));
  return res.json();
}

export async function deleteEvent(eventId: string): Promise<void> {
  const res = await fetch(`${API_BASE}/api/events/${eventId}`, {
    method: "DELETE",
  });
  if (!res.ok) throw new Error(await parseError(res));
}
