# 会话管理 API 文档

## 概述

`conversations.py` 模块提供了完整的会话管理系统，包括会话的创建、查询、更新、删除，以及消息管理、实时通信、语音支持等功能。该模块支持多模态消息、实时WebSocket通信，并集成了限流和权限控制机制。

## 功能列表

### 1. 会话管理
- **创建会话**: 创建新会话并关联角色
- **查询会话**: 支持分页查询和条件过滤
- **获取会话详情**: 根据ID获取单个会话信息
- **更新会话**: 修改会话信息和设置
- **删除会话**: 软删除会话（保留数据）

### 2. 消息管理
- **发送消息**: 发送文本、语音、图片消息
- **获取消息列表**: 支持分页和过滤的消息查询
- **获取消息详情**: 根据ID获取单个消息信息
- **更新消息**: 修改消息内容或状态
- **删除消息**: 删除指定消息

### 3. 实时通信
- **WebSocket连接**: 实时双向消息传输
- **消息搜索**: 在会话中搜索特定消息
- **消息确认**: 消息发送状态跟踪

### 4. 语音支持
- **语音上传**: 上传语音文件并转换为文本
- **语音回复**: 生成角色语音回复
- **音频管理**: 音频文件存储和访问

### 5. 会话分析
- **会话统计**: 获取会话数据统计
- **数据导出**: 导出会话数据
- **情感分析**: 消息情感分析

## API 详细说明

### 1. 会话管理

#### 1.1 创建会话

**端点**: `POST /api/v1/conversations/`

**权限要求**: 需要用户认证

**请求体**:
```json
{
  "character_id": "character-uuid",
  "title": "与苏格拉底的哲学对话",
  "description": "讨论哲学问题的深度对话",
  "settings": {
    "temperature": 0.7,
    "max_tokens": 2000,
    "voice_enabled": true
  }
}
```

**响应**:
```json
{
  "code": 0,
  "msg": "会话创建成功",
  "data": {
    "id": "conversation-uuid",
    "user_id": "user-uuid",
    "character_id": "character-uuid",
    "title": "与苏格拉底的哲学对话",
    "description": "讨论哲学问题的深度对话",
    "status": "active",
    "settings": {
      "temperature": 0.7,
      "max_tokens": 2000,
      "voice_enabled": true
    },
    "message_count": 0,
    "last_message_at": null,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

**使用示例**:
```bash
curl -X POST "http://localhost:8000/api/v1/conversations/" \
  -H "Authorization: Bearer your_token" \
  -H "Content-Type: application/json" \
  -d '{
    "character_id": "character-uuid",
    "title": "与苏格拉底的哲学对话",
    "settings": {
      "temperature": 0.7,
      "voice_enabled": true
    }
  }'
