## 前端对接 API 文档（v1）

本文档面向前端，覆盖常用鉴权、对话编排、语音处理、任务查询与图片生成等接口。所有接口均返回统一响应结构。

### 基本信息
- 基础路径 Base URL: `/api/v1`
- 鉴权方式: Bearer Token（登录后在请求头携带）
  - `Authorization: Bearer <access_token>`
- 统一响应结构:
```json
{
  "code": 0,
  "msg": "ok",
  "data": { ... }
}
```
- OpenAPI 文档: `/api/v1/openapi.json`

---

### 1) 认证与会话

#### 登录获取访问令牌
- POST `/login/access-token-v2`
- 请求: `application/x-www-form-urlencoded`
  - `username`: string（邮箱）
  - `password`: string
- 响应示例
```json
{
  "code": 0,
  "msg": "登录成功",
  "data": {
    "access_token": "<JWT>",
    "token_type": "bearer"
  }
}
```

#### 校验令牌
- POST `/login/test-token`
- 头: `Authorization: Bearer <token>`
- 返回当前用户信息。

#### 重置密码（摘要）
- POST `/password-recovery/{email}` 发起找回
- POST `/reset-password/` 使用邮件令牌重置

---

### 2) 用户

#### 获取当前用户
- GET `/users/me`
- 头: `Authorization`
- 响应: 用户信息（含统计字段 `character_count`, `conversation_count`）。

#### 更新当前用户资料
- PATCH `/users/me`
- 体: `UserUpdateMe` 可选字段（如 `full_name`, `email` 等）

#### 修改当前用户密码
- PATCH `/users/me/password`
- 体: `{ "current_password": "...", "new_password": "..." }`

---

### 3) 对话编排 Orchestration

#### 发送文本消息（异步）
- POST `/orchestration/conversations/{conversation_id}/send-message`
- 头: `Authorization`
- 体: `SendMessageRequest`
```json
{
  "message": "你好，今天天气如何？",
  "settings": { "enable_tts": true }
}
```
- 响应（返回任务ID，前端需轮询任务状态）
```json
{
  "code": 0,
  "msg": "消息发送任务已创建",
  "data": {
    "task_id": "TEXT_MESSAGE_...",
    "status": "PENDING",
    "progress": 0,
    "created_at": "2025-09-27T00:00:00Z"
  }
}
```

#### 获取会话上下文
- GET `/orchestration/conversations/{conversation_id}/context?limit=10`
- 响应: 最近消息列表、角色摘要等。

#### 获取/更新会话设置
- GET `/orchestration/conversations/{conversation_id}/settings`
- PUT `/orchestration/conversations/{conversation_id}/settings`
- 体: `UpdateConversationSettingsRequest`（仅提供需要更新的字段）。

---

### 4) 语音处理 Voice

#### 获取可用音色
- GET `/voice/voices?provider=qwen3-tts`
- 响应: `voices` 列表及总数。

#### 上传音频文件（返回公网 URL）
- POST `/voice/upload-audio`
- 头: `Authorization`
- 表单: `multipart/form-data`，字段 `file`（音频文件，≤10MB）
- 响应
```json
{
  "code": 0,
  "msg": "音频文件上传成功",
  "data": {
    "success": true,
    "audio_url": "https://...",
    "filename": "voice_<user>_<ts>.wav",
    "file_size": 12345
  }
}
```

#### 语音消息流水线（STT→LLM→TTS，异步）
- POST `/voice/message`
- 体: `VoiceMessageRequest`
```json
{
  "conversation_id": "<uuid>",
  "audio_file_url": "https://...",
  "voice_preference": "Cherry"
}
```
- 响应: 返回 `task_id` 供轮询。

#### 文本转语音 TTS（异步）
- POST `/voice/tts`
- 查询参数（Query）:
  - `text` 必填，≤600 字符
  - `voice` 可选，默认 `Cherry`
  - `audio_format` 可选，默认 `wav`
  - `sample_rate` 可选，默认 `24000`
- 响应: 返回 `task_id`。

#### 语音转文本 STT（异步）
- POST `/voice/stt`
- 查询参数（Query）:
  - `audio_url` 必填，公网可访问的 http(s)
  - `model` 可选，默认服务内置
  - `prompt` 可选
  - `response_format` 可选（内部使用，不影响结果）
  - `temperature` 可选（内部使用）
- 响应: 返回 `task_id`。

#### 一键生成所有音色示例（仅超级用户）
- POST `/voice/generate-all?provider=qwen3-tts&force_regenerate=false`

---

### 5) 图片生成 Image

#### 生成图片（并上传到七牛）
- POST `/image/generate`
- 查询参数（Query）:
  - `prompt` 必填
  - `size` 默认 `720*1280`
  - `style` 默认 `realistic`
  - `quality` 默认 `standard`
- 响应: 七牛上传结果（含 `url`）。

---

### 6) 任务管理 Tasks（轮询）

#### 获取任务状态
- GET `/tasks/{task_id}`
- 响应示例
```json
{
  "code": 0,
  "msg": "任务状态获取成功",
  "data": {
    "id": "TTS_GENERATION_...",
    "task_type": "TTS_GENERATION",
    "status": "PROCESSING|COMPLETED|FAILED",
    "progress": 50,
    "steps": [ {"name": "TTS", "status": "PROCESSING"} ],
    "result": { /* 任务完成后的结果，如音频URL/文本等 */ }
  }
}
```

#### 获取我的任务列表
- GET `/tasks?task_type=TTS_GENERATION&status_1=PROCESSING&skip=0&limit=20&order_by=created_at&order=desc`
- 注意: 状态过滤参数名为 `status_1`。

#### 取消任务
- POST `/tasks/{task_id}/cancel`
- 体: `{ "reason": "..." }`

#### 任务统计
- GET `/tasks/stats/summary`

---

### 7) 错误与重试建议
- `401/403`: 检查 `Authorization` 头是否携带或是否过期。
- `400/422`: 按返回的字段级错误提示调整参数。
- 任务轮询建议: 500ms~1500ms 间隔，状态进入 `COMPLETED`/`FAILED`/`CANCELLED`/`TIMEOUT` 后停止。

---

### 8) Curl 示例

登录获取 Token
```bash
curl -X POST \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=<email>&password=<password>" \
  http://localhost:8000/api/v1/login/access-token-v2
```

发送文本消息（异步）
```bash
curl -X POST \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"message":"你好","settings":{"enable_tts":true}}' \
  http://localhost:8000/api/v1/orchestration/conversations/<conversation_id>/send-message
```

查询任务状态
```bash
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/v1/tasks/<task_id>
```

---

### 备注
- 本文档仅覆盖与前端交互最常用接口；更多资源（如角色、会话管理的完整 CRUD）请参考 OpenAPI 文档。
- 语音/图片等大文件上传务必使用后端提供的上传接口以获取稳定的公网 URL。


