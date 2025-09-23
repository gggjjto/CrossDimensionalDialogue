"""
RAG (Retrieval Augmented Generation) 服务
"""

import uuid
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
import numpy as np

from sqlmodel import Session, select

from app.models.knowledge import (
    KnowledgeBase,
    KnowledgeItem,
    KnowledgeSearchRequest,
    KnowledgeSearchResult,
    KnowledgeType,
)
from app.services.embedding_service import embedding_service
from app.core.config import settings

logger = logging.getLogger(__name__)


class RAGService:
    """RAG服务类"""

    def __init__(self):
        self.embedding_service = embedding_service

    async def search_knowledge(
        self, db: Session, request: KnowledgeSearchRequest
    ) -> List[KnowledgeSearchResult]:
        """
        搜索相关知识

        Args:
            db: 数据库会话
            request: 搜索请求

        Returns:
            List[KnowledgeSearchResult]: 搜索结果列表
        """
        try:
            # 生成查询向量
            query_embedding = await self.embedding_service.generate_embedding(
                request.query
            )

            # 构建搜索查询
            query = select(KnowledgeItem).where(KnowledgeItem.is_active == True)

            # 添加过滤条件
            if request.knowledge_base_ids:
                query = query.where(
                    KnowledgeItem.knowledge_base_id.in_(request.knowledge_base_ids)
                )

            if request.character_id:
                # 通过知识库关联角色
                kb_query = select(KnowledgeBase).where(
                    KnowledgeBase.character_id == request.character_id
                )
                knowledge_bases = db.exec(kb_query).all()
                kb_ids = [kb.id for kb in knowledge_bases]
                if kb_ids:
                    query = query.where(KnowledgeItem.knowledge_base_id.in_(kb_ids))

            if request.knowledge_types:
                # 通过知识库关联知识类型
                kb_query = select(KnowledgeBase).where(
                    KnowledgeBase.knowledge_type.in_(request.knowledge_types)
                )
                knowledge_bases = db.exec(kb_query).all()
                kb_ids = [kb.id for kb in knowledge_bases]
                if kb_ids:
                    query = query.where(KnowledgeItem.knowledge_base_id.in_(kb_ids))

            # 获取所有候选知识条目
            knowledge_items = db.exec(query).all()

            if not knowledge_items:
                return []

            # 计算相似度并排序
            results = []
            for item in knowledge_items:
                if item.embedding:
                    similarity = self._calculate_similarity(
                        query_embedding, item.embedding
                    )

                    if similarity >= request.threshold:
                        # 更新访问次数
                        item.access_count += 1
                        db.add(item)

                        # 提取匹配内容片段
                        matched_content = self._extract_matched_content(
                            item.content, request.query
                        )

                        results.append(
                            KnowledgeSearchResult(
                                knowledge_item=item,
                                relevance_score=similarity,
                                matched_content=matched_content,
                                context=self._generate_context(item),
                            )
                        )

            # 按相关性排序
            results.sort(key=lambda x: x.relevance_score, reverse=True)

            # 限制结果数量
            return results[: request.max_results]

        except Exception as e:
            logger.error(f"知识搜索失败: {str(e)}")
            return []

    async def add_knowledge_item(
        self,
        db: Session,
        knowledge_base_id: uuid.UUID,
        title: str,
        content: str,
        summary: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> KnowledgeItem:
        """
        添加知识条目

        Args:
            db: 数据库会话
            knowledge_base_id: 知识库ID
            title: 知识标题
            content: 知识内容
            summary: 知识摘要
            tags: 标签
            metadata: 元数据

        Returns:
            KnowledgeItem: 创建的知识条目
        """
        try:
            # 生成嵌入向量
            embedding = await self.embedding_service.generate_embedding(content)

            # 如果没有提供摘要，自动生成
            if not summary:
                summary = self._generate_summary(content)

            # 创建知识条目
            knowledge_item = KnowledgeItem(
                knowledge_base_id=knowledge_base_id,
                title=title,
                content=content,
                summary=summary,
                tags=tags or [],
                metadata=metadata or {},
                embedding=embedding.tolist() if embedding is not None else None,
            )

            db.add(knowledge_item)
            db.commit()
            db.refresh(knowledge_item)

            logger.info(f"知识条目已添加: {title}")
            return knowledge_item

        except Exception as e:
            logger.error(f"添加知识条目失败: {str(e)}")
            raise

    async def update_knowledge_item_embedding(
        self, db: Session, knowledge_item_id: uuid.UUID
    ) -> bool:
        """
        更新知识条目的嵌入向量

        Args:
            db: 数据库会话
            knowledge_item_id: 知识条目ID

        Returns:
            bool: 是否成功更新
        """
        try:
            knowledge_item = db.get(KnowledgeItem, knowledge_item_id)
            if not knowledge_item:
                return False

            # 重新生成嵌入向量
            embedding = await self.embedding_service.generate_embedding(
                knowledge_item.content
            )

            knowledge_item.embedding = (
                embedding.tolist() if embedding is not None else None
            )
            knowledge_item.updated_at = datetime.utcnow()

            db.add(knowledge_item)
            db.commit()

            logger.info(f"知识条目 {knowledge_item_id} 的嵌入向量已更新")
            return True

        except Exception as e:
            logger.error(f"更新嵌入向量失败: {str(e)}")
            return False

    def _calculate_similarity(
        self, embedding1: List[float], embedding2: List[float]
    ) -> float:
        """
        计算两个向量的余弦相似度

        Args:
            embedding1: 向量1
            embedding2: 向量2

        Returns:
            float: 相似度分数
        """
        try:
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)

            # 计算余弦相似度
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)

            if norm1 == 0 or norm2 == 0:
                return 0.0

            similarity = dot_product / (norm1 * norm2)
            return float(similarity)

        except Exception as e:
            logger.error(f"计算相似度失败: {str(e)}")
            return 0.0

    def _extract_matched_content(
        self, content: str, query: str, max_length: int = 200
    ) -> str:
        """
        提取匹配的内容片段

        Args:
            content: 原始内容
            query: 查询文本
            max_length: 最大长度

        Returns:
            str: 匹配的内容片段
        """
        query_words = query.lower().split()
        content_lower = content.lower()

        # 找到包含最多查询词的位置
        best_start = 0
        best_score = 0

        for i in range(len(content) - max_length + 1):
            snippet = content_lower[i : i + max_length]
            score = sum(1 for word in query_words if word in snippet)

            if score > best_score:
                best_score = score
                best_start = i

        # 提取片段并添加省略号
        snippet = content[best_start : best_start + max_length]
        if best_start > 0:
            snippet = "..." + snippet
        if best_start + max_length < len(content):
            snippet = snippet + "..."

        return snippet

    def _generate_summary(self, content: str, max_length: int = 100) -> str:
        """
        生成内容摘要

        Args:
            content: 原始内容
            max_length: 最大长度

        Returns:
            str: 摘要
        """
        if len(content) <= max_length:
            return content

        # 简单的截断摘要
        return content[:max_length] + "..."

    def _generate_context(self, knowledge_item: KnowledgeItem) -> str:
        """
        生成上下文信息

        Args:
            knowledge_item: 知识条目

        Returns:
            str: 上下文信息
        """
        context_parts = []

        if knowledge_item.tags:
            context_parts.append(f"标签: {', '.join(knowledge_item.tags)}")

        if knowledge_item.metadata:
            if "source" in knowledge_item.metadata:
                context_parts.append(f"来源: {knowledge_item.metadata['source']}")
            if "category" in knowledge_item.metadata:
                context_parts.append(f"分类: {knowledge_item.metadata['category']}")

        return " | ".join(context_parts) if context_parts else ""


# 全局RAG服务实例
rag_service = RAGService()
