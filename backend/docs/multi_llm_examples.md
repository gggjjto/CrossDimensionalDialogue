# 多LLM模型使用示例

## 概述

对话编排服务现在支持多种LLM提供商，包括OpenAI、DeepSeek和阿里千问。用户可以在会话级别选择不同的模型来生成角色回复。

## 支持的模型

### OpenAI
- **模型**: `gpt-3.5-turbo`, `gpt-4`, `gpt-4-turbo`
- **特点**: 通用性强，回复质量高
- **适用场景**: 日常对话、创意写作、复杂推理

### DeepSeek
- **模型**: `deepseek-chat`, `deepseek-coder`
- **特点**: 性价比高，中文理解能力强
- **适用场景**: 中文对话、代码生成、技术问答

### 阿里千问
- **模型**: `qwen-turbo`, `qwen-plus`, `qwen-max`
- **特点**: 中文优化，多模态支持
- **适用场景**: 中文对话、知识问答、多语言支持

## 使用示例

### 1. 基础模型切换

```python
import httpx
import asyncio

async def test_model_switching():
    """测试模型切换"""
    async with httpx.AsyncClient() as client:
        conversation_id = "your-conversation-id"
        token = "your-auth-token"
        
        # 使用OpenAI模型
        response1 = await client.post(
            f"http://localhost:8000/api/v1/orchestration/conversations/{conversation_id}/send-message",
            json={
                "message": "请介绍一下人工智能的发展历史",
                "settings": {
                    "llm_provider": "openai",
                    "llm_model": "gpt-3.5-turbo",
                    "temperature": 0.7
                }
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # 使用DeepSeek模型
        response2 = await client.post(
            f"http://localhost:8000/api/v1/orchestration/conversations/{conversation_id}/send-message",
            json={
                "message": "请介绍一下人工智能的发展历史",
                "settings": {
                    "llm_provider": "deepseek",
                    "llm_model": "deepseek-chat",
                    "temperature": 0.7
                }
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # 使用千问模型
        response3 = await client.post(
            f"http://localhost:8000/api/v1/orchestration/conversations/{conversation_id}/send-message",
            json={
                "message": "请介绍一下人工智能的发展历史",
                "settings": {
                    "llm_provider": "qwen",
                    "llm_model": "qwen-turbo",
                    "temperature": 0.7
                }
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        print("OpenAI回复:", response1.json()["character_response"])
        print("DeepSeek回复:", response2.json()["character_response"])
        print("千问回复:", response3.json()["character_response"])

# 运行示例
asyncio.run(test_model_switching())
```

### 2. 角色特定模型配置

```python
async def setup_character_models():
    """为不同角色配置不同模型"""
    async with httpx.AsyncClient() as client:
        token = "your-auth-token"
        
        # 哲学家角色 - 使用GPT-4进行深度思考
        philosopher_conversation = await client.post(
            "http://localhost:8000/api/v1/conversations/",
            json={
                "character_id": "philosopher-character-id",
                "title": "哲学对话",
                "settings": {
                    "llm_provider": "openai",
                    "llm_model": "gpt-4",
                    "temperature": 0.3,  # 更稳定的思考
                    "max_tokens": 2000
                }
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # 程序员角色 - 使用DeepSeek进行代码生成
        programmer_conversation = await client.post(
            "http://localhost:8000/api/v1/conversations/",
            json={
                "character_id": "programmer-character-id", 
                "title": "编程对话",
                "settings": {
                    "llm_provider": "deepseek",
                    "llm_model": "deepseek-coder",
                    "temperature": 0.1,  # 更精确的代码
                    "max_tokens": 1500
                }
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # 中文助手 - 使用千问进行中文对话
        chinese_helper_conversation = await client.post(
            "http://localhost:8000/api/v1/conversations/",
            json={
                "character_id": "chinese-helper-character-id",
                "title": "中文助手",
                "settings": {
                    "llm_provider": "qwen",
                    "llm_model": "qwen-plus",
                    "temperature": 0.8,  # 更自然的对话
                    "max_tokens": 1000
                }
            },
            headers={"Authorization": f"Bearer {token}"}
        )

asyncio.run(setup_character_models())
```

### 3. 动态模型选择

