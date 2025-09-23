"""
测试第三阶段高级功能
"""

import asyncio
import uuid
from sqlmodel import Session

from app.core.db import engine
from app.core.config import settings
from app.models.conversation import (
    ConversationSettings,
    MultiCharacterMode,
    CharacterResponseStrategy,
)
from app.models.knowledge import (
    KnowledgeBase,
    KnowledgeBaseCreate,
    KnowledgeItemCreate,
    KnowledgeSearchRequest,
    KnowledgeType,
    KnowledgeSource,
)
from app.services.multi_character_service import multi_character_service
from app.services.rag_service import rag_service
from app.services.context_management_service import context_management_service


async def test_advanced_features():
    """测试第三阶段高级功能"""
    print("开始测试第三阶段高级功能...")

    with Session(engine) as session:
        # 测试多角色功能
        await test_multi_character_features(session)

        # 测试RAG功能
        await test_rag_features(session)

        # 测试上下文管理功能
        await test_context_management_features(session)

    print("\n🎉 第三阶段高级功能测试完成!")


async def test_multi_character_features(session: Session):
    """测试多角色功能"""
    print("\n=== 测试多角色功能 ===")

    try:
        # 创建测试会话ID
        test_conversation_id = uuid.uuid4()
        test_character_id = uuid.uuid4()

        # 测试添加角色到会话
        print("测试添加角色到会话...")
        multi_char_conv = multi_character_service.add_character_to_conversation(
            session, test_conversation_id, test_character_id, priority=5
        )
        print(f"✅ 角色添加成功: {multi_char_conv.id}")

        # 测试获取会话角色
        print("测试获取会话角色...")
        characters = multi_character_service.get_conversation_characters(
            session, test_conversation_id
        )
        print(f"✅ 获取到 {len(characters)} 个角色")

        # 测试更新角色优先级
        print("测试更新角色优先级...")
        success = multi_character_service.update_character_priority(
            session, test_conversation_id, test_character_id, priority=8
        )
        print(f"✅ 优先级更新: {success}")

        # 测试角色选择策略
        print("测试角色选择策略...")
        settings = ConversationSettings(
            character_response_strategy=CharacterResponseStrategy.CONTEXT_AWARE
        )
        selected_character = multi_character_service.select_responding_character(
            session, test_conversation_id, "你好，请介绍一下自己", settings
        )
        print(
            f"✅ 选中角色: {selected_character.name if selected_character else 'None'}"
        )

        # 清理测试数据
        multi_character_service.remove_character_from_conversation(
            session, test_conversation_id, test_character_id
        )
        print("✅ 测试数据清理完成")

    except Exception as e:
        print(f"❌ 多角色功能测试失败: {str(e)}")


async def test_rag_features(session: Session):
    """测试RAG功能"""
    print("\n=== 测试RAG功能 ===")

    try:
        # 创建测试知识库
        print("创建测试知识库...")
        kb_create = KnowledgeBaseCreate(
            name="测试知识库",
            description="用于测试的知识库",
            knowledge_type=KnowledgeType.CHARACTER_BACKGROUND,
            source=KnowledgeSource.MANUAL,
        )

        kb = KnowledgeBase(
            name=kb_create.name,
            description=kb_create.description,
            knowledge_type=kb_create.knowledge_type,
            source=kb_create.source,
        )

        session.add(kb)
        session.commit()
        session.refresh(kb)
        print(f"✅ 知识库创建成功: {kb.id}")

        # 添加知识条目
        print("添加知识条目...")
        knowledge_item = await rag_service.add_knowledge_item(
            session=session,
            knowledge_base_id=kb.id,
            title="角色背景知识",
            content="这是一个测试角色的背景知识，包含角色的历史、性格特点和重要经历。",
            summary="角色背景信息",
            tags=["角色", "背景", "测试"],
            metadata={"category": "character", "importance": "high"},
        )
        print(f"✅ 知识条目添加成功: {knowledge_item.id}")

        # 测试知识搜索
        print("测试知识搜索...")
        search_request = KnowledgeSearchRequest(
            query="角色背景", knowledge_base_ids=[kb.id], max_results=3, threshold=0.5
        )

        results = await rag_service.search_knowledge(session, search_request)
        print(f"✅ 搜索到 {len(results)} 个相关结果")

        for result in results:
            print(
                f"  - {result.knowledge_item.title} (相关性: {result.relevance_score:.3f})"
            )

        # 清理测试数据
        session.delete(knowledge_item)
        session.delete(kb)
        session.commit()
        print("✅ 测试数据清理完成")

    except Exception as e:
        print(f"❌ RAG功能测试失败: {str(e)}")


async def test_context_management_features(session: Session):
    """测试上下文管理功能"""
    print("\n=== 测试上下文管理功能 ===")

    try:
        # 测试上下文构建
        print("测试上下文构建...")
        test_conversation_id = uuid.uuid4()
        test_character_id = uuid.uuid4()
        test_user_message = "你好，请介绍一下自己"

        settings = ConversationSettings(
            context_window_size=10,
            enable_context_summary=True,
            context_summary_threshold=5,
            enable_rag=True,
            rag_threshold=0.7,
            max_rag_results=3,
        )

        context = await context_management_service.build_conversation_context(
            session,
            test_conversation_id,
            test_character_id,
            test_user_message,
            settings,
        )

        print(f"✅ 上下文构建成功")
        print(f"  - 消息数量: {context['context_length']}")
        print(f"  - 是否有摘要: {context['summary'] is not None}")
        print(f"  - RAG知识数量: {len(context['rag_knowledge'])}")

        # 测试主题检测
        print("测试主题检测...")
        from app.models.conversation import Message, SenderType
        from datetime import datetime

        test_messages = [
            Message(
                id=uuid.uuid4(),
                conversation_id=test_conversation_id,
                sender_type=SenderType.USER,
                content="我想学习Python编程",
                created_at=datetime.utcnow(),
            ),
            Message(
                id=uuid.uuid4(),
                conversation_id=test_conversation_id,
                sender_type=SenderType.CHARACTER,
                content="Python是一门很好的编程语言",
                created_at=datetime.utcnow(),
            ),
        ]

        topic = context_management_service.detect_conversation_topic(test_messages)
        print(f"✅ 检测到主题: {topic}")

        # 测试上下文窗口优化
        print("测试上下文窗口优化...")
        optimized_messages = context_management_service.optimize_context_window(
            test_messages, max_tokens=100
        )
        print(f"✅ 优化后消息数量: {len(optimized_messages)}")

    except Exception as e:
        print(f"❌ 上下文管理功能测试失败: {str(e)}")


if __name__ == "__main__":
    asyncio.run(test_advanced_features())
