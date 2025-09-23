# 会话服务MVP设计

## 概述

在项目初期，我们需要专注于MVP（最小可行产品）的设计，确保核心功能能够快速实现和验证。本文档重新设计了会话服务，专注于最核心的功能。

> **注意**: 这是MVP版本的设计，专注于核心功能。完整设计请参考：[会话管理服务设计](./conversation_service.md)

## MVP核心功能

### 1. 基础会话管理
- ✅ 创建会话（单角色）
- ✅ 获取会话列表
- ✅ 获取会话详情
- ✅ 删除会话
- ✅ 基础权限控制

### 2. 基础消息管理
- ✅ 发送文本消息
- ✅ 获取消息列表
- ✅ 基础消息搜索
- ✅ 消息状态管理

### 3. 基础实时通信
- ✅ WebSocket连接
- ✅ 实时消息传输
- ✅ 基础错误处理

## 简化的数据库设计

### 1. 会话表 (conversations) - 简化版

```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    character_id UUID NOT NULL REFERENCES characters(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'ended')),
    message_count INTEGER DEFAULT 0 CHECK (message_count >= 0),
    last_message_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- 基础索引
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_character_id ON conversations(character_id);
CREATE INDEX idx_conversations_status ON conversations(status);
CREATE INDEX idx_conversations_last_message_at ON conversations(last_message_at DESC);
CREATE INDEX idx_conversations_deleted_at ON conversations(deleted_at) WHERE deleted_at IS NULL;
```

### 2. 消息表 (messages) - 简化版

```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    sender_type VARCHAR(20) NOT NULL CHECK (sender_type IN ('user', 'character')),
    content TEXT NOT NULL,
    content_type VARCHAR(20) NOT NULL DEFAULT 'text' CHECK (content_type IN ('text')),
    status VARCHAR(20) NOT NULL DEFAULT 'sent' CHECK (status IN ('sending', 'sent', 'failed')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- 基础索引
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_sender_type ON messages(sender_type);
CREATE INDEX idx_messages_created_at ON messages(created_at DESC);
CREATE INDEX idx_messages_conversation_created ON messages(conversation_id, created_at DESC);
```

### 3. 用户会话限制表 (user_conversation_limits) - 简化版

```sql
CREATE TABLE user_conversation_limits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    limit_type VARCHAR(30) NOT NULL CHECK (limit_type IN ('daily_messages', 'max_conversations')),
    limit_value INTEGER NOT NULL CHECK (limit_value > 0),
    current_value INTEGER DEFAULT 0 CHECK (current_value >= 0),
    reset_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- 索引
CREATE INDEX idx_user_limits_user_id ON user_conversation_limits(user_id);
CREATE INDEX idx_user_limits_type ON user_conversation_limits(limit_type);
CREATE UNIQUE INDEX idx_user_limits_user_type ON user_conversation_limits(user_id, limit_type);
```

## 简化的API设计

### 1. 会话管理API

#### 1.1 创建会话
```
POST /api/v1/conversations/
```