```

#### 1.2 获取会话列表

**端点**: `GET /api/v1/conversations/`

**请求参数**:
- `skip` (int, optional): 跳过的记录数，默认 0
- `limit` (int, optional): 返回的记录数，默认 20，最大 100
- `status` (str, optional): 会话状态过滤，可选值：active/paused/ended/archived
- `character_id` (UUID, optional): 角色ID过滤
- `order_by` (str, optional): 排序字段，可选值：created_at/last_message_at，默认 last_message_at
- `order` (str, optional): 排序方向，可选值：asc/desc，默认 desc

**响应**:
```json
{
  "code": 0,
  "msg": "获取会话列表成功",
  "data": {
    "conversations": [
      {
        "id": "conversation-uuid",
        "title": "与苏格拉底的哲学对话",
        "description": "讨论哲学问题的深度对话",
        "status": "active",
        "message_count": 15,
        "last_message_at": "2024-01-01T12:00:00Z",
        "character": {
          "id": "character-uuid",
          "name": "苏格拉底",
          "short_bio": "古希腊哲学家",
          "avatar_url": "https://example.com/socrates.jpg"
        },
        "created_at": "2024-01-01T10:00:00Z",
        "updated_at": "2024-01-01T12:00:00Z"
      }
    ],
    "total": 1,
    "skip": 0,
    "limit": 20
  }
}
```

**使用示例**:
```bash
curl -X GET "http://localhost:8000/api/v1/conversations/?skip=0&limit=10&status=active&order_by=last_message_at&order=desc"
```

#### 1.3 获取会话详情

**端点**: `GET /api/v1/conversations/{conversation_id}`

**路径参数**:
- `conversation_id` (UUID): 会话ID

**响应**:
```json
{
  "code": 0,
  "msg": "获取会话详情成功",
  "data": {
    "id": "conversation-uuid",
    "title": "与苏格拉底的哲学对话",
    "description": "讨论哲学问题的深度对话",
    "status": "active",
    "settings": {
      "temperature": 0.7,
      "max_tokens": 2000,
      "voice_enabled": true
    },
    "message_count": 15,
    "last_message_at": "2024-01-01T12:00:00Z",
    "character": {
      "id": "character-uuid",
      "name": "苏格拉底",
      "short_bio": "古希腊哲学家",
      "avatar_url": "https://example.com/socrates.jpg",
      "persona_text": "你是一个古希腊哲学家苏格拉底..."
    },
    "created_at": "2024-01-01T10:00:00Z",
    "updated_at": "2024-01-01T12:00:00Z"
  }
}
```

**使用示例**:
```bash
curl -X GET "http://localhost:8000/api/v1/conversations/conversation-uuid"
```

#### 1.4 更新会话

**端点**: `PUT /api/v1/conversations/{conversation_id}`

**权限要求**: 需要用户认证且为会话所有者

**请求体**:
```json
{
  "title": "更新后的会话标题",
  "description": "更新后的描述",
  "status": "paused",
  "settings": {
    "temperature": 0.8,
    "voice_enabled": false
  }
}
```

**响应**:
```json
{
  "code": 0,
  "msg": "会话更新成功",
  "data": {
    "id": "conversation-uuid",
    "title": "更新后的会话标题",
    "description": "更新后的描述",
    "status": "paused",
    "settings": {
      "temperature": 0.8,
      "voice_enabled": false
    },
    "updated_at": "2024-01-01T12:30:00Z"
  }
}
```

**使用示例**:
```bash
curl -X PUT "http://localhost:8000/api/v1/conversations/conversation-uuid" \
  -H "Authorization: Bearer your_token" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "更新后的会话标题",
    "status": "paused"
  }'
```

#### 1.5 删除会话

**端点**: `DELETE /api/v1/conversations/{conversation_id}`

**权限要求**: 需要用户认证且为会话所有者

**响应**:
```json
{
  "code": 0,
  "msg": "会话删除成功",
  "data": {
    "id": "conversation-uuid",
    "title": "与苏格拉底的哲学对话",
    "deleted_at": "2024-01-01T12:00:00Z"
  }
}
```

**使用示例**:
```bash
curl -X DELETE "http://localhost:8000/api/v1/conversations/conversation-uuid" \
  -H "Authorization: Bearer your_token"
```

### 2. 消息管理

#### 2.1 发送消息

**端点**: `POST /api/v1/conversations/{conversation_id}/messages`

**权限要求**: 需要用户认证且为会话所有者

**请求体**:
```json
{
  "content": "你好，苏格拉底！我想和你讨论哲学问题。",
  "content_type": "text",
  "parent_id": null
}
```

**响应**:
```json
{
  "code": 0,
  "msg": "消息发送成功",
  "data": {
    "id": "message-uuid",
    "conversation_id": "conversation-uuid",
    "sender_type": "user",
    "sender_id": "user-uuid",
    "content": "你好，苏格拉底！我想和你讨论哲学问题。",
    "content_type": "text",
    "status": "sent",
    "parent_id": null,
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-01-01T12:00:00Z"
  }
}
```

**使用示例**:
```bash
curl -X POST "http://localhost:8000/api/v1/conversations/conversation-uuid/messages" \
  -H "Authorization: Bearer your_token" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "你好，苏格拉底！我想和你讨论哲学问题。",
    "content_type": "text"
  }'
