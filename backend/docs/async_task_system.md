# 异步任务处理系统

## 概述

本系统实现了基于Redis和RQ的异步任务处理架构，将原本同步的AI处理任务（STT、LLM、TTS）改为异步处理，提升用户体验和系统性能。

## 架构组件

### 1. 基础设施层
- **Redis连接** (`app/core/redis.py`): Redis客户端单例，支持连接池和健康检查
- **RQ队列管理** (`app/core/rq.py`): 队列管理器，支持多种队列类型和优先级
- **任务模型** (`app/models/task.py`): AI任务数据模型和状态管理
- **任务Schema** (`app/schemas/task.py`): Pydantic验证模型

### 2. 服务层
- **任务队列服务** (`app/services/task_queue_service.py`): 任务创建、查询、状态更新
- **AI任务Worker** (`app/workers/ai_task_worker.py`): 后台任务处理器

### 3. API层
- **语音处理API** (`app/api/routes/voice_processing.py`): 异步语音消息处理
- **对话编排API** (`app/api/routes/dialogue_orchestration.py`): 异步文本消息处理
- **任务管理API** (`app/api/routes/tasks.py`): 任务状态查询和管理

## 任务类型

| 任务类型 | 描述 | 处理步骤 |
|---------|------|---------|
| `VOICE_MESSAGE` | 语音消息处理 | STT → LLM → TTS |
| `TEXT_MESSAGE` | 文本消息处理 | LLM → TTS |
| `TTS_GENERATION` | 文本转语音 | TTS |
| `STT_TRANSCRIPTION` | 语音转文本 | STT |
| `IMAGE_GENERATION` | 图像生成 | Image Generation |
| `CHARACTER_GENERATION` | 角色生成 | Character Generation |

## 任务状态

| 状态 | 描述 |
|------|------|
| `PENDING` | 等待处理 |
| `PROCESSING` | 正在处理 |
| `COMPLETED` | 处理完成 |
| `FAILED` | 处理失败 |
| `CANCELLED` | 用户取消 |
| `TIMEOUT` | 处理超时 |

## 队列配置

- **voice_queue**: 语音相关任务（STT、TTS）
- **text_queue**: 文本相关任务（LLM、角色生成）
- **image_queue**: 图像生成任务
- **priority_queue**: 高优先级任务（priority > 5）

## 使用方法

### 1. 启动Worker进程

```bash
# 启动所有队列的Worker
python start_worker.py

# 启动特定队列的Worker
python start_worker.py voice_queue text_queue

# 启动高优先级队列Worker
python start_worker.py priority_queue
```

### 2. API使用示例

#### 发送语音消息（异步）
```bash
POST /api/v1/voice/message
{
    "audio_file_url": "https://example.com/audio.wav",
    "conversation_id": "uuid",
    "voice_preference": "Cherry"
}

# 响应
{
    "success": true,
    "data": {
        "task_id": "voice_message_abc123",
        "status": "pending",
        "progress": 0,
        "created_at": "2024-01-01T00:00:00Z"
    }
}
```

#### 查询任务状态
```bash
GET /api/v1/tasks/{task_id}

# 响应
{
    "success": true,
    "data": {
        "id": "voice_message_abc123",
        "status": "completed",
        "progress": 100,
        "result": {
            "success": true,
            "stt_text": "你好",
            "character_response": "你好！很高兴见到你",
            "audio_url": "https://example.com/response.wav",
            "voice_used": "Cherry"
        }
    }
}
```

#### 获取任务列表
```bash
GET /api/v1/tasks/?status=completed&limit=10

# 响应
{
    "success": true,
    "data": {
        "tasks": [...],
        "total": 50,
        "skip": 0,
        "limit": 10
    }
}
```

#### 取消任务
```bash
POST /api/v1/tasks/{task_id}/cancel
{
    "reason": "用户取消"
}
```

### 3. 数据库迁移

```bash
# 应用迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

## 配置说明

### 环境变量

```bash
# Redis配置
REDIS_URL=redis://localhost:6379/0
REDIS_MAX_CONNECTIONS=20
REDIS_RETRY_ON_TIMEOUT=true
REDIS_HEALTH_CHECK_INTERVAL=30

# 任务队列配置
TASK_QUEUE_ENABLED=true
TASK_DEFAULT_TIMEOUT=300
TASK_DEFAULT_RETRY=3
TASK_RESULT_TTL=3600
TASK_FAILURE_TTL=86400
TASK_MAX_WORKERS=4
```

## 监控和调试

### 1. 队列状态监控
```python
from app.core.rq import queue_manager

# 获取队列统计
stats = queue_manager.get_all_queue_stats()
print(stats)
```

### 2. 任务状态查询
```python
from app.services.task_queue_service import task_queue_service

# 获取任务详情
task = await task_queue_service.get_task(db, task_id, user_id)
print(task.status, task.progress)
```

### 3. 日志查看
```bash
# 查看Worker日志
tail -f logs/ai_task_worker.log

# 查看任务队列服务日志
tail -f logs/task_queue_service.log
```

## 性能优化

### 1. Worker扩展
- 根据队列负载启动多个Worker进程
- 使用不同队列分离不同类型的任务
- 设置合理的任务超时时间

### 2. 队列优化
- 高优先级任务使用独立队列
- 设置合理的重试策略
- 定期清理过期任务

### 3. 数据库优化
- 为任务状态和类型添加索引
- 定期清理已完成的任务记录
- 使用连接池管理数据库连接

## 故障处理

### 1. Worker进程异常
- 检查Redis连接状态
- 查看Worker日志
- 重启Worker进程

### 2. 任务处理失败
- 检查任务输入数据
- 查看错误日志
- 手动重试或取消任务

### 3. 队列积压
- 增加Worker进程数量
- 检查任务处理性能
- 优化任务处理逻辑

## 扩展功能

### 1. WebSocket实时推送
- 任务状态变更时推送通知
- 实时进度更新
- 错误信息推送

### 2. 任务优先级动态调整
- 根据用户等级调整优先级
- 根据任务类型设置优先级
- 支持任务优先级修改

### 3. 任务结果缓存
- 相同输入的任务结果缓存
- 减少重复计算
- 提升响应速度
