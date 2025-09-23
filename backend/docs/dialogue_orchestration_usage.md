# 对话编排功能使用指南

## 概述

对话编排功能是AI角色扮演平台的核心组件，负责将用户输入、角色persona、历史消息组合起来，动态构建prompt，并调用LLM生成角色回复。

## 功能特性

### ✅ 已实现功能
- **LLM集成服务** - 支持OpenAI GPT模型
- **基础上下文拼接** - 自动构建包含角色persona和历史消息的prompt
- **消息流控制** - 完整的用户消息到角色回复流程
- **会话设置管理** - 可配置的LLM参数和对话设置
- **REST API接口** - 完整的API端点支持

### 🚧 待实现功能
- **多角色支持** - 多角色对话和角色切换
- **RAG知识注入** - 外部知识库检索增强
- **高级策略调度** - 智能上下文管理和摘要

## API接口

### 1. 发送消息并获取角色回复

```http
POST /api/v1/orchestration/conversations/{conversation_id}/send-message
```

**请求体:**
```json
{
  "message": "你好，请介绍一下自己",
  "settings": {
    "temperature": 0.7,
    "max_tokens": 1000,
    "context_window_size": 10,
    "enable_tts": false
  }
}
```

**响应:**
```json
{
  "success": true,
  "user_message_id": "uuid",
  "character_message_id": "uuid", 
  "character_response": "你好！我是...",
  "audio_url": null,
  "usage": {
    "prompt_tokens": 150,
    "completion_tokens": 50,
    "total_tokens": 200
  }
}
```

### 2. 获取会话上下文

```http
GET /api/v1/orchestration/conversations/{conversation_id}/context?limit=10
```

**响应:**
```json
{
  "conversation_id": "uuid",
  "character_name": "苏格拉底",
  "character_bio": "古希腊哲学家",
  "recent_messages": [
    {
      "id": "uuid",
      "content": "你好",
      "sender_type": "user",
      "sender_name": "用户",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "message_count": 1,
  "context_window_size": 10
}
```

### 3. 更新会话设置

```http
PUT /api/v1/orchestration/conversations/{conversation_id}/settings
```

**请求体:**
```json
{
  "temperature": 0.8,
  "max_tokens": 1500,
  "context_window_size": 15,
  "enable_tts": true
}
```

### 4. 获取会话设置

```http
GET /api/v1/orchestration/conversations/{conversation_id}/settings
```

### 5. 获取可用模型列表

```http
GET /api/v1/orchestration/models
```

**响应:**
```json
{
  "models": {
    "openai": {
      "provider": "openai",
      "model": "gpt-3.5-turbo",
      "available": true,
      "description": "OpenAI GPT模型"
    },
    "deepseek": {
      "provider": "deepseek",
      "model": "deepseek-chat", 
      "available": true,
      "description": "DeepSeek Chat模型"
    },
    "qwen": {
      "provider": "qwen",
      "model": "qwen-turbo",
      "available": false,
      "description": "阿里千问模型"
    }
  },
  "default_provider": "openai",
  "total_available": 2
}
```

## 配置说明

### 环境变量配置

在 `.env` 文件中添加以下配置：

```env
# LLM提供商选择
LLM_PROVIDER=openai  # 可选: openai, deepseek, qwen

# OpenAI配置
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo

# DeepSeek配置
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_BASE_URL=https://api.deepseek.com

# 阿里千问配置
QWEN_API_KEY=your_qwen_api_key_here
QWEN_MODEL=qwen-turbo
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
```

### 会话设置参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `llm_provider` | string | "openai" | LLM提供商 (openai/deepseek/qwen) |
| `llm_model` | string | "gpt-3.5-turbo" | LLM模型 |
| `temperature` | float | 0.7 | 温度参数 (0.0-2.0) |
| `max_tokens` | int | 1000 | 最大token数 (1-4000) |
| `top_p` | float | 0.9 | top_p参数 (0.0-1.0) |
| `context_window_size` | int | 10 | 上下文窗口大小 (1-50) |
| `enable_context_summary` | bool | false | 是否启用上下文摘要 |
| `enable_tts` | bool | false | 是否启用TTS |
| `tts_voice` | string | null | TTS音色 |
| `auto_save` | bool | true | 是否自动保存 |
| `enable_typing_indicator` | bool | true | 是否显示输入状态 |

