# 大黄鸭后端服务

大黄鸭是一个基于AI的智能对话平台，支持多角色对话、语音交互、图像生成等功能。后端采用FastAPI框架构建，提供RESTful API和WebSocket服务。

## 🚀 快速开始

### 环境要求

- Python 3.10+
- PostgreSQL 12+ (支持pgvector扩展)
- Redis 6+
- 七牛云存储账号
- 阿里云DashScope API Key

### 安装依赖

```bash
# 使用uv包管理器（推荐）
uv sync

# 或使用pip
pip install -r requirements.txt
```

### 环境配置

创建 `.env` 文件在项目根目录：

```bash
# 数据库配置
DATABASE_URL=postgresql://username:password@localhost:5432/dahuanya

# Redis配置
REDIS_URL=redis://localhost:6379

# 安全配置
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=11520

# 前端配置
FRONTEND_HOST=http://localhost:5173

# 阿里云DashScope配置
QWEN_API_KEY=your-dashscope-api-key

# 七牛云存储配置
QINIU_ACCESS_KEY=your-qiniu-access-key
QINIU_SECRET_KEY=your-qiniu-secret-key
QINIU_BUCKET_NAME=your-bucket-name
QINIU_DOMAIN=your-domain.com

# 邮件配置（可选）
SMTP_TLS=true
SMTP_PORT=587
SMTP_HOST=smtp.gmail.com
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# 环境配置
ENVIRONMENT=local
```

### 数据库初始化

```bash
# 创建数据库迁移
alembic upgrade head

# 初始化基础数据
python -m app.initial_data
```

### 运行服务

```bash
# 开发模式
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 访问服务

- API文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/api/v1/health

## 🏗️ 架构设计

### 整体架构



### 技术栈

- **Web框架**: FastAPI + Uvicorn
- **数据库**: PostgreSQL + pgvector (向量搜索)
- **缓存**: Redis
- **存储**: 七牛云对象存储
- **AI服务**: 阿里云DashScope (通义千问)
- **语音**: TTS/STT服务
- **认证**: JWT Token
- **文档**: OpenAPI/Swagger

### 模块架构

```
app/
├── main.py                 # 应用入口
├── core/                   # 核心配置
│   ├── config.py          # 环境配置
│   ├── db.py              # 数据库连接
│   └── security.py        # 安全认证
├── models/                 # 数据模型
│   ├── user.py            # 用户模型
│   ├── character.py       # 角色模型
│   ├── conversation.py    # 对话模型
│   └── voice_catalog.py   # 音色目录
├── schemas/                # API数据模式
│   ├── user.py            # 用户API模式
│   ├── character.py       # 角色API模式
│   └── conversation.py    # 对话API模式
├── crud/                   # 数据库操作
│   ├── user.py            # 用户CRUD
│   ├── character.py       # 角色CRUD
│   └── conversation.py    # 对话CRUD
├── services/               # 业务服务
│   ├── llm_service.py     # LLM服务
│   ├── tts_service.py     # 语音合成
│   ├── stt_service.py     # 语音识别
│   ├── embedding_service.py # 向量嵌入
│   └── voice_demo_service.py # 音色示例
├── api/                    # API路由
│   ├── main.py            # API路由入口
│   └── routes/            # 具体路由
│       ├── users/         # 用户相关API
│       ├── characters/    # 角色相关API
│       ├── conversations/ # 对话相关API
│       └── voice/         # 语音相关API
└── utils/                  # 工具函数
    ├── response.py        # 响应工具
    ├── email.py           # 邮件工具
    └── qiniu_storage.py   # 存储工具
```

## 📋 核心功能模块

### 1. 用户管理模块

**功能特性**:
- 用户注册/登录/注销
- JWT Token认证
- 个人资料管理
- 用户统计信息

**API端点**:
- `POST /api/v1/login/access-token` - 用户登录
- `GET /api/v1/users/me` - 获取当前用户信息
- `PUT /api/v1/users/me` - 更新用户信息

**数据模型**:
```python
class User:
    id: UUID
    email: str
    full_name: str
    avatar_url: str
    bio: str
    location: str
    website: str
    created_at: datetime
    character_count: int
    conversation_count: int
