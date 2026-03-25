# AI Calendar MVP 开发计划

## 1. 当前开发选型

- 前端：React + Vite + TypeScript
- 后端：FastAPI + SQLAlchemy + Alembic
- 数据层：当前使用 SQLite 持久化，已支持通过 `DATABASE_URL` 切换 PostgreSQL
- 密钥存储：当前使用本地 Fernet 加密文件进行 API Key 加密

## 2. 已初始化内容

- 基础产品 PRD
- FastAPI 服务入口
- SQLite 数据库与事件表
- Alembic 迁移目录与初始 migration
- PostgreSQL Docker Compose 模板
- PostgreSQL 连通性验证脚本
- BYOK 配置模型与接口
- 简化版自然语言解析接口
- React 首页骨架
- 聊天流、双轨时间轴与设置面板基础展示

## 3. 已实现接口

- `GET /health`
- `GET /api/events`
- `POST /api/events`
- `POST /api/parse`
- `GET /api/model-config`
- `PUT /api/model-config`
- `POST /api/model-config/test`

## 4. 数据库迁移

### SQLite

```bash
cd backend
alembic -c alembic.ini upgrade head
```

### PostgreSQL

1. 确保 Docker Desktop 已启动。

2. 启动数据库：

```bash
docker compose up -d postgres
```

3. 设置环境变量：

```bash
set DATABASE_URL=postgresql+psycopg://ai_calendar:ai_calendar_dev@127.0.0.1:5432/ai_calendar
```

4. 跑迁移并验证：

```bash
cd backend
alembic -c alembic.ini upgrade head
python scripts/verify_postgres.py
```

## 5. 当前验证结果

- Alembic 已在 SQLite 干净库上验证通过
- Docker CLI 可用
- 当前环境的 Docker daemon 未启动，因此尚未完成真实 PostgreSQL 容器验证

## 6. 建议下一步开发顺序

1. 启动 Docker Desktop 后完成 PostgreSQL 实例验证
2. 将规则解析替换为 LiteLLM 结构化输出
3. 将模型测试接口接到真实供应商请求
4. 接入语音转写链路
5. 增加事件编辑、删除和筛选能力

## 7. 本地启动方式

### 后端

```bash
cd backend
pip install -r requirements.txt
alembic -c alembic.ini upgrade head
uvicorn app.main:app --reload
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

默认本地地址：

- 前端：`http://127.0.0.1:5173`
- 后端：`http://127.0.0.1:8000`
