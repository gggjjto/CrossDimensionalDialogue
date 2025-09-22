# 会话管理服务详细设计

## 概述

会话管理服务是AI角色扮演平台的核心组件，负责管理用户与AI角色之间的对话会话，包括会话生命周期管理、消息存储、上下文维护、多模态支持等功能。

## 功能设计

### 1. 会话生命周期管理

#### 1.1 创建会话
- **功能**: 用户选择角色后创建新会话
- **特性**:
  - 支持多会话并行（如"和苏格拉底聊哲学"，"和哈利波特聊魔法"）
  - 自动生成会话标题（基于第一条消息）
  - 会话状态管理（活跃/暂停/结束）
  - 会话元数据记录（创建时间、最后活动时间等）

#### 1.2 获取会话列表
- **功能**: 展示用户的历史会话
- **特性**:
  - 分页查询支持
  - 按时间排序（最近活动优先）
  - 会话状态过滤
  - 角色信息关联显示
  - 会话摘要信息（消息数量、最后消息时间等）

#### 1.3 会话详情管理
- **功能**: 获取单个会话的详细信息
- **特性**:
  - 完整的会话元数据
  - 关联角色信息
  - 消息统计信息
  - 会话设置信息

#### 1.4 关闭/删除会话
- **功能**: 用户主动结束或系统定期清理
- **特性**:
  - 软删除（保留数据用于分析）
  - 批量删除支持
  - 自动清理机制（超过一定时间未活动的会话）
  - 数据归档功能

### 2. 消息管理

#### 2.1 消息存储
- **功能**: 保存会话中的所有消息
- **特性**:
  - 支持文本和语音消息
  - 消息类型标识（用户/角色/系统）
  - 消息状态跟踪（发送中/已发送/失败）
  - 消息元数据（时间戳、长度等）

#### 2.2 上下文管理
- **功能**: 维护会话上下文以支持连续对话
- **特性**:
  - 滚动窗口机制（只保留最近N条消息）
  - 上下文摘要生成（长期记忆）
  - 关键信息提取和存储
  - 上下文压缩优化

#### 2.3 消息搜索
- **功能**: 在会话中搜索特定消息
- **特性**:
  - 全文搜索支持
  - 时间范围过滤
  - 消息类型过滤
  - 关键词高亮显示

### 3. 多模态扩展

#### 3.1 语音消息支持
- **功能**: 处理语音输入和输出
- **特性**:
  - STT（语音转文本）集成
  - 语音文件存储和管理
  - 语音质量检测
  - 多语言语音识别支持

#### 3.2 音频回复
- **功能**: 生成角色语音回复
- **特性**:
  - TTS（文本转语音）集成
  - 角色音色定制
  - 情感语调控制
  - 音频流式传输

### 4. 权限与限流

#### 4.1 用户权限控制
- **功能**: 控制用户对会话的访问权限
- **特性**:
  - 会话所有权验证
  - 共享会话支持（可选）
  - 管理员权限管理
  - 隐私设置控制

#### 4.2 限流机制
- **功能**: 防止系统滥用
- **特性**:
  - 用户每日/每小时消息数限制
  - 会话创建频率限制
  - 消息长度限制
  - 并发会话数限制

### 5. 实时通信

#### 5.1 WebSocket支持
- **功能**: 实时消息传输
- **特性**:
  - 双向实时通信
  - 连接状态管理
  - 消息确认机制
  - 断线重连支持

#### 5.2 消息队列
- **功能**: 异步消息处理
- **特性**:
  - 消息队列集成
  - 消息优先级管理
  - 失败重试机制
  - 消息持久化

## 数据库设计

### 1. 会话表 (conversations)

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | UUID | PK | 会话唯一标识 |
| user_id | UUID | FK, NOT NULL | 用户ID，关联users表 |
| character_id | UUID | FK, NOT NULL | 角色ID，关联characters表 |
| title | VARCHAR(255) | NOT NULL | 会话标题 |
| description | TEXT | NULL | 会话描述 |
| status | ENUM | NOT NULL | 会话状态：active/paused/ended/archived |
| settings | JSONB | NULL | 会话设置（如温度、最大长度等） |
| message_count | INTEGER | DEFAULT 0 | 消息总数 |
| last_message_at | TIMESTAMP | NULL | 最后消息时间 |
| created_at | TIMESTAMP | NOT NULL | 创建时间 |
| updated_at | TIMESTAMP | NOT NULL | 更新时间 |
| deleted_at | TIMESTAMP | NULL | 软删除时间 |