## 使用示例

### Python客户端示例

```python
import httpx
import asyncio

async def send_message_to_character():
    async with httpx.AsyncClient() as client:
        # 发送消息
        response = await client.post(
            "http://localhost:8000/api/v1/orchestration/conversations/{conversation_id}/send-message",
            json={
                "message": "你好，请介绍一下自己",
                "settings": {
                    "temperature": 0.7,
                    "max_tokens": 1000
                }
            },
            headers={"Authorization": "Bearer your_token"}
        )
        
        result = response.json()
        if result["success"]:
            print(f"角色回复: {result['character_response']}")
        else:
            print(f"错误: {result['error']}")

# 运行示例
asyncio.run(send_message_to_character())
```

### JavaScript客户端示例

```javascript
async function sendMessageToCharacter(conversationId, message) {
    const response = await fetch(
        `/api/v1/orchestration/conversations/${conversationId}/send-message`,
        {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer your_token'
            },
            body: JSON.stringify({
                message: message,
                settings: {
                    temperature: 0.7,
                    max_tokens: 1000
                }
            })
        }
    );
    
    const result = await response.json();
    if (result.success) {
        console.log('角色回复:', result.character_response);
        return result.character_response;
    } else {
        console.error('错误:', result.error);
        return null;
    }
}

// 使用示例
sendMessageToCharacter('conversation-uuid', '你好，请介绍一下自己');
```

## 测试

### 运行LLM服务测试

```bash
cd backend
python -m app.scripts.test_llm_service
```

### 运行多模型测试

```bash
cd backend
python -m app.scripts.test_multi_llm
```

### API测试

使用以下curl命令测试API：

```bash
# 发送消息
curl -X POST "http://localhost:8000/api/v1/orchestration/conversations/{conversation_id}/send-message" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_token" \
  -d '{
    "message": "你好，请介绍一下自己",
    "settings": {
      "temperature": 0.7,
      "max_tokens": 1000
    }
  }'

# 获取上下文
curl -X GET "http://localhost:8000/api/v1/orchestration/conversations/{conversation_id}/context" \
  -H "Authorization: Bearer your_token"

# 获取可用模型列表
curl -X GET "http://localhost:8000/api/v1/orchestration/models" \
  -H "Authorization: Bearer your_token"

# 使用DeepSeek模型发送消息
curl -X POST "http://localhost:8000/api/v1/orchestration/conversations/{conversation_id}/send-message" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_token" \
  -d '{
    "message": "你好，请介绍一下自己",
    "settings": {
      "llm_provider": "deepseek",
      "llm_model": "deepseek-chat",
      "temperature": 0.7,
      "max_tokens": 1000
    }
  }'
```

## 故障排除

### 常见问题

1. **LLM调用失败**
   - 检查对应API密钥是否正确配置（`OPENAI_API_KEY`、`DEEPSEEK_API_KEY`、`QWEN_API_KEY`）
   - 确认网络连接正常
   - 检查API配额是否充足
   - 验证模型名称是否正确

2. **角色回复质量不佳**
   - 调整 `temperature` 参数 (0.1-0.9 更稳定，0.7-1.0 更有创意)
   - 增加 `max_tokens` 限制
   - 优化角色的 `persona_text` 和 `example_lines`

3. **上下文过长**
   - 减少 `context_window_size` 参数
   - 启用 `enable_context_summary` 功能

### 日志查看

```bash
# 查看应用日志
tail -f logs/app.log

# 查看LLM服务日志
grep "LLM" logs/app.log
```

## 下一步开发

### 第二阶段：上下文优化
- [ ] 实现智能上下文截断
- [ ] 添加角色persona动态加载
- [ ] 优化prompt模板系统

### 第三阶段：高级功能
- [ ] 多角色支持
- [ ] RAG知识注入
- [ ] 高级策略调度
- [ ] 情感分析集成
