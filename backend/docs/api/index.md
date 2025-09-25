# API 文档索引

大黄鸭项目 API 文档总览，包含所有可用的接口和功能模块。

## 文档结构

### 认证与用户管理
- [用户管理 API](user.md) - 用户注册、登录、密码管理等功能
- [登录认证 API](login.md) - 用户认证、令牌管理、密码重置等功能

### 核心功能模块
- [角色管理 API](characters.md) - 角色创建、管理、搜索、AI图片生成等功能
- [对话管理 API](conversations.md) - 会话创建、消息管理、搜索等功能
- [对话编排 API](dialogue_orchestration.md) - 智能对话编排、上下文管理、设置配置等功能

### 多媒体处理
- [语音处理 API](voice_processing.md) - TTS、STT、音色管理、语音对话等功能
- [语音目录 API](voice_catalog.md) - 音色目录管理、预览等功能
- [图片生成 API](image.md) - AI图片生成、风格管理等功能

### 角色语音功能
- [角色语音功能 API](character_voice_feature.md) - 角色语音设置、音色配置等功能

## API 基础信息

### 基础URL
```
开发环境: http://localhost:8000
生产环境: https://api.dahuanya.com
```

### 认证方式
所有API接口（除公开接口外）都需要在请求头中包含访问令牌：

```http
Authorization: Bearer <your_access_token>
```

### 响应格式
所有API响应都遵循统一的格式：

```json
{
  "code": 0,
  "msg": "操作成功",
  "data": {
    // 具体数据
  }
}
```

### 错误处理
错误响应格式：

```json
{
  "code": 400,
  "msg": "错误描述",
  "detail": "详细错误信息"
}
```

## 快速开始

### 1. 用户注册
```bash
curl -X POST "http://localhost:8000/users/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123",
    "full_name": "测试用户"
  }'
```

### 2. 用户登录
```bash
curl -X POST "http://localhost:8000/login/access-token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=password123"
```

### 3. 创建角色
```bash
curl -X POST "http://localhost:8000/characters/" \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "小助手",
    "short_bio": "我是一个友好的AI助手",
    "persona": "你是一个乐于助人的AI助手...",
    "is_active": true
  }'
```

### 4. 开始对话
```bash
curl -X POST "http://localhost:8000/orchestration/conversations/{conversation_id}/send-message" \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "你好！",
    "settings": {
      "voice_enabled": true
    }
  }'
```

## 功能特性

### 🎭 角色管理
- 创建和管理AI角色
- 支持角色标签分类
- 智能搜索（文本、向量、混合搜索）
- AI图片生成和角色形象管理

### 💬 对话系统
- 多轮对话管理
- 上下文感知对话
- 对话设置和个性化配置
- 消息搜索和过滤

### 🎵 语音功能
- 文本转语音（TTS）
- 语音转文本（STT）
- 多种音色选择
- 语音对话支持

### 🖼️ 图片生成
- AI图片生成
- 多种风格和尺寸支持
- 角色形象自动生成

### 🔍 智能搜索
- 语义搜索
- 混合搜索算法
- 向量嵌入技术

## 状态码说明

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未认证 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 422 | 数据验证错误 |
| 429 | 请求频率限制 |
| 500 | 服务器内部错误 |

## 开发工具

### API 测试
推荐使用以下工具进行API测试：
- [Postman](https://www.postman.com/)
- [Insomnia](https://insomnia.rest/)
- [curl](https://curl.se/)

### 文档生成
API文档基于OpenAPI 3.0规范，可以通过以下方式访问：
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

## 更新日志

### v1.0.0 (2024-01-01)
- 初始版本发布
- 基础用户管理和认证功能
- 角色管理和对话系统
- 语音处理功能
- 图片生成功能

## 支持与反馈

如有问题或建议，请通过以下方式联系：
- 项目Issues: [GitHub Issues](https://github.com/your-repo/issues)
- 邮箱: support@dahuanya.com
- 文档更新: 请提交Pull Request

---

*最后更新: 2024-01-01*
