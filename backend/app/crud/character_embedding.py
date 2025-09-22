"""
角色向量嵌入 CRUD 操作
"""

import logging
from typing import List, Optional, Dict, Any
from uuid import UUID

from sqlmodel import Session, select, func, and_, or_

from app.models.character import (
    Character,
    CharacterEmbedding,
    CharacterEmbeddingCreate,
    CharacterEmbeddingPublic,
    CharacterSearchRequest,
    CharacterSearchResult,
    CharacterSearchResponse,
    CharacterPublic,
    CharacterTagPublic,
)

logger = logging.getLogger(__name__)


class CharacterEmbeddingCRUD:
    """角色向量嵌入 CRUD 类"""

    def create_embedding(
        self, session: Session, embedding_data: CharacterEmbeddingCreate
    ) -> CharacterEmbeddingPublic:
        """创建向量嵌入"""
        embedding = CharacterEmbedding(**embedding_data.model_dump())
        session.add(embedding)
        session.commit()
        session.refresh(embedding)
        return CharacterEmbeddingPublic.model_validate(embedding)

    def get_character_embeddings(
        self, session: Session, character_id: UUID, embedding_type: Optional[str] = None
    ) -> List[CharacterEmbeddingPublic]:
        """获取角色的向量嵌入"""
        stmt = select(CharacterEmbedding).where(
            CharacterEmbedding.character_id == character_id
        )

        if embedding_type:
            stmt = stmt.where(CharacterEmbedding.embedding_type == embedding_type)

        embeddings = session.exec(stmt).all()
        return [CharacterEmbeddingPublic.model_validate(emb) for emb in embeddings]

    def delete_character_embeddings(
        self, session: Session, character_id: UUID, embedding_type: Optional[str] = None
    ) -> int:
        """删除角色的向量嵌入"""
        stmt = select(CharacterEmbedding).where(
            CharacterEmbedding.character_id == character_id
        )

        if embedding_type:
            stmt = stmt.where(CharacterEmbedding.embedding_type == embedding_type)

        embeddings = session.exec(stmt).all()
        count = len(embeddings)

        for embedding in embeddings:
            session.delete(embedding)

        session.commit()
        return count

    def text_search_characters(
        self, session: Session, search_request: CharacterSearchRequest
    ) -> CharacterSearchResponse:
        """文本搜索角色"""
        stmt = select(Character).where(Character.is_active == search_request.is_active)

        # 添加标签过滤
        if search_request.tag_ids:
            stmt = stmt.join(Character.tag_relations).where(
                Character.tag_relations.any(
                    Character.tag_relations.c.tag_id.in_(search_request.tag_ids)
                )
            )

        # 添加文本搜索条件
        search_term = f"%{search_request.query}%"
        stmt = stmt.where(
            or_(
                Character.name.ilike(search_term),
                Character.short_bio.ilike(search_term),
                Character.persona_text.ilike(search_term),
            )
        )

        # 获取总数
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = session.exec(count_stmt).one()

        # 分页
        stmt = stmt.offset(search_request.offset).limit(search_request.limit)
        characters = session.exec(stmt).all()

        # 构建结果
        results = []
        for character in characters:
            # 获取角色的标签
            tags = self._get_character_tags(session, character.id)

            character_public = CharacterPublic(
                id=character.id,
                name=character.name,
                short_bio=character.short_bio,
                avatar_url=character.avatar_url,
                persona_text=character.persona_text,
                example_lines=character.example_lines,
                source=character.source,
                is_active=character.is_active,
                created_at=character.created_at,
                updated_at=character.updated_at,
                tags=tags,
            )

            results.append(
                CharacterSearchResult(
                    character=character_public, score=None, match_type="text"
                )
            )

        return CharacterSearchResponse(
            results=results,
            total=total,
            query=search_request.query,
            search_type=search_request.search_type,
        )

    def vector_search_characters(
        self,
        session: Session,
        search_request: CharacterSearchRequest,
        query_embedding: List[float],
        embedding_type: str = "combined",
    ) -> CharacterSearchResponse:
        """向量搜索角色"""
        # 使用 pgvector 进行相似度搜索
        # 注意：这需要数据库支持 pgvector 扩展
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
        AND c.is_active = %s
        AND 1 - (ce.embedding <=> %s) > 0.5
        """

        params = [
            query_embedding,
            embedding_type,
            search_request.is_active,
            query_embedding,
        ]

        # 添加标签过滤
        if search_request.tag_ids:
            stmt += """
            AND c.id IN (
                SELECT ctm.character_id 
                FROM character_tag_maps ctm 
                WHERE ctm.tag_id = ANY(%s)
            )
            """
            params.append(search_request.tag_ids)

        stmt += """
        ORDER BY ce.embedding <=> %s
        LIMIT %s OFFSET %s
        """
        params.extend([query_embedding, search_request.limit, search_request.offset])

        # 获取总数
        count_stmt = f"""
        SELECT COUNT(*)
        FROM characters c
        JOIN character_embeddings ce ON c.id = ce.character_id
        WHERE ce.embedding_type = %s
        AND c.is_active = %s
        AND 1 - (ce.embedding <=> %s) > 0.5
        """
        count_params = [embedding_type, search_request.is_active, query_embedding]

        if search_request.tag_ids:
            count_stmt += """
            AND c.id IN (
                SELECT ctm.character_id 
                FROM character_tag_maps ctm 
                WHERE ctm.tag_id = ANY(%s)
            )
            """
            count_params.append(search_request.tag_ids)

        total = session.exec(count_stmt, count_params).one()

        # 执行搜索
        results_data = session.exec(stmt, params).all()

        # 构建结果
        results = []
        for row in results_data:
            character_id = row[0]
            tags = self._get_character_tags(session, character_id)

            character_public = CharacterPublic(
                id=row[0],
                name=row[1],
                short_bio=row[2],
                avatar_url=row[3],
                persona_text=row[4],
                example_lines=row[5],
                source=row[6],
                is_active=row[7],
                created_at=row[8],
                updated_at=row[9],
                tags=tags,
            )

            results.append(
                CharacterSearchResult(
                    character=character_public,
                    score=float(row[10]),
                    match_type="vector",
                )
            )

        return CharacterSearchResponse(
            results=results,
            total=total,
            query=search_request.query,
            search_type=search_request.search_type,
        )

    def hybrid_search_characters(
        self,
        session: Session,
        search_request: CharacterSearchRequest,
        query_embedding: List[float],
        embedding_type: str = "combined",
        text_weight: float = 0.3,
        vector_weight: float = 0.7,
    ) -> CharacterSearchResponse:
        """混合搜索角色（文本 + 向量）"""
        # 先进行文本搜索
        text_results = self.text_search_characters(session, search_request)

        # 再进行向量搜索
        vector_results = self.vector_search_characters(
            session, search_request, query_embedding, embedding_type
        )

        # 合并结果并重新排序
        character_scores = {}

        # 处理文本搜索结果
        for result in text_results.results:
            character_id = result.character.id
            character_scores[character_id] = {
                "character": result.character,
                "text_score": 1.0,  # 文本搜索匹配度设为1.0
                "vector_score": 0.0,
            }

        # 处理向量搜索结果
        for result in vector_results.results:
            character_id = result.character.id
            if character_id in character_scores:
                character_scores[character_id]["vector_score"] = result.score or 0.0
            else:
                character_scores[character_id] = {
                    "character": result.character,
                    "text_score": 0.0,
                    "vector_score": result.score or 0.0,
                }

        # 计算混合分数并排序
        hybrid_results = []
        for character_id, data in character_scores.items():
            hybrid_score = (
                data["text_score"] * text_weight + data["vector_score"] * vector_weight
            )

            hybrid_results.append(
                CharacterSearchResult(
                    character=data["character"], score=hybrid_score, match_type="hybrid"
                )
            )

        # 按分数排序
        hybrid_results.sort(key=lambda x: x.score or 0, reverse=True)

        # 应用分页
        start = search_request.offset
        end = start + search_request.limit
        paginated_results = hybrid_results[start:end]

        return CharacterSearchResponse(
            results=paginated_results,
            total=len(hybrid_results),
            query=search_request.query,
            search_type=search_request.search_type,
        )

    def _get_character_tags(
        self, session: Session, character_id: UUID
    ) -> List[CharacterTagPublic]:
        """获取角色的标签"""
        from app.models.character import CharacterTagMap, CharacterTag

        stmt = (
            select(CharacterTag)
            .join(CharacterTagMap)
            .where(CharacterTagMap.character_id == character_id)
        )
        tags = session.exec(stmt).all()
        return [CharacterTagPublic.model_validate(tag) for tag in tags]


# 全局 CRUD 实例
character_embedding_crud = CharacterEmbeddingCRUD()