### 2. 消息表 (messages)

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | UUID | PK | 消息唯一标识 |
| conversation_id | UUID | FK, NOT NULL | 会话ID，关联conversations表 |
| sender_type | ENUM | NOT NULL | 发送者类型：user/character/system |
| sender_id | UUID | NULL | 发送者ID（用户ID或角色ID） |
| content | TEXT | NOT NULL | 消息内容 |
| content_type | ENUM | NOT NULL | 内容类型：text/audio/image |
| audio_url | VARCHAR(500) | NULL | 音频文件URL（语音消息） |
| audio_duration | INTEGER | NULL | 音频时长（秒） |
| image_url | VARCHAR(500) | NULL | 图片文件URL（图片消息） |
| metadata | JSONB | NULL | 消息元数据（如情感、置信度等） |
| status | ENUM | NOT NULL | 消息状态：sending/sent/failed |
| parent_id | UUID | FK, NULL | 父消息ID（回复关系） |
| created_at | TIMESTAMP | NOT NULL | 创建时间 |
| updated_at | TIMESTAMP | NOT NULL | 更新时间 |

### 3. 会话上下文表 (conversation_contexts)

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | UUID | PK | 上下文唯一标识 |
| conversation_id | UUID | FK, NOT NULL | 会话ID |
| context_type | ENUM | NOT NULL | 上下文类型：summary/memory/key_points |
| content | TEXT | NOT NULL | 上下文内容 |
| importance_score | FLOAT | NULL | 重要性评分 |
| created_at | TIMESTAMP | NOT NULL | 创建时间 |
| updated_at | TIMESTAMP | NOT NULL | 更新时间 |

### 4. 会话标签表 (conversation_tags)

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | UUID | PK | 标签唯一标识 |
| conversation_id | UUID | FK, NOT NULL | 会话ID |
| tag_name | VARCHAR(50) | NOT NULL | 标签名称 |
| tag_value | VARCHAR(100) | NULL | 标签值 |
| created_at | TIMESTAMP | NOT NULL | 创建时间 |

### 5. 用户会话限制表 (user_conversation_limits)

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | UUID | PK | 限制记录唯一标识 |
| user_id | UUID | FK, NOT NULL | 用户ID |
| limit_type | ENUM | NOT NULL | 限制类型：daily_messages/hourly_messages/max_conversations |
| limit_value | INTEGER | NOT NULL | 限制值 |
| current_value | INTEGER | DEFAULT 0 | 当前值 |
| reset_at | TIMESTAMP | NOT NULL | 重置时间 |
| created_at | TIMESTAMP | NOT NULL | 创建时间 |
| updated_at | TIMESTAMP | NOT NULL | 更新时间 |

## API设计

### 1. 会话管理API

#### 1.1 创建会话
```
POST /api/v1/conversations/
```

**请求体**:
```json
{
  "character_id": "uuid",
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
    "status": "active",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

#### 1.2 获取会话列表
```
GET /api/v1/conversations/
```

**查询参数**:
- `skip`: 跳过的记录数（默认0）
- `limit`: 返回的记录数（默认20，最大100）
- `status`: 会话状态过滤
- `character_id`: 角色ID过滤
- `order_by`: 排序字段（created_at/last_message_at）
- `order`: 排序方向（asc/desc）

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
        "status": "active",
        "message_count": 15,
        "last_message_at": "2024-01-01T12:00:00Z",
        "character": {
          "id": "character-uuid",
          "name": "苏格拉底",
          "avatar_url": "https://example.com/socrates.jpg"
        },
        "created_at": "2024-01-01T10:00:00Z"
      }
    ],
    "total": 1,
    "skip": 0,
    "limit": 20
  }
}
```

#### 1.3 获取会话详情
```
GET /api/v1/conversations/{conversation_id}
```

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
      "avatar_url": "https://example.com/socrates.jpg"
    },
    "created_at": "2024-01-01T10:00:00Z",
    "updated_at": "2024-01-01T12:00:00Z"
  }
}
```

#### 1.4 更新会话
```
PUT /api/v1/conversations/{conversation_id}
```

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

#### 1.5 删除会话
```
DELETE /api/v1/conversations/{conversation_id}
```

**响应**:
```json
{
  "code": 0,
  "msg": "会话删除成功",
  "data": {
    "id": "conversation-uuid",
    "deleted_at": "2024-01-01T12:00:00Z"
  }
}
```

### 2. 消息管理API

#### 2.1 发送消息
```
POST /api/v1/conversations/{conversation_id}/messages
```

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
    "content": "你好，苏格拉底！我想和你讨论哲学问题。",
    "content_type": "text",
    "status": "sent",
    "created_at": "2024-01-01T12:00:00Z"
  }
}
```

