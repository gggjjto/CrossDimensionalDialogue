# 大话鸭角色管理系统文档

欢迎使用大话鸭AI角色扮演平台的角色管理系统！本系统提供了完整的角色管理、向量搜索和智能推荐功能。

## 📚 文档导航

### 🚀 快速开始
- [快速开始指南](quick_start.md) - 5分钟快速体验系统功能
- [API使用示例](api_examples.md) - 详细的API调用示例和代码

### 📖 完整文档
- [角色管理系统文档](character_management.md) - 完整的功能说明和技术文档
- [框架架构文档](framework.md) - 整体系统架构和设计理念

## 🎯 核心功能

### 角色管理
- ✅ 角色的创建、更新、删除和查询
- ✅ 支持角色头像、简介、人格定义等完整信息
- ✅ 示例台词和来源信息管理

### 标签系统
- ✅ 灵活的标签分类系统
- ✅ 支持标签颜色和描述
- ✅ 角色-标签多对多关系

### 智能搜索
- ✅ **文本搜索**: 基于关键词的传统搜索
- ✅ **向量搜索**: 基于语义相似度的AI搜索
- ✅ **混合搜索**: 结合文本和向量的智能搜索

### 多模型支持
- ✅ **阿里云 text-embedding-v4**: 1024维，中文优化
- ✅ **OpenAI text-embedding-3-small**: 1536维，多语言支持
- ✅ **动态切换**: 运行时切换嵌入模型提供商

## 🛠️ 技术特性

### 高性能
- 基于PostgreSQL + pgvector的向量数据库
- 高效的向量相似度计算
- 支持大规模角色数据

### 可扩展
- 适配器模式支持多种嵌入模型
- 模块化设计便于功能扩展
- 支持自定义嵌入模型提供商

### 易用性
- 完整的RESTful API
- 详细的API文档和示例
- 丰富的测试用例

## 📊 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   前端界面      │    │   API网关       │    │   后端服务      │
│   React/Vue     │◄──►│   FastAPI       │◄──►│   角色管理      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                       ┌─────────────────┐              │
                       │   嵌入模型      │◄─────────────┘
                       │   OpenAI/阿里云  │
                       └─────────────────┘
                                │
                       ┌─────────────────┐
                       │   向量数据库    │
                       │ PostgreSQL+     │
                       │ pgvector        │
                       └─────────────────┘
```

## 🚀 快速体验

### 1. 环境准备
```bash
cd backend
.\.venv\Scripts\Activate.ps1
uv sync
```

### 2. 启动服务
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. 测试功能
```bash
# 测试嵌入模型
python app/scripts/test_embedding_models.py

# 测试向量搜索
python app/scripts/test_vector_search_final.py
```

### 4. 查看API文档
访问 `http://localhost:8000/docs` 查看完整的API文档

## 📈 性能指标

- **向量维度**: 1024维（阿里云）/ 1536维（OpenAI）
- **搜索精度**: 相似度阈值0.5，实际结果0.53+
- **响应时间**: 毫秒级向量搜索
- **并发支持**: 支持高并发API请求

## 🔧 配置说明

### 环境变量
```bash
# 嵌入模型配置
EMBEDDING_PROVIDER=aliyun  # 或 openai

# API密钥
OPENAI_API_KEY=your_openai_api_key
ALIYUN_API_KEY=your_aliyun_api_key
```

### 数据库配置
确保PostgreSQL已安装pgvector扩展：
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

## 📝 更新日志

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

## 📞 支持与反馈

- 📧 邮箱: support@dahuanya.com
- 🐛 问题反馈: [GitHub Issues](https://github.com/your-repo/issues)
- 📖 文档更新: 欢迎提交文档改进建议

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](../LICENSE) 文件了解详情。

---

**大话鸭团队** - 让AI角色扮演更加智能和有趣！ 🦆✨