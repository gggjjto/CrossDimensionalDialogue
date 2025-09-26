# 角色管理 API 文档

## 概述

角色管理模块是大黄鸭项目的核心功能之一，提供了完整的AI角色管理系统。该模块不仅支持角色的基础CRUD操作，还集成了先进的AI技术，包括向量嵌入、智能搜索、AI图片生成等功能，为用户提供丰富多样的AI角色交互体验。

## 核心功能

### 🎭 角色管理系统
- **角色创建**: 支持创建具有完整人格设定的AI角色
- **角色管理**: 提供角色的查询、更新、删除等基础管理功能
- **角色分类**: 通过标签系统对角色进行分类管理
- **角色搜索**: 支持多种搜索方式快速找到目标角色

### 🔍 智能搜索系统
- **文本搜索**: 基于关键词的模糊搜索，支持角色名称、简介等字段
- **向量搜索**: 基于语义相似度的智能搜索，理解用户意图
- **混合搜索**: 结合文本和向量搜索，提供最精准的搜索结果
- **过滤功能**: 支持按标签、状态等条件进行精确过滤

### 🎨 AI图片生成系统
- **自动生成**: 创建角色时自动生成AI形象图片
- **手动生成**: 为现有角色重新生成形象图片
- **多风格支持**: 支持写实、动漫、卡通、艺术等多种风格
- **多尺寸支持**: 支持多种图片尺寸，适应不同使用场景

### 🏷️ 标签管理系统
- **标签创建**: 创建角色分类标签
- **标签管理**: 支持标签的增删改查操作
- **标签关联**: 角色与标签的多对多关联关系
- **标签过滤**: 基于标签进行角色筛选

### 🧠 向量嵌入系统
- **自动嵌入**: 角色创建时自动生成向量嵌入
- **语义搜索**: 基于向量嵌入的语义相似度搜索
- **智能推荐**: 基于向量相似度的角色推荐
- **性能优化**: 高效的向量存储和检索机制

## 可以实现的功能

### 🎯 用户端功能

#### 1. 角色浏览与发现
- **角色列表**: 浏览所有可用的AI角色
- **角色详情**: 查看角色的完整信息和设定
- **智能搜索**: 通过关键词或语义搜索找到合适的角色
- **标签筛选**: 通过标签快速筛选特定类型的角色

#### 2. 角色交互
- **角色选择**: 选择喜欢的角色进行对话
- **角色定制**: 根据个人喜好调整角色设定
- **角色收藏**: 收藏喜欢的角色便于后续使用
- **角色分享**: 与朋友分享有趣的AI角色

#### 3. 个性化体验
- **角色推荐**: 基于用户偏好推荐相似角色
- **历史记录**: 查看与角色的对话历史
- **角色评价**: 对角色进行评分和反馈
- **个人角色**: 创建和管理个人专属角色

### 🛠️ 管理员功能

#### 1. 角色管理
- **角色审核**: 审核用户创建的角色内容
- **角色编辑**: 修改和优化角色设定
- **角色分类**: 管理角色标签和分类
- **角色统计**: 查看角色使用情况和受欢迎程度

#### 2. 内容管理
- **标签管理**: 创建和管理角色分类标签
- **内容审核**: 确保角色内容符合平台规范
- **质量监控**: 监控角色生成质量和用户反馈
- **系统优化**: 优化搜索算法和推荐系统

#### 3. 系统监控
- **使用统计**: 监控角色使用频率和用户活跃度
- **性能监控**: 监控系统性能和响应时间
- **错误处理**: 处理系统错误和用户反馈
- **数据备份**: 定期备份角色数据和配置

### 🔧 开发者功能

#### 1. API集成
- **RESTful接口**: 标准的REST API接口
- **数据验证**: 自动的数据格式验证
- **错误处理**: 完善的错误码和错误信息
- **文档支持**: 自动生成的API文档

#### 2. 扩展功能
- **自定义字段**: 支持添加自定义角色属性
- **插件系统**: 支持第三方插件扩展功能
- **API版本**: 支持API版本管理和向后兼容
- **批量操作**: 支持批量创建和管理角色

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

### 4. AI图片生成
- **生成角色形象**: 为角色生成AI形象图片
- **图片风格管理**: 支持多种图片风格和尺寸
- **图片验证**: 验证角色头像图片的有效性

### 5. 向量嵌入管理
- **生成嵌入**: 为角色生成向量嵌入
- **查询嵌入**: 获取角色的向量嵌入信息
- **删除嵌入**: 清理角色的向量嵌入数据

## 业务场景应用

### 🎮 游戏与娱乐
- **虚拟角色**: 为游戏创建具有独特个性的NPC角色
- **互动故事**: 构建交互式故事中的角色设定
- **虚拟偶像**: 创建虚拟偶像角色进行粉丝互动
- **角色扮演**: 支持用户创建自定义角色进行角色扮演

### 📚 教育与培训
- **教学助手**: 创建不同学科的专业教学助手
- **语言学习**: 设计语言学习伙伴角色
- **历史人物**: 重现历史人物进行历史教学
- **技能培训**: 创建专业技能培训师角色