```python
async def dynamic_model_selection():
    """根据消息内容动态选择模型"""
    async with httpx.AsyncClient() as client:
        conversation_id = "your-conversation-id"
        token = "your-auth-token"
        
        messages = [
            "请写一个Python函数来计算斐波那契数列",  # 代码生成
            "请解释一下量子计算的基本原理",  # 知识问答
            "请帮我写一首关于春天的诗",  # 创意写作
        ]
        
        for message in messages:
            # 根据消息内容选择模型
            if "函数" in message or "代码" in message:
                provider = "deepseek"
                model = "deepseek-coder"
                temperature = 0.1
            elif "解释" in message or "原理" in message:
                provider = "openai"
                model = "gpt-4"
                temperature = 0.3
            else:
                provider = "qwen"
                model = "qwen-plus"
                temperature = 0.8
            
            response = await client.post(
                f"http://localhost:8000/api/v1/orchestration/conversations/{conversation_id}/send-message",
                json={
                    "message": message,
                    "settings": {
                        "llm_provider": provider,
                        "llm_model": model,
                        "temperature": temperature
                    }
                },
                headers={"Authorization": f"Bearer {token}"}
            )
            
            result = response.json()
            print(f"消息: {message}")
            print(f"使用模型: {provider}/{model}")
            print(f"回复: {result['character_response']}")
            print("-" * 50)

asyncio.run(dynamic_model_selection())
```

### 4. 模型性能对比

```python
async def compare_model_performance():
    """对比不同模型的性能"""
    import time
    
    async with httpx.AsyncClient() as client:
        conversation_id = "your-conversation-id"
        token = "your-auth-token"
        
        test_message = "请详细解释一下机器学习中的梯度下降算法"
        
        models = [
            {"provider": "openai", "model": "gpt-3.5-turbo"},
            {"provider": "deepseek", "model": "deepseek-chat"},
            {"provider": "qwen", "model": "qwen-turbo"}
        ]
        
        results = []
        
        for model_config in models:
            start_time = time.time()
            
            response = await client.post(
                f"http://localhost:8000/api/v1/orchestration/conversations/{conversation_id}/send-message",
                json={
                    "message": test_message,
                    "settings": {
                        "llm_provider": model_config["provider"],
                        "llm_model": model_config["model"],
                        "temperature": 0.7,
                        "max_tokens": 1000
                    }
                },
                headers={"Authorization": f"Bearer {token}"}
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            result = response.json()
            results.append({
                "provider": model_config["provider"],
                "model": model_config["model"],
                "response_time": response_time,
                "response_length": len(result["character_response"]),
                "usage": result.get("usage", {}),
                "content": result["character_response"][:100] + "..."
            })
        
        # 输出对比结果
        print("模型性能对比:")
        print("-" * 80)
        for result in results:
            print(f"提供商: {result['provider']}")
            print(f"模型: {result['model']}")
            print(f"响应时间: {result['response_time']:.2f}秒")
            print(f"回复长度: {result['response_length']}字符")
            print(f"Token使用: {result['usage']}")
            print(f"回复预览: {result['content']}")
            print("-" * 80)

asyncio.run(compare_model_performance())
```

## 最佳实践

### 1. 模型选择策略

- **通用对话**: OpenAI GPT-3.5-turbo
- **代码生成**: DeepSeek Coder
- **中文对话**: 阿里千问
- **复杂推理**: OpenAI GPT-4
- **成本敏感**: DeepSeek Chat

### 2. 参数调优

- **温度参数**:
  - 0.1-0.3: 精确、一致的回答
  - 0.7-0.9: 平衡创造性和一致性
  - 1.0-1.2: 高创造性，适合创意任务

- **Token限制**:
  - 500-1000: 简短回答
  - 1000-2000: 中等长度回答
  - 2000+: 详细回答

### 3. 错误处理

```python
async def robust_model_calling():
    """健壮的模型调用"""
    models_to_try = [
        {"provider": "openai", "model": "gpt-3.5-turbo"},
        {"provider": "deepseek", "model": "deepseek-chat"},
        {"provider": "qwen", "model": "qwen-turbo"}
    ]
    
    for model_config in models_to_try:
        try:
            response = await client.post(
                f"http://localhost:8000/api/v1/orchestration/conversations/{conversation_id}/send-message",
                json={
                    "message": "你好",
                    "settings": {
                        "llm_provider": model_config["provider"],
                        "llm_model": model_config["model"]
                    }
                },
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 200:
                return response.json()
                
        except Exception as e:
            print(f"模型 {model_config['provider']} 调用失败: {e}")
            continue
    
    raise Exception("所有模型都调用失败")
```

## 总结

多LLM支持为AI角色扮演平台提供了更大的灵活性：

1. **成本优化**: 可以根据任务复杂度选择合适的模型
2. **质量提升**: 不同模型在不同领域有各自的优势
3. **可靠性增强**: 多模型备份提高系统可用性
4. **个性化体验**: 用户可以根据偏好选择模型

通过合理配置和使用多模型功能，可以为用户提供更好的AI对话体验。
