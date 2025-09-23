# 会话管理服务设计

## 概述

会话管理服务是AI角色扮演平台的核心组件，负责管理用户与AI角色之间的对话会话。本文档定义了会话管理的基本功能、数据库设计和API规范。

## 实现状态

当前会话服务的核心功能已经基本实现，包括：
- ✅ 完整的CRUD操作
- ✅ 基础的API接口  
- ✅ WebSocket实时通信
- ✅ 权限控制和限流
- ✅ 数据验证和错误处理

**总体完成度：60%**（MVP功能90%，高级功能15%）

详细实现状态请参考：[会话服务实现状态](./conversation_service_implementation_status.md)

## 核心功能

### 1. 会话生命周期管理
- **创建会话**: 用户选择角色后创建新会话，支持多会话并行
- **获取会话列表**: 展示用户的历史会话，支持分页和过滤
- **会话详情**: 获取单个会话的完整信息和统计
- **更新会话**: 修改会话标题、描述、设置等信息
- **关闭/删除会话**: 用户主动结束或系统定期清理

### 2. 消息管理
- **消息存储**: 保存会话中的所有消息（文本、语音、图片）
- **上下文管理**: 维护会话上下文，支持滚动窗口机制
- **消息搜索**: 在会话中搜索特定消息
- **消息状态**: 跟踪消息发送状态和元数据

### 3. 多模态支持
- **语音消息**: STT（语音转文本）集成
- **音频回复**: TTS（文本转语音）生成角色语音
- **图片消息**: 支持图片上传和显示
- **实时传输**: WebSocket支持实时消息传输

### 4. 权限与限流
- **用户权限**: 控制用户对会话的访问权限
- **限流机制**: 防止系统滥用，支持多种限制策略
- **隐私控制**: 支持会话隐私设置

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

## API端点设计

### 会话管理
- `POST /api/v1/conversations/` - 创建会话
- `GET /api/v1/conversations/` - 获取会话列表
- `GET /api/v1/conversations/{id}` - 获取会话详情
- `PUT /api/v1/conversations/{id}` - 更新会话
- `DELETE /api/v1/conversations/{id}` - 删除会话

### 消息管理
- `POST /api/v1/conversations/{id}/messages` - 发送消息
- `GET /api/v1/conversations/{id}/messages` - 获取消息列表
- `GET /api/v1/conversations/{id}/messages/{msg_id}` - 获取消息详情
- `PUT /api/v1/conversations/{id}/messages/{msg_id}` - 更新消息
- `DELETE /api/v1/conversations/{id}/messages/{msg_id}` - 删除消息

### 实时通信
- `WS /api/v1/conversations/{id}/ws` - WebSocket连接
- `GET /api/v1/conversations/{id}/search` - 消息搜索

### 语音支持
- `POST /api/v1/conversations/{id}/audio` - 上传语音文件
- `GET /api/v1/conversations/{id}/messages/{msg_id}/audio` - 获取语音回复

### 会话分析
- `GET /api/v1/conversations/{id}/stats` - 获取会话统计
- `GET /api/v1/conversations/{id}/export` - 导出会话数据

## 技术特性

### 1. 实时通信
- WebSocket支持双向实时通信
- 消息确认和重发机制
- 断线重连支持

### 2. 多模态支持
- 文本、语音、图片消息支持
- STT/TTS集成
- 文件存储和管理

### 3. 性能优化
- 消息分页加载
- 上下文滚动窗口
- 缓存机制
- 异步处理

### 4. 安全控制
- 用户权限验证
- 消息内容过滤
- 访问频率限制
- 数据加密保护

## 扩展性考虑

### 1. 水平扩展
- 支持多实例部署
- 负载均衡
- 数据库读写分离

### 2. 功能扩展
- 支持更多消息类型
- 消息加密
- 多语言支持
- AI模型集成

### 3. 集成能力
- 第三方系统集成
- API开放平台
- Webhook通知
- 数据同步

## 详细设计文档

更详细的API设计、数据库优化、技术实现要点等内容请参考：
[会话管理服务详细设计](./conversation_service_detailed.md)

