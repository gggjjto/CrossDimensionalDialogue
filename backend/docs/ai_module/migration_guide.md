# AI模块迁移指南

## 概述

本指南将帮助你将现有的AI服务迁移到新的统一AI模块。新的AI模块提供了更好的解耦设计、统一的接口和更强的可扩展性。

## 迁移优势

- **统一接口**：所有AI任务使用相同的调用方式
- **解耦设计**：提示词和API调用完全分离
- **多模态支持**：支持文生文、文生图、图生文、向量嵌入
- **多供应商支持**：轻松切换不同的AI模型提供商
- **更好的错误处理**：统一的错误处理机制
- **可扩展性**：易于添加新的提供商和模态

## 迁移步骤

### 1. LLM服务迁移

#### 原有代码
```python
from app.services.llm_service import llm_service

# 生成回复
request = LLMRequest(
    messages=[{"role": "user", "content": "你好"}],
    temperature=0.7,
    max_tokens=1000
)
response = await llm_service.generate_response(request)
```

#### 新代码
```python
from app.services.ai_module import ai_service_manager

# 获取服务
service = ai_service_manager.get_service("openai_gpt")

# 生成回复
response = await service.generate_text("你好", temperature=0.7, max_tokens=1000)
```

#### 角色对话迁移

#### 原有代码
```python
response = await llm_service.generate_character_response(
    character=character,
    user_message="你好",
    conversation_history=messages,
    temperature=0.7
)
```

#### 新代码
```python
character_data = {
    "character_name": character.name,
    "character_description": character.description,
    "personality": character.personality,
    "background": character.background,
    "speaking_style": character.speaking_style
}

response = await service.generate_character_response(
    character_data=character_data,
    user_message="你好",
    conversation_history=messages,
    temperature=0.7
)
```

### 2. 图像生成服务迁移

#### 原有代码
```python
from app.services.character_image_service import character_image_service

image_url = await character_image_service.generate_character_image(
    character=character,
    style="anime",
    size="1024x1024"
)
```

#### 新代码
```python
from app.services.ai_module import ai_service_manager

# 使用阿里云通义万相生成图像
aliyun_service = ai_service_manager.get_service("aliyun_wanx")

# 生成角色图像
character_data = {
    "character_description": f"{character.name}: {character.description}",
    "style": "anime",
    "quality": "high",
    "aspect_ratio": "1:1"
}

image_data = await aliyun_service.generate_character_image(character_data)
```

### 3. 向量嵌入服务迁移

#### 原有代码
```python
from app.services.embedding_service import embedding_service

embedding = await embedding_service.generate_embedding("文本内容")
```

#### 新代码
```python
from app.services.ai_module import ai_service_manager

# 获取向量嵌入服务
embedding_service = ai_service_manager.get_service("aliyun_embedding")

# 生成向量嵌入
embedding = await embedding_service.generate_embedding("文本内容")
```

## 配置迁移

### 环境变量

确保以下环境变量已正确配置：

```bash
# OpenAI配置
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# DeepSeek配置
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_BASE_URL=https://api.deepseek.com

# 阿里千问配置
QWEN_API_KEY=your_qwen_api_key
QWEN_MODEL=qwen-turbo
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1

# 阿里云配置
ALIYUN_API_KEY=your_aliyun_api_key
ALIYUN_EMBEDDING_MODEL=text-embedding-v4
```

### 服务配置

AI模块会自动读取这些环境变量并创建相应的配置。你可以在 `app/services/ai_module/config.py` 中查看和修改配置。

## 渐进式迁移

### 阶段1：并行运行

在迁移初期，建议保持原有服务和新的AI模块并行运行：

```python
# 在服务类中同时支持两种方式
class MyService:
    def __init__(self):
        # 原有服务
        self.llm_service = llm_service
        self.image_service = character_image_service
        
        # 新AI模块
        self.ai_service_manager = ai_service_manager
    
    async def generate_response(self, use_new_module=True):
        if use_new_module:
            service = self.ai_service_manager.get_service("openai_gpt")
            return await service.generate_text("test")
        else:
            request = LLMRequest(messages=[{"role": "user", "content": "test"}])
            response = await self.llm_service.generate_response(request)
            return response.content
```

