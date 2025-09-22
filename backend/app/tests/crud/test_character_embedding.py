"""
角色向量嵌入 CRUD 测试
"""

import pytest
from unittest.mock import MagicMock, patch
from uuid import uuid4

from app.crud.character_embedding import CharacterEmbeddingCRUD
from app.models.character import (
    CharacterSearchRequest,
    CharacterEmbeddingCreate,
    Character,
    CharacterTag,
    CharacterTagMap,
)


class TestCharacterEmbeddingCRUD:
    """角色向量嵌入 CRUD 测试类"""

    @pytest.fixture
    def crud(self):
        """创建 CRUD 实例"""
        return CharacterEmbeddingCRUD()

    @pytest.fixture
    def mock_session(self):
        """创建模拟数据库会话"""
        session = MagicMock()
        session.add = MagicMock()
        session.commit = MagicMock()
        session.refresh = MagicMock()
        return session

    @pytest.fixture
    def mock_character(self):
        """创建模拟角色"""
        return Character(
            id=uuid4(),
            name="测试角色",
            short_bio="这是一个测试角色",
            persona_text="你是一个友好的AI助手",
            is_active=True,
        )

    @pytest.fixture
    def mock_embedding_data(self):
        """创建模拟嵌入数据"""
        return CharacterEmbeddingCreate(
            character_id=uuid4(),
            embedding_type="combined",
            model_name="text-embedding-3-small",
            dimension=1536,
            embedding=[0.1] * 1536,
        )

    def test_create_embedding(self, crud, mock_session, mock_embedding_data):
        """测试创建向量嵌入"""
        # 模拟数据库操作
        mock_embedding = MagicMock()
        mock_embedding.id = uuid4()
        mock_session.refresh.return_value = mock_embedding

        result = crud.create_embedding(mock_session, mock_embedding_data)

        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()
        assert result is not None

    def test_get_character_embeddings(self, crud, mock_session):
        """测试获取角色向量嵌入"""
        character_id = uuid4()

        # 模拟查询结果
        mock_embeddings = [
            MagicMock(id=uuid4(), character_id=character_id, embedding_type="persona"),
            MagicMock(id=uuid4(), character_id=character_id, embedding_type="bio"),
        ]
        mock_session.exec.return_value.all.return_value = mock_embeddings

        result = crud.get_character_embeddings(mock_session, character_id)

        assert len(result) == 2
        mock_session.exec.assert_called_once()

    def test_get_character_embeddings_with_type_filter(self, crud, mock_session):
        """测试按类型过滤获取角色向量嵌入"""
        character_id = uuid4()
        embedding_type = "persona"

        # 模拟查询结果
        mock_embeddings = [
            MagicMock(id=uuid4(), character_id=character_id, embedding_type="persona"),
        ]
        mock_session.exec.return_value.all.return_value = mock_embeddings

        result = crud.get_character_embeddings(
            mock_session, character_id, embedding_type
        )

        assert len(result) == 1
        mock_session.exec.assert_called_once()

    def test_delete_character_embeddings(self, crud, mock_session):
        """测试删除角色向量嵌入"""
        character_id = uuid4()

        # 模拟查询结果
        mock_embeddings = [
            MagicMock(id=uuid4()),
            MagicMock(id=uuid4()),
        ]
        mock_session.exec.return_value.all.return_value = mock_embeddings

        result = crud.delete_character_embeddings(mock_session, character_id)

        assert result == 2
        assert mock_session.delete.call_count == 2
        mock_session.commit.assert_called_once()

    def test_text_search_characters(self, crud, mock_session):
        """测试文本搜索角色"""
        search_request = CharacterSearchRequest(
            query="测试查询", search_type="text", limit=10, offset=0, is_active=True
        )

        # 模拟角色查询结果
        mock_characters = [
            MagicMock(
                id=uuid4(),
                name="角色1",
                short_bio="简介1",
                avatar_url=None,
                persona_text="人格1",
                example_lines=None,
                source=None,
                is_active=True,
            )
        ]
        mock_session.exec.return_value.one.return_value = 1  # 总数
        mock_session.exec.return_value.all.return_value = mock_characters

        with patch.object(crud, "_get_character_tags", return_value=[]):
            result = crud.text_search_characters(mock_session, search_request)

            assert len(result.results) == 1
            assert result.total == 1
            assert result.query == "测试查询"
            assert result.search_type == "text"
            assert result.results[0].match_type == "text"

    def test_text_search_characters_with_tag_filter(self, crud, mock_session):
        """测试带标签过滤的文本搜索"""
        tag_id = uuid4()
        search_request = CharacterSearchRequest(
            query="测试查询",
            search_type="text",
            limit=10,
            offset=0,
            tag_ids=[tag_id],
            is_active=True,
        )

        # 模拟角色查询结果
        mock_characters = []
        mock_session.exec.return_value.one.return_value = 0
        mock_session.exec.return_value.all.return_value = mock_characters

        with patch.object(crud, "_get_character_tags", return_value=[]):
            result = crud.text_search_characters(mock_session, search_request)

            assert len(result.results) == 0
            assert result.total == 0

    def test_vector_search_characters(self, crud, mock_session):
        """测试向量搜索角色"""
        search_request = CharacterSearchRequest(
            query="测试查询", search_type="vector", limit=10, offset=0, is_active=True
        )
        query_embedding = [0.1] * 1536

        # 模拟数据库查询结果
        mock_results = [
            (
                uuid4(),
                "角色1",
                "简介1",
                None,
                "人格1",
                None,
                None,
                True,
                "2023-01-01",
                "2023-01-01",
                0.95,
            )
        ]
        mock_session.exec.return_value.one.return_value = 1  # 总数
        mock_session.exec.return_value.all.return_value = mock_results

        with patch.object(crud, "_get_character_tags", return_value=[]):
            result = crud.vector_search_characters(
                mock_session, search_request, query_embedding
            )

            assert len(result.results) == 1
            assert result.total == 1
            assert result.results[0].score == 0.95
            assert result.results[0].match_type == "vector"

    def test_hybrid_search_characters(self, crud, mock_session):
        """测试混合搜索角色"""
        search_request = CharacterSearchRequest(
            query="测试查询", search_type="hybrid", limit=10, offset=0, is_active=True
        )
        query_embedding = [0.1] * 1536

        # 模拟文本搜索结果
        mock_text_results = MagicMock()
        mock_text_results.results = [
            MagicMock(character=MagicMock(id=uuid4()), score=1.0, match_type="text")
        ]

        # 模拟向量搜索结果
        mock_vector_results = MagicMock()
        mock_vector_results.results = [
            MagicMock(character=MagicMock(id=uuid4()), score=0.9, match_type="vector")
        ]

        with patch.object(
            crud, "text_search_characters", return_value=mock_text_results
        ), patch.object(
            crud, "vector_search_characters", return_value=mock_vector_results
        ):

            result = crud.hybrid_search_characters(
                mock_session, search_request, query_embedding
            )

            assert len(result.results) == 2
            assert result.search_type == "hybrid"
            # 验证结果按分数排序
            scores = [r.score for r in result.results if r.score is not None]
            assert scores == sorted(scores, reverse=True)

    def test_get_character_tags(self, crud, mock_session):
        """测试获取角色标签"""
        character_id = uuid4()

        # 模拟标签查询结果
        mock_tags = [
            MagicMock(id=uuid4(), name="标签1"),
            MagicMock(id=uuid4(), name="标签2"),
        ]
        mock_session.exec.return_value.all.return_value = mock_tags

        result = crud._get_character_tags(mock_session, character_id)

        assert len(result) == 2
        mock_session.exec.assert_called_once()
