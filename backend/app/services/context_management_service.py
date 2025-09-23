"""
智能上下文管理服务
"""

import uuid
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple

from sqlmodel import Session

from app.models.conversation import Message, ConversationSettings, SenderType
from app.models.knowledge import KnowledgeSearchRequest, KnowledgeType
from app.crud.conversation import message as message_crud
from app.services.rag_service import rag_service
from app.services.llm_service import llm_service

logger = logging.getLogger(__name__)


class ContextManagementService:
    """智能上下文管理服务"""

    def __init__(self):
        self.rag_service = rag_service
        self.llm_service = llm_service

    async def build_conversation_context(
        self,
        db: Session,
        conversation_id: uuid.UUID,
        character_id: uuid.UUID,
        user_message: str,
        settings: ConversationSettings,
    ) -> Dict[str, Any]:
        """
        构建对话上下文

        Args:
            db: 数据库会话
            conversation_id: 会话ID
            character_id: 角色ID
            user_message: 用户消息
            settings: 会话设置

        Returns:
            Dict[str, Any]: 上下文信息
        """
        context = {
            "conversation_id": conversation_id,
            "character_id": character_id,
            "user_message": user_message,
            "settings": settings,
            "messages": [],
            "rag_knowledge": [],
            "summary": None,
            "context_length": 0,
        }

        # 获取历史消息
        recent_messages = message_crud.get_recent_messages(
            db, conversation_id=conversation_id, limit=settings.context_window_size
        )

        # 检查是否需要生成摘要
        if (
            settings.enable_context_summary
            and len(recent_messages) > settings.context_summary_threshold
        ):
            context["summary"] = await self._generate_context_summary(
                recent_messages[:-5]
            )  # 保留最近5条消息
            context["messages"] = recent_messages[-5:]  # 只使用最近5条消息
        else:
            context["messages"] = recent_messages

        # 如果启用RAG，搜索相关知识
        if settings.enable_rag:
            context["rag_knowledge"] = await self._search_relevant_knowledge(
                db, character_id, user_message, settings
            )

        context["context_length"] = len(context["messages"])

        return context

    async def _generate_context_summary(self, messages: List[Message]) -> str:
        """
        生成上下文摘要

        Args:
            messages: 消息列表

        Returns:
            str: 上下文摘要
        """
        try:
            # 构建摘要提示词
            conversation_text = ""
            for msg in messages:
                sender = "用户" if msg.sender_type == SenderType.USER else "角色"
                conversation_text += f"{sender}: {msg.content}\n"

            summary_prompt = f"""
请为以下对话生成一个简洁的摘要，保留关键信息和上下文：

{conversation_text}

摘要要求：
1. 控制在100字以内
2. 保留重要的对话主题和关键信息
3. 使用第三人称描述
4. 不要包含具体的对话内容，只描述主题和要点

摘要：
"""

            # 使用LLM生成摘要
            response = await self.llm_service.generate_response_with_provider(
                messages=[{"role": "user", "content": summary_prompt}],
                provider="openai",  # 使用OpenAI生成摘要
                temperature=0.3,  # 低温度确保稳定性
                max_tokens=150,
            )

            return response.content.strip()

        except Exception as e:
            logger.error(f"生成上下文摘要失败: {str(e)}")
            return "对话摘要生成失败"

    async def _search_relevant_knowledge(
        self,
        db: Session,
        character_id: uuid.UUID,
        user_message: str,
        settings: ConversationSettings,
    ) -> List[Dict[str, Any]]:
        """
        搜索相关知识

        Args:
            db: 数据库会话
            character_id: 角色ID
            user_message: 用户消息
            settings: 会话设置

        Returns:
            List[Dict[str, Any]]: 相关知识列表
        """
        try:
            # 构建搜索请求
            search_request = KnowledgeSearchRequest(
                query=user_message,
                character_id=character_id,
                knowledge_types=[
                    KnowledgeType.CHARACTER_BACKGROUND,
                    KnowledgeType.WORLD_BUILDING,
                ],
                max_results=settings.max_rag_results,
                threshold=settings.rag_threshold,
            )

            # 执行搜索
            results = await self.rag_service.search_knowledge(db, search_request)

            # 转换为字典格式
            knowledge_list = []
            for result in results:
                knowledge_list.append(
                    {
                        "title": result.knowledge_item.title,
                        "content": result.knowledge_item.content,
                        "summary": result.knowledge_item.summary,
                        "relevance_score": result.relevance_score,
                        "matched_content": result.matched_content,
                        "context": result.context,
                    }
                )

            return knowledge_list

        except Exception as e:
            logger.error(f"搜索相关知识失败: {str(e)}")
            return []

    def build_enhanced_prompt(self, character, context: Dict[str, Any]) -> str:
        """
        构建增强的提示词

        Args:
            character: 角色对象
            context: 上下文信息

        Returns:
            str: 增强的提示词
        """
        prompt_parts = []

        # 基础角色设定
        prompt_parts.append(f"你是{character.name}。")

        # 角色简介
        if character.short_bio:
            prompt_parts.append(f"简介：{character.short_bio}")

        # 角色persona
        if character.persona_text:
            prompt_parts.append(f"角色设定：{character.persona_text}")

        # 示例台词
        if character.example_lines:
            prompt_parts.append("示例台词：")
            for line in character.example_lines[:3]:
                prompt_parts.append(f"- {line}")

        # 添加上下文摘要
        if context.get("summary"):
            prompt_parts.append(f"\n对话背景：{context['summary']}")

        # 添加RAG知识
        if context.get("rag_knowledge"):
            prompt_parts.append("\n相关知识：")
            for knowledge in context["rag_knowledge"]:
                prompt_parts.append(f"- {knowledge['title']}: {knowledge['summary']}")

        # 对话要求
        prompt_parts.extend(
            [
                "",
                "请按照以上设定进行对话，保持角色的一致性。",
                "如果有相关知识，请自然地融入到回复中。",
                "回复要自然、有趣，符合角色的性格特点。",
                "每次回复控制在200字以内。",
            ]
        )

        return "\n".join(prompt_parts)

    def optimize_context_window(
        self, messages: List[Message], max_tokens: int = 4000
    ) -> List[Message]:
        """
        优化上下文窗口

        Args:
            messages: 消息列表
            max_tokens: 最大token数

        Returns:
            List[Message]: 优化后的消息列表
        """
        if not messages:
            return messages

        # 简单的token估算（实际应用中可以使用tiktoken等库）
        optimized_messages = []
        current_tokens = 0

        # 从最新消息开始添加
        for message in reversed(messages):
            message_tokens = len(message.content.split()) * 1.3  # 粗略估算

            if current_tokens + message_tokens > max_tokens:
                break

            optimized_messages.insert(0, message)
            current_tokens += message_tokens

        return optimized_messages

    def detect_conversation_topic(self, messages: List[Message]) -> Optional[str]:
        """
        检测对话主题

        Args:
            messages: 消息列表

        Returns:
            Optional[str]: 检测到的主题
        """
        if not messages:
            return None

        # 简单的关键词提取
        recent_messages = messages[-5:]  # 只看最近5条消息
        all_text = " ".join([msg.content for msg in recent_messages])

        # 常见主题关键词
        topic_keywords = {
            "技术": ["代码", "编程", "算法", "技术", "开发", "软件"],
            "生活": ["吃饭", "睡觉", "工作", "学习", "生活", "日常"],
            "娱乐": ["游戏", "电影", "音乐", "娱乐", "休闲", "放松"],
            "学习": ["学习", "教育", "知识", "课程", "考试", "作业"],
            "工作": ["工作", "项目", "会议", "任务", "职业", "事业"],
        }

        topic_scores = {}
        for topic, keywords in topic_keywords.items():
            score = sum(1 for keyword in keywords if keyword in all_text)
            if score > 0:
                topic_scores[topic] = score

        if topic_scores:
            return max(topic_scores, key=topic_scores.get)

        return None


# 全局上下文管理服务实例
context_management_service = ContextManagementService()
