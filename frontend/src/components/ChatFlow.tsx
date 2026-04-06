import type { EventItem } from "../types";

type Props = {
  events: EventItem[];
};

export function ChatFlow({ events }: Props) {
  return (
    <article className="glass-card panel">
      <div className="panel-header">
        <h2>对话流</h2>
        <p>保留原始输入，联动时间轴结果</p>
      </div>
      <div className="chat-list">
        {events.length === 0 && <p className="empty-hint">暂无交互记录</p>}
        {events.map((event) => (
          <div className="chat-bubble" key={event.id}>
            <div className="chat-meta">
              <span className={`tense-badge ${event.tense}`}>
                {event.tense === "past" ? "过去轨迹" : "未来计划"}
              </span>
              <span>{Math.round(event.confidence * 100)}%</span>
            </div>
            <strong>{event.raw_input}</strong>
            <p>{event.description}</p>
          </div>
        ))}
      </div>
    </article>
  );
}
