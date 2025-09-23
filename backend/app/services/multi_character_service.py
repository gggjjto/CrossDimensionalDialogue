"""
多角色管理服务
"""

import uuid
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any

from sqlmodel import Session, select

from app.models.conversation import (
    MultiCharacterConversation,
    ConversationSettings,
    MultiCharacterMode,
    CharacterResponseStrategy,
)
from app.models.character import Character
from app.crud.character import character as character_crud

logger = logging.getLogger(__name__)


class MultiCharacterService:
    """多角色管理服务"""

    def __init__(self):
        pass

    def add_character_to_conversation(
        self,
        db: Session,
        conversation_id: uuid.UUID,
        character_id: uuid.UUID,
        priority: int = 1,
    ) -> MultiCharacterConversation:
        """
        添加角色到多角色会话

        Args:
            db: 数据库会话
            conversation_id: 会话ID
            character_id: 角色ID
            priority: 角色优先级

        Returns:
            MultiCharacterConversation: 多角色会话记录
        """
        # 检查角色是否存在
        character = character_crud.get(db, id=character_id)
        if not character:
            raise ValueError(f"角色不存在: {character_id}")

        # 检查是否已经添加过
        existing = db.exec(
            select(MultiCharacterConversation).where(
                MultiCharacterConversation.conversation_id == conversation_id,
                MultiCharacterConversation.character_id == character_id,
            )
        ).first()

        if existing:
            raise ValueError("角色已经存在于会话中")

        # 创建多角色会话记录
        multi_char_conv = MultiCharacterConversation(
            conversation_id=conversation_id,
            character_id=character_id,
            priority=priority,
            is_active=True,
        )

        db.add(multi_char_conv)
        db.commit()
        db.refresh(multi_char_conv)

        logger.info(f"角色 {character.name} 已添加到会话 {conversation_id}")
        return multi_char_conv

    def remove_character_from_conversation(
        self, db: Session, conversation_id: uuid.UUID, character_id: uuid.UUID
    ) -> bool:
        """
        从多角色会话中移除角色

        Args:
            db: 数据库会话
            conversation_id: 会话ID
            character_id: 角色ID

        Returns:
            bool: 是否成功移除
        """
        multi_char_conv = db.exec(
            select(MultiCharacterConversation).where(
                MultiCharacterConversation.conversation_id == conversation_id,
                MultiCharacterConversation.character_id == character_id,
            )
        ).first()

        if not multi_char_conv:
            return False

        db.delete(multi_char_conv)
        db.commit()

        logger.info(f"角色 {character_id} 已从会话 {conversation_id} 中移除")
        return True

    def get_conversation_characters(
        self, db: Session, conversation_id: uuid.UUID, active_only: bool = True
    ) -> List[MultiCharacterConversation]:
        """
        获取会话中的所有角色

        Args:
            db: 数据库会话
            conversation_id: 会话ID
            active_only: 是否只返回激活的角色

        Returns:
            List[MultiCharacterConversation]: 多角色会话记录列表
        """
        query = select(MultiCharacterConversation).where(
            MultiCharacterConversation.conversation_id == conversation_id
        )

        if active_only:
            query = query.where(MultiCharacterConversation.is_active == True)

        query = query.order_by(MultiCharacterConversation.priority.desc())

        return db.exec(query).all()

    def select_responding_character(
        self,
        db: Session,
        conversation_id: uuid.UUID,
        user_message: str,
        settings: ConversationSettings,
    ) -> Optional[Character]:
        """
        根据策略选择回复的角色

        Args:
            db: 数据库会话
            conversation_id: 会话ID
            user_message: 用户消息
            settings: 会话设置

        Returns:
            Optional[Character]: 选中的角色
        """
        characters = self.get_conversation_characters(db, conversation_id)

        if not characters:
            return None

        if len(characters) == 1:
            character = character_crud.get(db, id=characters[0].character_id)
            return character

        # 根据策略选择角色
        if (
            settings.character_response_strategy
            == CharacterResponseStrategy.ROUND_ROBIN
        ):
            return self._select_by_round_robin(db, characters)
        elif (
            settings.character_response_strategy
            == CharacterResponseStrategy.PRIORITY_BASED
        ):
            return self._select_by_priority(db, characters)
        elif (
            settings.character_response_strategy
            == CharacterResponseStrategy.CONTEXT_AWARE
        ):
            return self._select_by_context(db, characters, user_message)
        else:
            # 默认使用优先级策略
            return self._select_by_priority(db, characters)

    def _select_by_round_robin(
        self, db: Session, characters: List[MultiCharacterConversation]
    ) -> Optional[Character]:
        """轮流选择角色"""
        # 找到最久没有回复的角色
        oldest_response = min(
            characters, key=lambda c: c.last_response_at or datetime.min
        )

        character = character_crud.get(db, id=oldest_response.character_id)
        return character

    def _select_by_priority(
        self, db: Session, characters: List[MultiCharacterConversation]
    ) -> Optional[Character]:
        """基于优先级选择角色"""
        # 按优先级排序，选择优先级最高的
        highest_priority = max(characters, key=lambda c: c.priority)
        character = character_crud.get(db, id=highest_priority.character_id)
        return character

    def _select_by_context(
        self,
        db: Session,
        characters: List[MultiCharacterConversation],
        user_message: str,
    ) -> Optional[Character]:
        """基于上下文选择角色"""
        # 简单的关键词匹配策略
        # 在实际应用中，这里可以使用更复杂的NLP算法

        user_message_lower = user_message.lower()

        # 为每个角色计算匹配分数
        character_scores = []

        for char_conv in characters:
            character = character_crud.get(db, id=char_conv.character_id)
            if not character:
                continue

            score = 0

            # 检查角色名称是否在消息中
            if character.name.lower() in user_message_lower:
                score += 10

            # 检查角色简介中的关键词
            if character.short_bio:
                bio_keywords = character.short_bio.lower().split()
                for keyword in bio_keywords:
                    if keyword in user_message_lower:
                        score += 2

            # 检查角色persona中的关键词
            if character.persona_text:
                persona_keywords = character.persona_text.lower().split()
                for keyword in persona_keywords:
                    if keyword in user_message_lower:
                        score += 1

            # 考虑优先级
            score += char_conv.priority

            character_scores.append((character, score))

        if not character_scores:
            return None

        # 选择分数最高的角色
        best_character, _ = max(character_scores, key=lambda x: x[1])
        return best_character

    def update_character_priority(
        self,
        db: Session,
        conversation_id: uuid.UUID,
        character_id: uuid.UUID,
        priority: int,
    ) -> bool:
        """
        更新角色优先级

        Args:
            db: 数据库会话
            conversation_id: 会话ID
            character_id: 角色ID
            priority: 新优先级

        Returns:
            bool: 是否成功更新
        """
        multi_char_conv = db.exec(
            select(MultiCharacterConversation).where(
                MultiCharacterConversation.conversation_id == conversation_id,
                MultiCharacterConversation.character_id == character_id,
            )
        ).first()

        if not multi_char_conv:
            return False

        multi_char_conv.priority = priority
        multi_char_conv.updated_at = datetime.utcnow()

        db.add(multi_char_conv)
        db.commit()
        db.refresh(multi_char_conv)

        logger.info(f"角色 {character_id} 优先级已更新为 {priority}")
        return True

    def update_character_response_stats(
        self, db: Session, conversation_id: uuid.UUID, character_id: uuid.UUID
    ) -> None:
        """
        更新角色回复统计

        Args:
            db: 数据库会话
            conversation_id: 会话ID
            character_id: 角色ID
        """
        multi_char_conv = db.exec(
            select(MultiCharacterConversation).where(
                MultiCharacterConversation.conversation_id == conversation_id,
                MultiCharacterConversation.character_id == character_id,
            )
        ).first()

        if multi_char_conv:
            multi_char_conv.response_count += 1
            multi_char_conv.last_response_at = datetime.utcnow()
            multi_char_conv.updated_at = datetime.utcnow()

            db.add(multi_char_conv)
            db.commit()


# 全局多角色服务实例
multi_character_service = MultiCharacterService()
