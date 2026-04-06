type Props = {
  value: string;
  onChange: (v: string) => void;
  onSend: () => void;
  status: string;
  loading: boolean;
};

export function Composer({ value, onChange, onSend, status, loading }: Props) {
  return (
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
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder="例如：昨天傍晚我在图书馆看论文，下周三上午 10 点提醒我开会"
          onKeyDown={(e) => {
            if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
              e.preventDefault();
              onSend();
            }
          }}
        />
        <div className="composer-footer">
          <span className="status-text">{status}</span>
          <button onClick={onSend} disabled={loading}>
            {loading ? "解析中..." : "解析并生成事件"}
          </button>
        </div>
      </div>
    </section>
  );
}