```

### 2. 角色管理模块

**功能特性**:
- 角色创建/编辑/删除
- 角色公开/私有设置
- 用户权限控制
- 角色标签管理

**API端点**:
- `GET /api/v1/characters/` - 获取用户角色列表
- `GET /api/v1/characters/public` - 获取公开角色列表
- `POST /api/v1/characters/` - 创建角色
- `PUT /api/v1/characters/{id}` - 更新角色
- `DELETE /api/v1/characters/{id}` - 删除角色

**数据模型**:
```python
class Character:
    id: UUID
    user_id: UUID
    name: str
    description: str
    personality: str
    voice: str
    avatar_url: str
    is_public: bool
    is_active: bool
    created_at: datetime
```

### 3. 对话管理模块

**功能特性**:
- 多角色对话编排
- 对话历史记录
- 消息类型支持（文本/语音/图像）

**API端点**:
- `GET /api/v1/conversations/` - 获取对话列表
- `POST /api/v1/conversations/` - 创建对话
- `GET /api/v1/conversations/{id}` - 获取对话详情

**数据模型**:
```python
class Conversation:
    id: UUID
    user_id: UUID
    title: str
    character_ids: List[UUID]
    created_at: datetime
    updated_at: datetime

class Message:
    id: UUID
    conversation_id: UUID
    character_id: UUID
    content: str
    message_type: str
    created_at: datetime
```

### 4. 语音处理模块

**功能特性**:
- 语音转文本 (STT)
- 文本转语音 (TTS)
- 音色目录管理
- 音色示例生成

**API端点**:
- `POST /api/v1/voice/stt` - 语音识别
- `POST /api/v1/voice/tts` - 语音合成
- `GET /api/v1/voice/catalog` - 获取音色目录
- `POST /api/v1/voice-demo/generate-all` - 生成音色示例

**支持格式**:
- 音频格式: WAV, MP3, M4A, FLAC, AAC
- 采样率: 8kHz - 48kHz
- 最大时长: 30分钟

### 5. 图像处理模块

**功能特性**:
- 图像上传和存储
- 图像生成和处理
- 七牛云存储集成

**API端点**:
- `POST /api/v1/images/upload` - 上传图像
- `GET /api/v1/images/{id}` - 获取图像

## 🔧 开发指南

### 代码规范

- 使用 `ruff` 进行代码格式化
- 使用 `mypy` 进行类型检查
- 遵循 PEP 8 编码规范

```bash
# 代码格式化
ruff format .

# 代码检查
ruff check .

# 类型检查
mypy app/
```

### 测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/services/test_llm_service.py

# 生成覆盖率报告
pytest --cov=app --cov-report=html
```

### 数据库迁移

```bash
# 创建新迁移
alembic revision --autogenerate -m "描述"

# 执行迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

### 环境变量说明

| 变量名 | 说明 | 必需 | 默认值 |
|--------|------|------|--------|
| `DATABASE_URL` | PostgreSQL数据库连接 | ✅ | - |
| `REDIS_URL` | Redis连接 | ✅ | - |
| `SECRET_KEY` | JWT密钥 | ✅ | - |
| `QWEN_API_KEY` | 阿里云DashScope API Key | ✅ | - |
| `QINIU_ACCESS_KEY` | 七牛云Access Key | ✅ | - |
| `QINIU_SECRET_KEY` | 七牛云Secret Key | ✅ | - |
| `QINIU_BUCKET_NAME` | 七牛云存储桶名 | ✅ | - |
| `FRONTEND_HOST` | 前端地址 | ❌ | http://localhost:5173 |
| `ENVIRONMENT` | 运行环境 | ❌ | local |

## 🚀 部署指南

### Docker部署

```bash
# 构建镜像
docker build -t dahuanya-backend .

# 运行容器
docker run -p 8000:8000 --env-file .env dahuanya-backend
```

### 生产环境配置

1. 设置环境变量
2. 配置数据库和Redis
3. 配置反向代理 (Nginx)
4. 配置SSL证书
5. 设置监控和日志

## 📊 监控和日志

### 健康检查

- 端点: `GET /api/v1/health`
- 检查项目: 数据库连接、Redis连接、外部服务

### 日志配置

- 使用Python标准logging模块
- 支持不同级别的日志输出
- 集成Sentry错误监控

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 创建Pull Request

## 📄 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🆘 支持

如有问题，请通过以下方式联系：

- 创建Issue
- 发送邮件
- 查看文档

---

**大黄鸭团队** - 让AI对话更智能、更自然
