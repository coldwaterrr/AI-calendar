import { useState } from "react";
import { generateSummary } from "../api";
import type { Summary as SummaryType } from "../types";

type Props = {
  onRefresh?: () => void;
};

export function SummaryPanel({ onRefresh }: Props) {
  const [summary, setSummary] = useState<SummaryType | null>(null);
  const [days, setDays] = useState(7);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleGenerate() {
    setLoading(true);
    setError(null);
    try {
      const result = await generateSummary(days);
      setSummary(result);
      onRefresh?.();
    } catch (err) {
      setError(err instanceof Error ? err.message : "生成总结失败");
    } finally {
      setLoading(false);
    }
  }

  return (
    <article className="glass-card panel summary-panel">
      <div className="panel-header">
        <h2>AI 总结</h2>
        <p>回顾你过去的活动轨迹</p>
      </div>

      <div className="summary-controls">
        <div className="summary-days">
          {[7, 30, 90].map((d) => (
            <button
              key={d}
              className={`day-btn ${d === days ? "active" : ""} secondary-button`}
              onClick={() => setDays(d)}
            >
              {d === 90 ? "近 90 天" : `近 ${d} 天`}
            </button>
          ))}
        </div>
        <button
          className="summary-generate-btn"
          onClick={handleGenerate}
          disabled={loading}
        >
          {loading ? "分析中..." : "生成总结"}
        </button>
      </div>

      {loading && (
        <div className="summary-skeleton">
          <div className="skeleton-line" />
          <div className="skeleton-line short" />
          <div className="skeleton-line" />
        </div>
      )}

      {error && <p className="summary-error">{error}</p>}

      {summary && (
        <div className="summary-result">
          <div className="summary-meta">
            <span>{summary.event_count} 条记录</span>
            <span className={`mode-badge ${summary.parser_mode}`}>
              {summary.parser_mode === "llm" ? "LLM 分析" : "快速汇总"}
            </span>
          </div>
          <p className="summary-text">{summary.summary_text}</p>
        </div>
      )}
    </article>
  );
}
