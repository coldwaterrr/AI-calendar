import { useEffect, useState } from "react";

type EventItem = {
  id: string;
  title: string;
  description: string;
  start_at: string;
  end_at: string;
  tense: "past" | "future";
  category: "research" | "life" | "meeting";
  color: string;
  raw_input: string;
  confidence: number;
};

type Provider = "openai" | "anthropic" | "gemini" | "ollama" | "custom";

type ModelConfig = {
  provider: Provider;
  model: string;
  base_url: string;
  api_key_masked: string;
  is_active: boolean;
  has_api_key: boolean;
  updated_at: string;
};

type TestResult = {
  success: boolean;
  latency_ms: number;
  message: string;
};

const API_BASE = "http://127.0.0.1:8000";

const providerOptions: Provider[] = ["openai", "anthropic", "gemini", "ollama", "custom"];

function formatTime(value: string) {
  return new Intl.DateTimeFormat("zh-CN", {
    month: "numeric",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

export function App() {
  const [events, setEvents] = useState<EventItem[]>([]);
  const [input, setInput] = useState("下周二早上 9 点提醒我开组会");
  const [status, setStatus] = useState("等待输入");
  const [configStatus, setConfigStatus] = useState("尚未配置模型");
  const [testResult, setTestResult] = useState<TestResult | null>(null);
  const [configForm, setConfigForm] = useState({
    provider: "openai" as Provider,
    model: "gpt-4o-mini",
    base_url: "",
    api_key: "",
    is_active: true,
  });
  const [savedConfig, setSavedConfig] = useState<ModelConfig | null>(null);

  useEffect(() => {
    void fetch(`${API_BASE}/api/events`)
      .then((response) => response.json())
      .then((data: EventItem[]) => setEvents(data))
      .catch(() => setStatus("后端尚未启动，当前展示为开发占位状态"));

    void fetch(`${API_BASE}/api/model-config`)
      .then(async (response) => {
        if (!response.ok) {
          throw new Error("missing");
        }
        return response.json();
      })
      .then((data: ModelConfig) => {
        setSavedConfig(data);
        setConfigStatus(`当前已启用 ${data.provider} / ${data.model}`);
        setConfigForm((current) => ({
          ...current,
          provider: data.provider,
          model: data.model,
          base_url: data.base_url,
          api_key: "",
          is_active: data.is_active,
        }));
      })
      .catch(() => setConfigStatus("尚未配置模型，可在右侧设置面板中保存"));
  }, []);

  async function handleSubmit() {
    setStatus("解析中...");
    try {
      const response = await fetch(`${API_BASE}/api/parse`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ text: input }),
      });
      const data = (await response.json()) as { event: EventItem; message: string };
      setEvents((current) => [data.event, ...current]);
      setStatus(data.message);
    } catch {
      setStatus("未连接到后端，已保留输入内容");
    }
  }

  async function handleSaveConfig() {
    setConfigStatus("保存中...");
    try {
      const response = await fetch(`${API_BASE}/api/model-config`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(configForm),
      });
      const data = (await response.json()) as ModelConfig;
      setSavedConfig(data);
      setConfigStatus(`已保存 ${data.provider} / ${data.model}`);
      setConfigForm((current) => ({ ...current, api_key: "" }));
    } catch {
      setConfigStatus("保存失败，请确认后端已启动");
    }
  }

  async function handleTestConfig() {
    setConfigStatus("测试连接中...");
    try {
      const response = await fetch(`${API_BASE}/api/model-config/test`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(configForm),
      });
      const data = (await response.json()) as TestResult;
      setTestResult(data);
      setConfigStatus(data.message);
    } catch {
      setConfigStatus("测试失败，请确认后端已启动");
    }
  }

  const pastEvents = events.filter((event) => event.tense === "past");
  const futureEvents = events.filter((event) => event.tense === "future");

  return (
    <div className="page-shell">
      <div className="aurora aurora-left" />
      <div className="aurora aurora-right" />
      <main className="layout">
        <section className="hero-card glass-card">
          <div className="hero-copy">
            <p className="eyebrow">Memory + Planning Assistant</p>
            <h1>AI Calendar</h1>
            <p className="hero-text">
              用一句自然语言，同时管理已经发生的轨迹和接下来要做的安排。
            </p>
          </div>
          <div className="composer">
            <textarea
              value={input}
              onChange={(event) => setInput(event.target.value)}
              placeholder="例如：昨天傍晚我在图书馆看论文，下周三上午 10 点提醒我开会"
            />
            <div className="composer-footer">
              <span>{status}</span>
              <button onClick={handleSubmit}>解析并生成事件</button>
            </div>
          </div>
        </section>

        <section className="content-grid expanded-grid">
          <article className="glass-card panel">
            <div className="panel-header">
              <h2>对话流</h2>
              <p>保留原始输入，联动时间轴结果</p>
            </div>
            <div className="chat-list">
              {events.map((event) => (
                <div className="chat-bubble" key={event.id}>
                  <div className="chat-meta">
                    <span>{event.tense === "past" ? "过去轨迹" : "未来计划"}</span>
                    <span>{Math.round(event.confidence * 100)}%</span>
                  </div>
                  <strong>{event.raw_input}</strong>
                  <p>{event.description}</p>
                </div>
              ))}
            </div>
          </article>

          <article className="glass-card panel">
            <div className="panel-header">
              <h2>双轨时间轴</h2>
              <p>上方为过去，下方为未来</p>
            </div>
            <div className="timeline">
              <div className="timeline-section">
                <span className="section-label muted">Past</span>
                {pastEvents.map((event) => (
                  <div className="event-card muted-card" key={event.id}>
                    <span className="event-dot" style={{ background: event.color }} />
                    <div>
                      <strong>{event.title}</strong>
                      <p>{formatTime(event.start_at)}</p>
                    </div>
                  </div>
                ))}
              </div>

              <div className="now-line">
                <span>NOW</span>
              </div>

              <div className="timeline-section">
                <span className="section-label">Future</span>
                {futureEvents.map((event) => (
                  <div className="event-card" key={event.id}>
                    <span className="event-dot" style={{ background: event.color }} />
                    <div>
                      <strong>{event.title}</strong>
                      <p>{formatTime(event.start_at)}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </article>

          <article className="glass-card panel settings-panel">
            <div className="panel-header">
              <h2>BYOK 设置</h2>
              <p>配置 OpenAI、Gemini、Anthropic、Ollama 或自定义接口</p>
            </div>

            <div className="settings-stack">
              <label>
                <span>Provider</span>
                <select
                  value={configForm.provider}
                  onChange={(event) =>
                    setConfigForm((current) => ({
                      ...current,
                      provider: event.target.value as Provider,
                    }))
                  }
                >
                  {providerOptions.map((provider) => (
                    <option key={provider} value={provider}>
                      {provider}
                    </option>
                  ))}
                </select>
              </label>

              <label>
                <span>Model</span>
                <input
                  value={configForm.model}
                  onChange={(event) =>
                    setConfigForm((current) => ({ ...current, model: event.target.value }))
                  }
                  placeholder="gpt-4o-mini"
                />
              </label>

              <label>
                <span>Base URL</span>
                <input
                  value={configForm.base_url}
                  onChange={(event) =>
                    setConfigForm((current) => ({ ...current, base_url: event.target.value }))
                  }
                  placeholder="https://api.openai.com/v1"
                />
              </label>

              <label>
                <span>API Key</span>
                <input
                  type="password"
                  value={configForm.api_key}
                  onChange={(event) =>
                    setConfigForm((current) => ({ ...current, api_key: event.target.value }))
                  }
                  placeholder="sk-..."
                />
              </label>

              <label className="checkbox-row">
                <input
                  type="checkbox"
                  checked={configForm.is_active}
                  onChange={(event) =>
                    setConfigForm((current) => ({ ...current, is_active: event.target.checked }))
                  }
                />
                <span>设为当前启用模型</span>
              </label>

              <div className="settings-actions">
                <button onClick={handleTestConfig} className="secondary-button">
                  测试连接
                </button>
                <button onClick={handleSaveConfig}>保存配置</button>
              </div>

              <div className="status-block">
                <strong>{configStatus}</strong>
                {savedConfig ? (
                  <p>
                    已保存密钥：{savedConfig.api_key_masked}，最近更新时间：
                    {formatTime(savedConfig.updated_at)}
                  </p>
                ) : null}
                {testResult ? (
                  <p>
                    测试结果：{testResult.success ? "成功" : "失败"}，耗时 {testResult.latency_ms} ms
                  </p>
                ) : null}
              </div>
            </div>
          </article>
        </section>
      </main>
    </div>
  );
}
