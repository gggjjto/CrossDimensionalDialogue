# 对话编排 API 文档

对话编排模块负责处理用户与AI角色的对话交互，包括消息发送、上下文管理和对话设置。

## 基础信息

- **基础路径**: `/orchestration`
- **认证**: 需要用户登录
- **内容类型**: `application/json`

## 接口列表

### 1. 发送消息

发送用户消息并获取角色回复。

**接口**: `POST /orchestration/conversations/{conversation_id}/send-message`

**请求参数**:
- `conversation_id` (路径参数): 会话ID (UUID)

**请求体**:
```json
{
  "message": "你好，今天天气怎么样？",
  "settings": {
    "temperature": 0.7,
    "max_tokens": 1000,
    "voice_enabled": true,
    "voice_preference": "Cherry"
  }
}
```

**请求体字段说明**:
- `message` (string, 必需): 用户发送的消息内容
- `settings` (object, 可选): 对话设置
  - `temperature` (float): 生成温度，范围0-2
  - `max_tokens` (int): 最大生成token数
  - `voice_enabled` (bool): 是否启用语音回复
  - `voice_preference` (string): 音色偏好

**响应**:
```json
{
  "success": true,
  "user_message_id": "uuid",
  "character_message_id": "uuid", 
  "character_response": "今天天气很好，阳光明媚！",
  "audio_url": "https://example.com/audio.wav",
  "usage": {
    "prompt_tokens": 50,
    "completion_tokens": 20,
    "total_tokens": 70
  }
}
```

**响应字段说明**:
- `success` (bool): 请求是否成功
- `user_message_id` (string): 用户消息ID
- `character_message_id` (string): 角色回复消息ID
- `character_response` (string): 角色回复内容
- `audio_url` (string, 可选): 语音回复URL
- `usage` (object): Token使用统计

**状态码**:
- `201`: 消息发送成功
- `400`: 请求参数错误
- `404`: 会话不存在
- `500`: 服务器内部错误

### 2. 获取会话上下文

获取指定会话的上下文信息，包括最近的消息和角色信息。

**接口**: `GET /orchestration/conversations/{conversation_id}/context`

**请求参数**:
- `conversation_id` (路径参数): 会话ID (UUID)
- `limit` (查询参数, 可选): 返回的消息数量限制，默认10

**响应**:
```json
{
  "conversation_id": "uuid",
  "character_name": "小助手",
  "character_bio": "我是一个友好的AI助手",
  "recent_messages": [
    {
      "id": "uuid",
      "content": "你好！",
      "sender_type": "user",
      "sender_name": "用户",
      "created_at": "2024-01-01T10:00:00Z"
    },
    {
      "id": "uuid", 
      "content": "你好！有什么可以帮助你的吗？",
      "sender_type": "character",
      "sender_name": "小助手",
      "created_at": "2024-01-01T10:00:01Z"
    }
  ],
  "message_count": 2,
  "context_window_size": 10
}
```

**响应字段说明**:
- `conversation_id` (string): 会话ID
- `character_name` (string): 角色名称
- `character_bio` (string): 角色简介
- `recent_messages` (array): 最近的消息列表
  - `id` (string): 消息ID
  - `content` (string): 消息内容
  - `sender_type` (string): 发送者类型 (user/character)
  - `sender_name` (string): 发送者名称
  - `created_at` (string): 创建时间
- `message_count` (int): 总消息数量
- `context_window_size` (int): 上下文窗口大小

**状态码**:
- `200`: 获取成功
- `400`: 请求参数错误
- `404`: 会话不存在
- `500`: 服务器内部错误

### 3. 更新会话设置

更新指定会话的对话设置。

**接口**: `PUT /orchestration/conversations/{conversation_id}/settings`

**请求参数**:
- `conversation_id` (路径参数): 会话ID (UUID)

**请求体**:
```json
{
  "temperature": 0.8,
  "max_tokens": 1500,
  "voice_enabled": true,
  "voice_preference": "Cherry",
  "system_prompt": "你是一个友好的AI助手"
}
```

**请求体字段说明**:
- `temperature` (float, 可选): 生成温度
- `max_tokens` (int, 可选): 最大生成token数
- `voice_enabled` (bool, 可选): 是否启用语音回复
- `voice_preference` (string, 可选): 音色偏好
- `system_prompt` (string, 可选): 系统提示词

**响应**:
```json
{
  "conversation_id": "uuid",
  "settings": {
    "temperature": 0.8,
    "max_tokens": 1500,
    "voice_enabled": true,
    "voice_preference": "Cherry",
    "system_prompt": "你是一个友好的AI助手"
  },
  "updated_at": "2024-01-01T10:00:00Z"
}
```

**状态码**:
- `200`: 更新成功
- `400`: 请求参数错误
- `404`: 会话不存在
- `500`: 服务器内部错误

### 4. 获取会话设置

获取指定会话的当前设置。

**接口**: `GET /orchestration/conversations/{conversation_id}/settings`

**请求参数**:
- `conversation_id` (路径参数): 会话ID (UUID)

**响应**:
```json
{
  "conversation_id": "uuid",
  "settings": {
    "temperature": 0.7,
    "max_tokens": 1000,
    "voice_enabled": false,
    "voice_preference": "Cherry",
    "system_prompt": null
  },
  "updated_at": "2024-01-01T10:00:00Z"
}
```

**状态码**:
- `200`: 获取成功
- `404`: 会话不存在
- `500`: 服务器内部错误

## 错误处理

所有接口都遵循统一的错误响应格式：

```json
{
  "detail": "错误描述信息"
}
```

常见错误类型：
- `400 Bad Request`: 请求参数错误
- `401 Unauthorized`: 未认证或认证失败
- `403 Forbidden`: 权限不足
- `404 Not Found`: 资源不存在
- `500 Internal Server Error`: 服务器内部错误

## 使用示例

### 发送消息示例

```bash
curl -X POST "https://api.example.com/orchestration/conversations/123e4567-e89b-12d3-a456-426614174000/send-message" \
  -H "Authorization: Bearer your_token" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "你好，请介绍一下自己",
    "settings": {
      "temperature": 0.7,
      "voice_enabled": true
    }
  }'
```

### 获取上下文示例

```bash
curl -X GET "https://api.example.com/orchestration/conversations/123e4567-e89b-12d3-a456-426614174000/context?limit=5" \
  -H "Authorization: Bearer your_token"
```

## 注意事项

1. 所有接口都需要用户认证，请在请求头中包含有效的访问令牌
2. 会话ID必须是有效的UUID格式
3. 消息内容不能为空，且长度建议不超过2000字符
4. 语音功能需要确保音频文件已正确上传到云存储
5. 设置更新会立即生效，影响后续的对话生成
