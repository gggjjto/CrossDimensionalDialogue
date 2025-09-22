# 角色管理 API 文档

## 概述

`characters.py` 模块提供了完整的角色管理系统，包括角色的创建、查询、更新、删除，以及标签管理、向量嵌入和智能搜索等功能。该模块支持多种搜索方式（文本搜索、向量搜索、混合搜索），并集成了 AI 嵌入模型用于语义搜索。

## 功能列表

### 1. 角色管理
- **创建角色**: 创建新角色并自动生成向量嵌入
- **查询角色**: 支持分页查询和条件过滤
- **获取角色详情**: 根据ID获取单个角色信息
- **更新角色**: 修改角色信息和标签关联
- **删除角色**: 软删除角色（保留数据）

### 2. 标签管理
- **创建标签**: 创建角色分类标签
- **查询标签**: 获取标签列表
- **更新标签**: 修改标签信息
- **删除标签**: 删除标签

### 3. 智能搜索
- **文本搜索**: 基于关键词的模糊搜索
- **向量搜索**: 基于语义相似度的搜索
- **混合搜索**: 结合文本和向量搜索的智能搜索

### 4. 向量嵌入管理
- **生成嵌入**: 为角色生成向量嵌入
- **查询嵌入**: 获取角色的向量嵌入信息
- **删除嵌入**: 清理角色的向量嵌入数据

### 5. 嵌入模型管理
- **模型信息**: 获取当前嵌入模型信息
- **切换提供商**: 动态切换嵌入模型提供商

## API 详细说明

### 1. 角色管理

#### 1.1 创建角色

**端点**: `POST /characters/`

**权限要求**: 需要超级用户权限

**请求体**:
```json
{
  "name": "角色名称",
  "short_bio": "角色简介",
  "avatar_url": "https://example.com/avatar.jpg",
  "persona_text": "角色人格定义（系统prompt）",
  "example_lines": ["示例台词1", "示例台词2"],
  "source": "来源/版权声明",
  "is_active": true,
  "tag_ids": ["tag-uuid-1", "tag-uuid-2"]
}
```

**响应**:
```json
{
  "code": 0,
  "msg": "角色创建成功",
  "data": {
    "id": "character-uuid",
    "name": "角色名称",
    "short_bio": "角色简介",
    "avatar_url": "https://example.com/avatar.jpg",
    "persona_text": "角色人格定义",
    "example_lines": ["示例台词1", "示例台词2"],
    "source": "来源/版权声明",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

**使用示例**:
```bash
curl -X POST "http://localhost:8000/characters/" \
  -H "Authorization: Bearer your_token" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "艾莉",
    "short_bio": "活泼开朗的魔法少女",
    "persona_text": "你是一个活泼开朗的魔法少女，喜欢帮助别人...",
    "example_lines": ["你好！我是艾莉！", "让我来帮助你吧！"],
    "is_active": true
  }'
