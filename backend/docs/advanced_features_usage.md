# 第三阶段高级功能使用指南

## 概述

第三阶段实现了对话编排的高级功能，包括多角色支持、RAG知识注入和智能上下文管理。这些功能大大增强了AI角色扮演平台的交互能力和智能化水平。

## 核心功能

### 1. 多角色支持

#### 1.1 多角色模式

- **单角色模式 (SINGLE)**: 传统的单角色对话
- **多角色模式 (MULTIPLE)**: 多个角色同时参与对话
- **角色切换模式 (SWITCHING)**: 根据上下文智能选择角色

#### 1.2 角色回复策略

- **轮流回复 (ROUND_ROBIN)**: 角色轮流回复
- **基于优先级 (PRIORITY_BASED)**: 按优先级选择角色
- **基于上下文 (CONTEXT_AWARE)**: 根据消息内容选择最合适的角色
- **用户选择 (USER_CHOICE)**: 用户手动选择角色

#### 1.3 API使用示例

```python
import httpx
import asyncio

async def test_multi_character():
    """测试多角色功能"""
    async with httpx.AsyncClient() as client:
        token = "your-auth-token"
        conversation_id = "your-conversation-id"
        
        # 1. 添加角色到会话
        response = await client.post(
            f"http://localhost:8000/api/v1/multi-character/conversations/{conversation_id}/characters/{character_id}",
            json={"priority": 5},
            headers={"Authorization": f"Bearer {token}"}
        )
        print("添加角色:", response.json())
        
        # 2. 获取会话中的所有角色
        response = await client.get(
            f"http://localhost:8000/api/v1/multi-character/conversations/{conversation_id}/characters",
            headers={"Authorization": f"Bearer {token}"}
        )
        print("会话角色:", response.json())
        
        # 3. 更新角色优先级
        response = await client.put(
            f"http://localhost:8000/api/v1/multi-character/conversations/{conversation_id}/characters/{character_id}/priority",
            json={"priority": 8},
            headers={"Authorization": f"Bearer {token}"}
        )
        print("更新优先级:", response.json())
        
        # 4. 选择回复角色
        response = await client.post(
            f"http://localhost:8000/api/v1/multi-character/conversations/{conversation_id}/select-character",
            json={"user_message": "你好，请介绍一下自己"},
            headers={"Authorization": f"Bearer {token}"}
        )
        print("选中角色:", response.json())

asyncio.run(test_multi_character())
```

### 2. RAG知识注入

#### 2.1 知识库管理

支持创建和管理不同类型的知识库：
- **文本知识**: 纯文本内容
- **文档知识**: 文档内容
- **常见问题**: FAQ知识
- **角色背景**: 角色相关信息
- **世界观设定**: 世界观和背景设定

#### 2.2 知识搜索

使用向量相似度搜索相关知识，支持：
- 语义搜索
- 相关性评分
- 多知识库搜索
- 角色特定知识过滤

#### 2.3 API使用示例

```python
async def test_rag_features():
    """测试RAG功能"""
    async with httpx.AsyncClient() as client:
        token = "your-auth-token"
        
        # 1. 创建知识库
        response = await client.post(
            "http://localhost:8000/api/v1/knowledge/knowledge-bases",
            json={
                "name": "角色背景知识库",
                "description": "存储角色背景信息",
                "character_id": "character-uuid",
                "knowledge_type": "character_background",
                "source": "manual"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        kb_id = response.json()["knowledge_base"]["id"]
        print("知识库创建:", response.json())
        
        # 2. 添加知识条目
        response = await client.post(
            f"http://localhost:8000/api/v1/knowledge/knowledge-bases/{kb_id}/items",
            json={
                "title": "角色历史",
                "content": "这个角色有着丰富的历史背景，曾经是一名勇敢的骑士...",
                "summary": "角色历史背景",
                "tags": ["历史", "背景", "骑士"],
                "metadata": {"category": "background", "importance": "high"}
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        print("知识条目添加:", response.json())
        
        # 3. 搜索知识
        response = await client.post(
            "http://localhost:8000/api/v1/knowledge/search",
            json={
                "query": "角色历史",
                "knowledge_base_ids": [kb_id],
                "max_results": 5,
                "threshold": 0.7
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        print("知识搜索:", response.json())

asyncio.run(test_rag_features())
```

### 3. 智能上下文管理

#### 3.1 上下文摘要

当对话历史超过阈值时，自动生成摘要：
- 保留关键信息
- 压缩历史内容
- 维持对话连贯性

#### 3.2 动态上下文窗口

根据token限制优化上下文：
- 智能截断历史消息
- 保留重要信息
- 平衡性能和效果

#### 3.3 主题检测

自动检测对话主题：
- 关键词分析
- 主题分类
- 上下文理解

#### 3.4 使用示例

```python
# 在对话编排中使用智能上下文
async def send_message_with_advanced_context():
    """使用高级上下文发送消息"""
    async with httpx.AsyncClient() as client:
        token = "your-auth-token"
        conversation_id = "your-conversation-id"
        
        response = await client.post(
            f"http://localhost:8000/api/v1/orchestration/conversations/{conversation_id}/send-message",
            json={
                "message": "请介绍一下你的历史",
                "settings": {
                    "multi_character_mode": "switching",
                    "character_response_strategy": "context_aware",
                    "enable_context_summary": True,
                    "context_summary_threshold": 10,
                    "enable_rag": True,
                    "rag_threshold": 0.7,
                    "max_rag_results": 3,
                    "llm_provider": "deepseek",
                    "llm_model": "deepseek-chat"
                }
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        print("高级对话:", response.json())
```

