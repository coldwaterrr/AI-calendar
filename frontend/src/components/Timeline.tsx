import type { EventItem } from "../types";

type Props = {
  events: EventItem[];
  onEdit?: (event: EventItem) => void;
};

export function Timeline({ events, onEdit }: Props) {
  const past = events.filter((e) => e.tense === "past");
  const future = events.filter((e) => e.tense === "future");

  return (
    <article className="glass-card panel">
      <div className="panel-header">
        <h2>双轨时间轴</h2>
        <p>上方为过去，下方为未来</p>
      </div>
      <div className="timeline">
        <div className="timeline-section">
          <span className="section-label muted">Past</span>
          {past.length === 0 && <p className="empty-hint">暂无过去记录</p>}
          {past.map((event) => (
            <div
              className="event-card muted-card clickable"
              key={event.id}
              onClick={() => onEdit?.(event)}
            >
              <span className="event-dot" style={{ background: event.color }} />
              <div className="event-info">
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
          {future.length === 0 && <p className="empty-hint">暂无未来计划</p>}
          {future.map((event) => (
            <div
              className="event-card clickable"
              key={event.id}
              onClick={() => onEdit?.(event)}
            >
              <span className="event-dot" style={{ background: event.color }} />
              <div className="event-info">
                <strong>{event.title}</strong>
                <p>{formatTime(event.start_at)}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </article>
  );
}

function formatTime(value?: string) {
  if (!value) return "时间未知";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "时间未知";
  return new Intl.DateTimeFormat("zh-CN", {
    month: "numeric",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}
