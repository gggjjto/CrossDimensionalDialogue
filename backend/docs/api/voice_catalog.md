# 音色目录API文档

## 概述

音色目录API提供了对TTS（文本转语音）音色资源的完整管理功能，包括查询、搜索、创建、更新和删除操作。

## API端点

### 1. 获取音色目录列表

**GET** `/api/v1/voice-catalog/`

获取音色目录列表，支持按提供方和可用状态过滤。

#### 查询参数

- `provider` (可选): 提供方过滤，如 "qwen3-tts"
- `is_active` (可选): 是否可用过滤，true/false
- `skip` (可选): 跳过数量，默认0
- `limit` (可选): 限制数量，默认100，最大1000

#### 响应示例

```json
{
  "items": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "provider": "qwen3-tts",
      "name": "温柔女声",
      "voice": "alloy",
      "preview_url": "https://example.com/preview.mp3",
      "description": "温柔甜美的女性声音",
      "is_active": true,
      "created_at": "2024-01-01T00:00:00",
      "updated_at": "2024-01-01T00:00:00"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 100
}
```

### 2. 获取音色目录详情

**GET** `/api/v1/voice-catalog/{voice_catalog_id}`

根据ID获取音色目录详情。

#### 路径参数

- `voice_catalog_id`: 音色目录ID (UUID)

#### 响应示例

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "provider": "qwen3-tts",
  "name": "温柔女声",
  "voice": "alloy",
  "preview_url": "https://example.com/preview.mp3",
  "description": "温柔甜美的女性声音",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

### 3. 根据提供方获取音色目录

**GET** `/api/v1/voice-catalog/provider/{provider}`

根据提供方获取音色目录列表。

#### 路径参数

- `provider`: 提供方名称，如 "qwen3-tts"

#### 查询参数

- `is_active` (可选): 是否可用过滤
- `skip` (可选): 跳过数量
- `limit` (可选): 限制数量

### 4. 搜索音色目录

**POST** `/api/v1/voice-catalog/search`

支持按关键词、提供方、可用状态等条件搜索音色目录。

#### 请求体

```json
{
  "query": "温柔",
  "provider": "qwen3-tts",
  "is_active": true,
  "skip": 0,
  "limit": 100
}
```

#### 响应格式

与获取列表接口相同。

### 5. 创建音色目录项

**POST** `/api/v1/voice-catalog/`

创建新的音色目录项。需要超级用户权限。

#### 请求体

```json
{
  "provider": "qwen3-tts",
  "name": "温柔女声",
  "voice": "alloy",
  "preview_url": "https://example.com/preview.mp3",
  "description": "温柔甜美的女性声音",
  "is_active": true
}
```

### 6. 更新音色目录项

**PUT** `/api/v1/voice-catalog/{voice_catalog_id}`

更新音色目录项。需要超级用户权限。

#### 请求体

```json
{
  "name": "温柔女声（更新）",
  "description": "更新后的描述",
  "is_active": false
}
```

### 7. 删除音色目录项

**DELETE** `/api/v1/voice-catalog/{voice_catalog_id}`

删除音色目录项。需要超级用户权限。

#### 响应示例

```json
{
  "success": true,
  "message": "音色目录项删除成功"
}
```

## 权限说明

- **普通用户**: 可以查看和搜索音色目录
- **超级用户**: 可以创建、更新和删除音色目录项

## 错误处理

API使用标准的HTTP状态码：

- `200`: 成功
- `201`: 创建成功
- `400`: 请求参数错误
- `401`: 未认证
- `403`: 权限不足
- `404`: 资源不存在
- `500`: 服务器内部错误

## 使用示例

### 获取所有可用的音色

```bash
curl -X GET "http://localhost:8000/api/v1/voice-catalog/?is_active=true" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 搜索特定音色

```bash
curl -X POST "http://localhost:8000/api/v1/voice-catalog/search" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "query": "女声",
    "provider": "qwen3-tts",
    "is_active": true
  }'
```

### 创建新音色

```bash
curl -X POST "http://localhost:8000/api/v1/voice-catalog/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_SUPERUSER_TOKEN" \
  -d '{
    "provider": "qwen3-tts",
    "name": "新音色",
    "voice": "new_voice",
    "description": "新的音色描述"
  }'
```
