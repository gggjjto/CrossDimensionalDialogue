"""
测试LLM服务
"""

import asyncio
import uuid
from sqlmodel import Session

from app.core.db import engine
from app.services.llm_service import llm_service, LLMRequest
from app.models.character import Character
from app.models.conversation import Conversation


async def test_llm_service():
    """测试LLM服务"""
    print("开始测试LLM服务...")

    # 测试基础LLM调用
    try:
        messages = [
            {"role": "system", "content": "你是一个友好的AI助手。"},
            {"role": "user", "content": "你好，请介绍一下自己。"},
        ]

        request = LLMRequest(messages=messages)
        response = await llm_service.generate_response(request)

        print(f"✅ LLM调用成功!")
        print(f"回复内容: {response.content}")
        print(f"使用模型: {response.model}")
        print(f"Token使用: {response.usage}")

    except Exception as e:
        print(f"❌ LLM调用失败: {str(e)}")
        return False

    # 测试角色回复生成
    try:
        with Session(engine) as session:
            # 创建一个测试角色
            test_character = Character(
                id=uuid.uuid4(),
                name="测试角色",
                short_bio="一个友好的测试角色",
                persona_text="你是一个友好、有趣的测试角色，喜欢帮助用户解决问题。",
                example_lines=["你好！我是测试角色", "有什么可以帮助你的吗？"],
                is_active=True,
            )

            # 创建一个测试会话
            test_conversation = Conversation(
                id=uuid.uuid4(),
                user_id=uuid.uuid4(),
                character_id=test_character.id,
                title="测试会话",
                status="active",
            )

            # 生成角色回复
            response = await llm_service.generate_character_response(
                character=test_character,
                conversation=test_conversation,
                user_message="你好，请介绍一下自己",
                session=session,
            )

            print(f"✅ 角色回复生成成功!")
            print(f"角色回复: {response.content}")
            print(f"使用模型: {response.model}")

    except Exception as e:
        print(f"❌ 角色回复生成失败: {str(e)}")
        return False

    print("🎉 LLM服务测试完成!")
    return True


if __name__ == "__main__":
    asyncio.run(test_llm_service())