```

#### 2.2 获取消息列表

**端点**: `GET /api/v1/conversations/{conversation_id}/messages`

**权限要求**: 需要用户认证且为会话所有者

**请求参数**:
- `skip` (int, optional): 跳过的记录数，默认 0
- `limit` (int, optional): 返回的记录数，默认 50，最大 200
- `sender_type` (str, optional): 发送者类型过滤，可选值：user/character/system
- `content_type` (str, optional): 内容类型过滤，可选值：text/audio/image
- `since` (datetime, optional): 获取此时间之后的消息
- `until` (datetime, optional): 获取此时间之前的消息

**响应**:
```json
{
  "code": 0,
  "msg": "获取消息列表成功",
  "data": {
    "messages": [
      {
        "id": "message-uuid-1",
        "sender_type": "user",
        "sender_id": "user-uuid",
        "content": "你好，苏格拉底！",
        "content_type": "text",
        "status": "sent",
        "parent_id": null,
        "created_at": "2024-01-01T12:00:00Z"
      },
      {
        "id": "message-uuid-2",
        "sender_type": "character",
        "sender_id": "character-uuid",
        "content": "你好！很高兴见到你。你想讨论什么哲学问题呢？",
        "content_type": "text",
        "status": "sent",
        "parent_id": "message-uuid-1",
        "created_at": "2024-01-01T12:01:00Z"
      }
    ],
    "total": 2,
    "skip": 0,
    "limit": 50
  }
}
```

**使用示例**:
```bash
curl -X GET "http://localhost:8000/api/v1/conversations/conversation-uuid/messages?skip=0&limit=20&sender_type=user"
```

#### 2.3 获取消息详情

**端点**: `GET /api/v1/conversations/{conversation_id}/messages/{message_id}`

**权限要求**: 需要用户认证且为会话所有者

**响应**:
```json
{
  "code": 0,
  "msg": "获取消息详情成功",
  "data": {
    "id": "message-uuid",
    "conversation_id": "conversation-uuid",
    "sender_type": "user",
    "sender_id": "user-uuid",
    "content": "你好，苏格拉底！",
    "content_type": "text",
    "status": "sent",
    "parent_id": null,
    "metadata": {
      "length": 8,
      "language": "zh-CN"
    },
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-01-01T12:00:00Z"
  }
}
```

**使用示例**:
```bash
curl -X GET "http://localhost:8000/api/v1/conversations/conversation-uuid/messages/message-uuid"
```

#### 2.4 更新消息

**端点**: `PUT /api/v1/conversations/{conversation_id}/messages/{message_id}`

**权限要求**: 需要用户认证且为消息发送者

**请求体**:
```json
{
  "content": "更新后的消息内容",
  "status": "sent"
}
```

**响应**:
```json
{
  "code": 0,
  "msg": "消息更新成功",
  "data": {
    "id": "message-uuid",
    "content": "更新后的消息内容",
    "status": "sent",
    "updated_at": "2024-01-01T12:30:00Z"
  }
}
```

**使用示例**:
```bash
curl -X PUT "http://localhost:8000/api/v1/conversations/conversation-uuid/messages/message-uuid" \
  -H "Authorization: Bearer your_token" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "更新后的消息内容"
  }'
```

#### 2.5 删除消息

**端点**: `DELETE /api/v1/conversations/{conversation_id}/messages/{message_id}`

**权限要求**: 需要用户认证且为消息发送者

**响应**:
```json
{
  "code": 0,
  "msg": "消息删除成功",
  "data": {
    "id": "message-uuid",
    "deleted_at": "2024-01-01T12:00:00Z"
  }
}
```

**使用示例**:
```bash
curl -X DELETE "http://localhost:8000/api/v1/conversations/conversation-uuid/messages/message-uuid" \
  -H "Authorization: Bearer your_token"
