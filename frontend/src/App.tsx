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

const API_BASE = "http://127.0.0.1:8000";

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

  useEffect(() => {
    void fetch(`${API_BASE}/api/events`)
      .then((response) => response.json())
      .then((data: EventItem[]) => setEvents(data))
      .catch(() => setStatus("后端尚未启动，当前展示为开发占位状态"));
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

        <section className="content-grid">
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
        </section>
      </main>
    </div>
  );
}