#### 2.2 获取消息列表
```
GET /api/v1/conversations/{conversation_id}/messages
```

**查询参数**:
- `skip`: 跳过的记录数（默认0）
- `limit`: 返回的记录数（默认50，最大200）
- `sender_type`: 发送者类型过滤
- `content_type`: 内容类型过滤
- `since`: 获取此时间之后的消息
- `until`: 获取此时间之前的消息

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
        "content": "你好，苏格拉底！",
        "content_type": "text",
        "status": "sent",
        "created_at": "2024-01-01T12:00:00Z"
      },
      {
        "id": "message-uuid-2",
        "sender_type": "character",
        "content": "你好！很高兴见到你。你想讨论什么哲学问题呢？",
        "content_type": "text",
        "status": "sent",
        "created_at": "2024-01-01T12:01:00Z"
      }
    ],
    "total": 2,
    "skip": 0,
    "limit": 50
  }
}
```

#### 2.3 获取消息详情
```
GET /api/v1/conversations/{conversation_id}/messages/{message_id}
```

#### 2.4 更新消息
```
PUT /api/v1/conversations/{conversation_id}/messages/{message_id}
```

#### 2.5 删除消息
```
DELETE /api/v1/conversations/{conversation_id}/messages/{message_id}
```

### 3. 实时通信API

#### 3.1 WebSocket连接
```
WS /api/v1/conversations/{conversation_id}/ws
```

**连接参数**:
- `token`: 认证令牌
- `user_id`: 用户ID

**消息格式**:
```json
{
  "type": "message",
  "data": {
    "content": "消息内容",
    "content_type": "text"
  }
}
```

#### 3.2 消息搜索API
```
GET /api/v1/conversations/{conversation_id}/search
```

**查询参数**:
- `query`: 搜索关键词
- `sender_type`: 发送者类型过滤
- `content_type`: 内容类型过滤
- `date_from`: 开始日期
- `date_to`: 结束日期

### 4. 语音消息API

#### 4.1 上传语音文件
```
POST /api/v1/conversations/{conversation_id}/audio
```

**请求体**: multipart/form-data
- `audio_file`: 音频文件
- `duration`: 音频时长（可选）

#### 4.2 获取语音回复
```
GET /api/v1/conversations/{conversation_id}/messages/{message_id}/audio
```

### 5. 会话分析API

#### 5.1 获取会话统计
```
GET /api/v1/conversations/{conversation_id}/stats
```

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
    "topics": ["哲学", "道德", "知识"],
    "sentiment_analysis": {
      "positive": 0.6,
      "neutral": 0.3,
      "negative": 0.1
    }
  }
}
```

#### 5.2 导出会话数据
```
GET /api/v1/conversations/{conversation_id}/export
```

**查询参数**:
- `format`: 导出格式（json/csv/txt）
- `include_metadata`: 是否包含元数据

## 技术实现要点

### 1. 数据库优化
- 为常用查询字段添加索引
- 使用分区表处理大量消息数据
- 实现数据归档策略
- 使用连接池优化数据库连接

### 2. 缓存策略
- 使用Redis缓存活跃会话数据
- 实现消息缓存机制
- 缓存用户会话限制信息
- 使用CDN缓存音频文件

### 3. 实时通信
- 使用WebSocket实现实时消息传输
- 实现消息确认和重发机制
- 支持断线重连
- 实现消息队列处理

### 4. 安全考虑
- 实现消息内容过滤
- 防止XSS和注入攻击
- 实现访问频率限制
- 保护用户隐私数据

### 5. 性能优化
- 实现消息分页加载
- 使用异步处理提高响应速度
- 实现消息压缩传输
- 优化数据库查询性能

## 监控和日志

### 1. 关键指标
- 会话创建数量
- 消息发送频率
- 用户活跃度
- 系统响应时间
- 错误率统计

### 2. 日志记录
- 用户操作日志
- 系统错误日志
- 性能监控日志
- 安全审计日志

### 3. 告警机制
- 系统异常告警
- 性能阈值告警
- 安全事件告警
- 容量预警

## 扩展性考虑

### 1. 水平扩展
- 支持多实例部署
- 实现负载均衡
- 数据库读写分离
- 缓存集群部署

### 2. 功能扩展
- 支持更多消息类型
- 实现消息加密
- 支持消息翻译
- 集成更多AI模型

### 3. 集成能力
- 支持第三方系统集成
- 提供API开放平台
- 支持Webhook通知
- 实现数据同步机制