```

### 3. 实时通信

#### 3.1 WebSocket连接

**端点**: `WS /api/v1/conversations/{conversation_id}/ws`

**连接参数**:
- `token`: 认证令牌
- `user_id`: 用户ID

**消息格式**:
```json
{
  "type": "message",
  "data": {
    "content": "消息内容",
    "content_type": "text",
    "parent_id": null
  }
}
```

**响应格式**:
```json
{
  "type": "message",
  "data": {
    "id": "message-uuid",
    "sender_type": "character",
    "content": "角色回复内容",
    "content_type": "text",
    "status": "sent",
    "created_at": "2024-01-01T12:00:00Z"
  }
}
```

#### 3.2 消息搜索

**端点**: `GET /api/v1/conversations/{conversation_id}/search`

**权限要求**: 需要用户认证且为会话所有者

**请求参数**:
- `query` (str, required): 搜索关键词
- `sender_type` (str, optional): 发送者类型过滤
- `content_type` (str, optional): 内容类型过滤
- `date_from` (datetime, optional): 开始日期
- `date_to` (datetime, optional): 结束日期
- `limit` (int, optional): 返回数量限制，默认 20，最大 100

**响应**:
```json
{
  "code": 0,
  "msg": "搜索完成",
  "data": {
    "results": [
      {
        "id": "message-uuid",
        "sender_type": "user",
        "content": "包含关键词的消息内容",
        "content_type": "text",
        "created_at": "2024-01-01T12:00:00Z",
        "highlight": "包含<em>关键词</em>的消息内容"
      }
    ],
    "total": 1,
    "query": "关键词"
  }
}
```

**使用示例**:
```bash
curl -X GET "http://localhost:8000/api/v1/conversations/conversation-uuid/search?query=哲学&sender_type=user&limit=10"
```

### 4. 语音支持

#### 4.1 上传语音文件

**端点**: `POST /api/v1/conversations/{conversation_id}/audio`

**权限要求**: 需要用户认证且为会话所有者

**请求体**: multipart/form-data
- `audio_file`: 音频文件（支持格式：mp3, wav, m4a）
- `duration`: 音频时长（秒，可选）

**响应**:
```json
{
  "code": 0,
  "msg": "语音文件上传成功",
  "data": {
    "id": "message-uuid",
    "conversation_id": "conversation-uuid",
    "sender_type": "user",
    "content": "转换后的文本内容",
    "content_type": "audio",
    "audio_url": "https://example.com/audio/message-uuid.mp3",
    "audio_duration": 15,
    "status": "sent",
    "created_at": "2024-01-01T12:00:00Z"
  }
}
```

**使用示例**:
```bash
curl -X POST "http://localhost:8000/api/v1/conversations/conversation-uuid/audio" \
  -H "Authorization: Bearer your_token" \
  -F "audio_file=@voice_message.mp3" \
  -F "duration=15"
```

#### 4.2 获取语音回复

**端点**: `GET /api/v1/conversations/{conversation_id}/messages/{message_id}/audio`

**权限要求**: 需要用户认证且为会话所有者

**响应**:
```json
{
  "code": 0,
  "msg": "获取语音回复成功",
  "data": {
    "id": "message-uuid",
    "audio_url": "https://example.com/audio/character-reply-uuid.mp3",
    "audio_duration": 20,
    "content": "角色回复的文本内容",
    "created_at": "2024-01-01T12:00:00Z"
  }
}
```

**使用示例**:
```bash
curl -X GET "http://localhost:8000/api/v1/conversations/conversation-uuid/messages/message-uuid/audio" \
  -H "Authorization: Bearer your_token"
```

### 5. 会话分析

#### 5.1 获取会话统计

**端点**: `GET /api/v1/conversations/{conversation_id}/stats`

**权限要求**: 需要用户认证且为会话所有者

**响应**:
```json
{
  "code": 0,
  "msg": "获取会话统计成功",
  "data": {
    "total_messages": 50,
    "user_messages": 25,
    "character_messages": 25,
    "total_duration": 3600,
    "average_message_length": 45,
    "message_types": {
      "text": 40,
      "audio": 8,
      "image": 2
    },
    "topics": ["哲学", "道德", "知识"],
    "sentiment_analysis": {
      "positive": 0.6,
      "neutral": 0.3,
      "negative": 0.1
    },
    "activity_timeline": [
      {
        "date": "2024-01-01",
        "message_count": 15
      }
    ]
  }
}
```

**使用示例**:
```bash
curl -X GET "http://localhost:8000/api/v1/conversations/conversation-uuid/stats" \
  -H "Authorization: Bearer your_token"
