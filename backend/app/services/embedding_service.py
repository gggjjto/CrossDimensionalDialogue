"""
向量嵌入服务
负责生成和管理角色相关的向量嵌入
支持多种嵌入模型提供商
"""

import asyncio
from typing import Any, Dict, List, Optional
from uuid import UUID

import dashscope
from app.core.config import settings
from app.core.logger import get_logger
from app.models.character import (
    Character,
    CharacterEmbedding,
    CharacterEmbeddingCreate,
    CharacterEmbeddingPublic,
)
from sqlmodel import Session, select, text

logger = get_logger("embedding_service")


class EmbeddingService:
    """向量嵌入服务类"""

    def __init__(self):
        dashscope.api_key = settings.QWEN_API_KEY
        self.model_name = settings.QWEN_EMBEDDING_MODEL
        self.dimension = 1536

    def get_model_info(self) -> Dict[str, Any]:
        """获取当前使用的模型信息"""
        return {
            "provider": "qwen",
            "model_name": self.model_name,
            "dimension": self.dimension,
        }

    async def generate_embedding(self, text: str) -> List[float]:
        """生成文本的向量嵌入"""
        try:
            rsp = dashscope.TextEmbedding.call(
                model=self.model_name,
                input=text,
            )
            return rsp["output"]["embeddings"][0]["embedding"]
        except Exception as e:
            logger.error("生成向量嵌入失败: %s", str(e))
            raise

    async def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """批量生成文本的向量嵌入"""
        try:
            rsp = dashscope.TextEmbedding.call(
                model=self.model_name,
                input=texts,
            )
            return [item["embedding"] for item in rsp["output"]["embeddings"]]
        except Exception as e:
            logger.error("批量生成向量嵌入失败: %s", str(e))
            raise

    async def generate_character_embeddings(
        self, character: Character, session: Session
    ) -> List[CharacterEmbeddingPublic]:
        """为角色生成多种类型的向量嵌入"""
        embeddings = []

        # persona
        persona_embedding = await self.generate_embedding(character.persona_text)
        persona_emb = CharacterEmbeddingCreate(
            character_id=character.id,
            embedding_type="persona",
            model_name=self.model_name,
            dimension=self.dimension,
            embedding=persona_embedding,
        )

        # short_bio
        bio_embedding = await self.generate_embedding(character.short_bio)
        bio_emb = CharacterEmbeddingCreate(
            character_id=character.id,
            embedding_type="bio",
            model_name=self.model_name,
            dimension=self.dimension,
            embedding=bio_embedding,
        )

        # combined
        combined_text = (
            f"{character.name} {character.short_bio} {character.persona_text}"
        )
        if character.example_lines:
            combined_text += " " + " ".join(character.example_lines)

        combined_embedding = await self.generate_embedding(combined_text)
        combined_emb = CharacterEmbeddingCreate(
            character_id=character.id,
            embedding_type="combined",
            model_name=self.model_name,
            dimension=self.dimension,
            embedding=combined_embedding,
        )

        # 保存
        for emb_data in [persona_emb, bio_emb, combined_emb]:
            await self._delete_character_embeddings(
                session, character.id, emb_data.embedding_type
            )
            emb = CharacterEmbedding(**emb_data.model_dump())
            session.add(emb)
            session.commit()
            session.refresh(emb)
            embeddings.append(CharacterEmbeddingPublic.model_validate(emb))

        return embeddings

    async def _delete_character_embeddings(
        self, session: Session, character_id: UUID, embedding_type: str
    ) -> None:
        """删除角色的指定类型嵌入"""
        stmt = select(CharacterEmbedding).where(
            CharacterEmbedding.character_id == character_id,
            CharacterEmbedding.embedding_type == embedding_type,
        )
        existing_embeddings = session.exec(stmt).all()
        for emb in existing_embeddings:
            session.delete(emb)
        session.commit()

    async def search_similar_characters(
        self,
        query: str,
        session: Session,
        embedding_type: str = "combined",
        limit: int = 10,
        threshold: float = 0.7,
    ) -> List[Dict[str, Any]]:
        """使用向量相似度搜索角色"""
        query_embedding = await self.generate_embedding(query)

        stmt = """
        SELECT 
            c.id,
            c.name,
            c.short_bio,
            c.avatar_url,
            c.persona_text,
            c.example_lines,
            c.source,
            c.is_active,
            c.created_at,
            c.updated_at,
            1 - (ce.embedding <=> :query_embedding) as similarity_score
        FROM characters c
        JOIN character_embeddings ce ON c.id = ce.character_id
        WHERE ce.embedding_type = :embedding_type
        AND c.is_active = true
        AND 1 - (ce.embedding <=> :query_embedding) > :threshold
        ORDER BY ce.embedding <=> :query_embedding
        LIMIT :limit
        """

        result = session.exec(
            text(stmt),
            {
                "query_embedding": query_embedding,
                "embedding_type": embedding_type,
                "threshold": threshold,
                "limit": limit,
            },
        ).all()

        return [
            {
                "character_id": row[0],
                "name": row[1],
                "short_bio": row[2],
                "avatar_url": row[3],
                "persona_text": row[4],
                "example_lines": row[5],
                "source": row[6],
                "is_active": row[7],
                "created_at": row[8],
                "updated_at": row[9],
                "similarity_score": float(row[10]),
            }
            for row in result
        ]

    async def batch_generate_embeddings(
        self, characters: List[Character], session: Session
    ) -> Dict[UUID, List[CharacterEmbeddingPublic]]:
        """批量生成角色向量嵌入"""
        results = {}
        tasks = [
            self.generate_character_embeddings(character, session)
            for character in characters
        ]
        embeddings_list = await asyncio.gather(*tasks)
        for character, embeddings in zip(characters, embeddings_list):
            results[character.id] = embeddings
        return results


# 全局实例
embedding_service = EmbeddingService()
