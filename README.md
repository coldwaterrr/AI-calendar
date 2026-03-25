# AI Calendar

AI Calendar 是一个以大语言模型驱动的“记忆与规划助理”项目，目标是通过自然语言交互完成过去轨迹记录与未来日程规划。

当前仓库已建立产品需求基线文档，详见 [docs/prd-ai-calendar.md](docs/prd-ai-calendar.md)。

目前已具备一版可继续开发的 Web + FastAPI MVP 骨架，并支持本地持久化与 BYOK 配置中心。

## 当前状态

- 仓库初始化完成
- PRD 已整理落地
- 前后端 MVP 骨架已创建
- 后端已支持环境变量数据库配置，可平滑切换 PostgreSQL
- 后端已接入 SQLite 持久化层
- BYOK 配置中心已具备保存、读取和测试接口
- 前端已补充 BYOK 设置面板

## 推荐下一步

1. 接入 PostgreSQL 与 Alembic
2. 用 LiteLLM 替换规则解析与测试占位逻辑
3. 完成语音转写链路
4. 增加事件编辑、删除与筛选