### 🏢 企业服务
- **客服助手**: 创建专业的客服代表角色
- **销售顾问**: 设计不同领域的销售顾问角色
- **技术支持**: 创建技术专家角色提供技术支持
- **品牌代言**: 为企业创建品牌代言角色

### 🎨 创意内容
- **内容创作**: 为小说、剧本创作提供角色灵感
- **艺术设计**: 为艺术作品提供角色设计参考
- **动画制作**: 为动画项目创建角色原型
- **虚拟主播**: 创建虚拟主播进行内容直播

### 🧠 心理健康
- **心理咨询**: 创建心理咨询师角色提供心理支持
- **情感陪伴**: 设计情感陪伴角色缓解孤独感
- **正念练习**: 创建冥想指导师角色
- **康复辅助**: 为康复患者提供鼓励和支持角色

## API 详细说明

### 1. 角色管理

#### 1.1 创建角色

**端点**: `POST /characters/`

**权限要求**: 需要用户权限

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

### 5. AI图片生成

#### 5.1 生成角色AI形象图片

**端点**: `POST /characters/{character_id}/generate-image`

**权限要求**: 需要用户权限

**请求参数**:
- `character_id` (路径参数): 角色ID (UUID)
- `style` (查询参数, 可选): 图片风格，默认 "realistic"
- `size` (查询参数, 可选): 图片尺寸，默认 "720*1280"

**支持的风格**:
- `realistic`: 写实风格
- `anime`: 动漫风格
- `cartoon`: 卡通风格
- `artistic`: 艺术风格

**支持的尺寸**:
- `720*1280`: 竖屏手机尺寸
- `1024*1024`: 正方形
- `1280*720`: 横屏尺寸
- `512*512`: 小尺寸正方形

**响应**:
```json
{
  "code": 0,
  "msg": "AI形象图片生成成功",
  "data": {
    "character_id": "uuid",
    "avatar_url": "https://example.com/character-avatar.jpg",
    "style": "realistic",
    "size": "720*1280"
  }
}
```

**使用示例**:
```bash
curl -X POST "http://localhost:8000/characters/123e4567-e89b-12d3-a456-426614174000/generate-image?style=anime&size=1024*1024" \
  -H "Authorization: Bearer your_token"
```

#### 5.2 获取支持的图片风格

**端点**: `GET /characters/image-generation/styles`

**权限要求**: 无需认证

**响应**:
```json
{
  "code": 0,
  "msg": "获取图片风格成功",
  "data": [
    {
      "name": "realistic",
      "display_name": "写实风格",
      "description": "真实感强的图片风格"
    },
    {
      "name": "anime",
      "display_name": "动漫风格", 
      "description": "二次元动漫风格"
    }
  ]
}
```

#### 5.3 获取支持的图片尺寸

**端点**: `GET /characters/image-generation/sizes`

**权限要求**: 无需认证

**响应**:
```json
{
  "code": 0,
  "msg": "获取图片尺寸成功",
  "data": [
    {
      "name": "720*1280",
      "display_name": "竖屏手机",
      "description": "适合手机屏幕的竖屏尺寸"
    },
    {
      "name": "1024*1024",
      "display_name": "正方形",
      "description": "1:1比例的正方形图片"
    }
  ]
}
```

#### 5.4 验证角色头像图片

**端点**: `POST /characters/{character_id}/validate-image`

**权限要求**: 需要用户权限

**请求参数**:
- `character_id` (路径参数): 角色ID (UUID)

**响应**:
```json
{
  "code": 0,
  "msg": "图片验证完成",
  "data": {
    "character_id": "uuid",
    "avatar_url": "https://example.com/character-avatar.jpg",
    "is_valid": true
  }
}
```

### 6. 嵌入模型管理

#### 6.1 获取嵌入模型信息

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

## 技术特性

### 🔒 安全特性
- **权限控制**: 基于角色的访问控制，确保数据安全
- **数据验证**: 自动的数据格式验证和类型检查
- **输入过滤**: 防止恶意输入和SQL注入攻击
- **软删除**: 支持软删除机制，保护重要数据

### ⚡ 性能特性
- **向量索引**: 高效的向量存储和检索机制
- **缓存支持**: 支持Redis缓存提高响应速度
- **分页查询**: 支持大数据量的分页查询
- **异步处理**: 支持异步生成向量嵌入和AI图片

### 🔧 开发特性
- **RESTful API**: 标准的REST接口设计
- **自动文档**: 自动生成的API文档和示例
- **错误处理**: 完善的错误处理和用户反馈
- **数据模型**: 清晰的数据模型和关系定义

### 🎨 AI特性
- **智能搜索**: 基于语义理解的智能搜索
- **向量嵌入**: 支持多种嵌入模型和提供商
- **AI图片生成**: 集成AI图片生成服务
- **个性化推荐**: 基于用户行为的智能推荐

## 总结

角色管理模块是大黄鸭项目的核心功能，通过集成先进的AI技术，为用户提供了丰富多样的AI角色交互体验。无论是游戏娱乐、教育培训、企业服务还是创意内容，都能找到合适的应用场景。

**核心优势**:
- ✅ 完整的角色生命周期管理
- ✅ 先进的AI技术集成
- ✅ 灵活的搜索和推荐系统
- ✅ 丰富的业务场景支持
- ✅ 高性能和可扩展的架构设计
