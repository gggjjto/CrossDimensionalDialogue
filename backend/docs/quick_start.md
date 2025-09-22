# 角色管理系统快速开始

## 5分钟快速体验

### 1. 环境准备

确保已安装依赖并配置环境变量：

```bash
# 激活虚拟环境
cd backend
.\.venv\Scripts\Activate.ps1

# 安装依赖
uv sync

# 配置环境变量（复制 .env.example 到 .env 并填入API密钥）
cp .env.example .env
```

### 2. 数据库迁移

```bash
# 运行数据库迁移
alembic upgrade head
```

### 3. 启动服务

```bash
# 启动FastAPI服务
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. 测试功能

#### 测试嵌入模型
```bash
python app/scripts/test_embedding_models.py
```

#### 测试向量搜索
```bash
python app/scripts/test_vector_search_final.py
```

### 5. API测试

#### 创建角色
```bash
curl -X POST "http://localhost:8000/api/v1/characters/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "测试角色",
    "short_bio": "这是一个测试角色",
    "persona_text": "我是测试角色，用于演示功能",
    "example_lines": ["你好", "再见"],
    "source": "测试"
  }'
```

#### 搜索角色
```bash
# 文本搜索
curl "http://localhost:8000/api/v1/characters/search?query=测试&search_type=text"

# 向量搜索
curl "http://localhost:8000/api/v1/characters/search?query=测试角色&search_type=vector"
```

## 核心概念

### 角色 (Character)
- **name**: 角色名称
- **short_bio**: 角色简介
- **persona_text**: 角色人格定义（系统prompt）
- **example_lines**: 示例台词
- **source**: 来源/版权声明

### 标签 (Tag)
- **name**: 标签名称
- **description**: 标签描述
- **color**: 标签颜色

### 向量嵌入 (Embedding)
- **embedding_type**: 向量类型（persona/bio/combined）
- **model_name**: 使用的模型名称
- **dimension**: 向量维度
- **embedding**: 向量数据

## 搜索类型

1. **text**: 基于关键词的文本搜索
2. **vector**: 基于语义相似度的向量搜索
3. **hybrid**: 结合文本和向量的混合搜索

## 嵌入模型

- **阿里云 text-embedding-v4**: 1024维，中文优化
- **OpenAI text-embedding-3-small**: 1536维，多语言支持

## 下一步

- 查看 [完整文档](character_management.md)
- 探索 [API文档](http://localhost:8000/docs)
- 运行 [测试用例](tests/)
