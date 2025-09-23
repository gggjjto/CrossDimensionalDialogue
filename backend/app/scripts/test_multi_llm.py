"""
测试多LLM模型支持
"""

import asyncio
import uuid
from sqlmodel import Session

from app.core.db import engine
from app.core.config import settings
from app.services.llm_service import llm_service, LLMRequest
from app.models.character import Character
from app.models.conversation import Conversation


async def test_multi_llm():
    """测试多LLM模型"""
    print("开始测试多LLM模型支持...")

    # 测试消息
    test_messages = [
        {"role": "system", "content": "你是一个友好的AI助手。"},
        {"role": "user", "content": "你好，请简单介绍一下自己。"},
    ]

    # 测试各个提供商
    providers = ["openai", "deepseek", "qwen"]

    for provider in providers:
        print(f"\n=== 测试 {provider.upper()} ===")

        try:
            # 检查API密钥是否配置
            api_key_attr = f"{provider.upper()}_API_KEY"
            api_key = getattr(settings, api_key_attr, "")

            if not api_key:
                print(f"❌ {provider} API密钥未配置，跳过测试")
                continue

            # 创建请求
            request = LLMRequest(messages=test_messages)

            # 使用指定提供商生成回复
            response = await llm_service.generate_response_with_provider(
                messages=test_messages,
                provider=provider,
                temperature=0.7,
                max_tokens=200,
            )

            print(f"✅ {provider} 调用成功!")
            print(f"模型: {response.model}")
            print(f"回复: {response.content[:100]}...")
            print(f"Token使用: {response.usage}")

        except Exception as e:
            print(f"❌ {provider} 调用失败: {str(e)}")

    # 测试角色回复生成
    print(f"\n=== 测试角色回复生成 ===")

    try:
        with Session(engine) as session:
            # 创建测试角色
            test_character = Character(
                id=uuid.uuid4(),
                name="苏格拉底",
                short_bio="古希腊哲学家",
                persona_text="你是一个智慧、善于提问的哲学家，喜欢通过对话来启发思考。",
                example_lines=["我知道我一无所知", "未经审视的人生不值得过"],
                is_active=True,
            )

            # 创建测试会话
            test_conversation = Conversation(
                id=uuid.uuid4(),
                user_id=uuid.uuid4(),
                character_id=test_character.id,
                title="哲学对话",
                status="active",
            )

            # 使用默认提供商生成角色回复
            response = await llm_service.generate_character_response(
                character=test_character,
                conversation=test_conversation,
                user_message="什么是智慧？",
                session=session,
            )

            print(f"✅ 角色回复生成成功!")
            print(f"角色: {test_character.name}")
            print(f"模型: {response.model}")
            print(f"回复: {response.content}")

    except Exception as e:
        print(f"❌ 角色回复生成失败: {str(e)}")

    print("\n🎉 多LLM模型测试完成!")


if __name__ == "__main__":
    asyncio.run(test_multi_llm())