```

#### 5.2 导出会话数据

**端点**: `GET /api/v1/conversations/{conversation_id}/export`

**权限要求**: 需要用户认证且为会话所有者

**请求参数**:
- `format` (str, optional): 导出格式，可选值：json/csv/txt，默认 json
- `include_metadata` (bool, optional): 是否包含元数据，默认 false
- `date_from` (datetime, optional): 开始日期
- `date_to` (datetime, optional): 结束日期

**响应**:
```json
{
  "code": 0,
  "msg": "导出成功",
  "data": {
    "download_url": "https://example.com/exports/conversation-uuid.json",
    "file_size": 1024000,
    "expires_at": "2024-01-02T00:00:00Z"
  }
}
```

**使用示例**:
```bash
curl -X GET "http://localhost:8000/api/v1/conversations/conversation-uuid/export?format=json&include_metadata=true" \
  -H "Authorization: Bearer your_token"
```

## 错误处理

### 常见错误码
- `400 Bad Request`: 请求参数错误或业务逻辑错误
- `401 Unauthorized`: 未授权访问
- `403 Forbidden`: 权限不足
- `404 Not Found`: 资源不存在
- `422 Unprocessable Entity`: 请求数据验证失败
- `429 Too Many Requests`: 请求频率超限
- `500 Internal Server Error`: 服务器内部错误

### 错误响应格式
```json
{
  "code": 400,
  "msg": "错误描述信息",
  "data": null,
  "details": {
    "field": "具体字段错误信息"
  }
}
```

## 权限说明

### 公开接口
- 无（所有接口都需要认证）

### 需要用户认证的接口
- 所有会话和消息管理接口
- 需要验证用户身份和会话所有权

### 权限验证规则
- 用户只能访问自己的会话
- 用户只能操作自己发送的消息
- 管理员可以访问所有会话（可选）

## 限流策略

### 用户限制
- 每日消息数限制：1000条
- 每小时消息数限制：100条
- 最大并发会话数：10个
- 单次消息长度限制：5000字符

### 系统限制
- API请求频率：每分钟100次
- WebSocket连接数：每用户最多5个
- 文件上传大小：50MB
- 语音文件时长：最长5分钟

## 最佳实践

### 1. 会话管理
- 合理设置会话标题便于识别
- 定期清理不活跃的会话
- 使用会话标签进行分类管理
- 合理配置会话设置参数

### 2. 消息处理
- 使用分页查询避免一次性加载大量消息
- 合理设置消息长度限制
- 及时处理消息状态更新
- 使用消息确认机制保证可靠性

### 3. 实时通信
- 实现断线重连机制
- 使用心跳检测连接状态
- 合理处理消息队列
- 实现消息去重机制

### 4. 语音处理
- 支持多种音频格式
- 实现音频质量检测
- 使用CDN加速音频文件访问
- 定期清理过期的音频文件

### 5. 性能优化
- 使用缓存减少数据库查询
- 实现消息批量处理
- 使用异步处理提高响应速度
- 监控系统性能指标

## 依赖关系

该模块依赖以下组件：
- `app.crud.conversation`: 会话数据操作
- `app.crud.message`: 消息数据操作
- `app.services.websocket_service`: WebSocket服务
- `app.services.audio_service`: 语音处理服务
- `app.services.llm_service`: LLM服务
- `app.models.conversation`: 会话相关数据模型
- `app.utils.response`: 统一响应格式
- `app.api.deps`: 依赖注入和权限控制

## 测试建议

### 单元测试
- 测试各种CRUD操作
- 测试权限控制逻辑
- 测试数据验证
- 测试限流机制

### 集成测试
- 测试完整的会话管理流程
- 测试WebSocket通信
- 测试语音处理功能
- 测试消息搜索功能

### 性能测试
- 测试大量消息的处理性能
- 测试并发用户访问
- 测试WebSocket连接稳定性
- 测试文件上传性能

### 安全测试
- 测试权限绕过漏洞
- 测试SQL注入防护
- 测试文件上传安全
- 测试XSS防护
