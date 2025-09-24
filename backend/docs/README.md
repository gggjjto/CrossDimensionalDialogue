# 大黄鸭AI角色扮演平台 - 后端文档

欢迎使用大黄鸭AI角色扮演平台！这是一个基于FastAPI的现代化后端服务，提供完整的角色管理、对话编排、语音处理和文件存储功能。

## 📚 文档导航

### 🚀 快速开始
- [快速开始指南](guides/quick_start.md) - 5分钟快速体验系统功能
- [API接口文档](api/) - 完整的API接口说明

### 📖 功能指南
- [角色管理](systematic_design/character/) - 角色创建、搜索、管理
- [对话服务](systematic_design/conversation/) - 对话编排和消息处理
- [存储服务](storage/) - 七牛云文件存储集成

### 🛠️ 开发文档
- [系统架构](development/framework.md) - 整体系统架构和设计理念
- [开发指南](development/) - 开发环境配置和最佳实践

## 🎯 核心功能

### 角色管理
- ✅ 角色的创建、更新、删除和查询
- ✅ 支持角色头像、简介、人格定义等完整信息
- ✅ 智能搜索（文本搜索 + 向量搜索 + 混合搜索）
- ✅ 灵活的标签分类系统
- ✅ 多模型嵌入支持（阿里云、OpenAI）

### 对话服务
- ✅ 完整的对话编排功能
- ✅ 多LLM模型支持（OpenAI、DeepSeek、阿里千问）
- ✅ 智能上下文管理
- ✅ 会话状态持久化
- ✅ 实时消息流处理

### 语音处理
- ✅ 语音转文本（STT）支持
- ✅ 文本转语音（TTS）支持
- ✅ 实时语音对话
- ✅ 多语音引擎支持

### 文件存储
- ✅ 七牛云对象存储集成
- ✅ 支持音频、图片、文档文件上传
- ✅ 图片缩略图生成
- ✅ CDN加速支持
- ✅ 私有文件访问控制

## 🛠️ 技术栈

### 后端框架
- **FastAPI** - 现代化Python Web框架
- **SQLModel** - 类型安全的ORM
- **PostgreSQL** - 主数据库
- **pgvector** - 向量数据库扩展

### AI服务
- **OpenAI GPT** - 大语言模型
- **阿里云千问** - 中文优化模型
- **DeepSeek** - 高性价比模型
- **Whisper** - 语音识别
- **Coqui TTS** - 语音合成

### 存储服务
- **七牛云** - 对象存储
- **Redis** - 缓存服务
- **MinIO/S3** - 本地存储

### 基础设施
- **Docker** - 容器化部署
- **GitHub Actions** - CI/CD
- **Traefik** - 反向代理

## 🚀 快速体验

### 1. 环境准备
```bash
cd backend
.\.venv\Scripts\Activate.ps1
uv sync
```

### 2. 配置环境变量
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑配置文件，填入必要的API密钥
# - 数据库配置
# - OpenAI API密钥
# - 阿里云API密钥
# - 七牛云存储配置
```

### 3. 数据库迁移
```bash
alembic upgrade head
```

### 4. 启动服务
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. 测试功能
```bash
# 测试七牛云存储
python app/scripts/test_qiniu_storage.py

# 测试嵌入模型
python app/scripts/test_embedding_models.py

# 测试向量搜索
python app/scripts/test_vector_search_final.py
```

### 6. 查看API文档
访问 `http://localhost:8000/docs` 查看完整的API文档

## 📊 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   前端界面      │    │   API网关       │    │   后端服务      │
│   React/Vue     │◄──►│   FastAPI       │◄──►│   角色管理      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                       ┌─────────────────┐              │
                       │   AI服务层      │◄─────────────┘
                       │   LLM/STT/TTS   │
                       └─────────────────┘
                                │
                       ┌─────────────────┐
                       │   存储层        │
                       │ PostgreSQL+     │
                       │ pgvector+七牛云  │
                       └─────────────────┘
```

## 📈 性能指标

- **向量维度**: 1024维（阿里云）/ 1536维（OpenAI）
- **搜索精度**: 相似度阈值0.5，实际结果0.53+
- **响应时间**: 毫秒级向量搜索
- **并发支持**: 支持高并发API请求
- **文件存储**: 支持大文件上传和CDN加速

## 🔧 配置说明

### 环境变量
```bash
# 数据库配置
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=changethis
POSTGRES_DB=app

# AI服务配置
EMBEDDING_PROVIDER=aliyun  # 或 openai
OPENAI_API_KEY=your_openai_api_key
ALIYUN_API_KEY=your_aliyun_api_key

# 七牛云存储配置
QINIU_ACCESS_KEY=your_qiniu_access_key
QINIU_SECRET_KEY=your_qiniu_secret_key
QINIU_BUCKET_NAME=your_bucket_name
QINIU_DOMAIN=your_domain.com
```

### 数据库配置
确保PostgreSQL已安装pgvector扩展：
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

## 📝 更新日志

### v2.0.0 (2024-09-23)
- ✅ 集成七牛云存储服务
- ✅ 完善文件上传和管理功能
- ✅ 添加图片处理功能
- ✅ 优化文档结构

### v1.0.0 (2024-09-22)
- ✅ 初始版本发布
- ✅ 支持基本的角色管理功能
- ✅ 集成阿里云和OpenAI嵌入模型
- ✅ 实现向量搜索功能
- ✅ 支持混合搜索模式
- ✅ 完整的API文档和示例

## 🤝 贡献指南

欢迎贡献代码和建议！请查看以下指南：

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 发起 Pull Request

### 开发规范
- 使用 `uv` 管理Python依赖
- 遵循PEP 8代码规范
- 编写完整的类型提示
- 添加必要的测试用例
- 更新相关文档

## 📞 支持与反馈

- 📧 邮箱: support@dahuangya.com
- 🐛 问题反馈: [GitHub Issues](https://github.com/your-repo/issues)
- 📖 文档更新: 欢迎提交文档改进建议

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](../LICENSE) 文件了解详情。

---

**大黄鸭团队** - 让AI角色扮演更加智能和有趣！ 🦆✨