```

#### 1.2 获取角色列表

**端点**: `GET /characters/`

**请求参数**:
- `skip` (int, optional): 跳过的记录数，默认 0
- `limit` (int, optional): 返回的记录数，默认 100，最大 100
- `is_active` (bool, optional): 是否只返回可用角色
- `tag_ids` (List[UUID], optional): 标签ID过滤

**响应**:
```json
{
  "code": 0,
  "msg": "获取角色列表成功",
  "data": {
    "characters": [
      {
        "id": "character-uuid",
        "name": "角色名称",
        "short_bio": "角色简介",
        "avatar_url": "https://example.com/avatar.jpg",
        "persona_text": "角色人格定义",
        "example_lines": ["示例台词1", "示例台词2"],
        "source": "来源/版权声明",
        "is_active": true,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
      }
    ],
    "total": 1,
    "skip": 0,
    "limit": 100
  }
}
```

**使用示例**:
```bash
curl -X GET "http://localhost:8000/characters/?skip=0&limit=10&is_active=true"
```

#### 1.3 获取角色详情

**端点**: `GET /characters/{character_id}`

**路径参数**:
- `character_id` (UUID): 角色ID

**响应**:
```json
{
  "code": 0,
  "msg": "获取角色详情成功",
  "data": {
    "id": "character-uuid",
    "name": "角色名称",
    "short_bio": "角色简介",
    "avatar_url": "https://example.com/avatar.jpg",
    "persona_text": "角色人格定义",
    "example_lines": ["示例台词1", "示例台词2"],
    "source": "来源/版权声明",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

**使用示例**:
```bash
curl -X GET "http://localhost:8000/characters/character-uuid"
```

#### 1.4 更新角色

**端点**: `PUT /characters/{character_id}`

**权限要求**: 需要超级用户权限

**请求体**:
```json
{
  "name": "更新后的角色名称",
  "short_bio": "更新后的角色简介",
  "persona_text": "更新后的角色人格定义",
  "is_active": false,
  "tag_ids": ["new-tag-uuid"]
}
```

**响应**:
```json
{
  "code": 0,
  "msg": "角色更新成功",
  "data": {
    "id": "character-uuid",
    "name": "更新后的角色名称",
    "short_bio": "更新后的角色简介",
    "persona_text": "更新后的角色人格定义",
    "is_active": false,
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

**使用示例**:
```bash
curl -X PUT "http://localhost:8000/characters/character-uuid" \
  -H "Authorization: Bearer your_token" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "更新后的角色名称",
    "is_active": false
  }'
```

#### 1.5 删除角色

**端点**: `DELETE /characters/{character_id}`

**权限要求**: 需要超级用户权限

**响应**:
```json
{
  "code": 0,
  "msg": "角色删除成功",
  "data": {
    "id": "character-uuid",
    "name": "角色名称",
    "is_active": false,
    "deleted_at": "2024-01-01T00:00:00Z"
  }
}
```

**使用示例**:
```bash
curl -X DELETE "http://localhost:8000/characters/character-uuid" \
  -H "Authorization: Bearer your_token"
```

### 2. 智能搜索

#### 2.1 搜索角色

**端点**: `GET /characters/search`

**请求参数**:
- `query` (string, required): 搜索查询
- `search_type` (string, optional): 搜索类型，可选值：`text`、`vector`、`hybrid`，默认 `text`
- `limit` (int, optional): 返回数量限制，默认 10，最大 100
- `offset` (int, optional): 偏移量，默认 0
- `tag_ids` (List[UUID], optional): 标签过滤
- `is_active` (bool, optional): 是否只搜索可用角色，默认 true

**响应**:
```json
{
  "code": 0,
  "msg": "搜索完成",
  "data": {
    "results": [
      {
        "character": {
          "id": "character-uuid",
          "name": "角色名称",
          "short_bio": "角色简介",
          "persona_text": "角色人格定义",
          "is_active": true
        },
        "score": 0.95,
        "match_type": "vector"
      }
    ],
    "total": 1,
    "query": "搜索关键词",
    "search_type": "vector"
  }
}
```

**使用示例**:
```bash
# 文本搜索
curl -X GET "http://localhost:8000/characters/search?query=魔法少女&search_type=text&limit=5"

# 向量搜索
curl -X GET "http://localhost:8000/characters/search?query=活泼开朗的女孩&search_type=vector&limit=5"

# 混合搜索
curl -X GET "http://localhost:8000/characters/search?query=帮助别人的角色&search_type=hybrid&limit=5"
```

### 3. 标签管理

#### 3.1 创建标签

**端点**: `POST /characters/tags/`

**权限要求**: 需要超级用户权限

**请求体**:
```json
{
  "name": "标签名称",
  "description": "标签描述",
  "color": "#FF5733"
}
```

**响应**:
```json
{
  "code": 0,
  "msg": "标签创建成功",
  "data": {
    "id": "tag-uuid",
    "name": "标签名称",
    "description": "标签描述",
    "color": "#FF5733",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

**使用示例**:
```bash
curl -X POST "http://localhost:8000/characters/tags/" \
  -H "Authorization: Bearer your_token" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "魔法少女",
    "description": "具有魔法能力的少女角色",
    "color": "#FF69B4"
  }'
```

#### 3.2 获取标签列表

**端点**: `GET /characters/tags/`

**请求参数**:
- `skip` (int, optional): 跳过的记录数，默认 0
- `limit` (int, optional): 返回的记录数，默认 100，最大 100

**响应**:
```json
{
  "code": 0,
  "msg": "获取标签列表成功",
  "data": {
    "tags": [
      {
        "id": "tag-uuid",
        "name": "标签名称",
        "description": "标签描述",
        "color": "#FF5733",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
      }
    ],
    "total": 1,
    "skip": 0,
    "limit": 100
  }
}
```

**使用示例**:
```bash
curl -X GET "http://localhost:8000/characters/tags/?skip=0&limit=20"
```

#### 3.3 获取标签详情

**端点**: `GET /characters/tags/{tag_id}`

**路径参数**:
- `tag_id` (UUID): 标签ID

**响应**:
```json
{
  "code": 0,
  "msg": "获取标签详情成功",
  "data": {
    "id": "tag-uuid",
    "name": "标签名称",
    "description": "标签描述",
    "color": "#FF5733",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

**使用示例**:
```bash
curl -X GET "http://localhost:8000/characters/tags/tag-uuid"
```

#### 3.4 更新标签

**端点**: `PUT /characters/tags/{tag_id}`

**权限要求**: 需要超级用户权限

**请求体**:
```json
{
  "name": "更新后的标签名称",
  "description": "更新后的标签描述",
  "color": "#00FF00"
}
```

**响应**:
```json
{
  "code": 0,
  "msg": "标签更新成功",
  "data": {
    "id": "tag-uuid",
    "name": "更新后的标签名称",
    "description": "更新后的标签描述",
    "color": "#00FF00",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

**使用示例**:
```bash
curl -X PUT "http://localhost:8000/characters/tags/tag-uuid" \
  -H "Authorization: Bearer your_token" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "更新后的标签名称",
    "color": "#00FF00"
  }'
```

#### 3.5 删除标签

**端点**: `DELETE /characters/tags/{tag_id}`

**权限要求**: 需要超级用户权限

**响应**:
```json
{
  "code": 0,
  "msg": "标签删除成功",
  "data": {
    "id": "tag-uuid",
    "name": "标签名称",
    "deleted_at": "2024-01-01T00:00:00Z"
  }
}
```

**使用示例**:
```bash
curl -X DELETE "http://localhost:8000/characters/tags/tag-uuid" \
  -H "Authorization: Bearer your_token"
```

### 4. 向量嵌入管理

#### 4.1 生成角色向量嵌入

**端点**: `POST /characters/{character_id}/embeddings/generate`

**权限要求**: 需要超级用户权限

**路径参数**:
- `character_id` (UUID): 角色ID

**响应**:
```json
{
  "code": 0,
  "msg": "向量嵌入生成成功",
  "data": [
    {
      "id": "embedding-uuid",
      "character_id": "character-uuid",
      "embedding_type": "persona",
      "model_name": "text-embedding-ada-002",
      "dimension": 1536,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

**使用示例**:
```bash
curl -X POST "http://localhost:8000/characters/character-uuid/embeddings/generate" \
  -H "Authorization: Bearer your_token"
```

#### 4.2 获取角色向量嵌入

**端点**: `GET /characters/{character_id}/embeddings`

**路径参数**:
- `character_id` (UUID): 角色ID

**请求参数**:
- `embedding_type` (string, optional): 嵌入类型过滤

**响应**:
```json
{
  "code": 0,
  "msg": "获取向量嵌入成功",
  "data": [
    {
      "id": "embedding-uuid",
      "character_id": "character-uuid",
      "embedding_type": "persona",
      "model_name": "text-embedding-ada-002",
      "dimension": 1536,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

**使用示例**:
```bash
curl -X GET "http://localhost:8000/characters/character-uuid/embeddings?embedding_type=persona"
```

#### 4.3 删除角色向量嵌入

**端点**: `DELETE /characters/{character_id}/embeddings`

**权限要求**: 需要超级用户权限

**路径参数**:
- `character_id` (UUID): 角色ID

**请求参数**:
- `embedding_type` (string, optional): 嵌入类型过滤

**响应**:
```json
{
  "code": 0,
  "msg": "向量嵌入删除成功",
  "data": {
    "deleted_count": 2
  }
}
```

**使用示例**:
```bash
curl -X DELETE "http://localhost:8000/characters/character-uuid/embeddings?embedding_type=persona" \
  -H "Authorization: Bearer your_token"
```

### 5. 嵌入模型管理

#### 5.1 获取嵌入模型信息

**端点**: `GET /characters/embeddings/model-info`

**权限要求**: 需要超级用户权限

**响应**:
```json
{
  "code": 0,
  "msg": "获取模型信息成功",
  "data": {
    "provider": "openai",
    "model_name": "text-embedding-ada-002",
    "dimension": 1536,
    "max_tokens": 8191,
    "status": "active"
  }
}
```

**使用示例**:
```bash
curl -X GET "http://localhost:8000/characters/embeddings/model-info" \
  -H "Authorization: Bearer your_token"
```

#### 5.2 切换嵌入模型提供商

**端点**: `POST /characters/embeddings/switch-provider`

**权限要求**: 需要超级用户权限

**请求参数**:
- `provider` (string, required): 提供商名称，可选值：`openai`、`aliyun`

**响应**:
```json
{
  "code": 0,
  "msg": "已切换到 aliyun 提供商",
  "data": {
    "provider": "aliyun",
    "model_name": "text-embedding-v1",
    "dimension": 1536,
    "max_tokens": 2048,
    "status": "active"
  }
}
```

**使用示例**:
```bash
curl -X POST "http://localhost:8000/characters/embeddings/switch-provider?provider=aliyun" \
  -H "Authorization: Bearer your_token"
```

## 搜索类型说明

### 1. 文本搜索 (text)
- 基于关键词的模糊匹配
- 搜索角色名称、简介、人格定义等文本字段
- 适合精确关键词搜索

### 2. 向量搜索 (vector)
- 基于语义相似度的搜索
- 将查询文本转换为向量，与角色向量进行相似度计算
- 适合语义相关搜索

### 3. 混合搜索 (hybrid)
- 结合文本搜索和向量搜索的结果
- 提供更全面的搜索结果
- 适合复杂查询场景

## 错误处理

### 常见错误码
- `400 Bad Request`: 请求参数错误或业务逻辑错误
- `401 Unauthorized`: 未授权访问
- `403 Forbidden`: 权限不足
- `404 Not Found`: 资源不存在
- `422 Unprocessable Entity`: 请求数据验证失败
- `500 Internal Server Error`: 服务器内部错误

### 错误响应格式
```json
{
  "code": 400,
  "msg": "错误描述信息",
  "data": null
}
```

## 权限说明

### 公开接口
- 获取角色列表
- 获取角色详情
- 搜索角色
- 获取标签列表
- 获取标签详情
- 获取角色向量嵌入

### 需要超级用户权限的接口
- 创建角色
- 更新角色
- 删除角色
- 创建标签
- 更新标签
- 删除标签
- 生成角色向量嵌入
- 删除角色向量嵌入
- 获取嵌入模型信息
- 切换嵌入模型提供商

## 最佳实践

### 1. 角色管理
- 创建角色时提供完整的角色信息
- 使用有意义的角色名称和简介
- 合理设置角色标签便于分类管理
- 定期更新角色信息保持数据新鲜度

### 2. 搜索优化
- 根据查询需求选择合适的搜索类型
- 使用标签过滤缩小搜索范围
- 合理设置搜索限制和偏移量
- 利用混合搜索获得最佳结果

### 3. 向量嵌入
- 定期为角色生成向量嵌入
- 选择合适的嵌入模型提供商
- 监控嵌入生成的成功率
- 及时清理无效的嵌入数据

### 4. 性能优化
- 使用分页查询避免一次性加载大量数据
- 合理使用缓存减少重复计算
- 定期清理软删除的数据
- 监控API响应时间

## 依赖关系

该模块依赖以下组件：
- `app.crud.character`: 角色数据操作
- `app.crud.character_embedding`: 向量嵌入数据操作
- `app.services.embedding_service`: 嵌入服务
- `app.models.character`: 角色相关数据模型
- `app.utils.response`: 统一响应格式
- `app.api.deps`: 依赖注入和权限控制

## 测试建议

### 单元测试
- 测试各种CRUD操作
- 测试搜索功能的不同类型
- 测试权限控制
- 测试数据验证

### 集成测试
- 测试完整的角色管理流程
- 测试向量嵌入生成和搜索
- 测试标签关联功能
- 测试模型切换功能

### 性能测试
- 测试大量数据的查询性能
- 测试向量搜索的响应时间
- 测试并发访问的处理能力
- 测试内存使用情况
