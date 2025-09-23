# 角色管理MVP功能文档

## 概述

角色管理系统是大黄鸭AI角色扮演平台的核心功能，目前已完成MVP版本，支持角色的创建、管理、搜索和向量化存储。

## 已实现功能

### 1. 角色管理 ✅

#### 核心功能
- **角色创建**: 支持创建包含人格、背景、示例台词等信息的角色
- **角色查询**: 支持按ID、名称等条件查询角色
- **角色更新**: 支持修改角色的所有属性
- **角色删除**: 支持软删除（设置is_active=false）
- **角色列表**: 支持分页和过滤查询

#### API接口
- `POST /api/v1/characters/` - 创建角色（需要超级用户权限）
- `GET /api/v1/characters/` - 获取角色列表（支持分页和过滤）
- `GET /api/v1/characters/{character_id}` - 获取角色详情
- `PUT /api/v1/characters/{character_id}` - 更新角色（需要超级用户权限）
- `DELETE /api/v1/characters/{character_id}` - 删除角色（需要超级用户权限）

### 2. 标签系统 ✅

#### 核心功能
- **标签管理**: 支持创建、更新、删除标签
- **标签分类**: 支持为角色添加多个标签进行分类
- **标签搜索**: 支持按标签筛选角色

#### API接口
- `POST /api/v1/characters/tags/` - 创建标签（需要超级用户权限）
- `GET /api/v1/characters/tags/` - 获取标签列表
- `GET /api/v1/characters/tags/{tag_id}` - 获取标签详情
- `PUT /api/v1/characters/tags/{tag_id}` - 更新标签（需要超级用户权限）
- `DELETE /api/v1/characters/tags/{tag_id}` - 删除标签（需要超级用户权限）

### 3. 搜索功能 ✅

#### 核心功能
- **文本搜索**: 基于关键词的模糊匹配，支持在角色名称、简介、人格文本中搜索
- **向量搜索**: 基于语义相似度的智能搜索，使用pgvector扩展
- **混合搜索**: 结合文本搜索和向量搜索的综合搜索

#### API接口
- `GET /api/v1/characters/search` - 搜索角色
  - 参数：`query`（搜索查询）、`search_type`（text/vector/hybrid）、`limit`、`offset`、`tag_ids`、`is_active`

### 4. 向量嵌入 ✅

#### 核心功能
- **多模型支持**: 支持OpenAI和阿里云等多种嵌入模型
- **自动生成**: 创建角色时自动生成向量嵌入
- **模型切换**: 支持运行时切换嵌入模型提供商

#### 支持的模型
- **阿里云 text-embedding-v4**: 1024维度，高质量中文语义理解
- **OpenAI text-embedding-3-small**: 1536维度，多语言支持

## 数据库设计

### 核心表结构

#### 1. 角色表 (characters)
```sql
CREATE TABLE characters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    short_bio VARCHAR(500),
    avatar_url VARCHAR(500),
    persona_text TEXT,
    example_lines JSON,
    source VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### 2. 标签表 (character_tags)
```sql
CREATE TABLE character_tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) UNIQUE NOT NULL,
    description VARCHAR(255),
    color VARCHAR(7),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### 3. 角色-标签关系表 (character_tag_maps)
```sql
CREATE TABLE character_tag_maps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    character_id UUID REFERENCES characters(id),
    tag_id UUID REFERENCES character_tags(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### 4. 角色向量表 (character_embeddings)
```sql
CREATE TABLE character_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    character_id UUID REFERENCES characters(id),
    embedding_type VARCHAR(50), -- 'persona', 'bio', 'combined'
    model_name VARCHAR(100),
    dimension INTEGER,
    embedding VECTOR(1536), -- 使用pgvector扩展
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## 技术实现

### 1. 数据模型
- 使用SQLModel进行ORM映射
- 支持JSON字段存储复杂数据
- 使用pgvector扩展支持向量存储

### 2. 搜索实现
- **文本搜索**: 使用SQL的ILIKE进行模糊匹配
- **向量搜索**: 使用pgvector的余弦相似度计算
- **混合搜索**: 结合文本和向量搜索的加权评分

### 3. 权限控制
- 创建、更新、删除操作需要超级用户权限
- 查询和搜索操作公开访问

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

### 1. 创建角色
```bash
curl -X POST "http://localhost:8000/api/v1/characters/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "苏格拉底",
    "short_bio": "古希腊哲学家，以问答法著称",
    "persona_text": "我是苏格拉底，古希腊的哲学家...",
    "example_lines": ["我知道我什么都不知道", "未经审视的人生不值得过"],
    "source": "古希腊哲学"
  }'
```

### 2. 搜索角色
```bash
# 文本搜索
curl "http://localhost:8000/api/v1/characters/search?query=哲学家&search_type=text&limit=10"

# 向量搜索
curl "http://localhost:8000/api/v1/characters/search?query=古希腊思想家&search_type=vector&limit=10"

# 混合搜索
curl "http://localhost:8000/api/v1/characters/search?query=哲学家&search_type=hybrid&limit=10"
```

### 3. 获取角色列表
```bash
curl "http://localhost:8000/api/v1/characters/?limit=10&offset=0&is_active=true"
```

## 性能优化

### 1. 数据库索引
- 角色名称索引：`CREATE INDEX idx_characters_name ON characters(name);`
- 向量索引：`CREATE INDEX ON character_embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);`

### 2. 分页查询
- 所有列表接口都支持分页
- 默认限制最大100条记录

### 3. 缓存策略
- 角色基本信息可考虑添加缓存
- 向量嵌入结果可缓存

## 测试覆盖

### 1. 单元测试
- 角色CRUD操作测试
- 搜索功能测试
- 标签管理测试

### 2. 集成测试
- API接口测试
- 数据库操作测试
- 权限验证测试

### 3. 性能测试
- 搜索性能测试
- 并发访问测试

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

## 扩展计划

### 短期计划（MVP+）
1. **角色版本管理**: 支持角色配置的版本控制
2. **角色组合**: 支持多角色组合对话
3. **用户偏好**: 支持用户个性化角色设置

### 中期计划
1. **RAG集成**: 集成知识检索增强生成
2. **性能监控**: 添加角色使用统计和性能监控
3. **高级搜索**: 支持多条件组合搜索

### 长期计划
1. **AI优化**: 使用AI自动优化角色配置
2. **社区功能**: 支持角色分享和评价
3. **数据分析**: 角色使用分析和推荐系统

## 总结

当前MVP版本已实现角色管理的核心功能，包括：
- ✅ 完整的CRUD操作
- ✅ 标签系统
- ✅ 多种搜索方式
- ✅ 向量嵌入支持
- ✅ 权限控制
- ✅ 测试覆盖

系统架构清晰，扩展性良好，为后续功能开发奠定了坚实基础。