**请求体**:
```json
{
  "character_id": "uuid",
  "title": "与苏格拉底的对话"
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
    "title": "与苏格拉底的对话",
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
- `limit`: 返回的记录数（默认20，最大50）
- `status`: 会话状态过滤

**响应**:
```json
{
  "code": 0,
  "msg": "获取会话列表成功",
  "data": {
    "conversations": [
      {
        "id": "conversation-uuid",
        "title": "与苏格拉底的对话",
        "status": "active",
        "message_count": 5,
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

#### 1.4 删除会话
```
DELETE /api/v1/conversations/{conversation_id}
```

### 2. 消息管理API

#### 2.1 发送消息
```
POST /api/v1/conversations/{conversation_id}/messages
```

**请求体**:
```json
{
  "content": "你好，苏格拉底！"
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
    "content": "你好，苏格拉底！",
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
- `limit`: 返回的记录数（默认50，最大100）

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
        "content": "你好！很高兴见到你。",
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

### 3. 实时通信API

#### 3.1 WebSocket连接
```
WS /api/v1/conversations/{conversation_id}/ws
```

**连接参数**:
- `token`: 认证令牌

**消息格式**:
```json
{
  "type": "message",
  "data": {
    "content": "消息内容"
  }
}
```

## 简化的触发器

### 1. 更新会话消息计数

```sql
CREATE OR REPLACE FUNCTION update_conversation_message_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE conversations 
        SET message_count = message_count + 1,
            last_message_at = NEW.created_at,
            updated_at = NOW()
        WHERE id = NEW.conversation_id;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE conversations 
        SET message_count = message_count - 1,
            updated_at = NOW()
        WHERE id = OLD.conversation_id;
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_conversation_message_count
    AFTER INSERT OR DELETE ON messages
    FOR EACH ROW
    EXECUTE FUNCTION update_conversation_message_count();
```

### 2. 更新消息时间戳

```sql
CREATE OR REPLACE FUNCTION update_message_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_message_updated_at
    BEFORE UPDATE ON messages
    FOR EACH ROW
    EXECUTE FUNCTION update_message_updated_at();
```

## 简化的视图

### 1. 会话详情视图

```sql
CREATE VIEW conversation_details AS
SELECT 
    c.id,
    c.user_id,
    c.character_id,
    c.title,
    c.description,
    c.status,
    c.message_count,
    c.last_message_at,
    c.created_at,
    c.updated_at,
    u.email as user_email,
    ch.name as character_name,
    ch.avatar_url as character_avatar
FROM conversations c
JOIN users u ON c.user_id = u.id
JOIN characters ch ON c.character_id = ch.id
WHERE c.deleted_at IS NULL;
```

## 数据迁移脚本

### 1. 创建扩展

```sql
-- 启用UUID扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

### 2. 创建表结构

```sql
-- 按顺序创建表
-- 1. conversations表
-- 2. messages表  
-- 3. user_conversation_limits表
```

### 3. 创建索引

```sql
-- 创建所有必要的索引
```

### 4. 创建触发器

```sql
-- 创建触发器函数和触发器
```

### 5. 创建视图

```sql
-- 创建视图
```

## 基础配置

### 1. 环境配置

```python
# 会话服务配置
CONVERSATION_CONFIG = {
    "max_messages_per_conversation": 1000,
    "max_conversations_per_user": 10,
    "daily_message_limit": 100,
    "message_content_max_length": 2000,
    "websocket_heartbeat_interval": 30,
    "websocket_timeout": 300
}
```

### 2. 限流配置

```python
# 用户限制配置
USER_LIMITS = {
    "daily_messages": 100,
    "max_conversations": 10,
    "message_length": 2000
}
```

## 实现优先级

### 第一阶段：核心功能（MVP）
1. ✅ 基础会话管理（CRUD）
2. ✅ 基础消息管理（发送/接收）
3. ✅ 基础权限控制
4. ✅ 基础限流机制

### 第二阶段：实时通信
1. ✅ WebSocket连接
2. ✅ 实时消息传输
3. ✅ 基础错误处理

### 第三阶段：优化和扩展
1. 消息搜索功能
2. 性能优化
3. 监控和日志
4. 高级功能（语音、多角色等）

## 技术实现要点

### 1. 数据库优化
- 基础索引优化
- 连接池配置
- 查询优化

### 2. 缓存策略
- Redis缓存活跃会话
- 消息缓存机制
- 用户限制缓存

### 3. 安全考虑
- JWT认证
- 输入验证
- SQL注入防护
- 限流控制

### 4. 性能优化
- 分页查询
- 异步处理
- 连接池管理

## 监控指标

### 1. 基础指标
- 会话创建数量
- 消息发送数量
- 用户活跃度
- 系统响应时间

### 2. 错误指标
- API错误率
- WebSocket连接失败率
- 数据库连接错误率

## 总结

这个MVP设计专注于核心功能，确保：

1. **快速实现** - 简化的表结构和API设计
2. **核心功能** - 会话管理和消息传输
3. **基础安全** - 权限控制和限流
4. **可扩展性** - 为后续功能扩展预留空间
5. **稳定性** - 基础错误处理和监控

通过这个MVP设计，我们可以快速验证核心功能，然后根据用户反馈逐步添加高级功能。