## 配置说明

### 环境变量

```env
# 多角色配置
ENABLE_MULTI_CHARACTER=true
MAX_CHARACTERS_PER_CONVERSATION=5

# RAG配置
ENABLE_RAG=true
RAG_DEFAULT_THRESHOLD=0.7
RAG_MAX_RESULTS=5

# 上下文管理配置
ENABLE_CONTEXT_SUMMARY=true
CONTEXT_SUMMARY_THRESHOLD=15
MAX_CONTEXT_TOKENS=4000
```

### 会话设置参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `multi_character_mode` | string | "single" | 多角色模式 |
| `character_response_strategy` | string | "context_aware" | 角色回复策略 |
| `enable_character_switching` | bool | false | 是否启用角色切换 |
| `max_characters` | int | 3 | 最大角色数量 |
| `enable_context_summary` | bool | false | 是否启用上下文摘要 |
| `context_summary_threshold` | int | 15 | 上下文摘要阈值 |
| `enable_rag` | bool | false | 是否启用RAG |
| `rag_threshold` | float | 0.7 | RAG相关性阈值 |
| `max_rag_results` | int | 3 | 最大RAG结果数 |

## 使用场景

### 1. 多角色对话场景

```python
# 创建多角色对话会话
async def create_multi_character_conversation():
    """创建多角色对话会话"""
    async with httpx.AsyncClient() as client:
        token = "your-auth-token"
        
        # 创建会话
        response = await client.post(
            "http://localhost:8000/api/v1/conversations/",
            json={
                "title": "多角色对话",
                "character_id": "main-character-id",
                "settings": {
                    "multi_character_mode": "multiple",
                    "character_response_strategy": "round_robin",
                    "max_characters": 3,
                    "enable_context_summary": True
                }
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        conversation_id = response.json()["id"]
        
        # 添加多个角色
        characters = ["character-1", "character-2", "character-3"]
        for i, char_id in enumerate(characters):
            await client.post(
                f"http://localhost:8000/api/v1/multi-character/conversations/{conversation_id}/characters/{char_id}",
                json={"priority": i + 1},
                headers={"Authorization": f"Bearer {token}"}
            )
        
        return conversation_id
```

### 2. 知识增强对话

```python
# 使用RAG增强对话
async def rag_enhanced_conversation():
    """RAG增强对话"""
    async with httpx.AsyncClient() as client:
        token = "your-auth-token"
        conversation_id = "your-conversation-id"
        
        # 发送消息时启用RAG
        response = await client.post(
            f"http://localhost:8000/api/v1/orchestration/conversations/{conversation_id}/send-message",
            json={
                "message": "请告诉我关于这个世界的历史",
                "settings": {
                    "enable_rag": True,
                    "rag_threshold": 0.6,
                    "max_rag_results": 5,
                    "enable_context_summary": True
                }
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        result = response.json()
        print("角色回复:", result["character_response"])
        
        # 检查是否使用了RAG知识
        if "rag_knowledge" in result:
            print("使用的知识:", result["rag_knowledge"])
```

### 3. 智能角色切换

```python
# 智能角色切换对话
async def intelligent_character_switching():
    """智能角色切换"""
    async with httpx.AsyncClient() as client:
        token = "your-auth-token"
        conversation_id = "your-conversation-id"
        
        # 设置角色切换模式
        await client.put(
            f"http://localhost:8000/api/v1/orchestration/conversations/{conversation_id}/settings",
            json={
                "multi_character_mode": "switching",
                "character_response_strategy": "context_aware",
                "enable_character_switching": True
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # 发送不同类型的消息，观察角色切换
        messages = [
            "你好，请介绍一下自己",  # 可能选择介绍型角色
            "我需要技术帮助",        # 可能选择技术型角色
            "能讲个故事吗？"        # 可能选择故事型角色
        ]
        
        for message in messages:
            response = await client.post(
                f"http://localhost:8000/api/v1/orchestration/conversations/{conversation_id}/send-message",
                json={"message": message},
                headers={"Authorization": f"Bearer {token}"}
            )
            
            result = response.json()
            print(f"消息: {message}")
            print(f"回复角色: {result.get('character_name', '未知')}")
            print(f"回复内容: {result['character_response']}")
            print("-" * 50)
```

## 性能优化

### 1. 上下文管理优化

- 使用摘要减少token消耗
- 智能截断历史消息
- 缓存常用上下文

### 2. RAG搜索优化

- 向量索引优化
- 批量嵌入生成
- 结果缓存机制

### 3. 多角色优化

- 角色选择算法优化
- 并行处理多角色回复
- 智能负载均衡

## 故障排除

### 常见问题

1. **多角色回复不一致**
   - 检查角色优先级设置
   - 验证角色选择策略
   - 确认角色persona配置

2. **RAG搜索结果不准确**
   - 调整相关性阈值
   - 优化知识条目内容
   - 检查嵌入向量质量

3. **上下文摘要质量差**
   - 调整摘要阈值
   - 优化摘要提示词
   - 检查LLM模型选择

4. **角色切换不智能**
   - 优化上下文分析算法
   - 增加角色关键词
   - 调整选择策略

## 总结

第三阶段的高级功能为AI角色扮演平台带来了：

1. **多角色支持**: 支持复杂的多角色对话场景
2. **RAG知识注入**: 提供丰富的背景知识和上下文信息
3. **智能上下文管理**: 优化对话连贯性和性能
4. **高级策略调度**: 智能选择最适合的角色和回复策略

这些功能大大提升了平台的智能化水平和用户体验，为构建更真实、更有趣的AI角色扮演体验奠定了基础。
