# AI模块使用指南

## 概述

AI模块是一个统一的AI模型调用接口，用于解耦提示词和API调用，支持多模态和多供应商。通过这个模块，你可以轻松地在不同的AI模型提供商之间切换，而不需要修改业务逻辑代码。

## 核心特性

- **解耦设计**：提示词独立管理，API调用通过统一接口
- **多模态支持**：文生文、文生图、图生文、向量嵌入
- **多供应商支持**：OpenAI、DeepSeek、阿里千问、阿里云等
- **可扩展性**：易于添加新的模型供应商或模态
- **统一接口**：所有AI任务使用相同的调用方式

## 快速开始

### 1. 基本使用

```python
from app.services.ai_module import ai_service_manager

# 获取AI服务
service = ai_service_manager.get_service("deepseek_chat")

# 生成文本
response = await service.generate_text("请写一首关于春天的短诗")
print(response)
```

### 2. 角色对话

```python
# 角色数据
character_data = {
    "character_name": "小黄鸭",
    "character_description": "一只可爱的黄色小鸭子",
    "personality": "活泼开朗，喜欢帮助别人",
    "background": "生活在湖边，喜欢游泳和交朋友",
    "speaking_style": "语气轻松，经常使用"嘎嘎"等拟声词"
}

# 生成角色回复
response = await service.generate_character_response(
    character_data=character_data,
    user_message="你好，小黄鸭！今天天气怎么样？",
    context="用户第一次见到小黄鸭"
)
```

### 3. 图像生成

```python
# 使用阿里云通义万相生成图像
aliyun_service = ai_service_manager.get_service("aliyun_wanx")

# 生成角色图像
character_data = {
    "character_description": "一只可爱的黄色小鸭子，戴着蓝色帽子",
    "style": "anime",
    "quality": "high",
    "aspect_ratio": "1:1"
}

image_data = await aliyun_service.generate_character_image(character_data)

# 保存图像
with open("character_aliyun.png", "wb") as f:
    f.write(image_data)
```

### 4. 图像分析

```python
# 注意：当前AI模块不支持图像分析功能
# 如需图像分析功能，请使用其他服务或等待后续更新
logger.info("当前AI模块不支持图像分析功能")
```

### 5. 向量嵌入

```python
# 获取向量嵌入服务
embedding_service = ai_service_manager.get_service("aliyun_embedding")

# 单个文本嵌入
embedding = await embedding_service.generate_embedding("这是一只可爱的小黄鸭")

# 批量文本嵌入
texts = ["小黄鸭在湖里游泳", "小黄鸭喜欢吃面包屑"]
embeddings = await embedding_service.generate_embedding(texts)
```

## 配置说明

### 可用配置

AI模块支持以下预配置：

#### 文生文配置
- `deepseek_chat`: DeepSeek聊天模型
- `qwen_chat`: 阿里千问聊天模型

#### 文生图配置
- `aliyun_wanx`: 阿里云通义万相图像生成

#### 向量嵌入配置
- `aliyun_embedding`: 阿里云向量嵌入

### 自定义配置

你也可以通过参数直接创建提供商：

```python
from app.services.ai_module.factory import AIProviderFactory

# 创建自定义提供商
provider = AIProviderFactory.create_provider_by_params(
    provider="openai",
    modality="text_to_text",
    model="gpt-4",
    api_key="your-api-key",
    base_url="https://api.openai.com/v1"
)
```

## 提示词管理

### 内置提示词类型

#### 文本提示词
- `CharacterSystemPrompt`: 角色系统提示词
- `CharacterDialoguePrompt`: 角色对话提示词
- `GeneralTextPrompt`: 通用文本提示词
- `RAGPrompt`: RAG检索增强生成提示词

#### 图像提示词
- `CharacterImagePrompt`: 角色图像生成提示词
- `GeneralImagePrompt`: 通用图像生成提示词
- `SceneImagePrompt`: 场景图像生成提示词

