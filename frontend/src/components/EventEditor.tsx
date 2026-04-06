import { useState } from "react";
import type { EventItem, EventTense, EventCategory } from "../types";

type Props = {
  event: EventItem | null;
  onClose: () => void;
  onSave: (id: string, patch: Record<string, unknown>) => void;
  onDelete: (id: string) => void;
};

export function EventEditor({ event, onClose, onSave, onDelete }: Props) {
  if (!event) return null;

  const [form, setForm] = useState({
    title: event.title,
    description: event.description,
    start_at: event.start_at.slice(0, 16),
    end_at: event.end_at.slice(0, 16),
    tense: event.tense as EventTense,
    category: event.category as EventCategory,
  });

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3>编辑事件</h3>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>

        <div className="modal-body">
          <label>
            <span>标题</span>
            <input
              value={form.title}
              onChange={(e) => setForm({ ...form, title: e.target.value })}
            />
          </label>

          <label>
            <span>描述</span>
            <textarea
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
            />
          </label>

          <div className="form-row">
            <label>
              <span>开始时间</span>
              <input
                type="datetime-local"
                value={form.start_at}
                onChange={(e) => setForm({ ...form, start_at: e.target.value })}
              />
            </label>
            <label>
              <span>结束时间</span>
              <input
                type="datetime-local"
                value={form.end_at}
                onChange={(e) => setForm({ ...form, end_at: e.target.value })}
              />
            </label>
          </div>

          <div className="form-row">
            <label>
              <span>时态</span>
              <select
                value={form.tense}
                onChange={(e) => setForm({ ...form, tense: e.target.value as EventTense })}
              >
                <option value="past">过去</option>
                <option value="future">未来</option>
              </select>
            </label>
            <label>
              <span>类别</span>
              <select
                value={form.category}
                onChange={(e) => setForm({ ...form, category: e.target.value as EventCategory })}
              >
                <option value="research">学术研究</option>
                <option value="meeting">会议</option>
                <option value="life">生活</option>
              </select>
            </label>
          </div>

          <p className="raw-input-preview">{event.raw_input}</p>
        </div>

        <div className="modal-footer">
          <button
            className="secondary-button danger"
            onClick={() => onDelete(event.id)}
          >
            删除
          </button>
          <div className="modal-actions">
            <button className="secondary-button" onClick={onClose}>取消</button>
            <button
              onClick={() =>
                onSave(event.id, {
                  title: form.title,
                  description: form.description,
                  start_at: form.start_at,
                  end_at: form.end_at,
                  tense: form.tense,
                  category: form.category,
                })
              }
            >
              保存
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
