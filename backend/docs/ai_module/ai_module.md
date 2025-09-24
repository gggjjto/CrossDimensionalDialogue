问题：我现在需要你设计一个模块，可以把AI 模型的API 和 提示词 解耦， 就是AI 模型因为要切换API的供应商，导致代码不同，但是提示词是相同的，并且会使用不同的 AI 模型，有时候是图生文，有时候是文生图

背景：项目在使用AI 模型时，每一次都没有解耦

gpt5.0的回复：

你这个需求我理解了：
你想要一个 解耦 AI 模型 API 调用和提示词 (Prompt) 的模块设计，这样在切换不同供应商（OpenAI、Anthropic、Moonshot、本地模型等）或者不同模态（文生文、文生图、图生文等）的时候，不需要改动业务逻辑里的提示词，只要改 API 接口的部分。

我给你一个 架构设计方案（Python/FastAPI 风格，模块化，便于扩展）：

设计目标

解耦 Prompt 与 API 调用：提示词配置独立存放，API 调用逻辑通过统一接口封装。

支持多模态：文生文（text → text）、文生图（text → image）、图生文（image → text）。

支持多供应商切换：只改配置，不改业务代码。

可扩展性：能新增新的模型供应商或模态。

模块结构
ai_module/
├── __init__.py
├── config.py              # 模型与供应商配置
├── prompts/
│   ├── __init__.py
│   ├── base.py            # Prompt 抽象基类
│   ├── text_prompts.py    # 文生文提示词
│   ├── image_prompts.py   # 文生图提示词
│   └── vision_prompts.py  # 图生文提示词
├── providers/
│   ├── __init__.py
│   ├── base.py            # Provider 抽象基类
│   ├── openai_provider.py # OpenAI 实现
│   ├── anthropic_provider.py
│   ├── local_provider.py
│   └── stabilityai_provider.py
├── service.py             # 核心服务层，组合 prompt 和 provider
└── factory.py             # Provider 工厂

关键代码示例
1. 配置文件 config.py
AI_PROVIDERS = {
    "openai_gpt": {
        "provider": "openai",
        "model": "gpt-4o-mini"
    },
    "anthropic_claude": {
        "provider": "anthropic",
        "model": "claude-3-5-sonnet"
    },
    "stability_ai": {
        "provider": "stabilityai",
        "model": "stable-diffusion-xl"
    }
}

2. Prompt 抽象 & 示例 prompts/base.py
from abc import ABC, abstractmethod

class BasePrompt(ABC):
    @abstractmethod
    def build(self, **kwargs) -> str:
        """生成提示词"""
        pass


class TextPrompt(BasePrompt):
    def build(self, topic: str, style: str = "default") -> str:
        return f"Write an article about {topic} in {style} style."

3. Provider 抽象 & 示例 providers/base.py
from abc import ABC, abstractmethod

class BaseProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str | bytes:
        """调用模型 API"""
        pass


示例：OpenAI 文生文 Provider

import openai
from .base import BaseProvider

class OpenAIProvider(BaseProvider):
    def __init__(self, model: str):
        self.model = model

    async def generate(self, prompt: str, **kwargs) -> str:
        resp = await openai.ChatCompletion.acreate(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return resp.choices[0].message["content"]

4. Provider 工厂 factory.py
from .providers.openai_provider import OpenAIProvider
from .providers.anthropic_provider import AnthropicProvider
from .providers.stabilityai_provider import StabilityAIProvider

def get_provider(name: str, model: str):
    if name == "openai":
        return OpenAIProvider(model)
    elif name == "anthropic":
        return AnthropicProvider(model)
    elif name == "stabilityai":
        return StabilityAIProvider(model)
    else:
        raise ValueError(f"Unknown provider: {name}")

5. 服务层 service.py
from .config import AI_PROVIDERS
from .factory import get_provider
from .prompts.text_prompts import TextPrompt

class AIService:
    def __init__(self, provider_key: str):
        cfg = AI_PROVIDERS[provider_key]
        self.provider = get_provider(cfg["provider"], cfg["model"])

    async def generate_text(self, topic: str, style: str = "default"):
        prompt = TextPrompt().build(topic=topic, style=style)
        return await self.provider.generate(prompt)

    async def generate_image(self, description: str):
        from .prompts.image_prompts import ImagePrompt
        prompt = ImagePrompt().build(description=description)
        return await self.provider.generate(prompt)

使用示例
from ai_module.service import AIService

service = AIService("openai_gpt")
text = await service.generate_text(topic="AI 模块解耦设计", style="technical")

service_img = AIService("stability_ai")
image_bytes = await service_img.generate_image(description="一只宇航员猫咪在月球上喝咖啡")


✅ 这样做后：

切换 API：只要在 config.py 里换 provider_key。

切换模态：调用 generate_text 或 generate_image 等函数。

新增供应商：只写一个新的 Provider 类，不影响 Prompt 和业务逻辑。