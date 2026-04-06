import { useState } from "react";
import type { Provider } from "../types";

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

type Props = {
  configForm: {
    provider: Provider;
    model: string;
    base_url: string;
    api_key: string;
    is_active: boolean;
  };
  onFormChange: (form: Props["configForm"]) => void;
  onSave: () => void;
  onTest: () => void;
  configStatus: string;
  savedConfig: ModelConfig | null;
  testResult: TestResult | null;
};

const providerOptions: Provider[] = ["openai", "anthropic", "gemini", "ollama", "openrouter", "custom"];

export function Settings({ configForm, onFormChange, onSave, onTest, configStatus, savedConfig, testResult }: Props) {
  const [showKey, setShowKey] = useState(false);

  const baseUrlPlaceholder = configForm.provider === "openrouter"
    ? "https://openrouter.ai/api/v1"
    : "https://api.openai.com/v1";

  const formatTime = (value?: string) => {
    if (!value) return "时间未知";
    try {
      const date = new Date(value);
      if (Number.isNaN(date.getTime())) return "时间未知";
      return new Intl.DateTimeFormat("zh-CN", {
        month: "numeric",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      }).format(date);
    } catch {
      return "时间未知";
    }
  };

  return (
    <article className="glass-card panel settings-panel">
      <div className="panel-header">
        <h2>模型配置</h2>
        <p>配置 OpenAI、OpenRouter、Gemini、Anthropic、Ollama 或自定义接口</p>
      </div>

      <div className="settings-stack">
        <label>
          <span>Provider</span>
          <select
            value={configForm.provider}
            onChange={(e) =>
              onFormChange({
                ...configForm,
                provider: e.target.value as Provider,
                base_url:
                  e.target.value === "openrouter"
                    ? "https://openrouter.ai/api/v1"
                    : configForm.base_url,
              })
            }
          >
            {providerOptions.map((p) => (
              <option key={p} value={p}>
                {p}
              </option>
            ))}
          </select>
        </label>

        <label>
          <span>Model</span>
          <input
            value={configForm.model}
            onChange={(e) => onFormChange({ ...configForm, model: e.target.value })}
            placeholder={configForm.provider === "openrouter" ? "stepfun/step-3.5-flash:free" : "gpt-4o-mini"}
          />
        </label>

        <label>
          <span>Base URL</span>
          <input
            value={configForm.base_url}
            onChange={(e) => onFormChange({ ...configForm, base_url: e.target.value })}
            placeholder={baseUrlPlaceholder}
          />
        </label>

        <label>
          <span>API Key</span>
          <input
            type={showKey ? "text" : "password"}
            value={configForm.api_key}
            onChange={(e) => onFormChange({ ...configForm, api_key: e.target.value })}
            placeholder="sk-..."
          />
        </label>

        <label className="checkbox-row">
          <input
            type="checkbox"
            checked={configForm.is_active}
            onChange={(e) => onFormChange({ ...configForm, is_active: e.target.checked })}
          />
          <span>设为当前启用模型</span>
        </label>

        <div className="settings-actions">
          <button onClick={onTest} className="secondary-button">
            测试连接
          </button>
          <button onClick={onSave}>保存配置</button>
        </div>

        <div className="status-block">
          <strong>{configStatus}</strong>
          {savedConfig ? (
            <p>
              已保存：{savedConfig.provider} / {savedConfig.model}，密钥：{savedConfig.api_key_masked}，
              更新：{formatTime(savedConfig.updated_at)}
            </p>
          ) : null}
          {testResult ? (
            <p>
              测试：{testResult.success ? "成功" : "失败"}，
              耗时 {testResult.latency_ms} ms — {testResult.message}
            </p>
          ) : null}
        </div>
      </div>
    </article>
  );
}