### 阶段2：逐步替换

逐步将各个功能迁移到新的AI模块：

```python
# 1. 先迁移简单的文本生成
async def simple_text_generation():
    service = ai_service_manager.get_service("openai_gpt")
    return await service.generate_text("简单文本生成")

# 2. 然后迁移角色对话
async def character_dialogue():
    service = ai_service_manager.get_service("qwen_chat")
    return await service.generate_character_response(...)

# 3. 最后迁移复杂的图像生成
async def image_generation():
    service = ai_service_manager.get_service("openai_dalle")
    return await service.generate_character_image(...)
```

### 阶段3：完全迁移

当所有功能都迁移完成后，可以移除原有的服务依赖：

```python
# 移除原有导入
# from app.services.llm_service import llm_service
# from app.services.character_image_service import character_image_service

# 只使用新的AI模块
from app.services.ai_module import ai_service_manager
```

## 常见问题

### Q: 如何处理不同提供商的API差异？

A: AI模块已经处理了这些差异，你只需要使用统一的接口即可。例如：

```python
# 无论是OpenAI、DeepSeek还是千问，都使用相同的接口
service = ai_service_manager.get_service("openai_gpt")  # 或 "deepseek_chat", "qwen_chat"
response = await service.generate_text("test")
```

### Q: 如何添加新的AI提供商？

A: 在 `app/services/ai_module/providers/` 目录下创建新的提供商类，继承 `BaseAIProvider` 并实现必要方法，然后在 `factory.py` 中添加创建逻辑。

### Q: 如何处理提示词的差异？

A: AI模块提供了统一的提示词管理。你可以使用内置的提示词类，或者创建自定义提示词：

```python
from app.services.ai_module.prompts import CharacterSystemPrompt

prompt = CharacterSystemPrompt()
system_message = prompt.build_message(
    character_name="小黄鸭",
    character_description="可爱的黄色小鸭子",
    personality="活泼开朗"
)
```

### Q: 如何保持向后兼容性？

A: 可以创建适配器类来保持向后兼容：

```python
class LLMServiceAdapter:
    """LLM服务适配器，保持向后兼容"""
    
    def __init__(self):
        self.ai_service = ai_service_manager.get_service("openai_gpt")
    
    async def generate_response(self, request: LLMRequest) -> LLMResponse:
        content = await self.ai_service.generate_text(
            request.messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        return LLMResponse(content=content, model=self.ai_service.config["model"])
```

## 测试迁移

### 1. 运行测试脚本

```bash
cd backend
python app/scripts/test_ai_module.py
```

### 2. 对比测试

创建对比测试来验证迁移的正确性：

```python
async def compare_services():
    # 原有服务
    old_response = await old_llm_service.generate_response(request)
    
    # 新AI模块
    new_service = ai_service_manager.get_service("openai_gpt")
    new_response = await new_service.generate_text(request.messages[0]["content"])
    
    # 比较结果
    assert old_response.content == new_response
```

### 3. 性能测试

```python
import time

async def performance_test():
    start_time = time.time()
    
    # 测试新AI模块的性能
    service = ai_service_manager.get_service("openai_gpt")
    for i in range(10):
        await service.generate_text(f"测试消息 {i}")
    
    end_time = time.time()
    print(f"新AI模块耗时: {end_time - start_time:.2f}秒")
```

## 迁移检查清单

- [ ] 环境变量配置正确
- [ ] AI模块测试通过
- [ ] 原有功能迁移完成
- [ ] 新功能测试通过
- [ ] 性能对比测试
- [ ] 错误处理测试
- [ ] 文档更新
- [ ] 团队培训完成

## 总结

AI模块的迁移是一个渐进的过程，建议分阶段进行。新的AI模块提供了更好的架构设计和更强的可扩展性，值得投入时间进行迁移。如果在迁移过程中遇到问题，可以参考测试脚本或联系开发团队。
