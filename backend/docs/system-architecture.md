# CCD 系统框架说明

本文档详细说明 Cross-dimensional dialogue（CCD）的系统架构、核心组件、数据与控制流、部署拓扑与安全实践，帮助研发与运维快速对齐与扩展。

### 总览

CCD 由前端 SPA、后端 FastAPI 服务、异步任务执行进程、关系型数据库（含向量检索）、缓存与消息队列、对象存储/CDN，以及（生产可选的）反向代理层组成。整体以 Docker Compose 管理，开发与生产配置分离，支持健康检查与自动化部署。

## 系统架构



### 1. 组件说明

- 前端（React + Vite + Chakra + TanStack）
  - 职责：界面渲染、路由与状态管理、与后端进行 HTTP 交互。
  - 能力：角色创建、聊天对话、多模态展示（文本/音频/图片）。


- 后端（FastAPI，前缀 `/api/v1`）
  - API 聚合路由：认证、用户、角色、对话、对话编排、图像、语音处理、任务、工具等。
  - 通用能力：CORS、全局异常处理、OpenAPI 文档、JWT 鉴权、邮件找回。
  - 代码分层：`routes/`（路由层）→ `services/`（业务服务层）→ `crud/`（数据访问层）→ `models/`（ORM）/`schemas/`（Pydantic）。
  - 配置：统一读取根目录 `.env`，包含派生字段与默认值校验。

- 异步任务与执行器（Redis + RQ + Worker）
  - 职责：执行耗时操作（LLM 生成、嵌入计算、音视频处理、图片生成与上传等）。
  - 流程：后端入队（Redis）→ Worker 消费并执行 → 回写数据库/存储 → 客户端轮询或拉取结果。
  - 配置：`TASK_*` 参数控制超时、重试、TTL、并发等。

- 数据与向量检索（PostgreSQL + pgvector）
  - 职责：存储用户、角色、对话与多模态关联数据；存储嵌入向量实现相似度检索（RAG）。
  - 管理：Alembic 迁移；`crud/` 统一数据访问。

- 外部 AI 服务与语音处理
  - LLM：默认通义千问（Qwen），可切换 DeepSeek；支持对话、嵌入与图像生成。
  - 语音：STT/TTS 引擎可选（Whisper/OpenAI/Azure/Google/ElevenLabs）。
  - 七牛云：对象存储与 CDN 加速（音频/图片等）。

- 可观测与运维
  - 健康检查：`GET /api/v1/utils/health-check/`

### 2. 典型请求流程（序列图）
![序列图](./img/flow.png)

### 3. 配置与环境

- 统一 `.env`（示例见仓库根目录 `.env.example`），通过 `ENVIRONMENT=local|staging|production` 区分环境。
- 关键变量：
  - 安全：`SECRET_KEY`、`FIRST_SUPERUSER_PASSWORD`、`POSTGRES_PASSWORD`
  - 数据库：`POSTGRES_*`，拼装为 `SQLALCHEMY_DATABASE_URI`
  - 跨域：`FRONTEND_HOST`、`BACKEND_CORS_ORIGINS`
  - 队列：`REDIS_URL`、`TASK_*`
  - 模型：`LLM_PROVIDER`、`QWEN_*`、`DEEPSEEK_*`
  - 存储：`QINIU_*`
  - 观测：`SENTRY_DSN`

> 注意：非 `local` 环境下会强制校验部分敏感项不得为默认值。

### 4. 部署拓扑

- 开发：`docker-compose.override.yml`
  - 端口直出、热加载、可选 Traefik 仪表盘；Adminer 便捷 DB 管理。
- 生产：`docker-compose.yml`
  - Traefik 暴露 `api.<DOMAIN>` 与 `dashboard.<DOMAIN>`，证书自动化；各服务带健康检查与重启策略。

### 5. 安全与合规

- 鉴权：JWT，密码哈希（passlib + bcrypt）。
- CORS：仅允许受信来源，生产建议使用域名级管控。
- 密钥管理：生产环境从安全密钥管理服务注入；严禁默认值。
- 暴露面：限制 `adminer`、Traefik 控制台对公网暴露；使用网络隔离与只读凭据。

### 6. 扩展与演进

- 模型接入：在 `services/` 增加新的 LLM/Embedding/TTS/STT 适配与配置项。
- 能力扩展：在 `api/routes/` + `services/` 中新增路由与服务，沿用分层模式。
- 计算扩容：横向扩容 Backend 与 Worker；将耗时操作下沉 Worker；为热点接口增加缓存与索引。
- 存储优化：针对七牛云与 pgvector 的缓存与索引策略进行专项优化。

---

