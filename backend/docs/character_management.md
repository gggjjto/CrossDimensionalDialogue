# 角色管理系统文档

## 概述

角色管理系统是大黄鸭AI角色扮演平台的核心功能，支持角色的创建、管理、搜索和向量化存储。系统集成了多种嵌入模型，提供强大的语义搜索能力。

## 核心功能

### 1. 角色管理
- **角色创建**: 支持创建包含人格、背景、示例台词等信息的角色
- **角色更新**: 支持修改角色的所有属性
- **角色删除**: 支持软删除和硬删除
- **角色查询**: 支持按ID、名称等条件查询角色

### 2. 标签系统
- **标签管理**: 支持创建、更新、删除标签
- **标签分类**: 支持为角色添加多个标签进行分类
- **标签搜索**: 支持按标签筛选角色

### 3. 向量搜索
- **多模型支持**: 支持OpenAI和阿里云等多种嵌入模型
- **语义搜索**: 基于向量相似度的智能搜索
- **混合搜索**: 结合文本搜索和向量搜索的综合搜索
- **实时切换**: 支持运行时切换嵌入模型提供商

## 技术架构

### 数据模型

#### 角色表 (characters)
```sql
CREATE TABLE characters (
    id UUID PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    short_bio VARCHAR(500),
    avatar_url VARCHAR(500),
    persona_text TEXT,
    example_lines JSON,
    source VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

#### 标签表 (character_tags)
```sql
CREATE TABLE character_tags (
    id UUID PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description VARCHAR(255),
    color VARCHAR(7),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

#### 角色-标签关系表 (character_tag_maps)
```sql
CREATE TABLE character_tag_maps (
    id UUID PRIMARY KEY,
    character_id UUID REFERENCES characters(id),
    tag_id UUID REFERENCES character_tags(id),
    created_at TIMESTAMP
);
```

#### 角色向量表 (character_embeddings)
```sql
CREATE TABLE character_embeddings (
    id UUID PRIMARY KEY,
    character_id UUID REFERENCES characters(id),
    embedding_type VARCHAR(50), -- 'persona', 'bio', 'combined'
    model_name VARCHAR(100),
    dimension INTEGER,
    embedding VECTOR(1024), -- 使用pgvector扩展
    created_at TIMESTAMP
);
```

### 嵌入模型支持

#### 阿里云 text-embedding-v4
- **维度**: 1024
- **提供商**: 阿里云
- **特点**: 高质量中文语义理解

#### OpenAI text-embedding-3-small
- **维度**: 1536
- **提供商**: OpenAI
- **特点**: 多语言支持，性能优秀

### 搜索功能

#### 1. 文本搜索
基于关键词的模糊匹配，支持在角色名称、简介、人格文本中搜索。

```python
# 示例：搜索包含"哲学家"的角色
search_request = CharacterSearchRequest(
    query="哲学家",
    search_type="text",
    limit=10,
    offset=0,
    is_active=True
)
```

#### 2. 向量搜索
基于语义相似度的智能搜索，能够理解查询意图并找到相关角色。

```python
# 示例：搜索与"古希腊思想家"相似的角色
query_embedding = await embedding_service.generate_embedding("古希腊思想家")
vector_results = character_embedding_crud.vector_search_characters(
    session, search_request, query_embedding
)
```

#### 3. 混合搜索
结合文本搜索和向量搜索，提供更全面的搜索结果。

```python
# 示例：混合搜索
hybrid_results = character_embedding_crud.hybrid_search_characters(
    session, search_request, query_embedding
)
```

## API 端点

### 角色管理

#### 创建角色
```http
POST /api/v1/characters/
Content-Type: application/json

{
    "name": "苏格拉底",
    "short_bio": "古希腊哲学家，以问答法著称",
    "persona_text": "我是苏格拉底，古希腊的哲学家...",
    "example_lines": ["我知道我什么都不知道", "未经审视的人生不值得过"],
    "source": "古希腊哲学",
    "tag_ids": ["tag-uuid-1", "tag-uuid-2"]
}
```

#### 获取角色列表
```http
GET /api/v1/characters/?limit=10&offset=0&is_active=true
```

#### 获取单个角色
```http
GET /api/v1/characters/{character_id}
```

#### 更新角色
```http
PUT /api/v1/characters/{character_id}
Content-Type: application/json

{
    "name": "苏格拉底",
    "short_bio": "更新后的简介",
    "persona_text": "更新后的人格文本"
}
```

#### 删除角色
```http
DELETE /api/v1/characters/{character_id}
```

### 角色搜索

#### 搜索角色
```http
GET /api/v1/characters/search?query=哲学家&search_type=vector&limit=10&offset=0
```

参数说明：
- `query`: 搜索查询文本
- `search_type`: 搜索类型 (`text`, `vector`, `hybrid`)
- `limit`: 返回数量限制 (1-100)
- `offset`: 偏移量
- `tag_ids`: 标签过滤 (可选)
- `is_active`: 是否只搜索可用角色

### 标签管理

#### 创建标签
```http
POST /api/v1/characters/tags/
Content-Type: application/json

{
    "name": "哲学",
    "description": "哲学相关角色",
    "color": "#FF5733"
}
```

#### 获取标签列表
```http
GET /api/v1/characters/tags/
```

### 嵌入模型管理

#### 获取模型信息
```http
GET /api/v1/characters/embeddings/model-info
```

#### 切换模型提供商
```http
POST /api/v1/characters/embeddings/switch-provider?provider=aliyun
```

## 配置说明

### 环境变量

```bash
# 嵌入模型配置
EMBEDDING_PROVIDER=aliyun  # 或 openai

# OpenAI 配置
OPENAI_API_KEY=your_openai_api_key
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# 阿里云配置
ALIYUN_API_KEY=your_aliyun_api_key
ALIYUN_EMBEDDING_MODEL=text-embedding-v4
```

### 数据库配置

确保PostgreSQL已安装pgvector扩展：

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

## 使用示例

### 1. 创建角色并生成向量

```python
from app.services.embedding_service import embedding_service
from app.crud.character_embedding import character_embedding_crud

# 创建角色
character = Character(
    name="苏格拉底",
    short_bio="古希腊哲学家，以问答法著称",
    persona_text="我是苏格拉底，古希腊的哲学家...",
    example_lines=["我知道我什么都不知道", "未经审视的人生不值得过"],
    source="古希腊哲学",
    is_active=True
)

# 生成向量嵌入
embeddings = await embedding_service.generate_character_embeddings(
    character, session
)
```

### 2. 执行向量搜索

```python
# 生成查询向量
query_embedding = await embedding_service.generate_embedding("古希腊思想家")

# 执行向量搜索
search_request = CharacterSearchRequest(
    query="古希腊思想家",
    search_type="vector",
    limit=10,
    offset=0,
    is_active=True
)

results = character_embedding_crud.vector_search_characters(
    session, search_request, query_embedding
)

# 处理结果
for result in results.results:
    print(f"角色: {result.character.name}")
    print(f"相似度: {result.score:.4f}")
    print(f"简介: {result.character.short_bio}")
```

### 3. 切换嵌入模型

```python
# 切换到阿里云模型
await embedding_service.switch_provider("aliyun")

# 获取当前模型信息
model_info = embedding_service.get_model_info()
print(f"当前模型: {model_info['provider']} - {model_info['model_name']}")
```

## 性能优化

### 1. 向量索引
建议为向量字段创建索引以提高搜索性能：

```sql
CREATE INDEX ON character_embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
```

### 2. 批量操作
使用批量嵌入生成减少API调用次数：

```python
texts = ["文本1", "文本2", "文本3"]
embeddings = await embedding_service.generate_embeddings_batch(texts)
```

### 3. 缓存策略
对于频繁查询的角色，可以考虑添加缓存层。

## 故障排除

### 常见问题

1. **向量搜索返回空结果**
   - 检查pgvector扩展是否已安装
   - 确认向量数据已正确生成
   - 调整相似度阈值

2. **嵌入模型切换失败**
   - 检查API密钥配置
   - 确认模型名称正确
   - 查看错误日志

3. **搜索性能慢**
   - 创建向量索引
   - 优化查询条件
   - 考虑分页处理

### 日志查看

```bash
# 查看应用日志
tail -f logs/app.log

# 查看数据库日志
tail -f /var/log/postgresql/postgresql.log
```

## 扩展功能

### 1. 自定义嵌入模型
可以通过实现 `BaseEmbeddingAdapter` 接口来支持其他嵌入模型。

### 2. 高级搜索
- 支持多条件组合搜索
- 支持搜索历史记录
- 支持个性化推荐

### 3. 数据分析
- 角色使用统计
- 搜索热词分析
- 用户行为分析

## 更新日志

### v1.0.0 (2024-09-22)
- 初始版本发布
- 支持基本的角色管理功能
- 集成阿里云和OpenAI嵌入模型
- 实现向量搜索功能
- 支持混合搜索模式

---

## 联系支持

如有问题或建议，请联系开发团队或提交Issue。
