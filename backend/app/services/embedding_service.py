"""
向量嵌入服务
负责生成和管理角色相关的向量嵌入
"""

import asyncio
import logging
from typing import List, Optional, Dict, Any
from uuid import UUID

import openai
from openai import AsyncOpenAI
from sqlmodel import Session, select

from app.core.config import settings
from app.models.character import (
    Character,
    CharacterEmbedding,
    CharacterEmbeddingCreate,
    CharacterEmbeddingPublic,
)

logger = logging.getLogger(__name__)


class EmbeddingService:
    """向量嵌入服务类"""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model_name = "text-embedding-3-small"  # 使用较小的模型以降低成本
        self.dimension = 1536  # text-embedding-3-small 的维度
    
    async def generate_embedding(self, text: str) -> List[float]:
        """
        生成文本的向量嵌入
        
        Args:
            text: 输入文本
            
        Returns:
            向量嵌入列表
        """
        try:
            response = await self.client.embeddings.create(
                model=self.model_name,
                input=text,
                encoding_format="float"
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"生成向量嵌入失败: {str(e)}")
            raise
    
    async def generate_character_embeddings(
        self, 
        character: Character, 
        session: Session
    ) -> List[CharacterEmbeddingPublic]:
        """
        为角色生成多种类型的向量嵌入
        
        Args:
            character: 角色对象
            session: 数据库会话
            
        Returns:
            生成的向量嵌入列表
        """
        embeddings = []
        
        # 生成 persona 向量嵌入
        persona_embedding = await self.generate_embedding(character.persona_text)
        persona_emb = CharacterEmbeddingCreate(
            character_id=character.id,
            embedding_type="persona",
            model_name=self.model_name,
            dimension=self.dimension,
            embedding=persona_embedding
        )
        
        # 生成 short_bio 向量嵌入
        bio_embedding = await self.generate_embedding(character.short_bio)
        bio_emb = CharacterEmbeddingCreate(
            character_id=character.id,
            embedding_type="bio",
            model_name=self.model_name,
            dimension=self.dimension,
            embedding=bio_embedding
        )
        
        # 生成组合向量嵌入（用于综合搜索）
        combined_text = f"{character.name} {character.short_bio} {character.persona_text}"
        if character.example_lines:
            combined_text += " " + " ".join(character.example_lines)
        
        combined_embedding = await self.generate_embedding(combined_text)
        combined_emb = CharacterEmbeddingCreate(
            character_id=character.id,
            embedding_type="combined",
            model_name=self.model_name,
            dimension=self.dimension,
            embedding=combined_embedding
        )
        
        # 保存到数据库
        for emb_data in [persona_emb, bio_emb, combined_emb]:
            # 先删除同类型的旧嵌入
            await self._delete_character_embeddings(
                session, character.id, emb_data.embedding_type
            )
            
            # 创建新嵌入
            emb = CharacterEmbedding(**emb_data.model_dump())
            session.add(emb)
            session.commit()
            session.refresh(emb)
            
            embeddings.append(CharacterEmbeddingPublic.model_validate(emb))
        
        return embeddings
    
    async def _delete_character_embeddings(
        self, 
        session: Session, 
        character_id: UUID, 
        embedding_type: str
    ) -> None:
        """删除角色的指定类型嵌入"""
        stmt = select(CharacterEmbedding).where(
            CharacterEmbedding.character_id == character_id,
            CharacterEmbedding.embedding_type == embedding_type
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
        threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        使用向量相似度搜索角色
        
        Args:
            query: 搜索查询
            session: 数据库会话
            embedding_type: 嵌入类型
            limit: 返回数量限制
            threshold: 相似度阈值
            
        Returns:
            相似角色列表，包含相似度分数
        """
        # 生成查询向量
        query_embedding = await self.generate_embedding(query)
        
        # 使用 pgvector 进行相似度搜索
        # 注意：这里需要数据库支持 pgvector 扩展
        stmt = f"""
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
            1 - (ce.embedding <=> %s) as similarity_score
        FROM characters c
        JOIN character_embeddings ce ON c.id = ce.character_id
        WHERE ce.embedding_type = %s
        AND c.is_active = true
        AND 1 - (ce.embedding <=> %s) > %s
        ORDER BY ce.embedding <=> %s
        LIMIT %s
        """
        
        result = session.exec(
            stmt, 
            [
                query_embedding,
                embedding_type,
                query_embedding,
                threshold,
                query_embedding,
                limit
            ]
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
                "similarity_score": float(row[10])
            }
            for row in result
        ]
    
    async def batch_generate_embeddings(
        self, 
        characters: List[Character], 
        session: Session
    ) -> Dict[UUID, List[CharacterEmbeddingPublic]]:
        """
        批量生成角色向量嵌入
        
        Args:
            characters: 角色列表
            session: 数据库会话
            
        Returns:
            角色ID到嵌入列表的映射
        """
        results = {}
        
        # 使用 asyncio.gather 并行处理
        tasks = [
            self.generate_character_embeddings(character, session)
            for character in characters
        ]
        
        embeddings_list = await asyncio.gather(*tasks)
        
        for character, embeddings in zip(characters, embeddings_list):
            results[character.id] = embeddings
        
        return results


# 全局服务实例
embedding_service = EmbeddingService()