#### 视觉提示词
- `ImageAnalysisPrompt`: 图像分析提示词
- `ImageDescriptionPrompt`: 图像描述提示词
- `ImageToTextPrompt`: 图像转文本提示词

### 自定义提示词

```python
from app.services.ai_module.prompts.base import BasePrompt, PromptType

class CustomPrompt(BasePrompt):
    def __init__(self):
        super().__init__(PromptType.USER)
    
    def build(self, **kwargs) -> str:
        return f"自定义提示词: {kwargs.get('content', '')}"

# 使用自定义提示词
prompt = CustomPrompt()
service = ai_service_manager.get_service("openai_gpt")
response = await service.generate_text(prompt.build(content="测试内容"))
```

## 服务管理

### 获取可用服务

```python
# 获取所有可用服务
services = ai_service_manager.get_available_services()

# 按模态获取服务
text_services = ai_service_manager.get_services_by_modality("text_to_text")
image_services = ai_service_manager.get_services_by_modality("text_to_image")

# 按提供商获取服务
openai_services = ai_service_manager.get_services_by_provider("openai")
```

### 服务信息

```python
service = ai_service_manager.get_service("openai_gpt")

# 获取服务信息
info = service.get_provider_info()
print(f"提供商: {info['provider']}")
print(f"模态: {info['modality']}")
print(f"模型: {info['model']}")

# 健康检查
health = await service.health_check()
print(f"服务状态: {'健康' if health else '异常'}")
```

## 错误处理

### 常见错误

1. **配置不存在**
```python
try:
    service = ai_service_manager.get_service("invalid_config")
except ValueError as e:
    print(f"配置错误: {e}")
```

2. **模态不匹配**
```python
try:
    text_service = ai_service_manager.get_service("openai_gpt")
    image_data = await text_service.generate_image("test")  # 错误：文本服务不能生成图像
except ValueError as e:
    print(f"模态错误: {e}")
```

3. **API调用失败**
```python
try:
    response = await service.generate_text("test")
except Exception as e:
    print(f"API调用失败: {e}")
```

## 最佳实践

### 1. 服务复用

```python
# 推荐：复用服务实例
class MyService:
    def __init__(self):
        self.text_service = ai_service_manager.get_service("openai_gpt")
        self.image_service = ai_service_manager.get_service("openai_dalle")
    
    async def process(self, text: str):
        return await self.text_service.generate_text(text)
```

### 2. 错误处理

```python
async def safe_generate(service, prompt):
    try:
        return await service.generate_text(prompt)
    except Exception as e:
        logger.error(f"生成失败: {e}")
        return "生成失败，请稍后重试"
```

### 3. 参数验证

```python
def validate_character_data(data: dict) -> bool:
    required_fields = ["character_name", "character_description", "personality"]
    return all(field in data for field in required_fields)
```

## 扩展指南

### 添加新的提供商

1. 在 `providers/` 目录下创建新的提供商类
2. 继承 `BaseAIProvider` 并实现必要方法
3. 在 `factory.py` 中添加创建逻辑
4. 在 `config.py` 中添加配置

### 添加新的提示词类型

1. 在 `prompts/` 目录下创建新的提示词类
2. 继承 `BasePrompt` 并实现 `build` 方法
3. 在 `prompts/__init__.py` 中导出

### 添加新的模态

1. 在 `config.py` 中添加新的模态枚举
2. 实现相应的提供商类
3. 在 `service.py` 中添加相应的生成方法

## 测试

运行测试脚本：

```bash
cd backend
python app/scripts/test_ai_module.py
```

这将测试所有功能，包括：
- 文本生成
- 角色对话
- 图像生成
- 图像分析
- 向量嵌入
- 服务管理

## 总结

AI模块提供了一个统一、灵活、可扩展的AI模型调用接口。通过解耦提示词和API调用，你可以：

- 轻松切换不同的AI模型提供商
- 统一管理各种AI任务
- 快速添加新的功能和提供商
- 保持代码的整洁和可维护性

这个模块设计遵循了SOLID原则，具有良好的可扩展性和可维护性，是构建AI应用的良好基础。
