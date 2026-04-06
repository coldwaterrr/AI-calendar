import { useEffect, useState } from "react";
import * as api from "./api";
import type { EventItem, Provider, TestResult, ModelConfig as ModelConfigType } from "./types";
import { Composer } from "./components/Composer";
import { Timeline } from "./components/Timeline";
import { ChatFlow } from "./components/ChatFlow";
import { SummaryPanel } from "./components/Summary";
import { Settings } from "./components/Settings";
import { EventEditor } from "./components/EventEditor";

export function App() {
  const [events, setEvents] = useState<EventItem[]>([]);
  const [input, setInput] = useState("下周二早上 9 点提醒我开组会");
  const [status, setStatus] = useState("等待输入");
  const [parseLoading, setParseLoading] = useState(false);
  const [configStatus, setConfigStatus] = useState("尚未配置模型");
  const [testResult, setTestResult] = useState<TestResult | null>(null);
  const [configForm, setConfigForm] = useState({
    provider: "openai" as Provider,
    model: "gpt-4o-mini",
    base_url: "",
    api_key: "",
    is_active: true,
  });
  const [savedConfig, setSavedConfig] = useState<ModelConfigType | null>(null);
  const [editingEvent, setEditingEvent] = useState<EventItem | null>(null);

  useEffect(() => {
    loadEvents();
    loadConfig();
  }, []);

  function loadEvents() {
    api.fetchEvents()
      .then((data) => setEvents(data))
      .catch(() => setStatus("后端尚未启动，当前展示为开发占位状态"));
  }

  function loadConfig() {
    api.fetchModelConfig()
      .then((data) => {
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
  }

  async function handleSend() {
    if (!input.trim()) return;
    setParseLoading(true);
    setStatus("解析中...");
    try {
      const data = await api.parseText(input);
      setEvents((current) => [data.event, ...current]);
      const modeLabel = data.parser_mode === "llm" ? "LLM 解析" : "规则回退";
      setStatus(`${modeLabel}：${data.message}`);
      setInput("");
    } catch (err) {
      setStatus(err instanceof Error ? err.message : "未连接到后端，已保留输入内容");
    } finally {
      setParseLoading(false);
    }
  }

  async function handleSaveConfig() {
    setConfigStatus("保存中...");
    try {
      const data = await api.saveModelConfig(configForm);
      setSavedConfig(data);
      setConfigStatus(`已保存 ${data.provider} / ${data.model}`);
      setConfigForm((current) => ({ ...current, api_key: "" }));
    } catch (err) {
      setConfigStatus(err instanceof Error ? err.message : "保存失败");
    }
  }

  async function handleTestConfig() {
    setConfigStatus("测试连接中...");
    try {
      const data = await api.testModelConfig(configForm);
      setTestResult(data);
      setConfigStatus(data.message);
    } catch (err) {
      setConfigStatus(err instanceof Error ? err.message : "测试失败");
    }
  }

  async function handleSaveEvent(id: string, patch: Record<string, unknown>) {
    try {
      const updated = await api.updateEvent(id, patch);
      setEvents((prev) => prev.map((e) => (e.id === id ? updated : e)));
      setEditingEvent(null);
    } catch (err) {
      alert(err instanceof Error ? err.message : "保存失败");
    }
  }

  async function handleDeleteEvent(id: string) {
    if (!confirm("确定删除此事件？")) return;
    try {
      await api.deleteEvent(id);
      setEvents((prev) => prev.filter((e) => e.id !== id));
      setEditingEvent(null);
    } catch (err) {
      alert(err instanceof Error ? err.message : "删除失败");
    }
  }

  return (
    <div className="page-shell">
      <div className="aurora aurora-left" />
      <div className="aurora aurora-right" />
      <main className="layout">
        <Composer
          value={input}
          onChange={setInput}
          onSend={handleSend}
          status={status}
          loading={parseLoading}
        />

        <section className="content-grid expanded-grid">
          <SummaryPanel onRefresh={loadEvents} />
          <ChatFlow events={events} />
          <Timeline events={events} onEdit={setEditingEvent} />
          <Settings
            configForm={configForm}
            onFormChange={setConfigForm}
            onSave={handleSaveConfig}
            onTest={handleTestConfig}
            configStatus={configStatus}
            savedConfig={savedConfig}
            testResult={testResult}
          />
        </section>

        <EventEditor
          event={editingEvent}
          onClose={() => setEditingEvent(null)}
          onSave={handleSaveEvent}
          onDelete={handleDeleteEvent}
        />
      </main>
    </div>
  );
}
