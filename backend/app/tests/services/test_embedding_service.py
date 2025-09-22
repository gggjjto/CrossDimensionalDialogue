"""
向量嵌入服务测试
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4

from app.services.embedding_service import EmbeddingService
from app.models.character import Character, CharacterEmbeddingCreate


class TestEmbeddingService:
    """向量嵌入服务测试类"""
    
    @pytest.fixture
    def embedding_service(self):
        """创建嵌入服务实例"""
        return EmbeddingService()
    
    @pytest.fixture
    def mock_character(self):
        """创建模拟角色"""
        return Character(
            id=uuid4(),
            name="测试角色",
            short_bio="这是一个测试角色",
            persona_text="你是一个友好的AI助手",
            example_lines=["你好", "很高兴见到你"],
            is_active=True
        )
    
    @pytest.fixture
    def mock_session(self):
        """创建模拟数据库会话"""
        session = MagicMock()
        session.add = MagicMock()
        session.commit = MagicMock()
        session.refresh = MagicMock()
        return session
    
    @pytest.mark.asyncio
    async def test_generate_embedding(self, embedding_service):
        """测试生成向量嵌入"""
        with patch.object(embedding_service.client.embeddings, 'create', new_callable=AsyncMock) as mock_create:
            # 模拟 OpenAI API 响应
            mock_response = MagicMock()
            mock_response.data = [MagicMock()]
            mock_response.data[0].embedding = [0.1, 0.2, 0.3] * 512  # 1536维向量
            mock_create.return_value = mock_response
            
            result = await embedding_service.generate_embedding("测试文本")
            
            assert len(result) == 1536
            assert result[0] == 0.1
            mock_create.assert_called_once_with(
                model="text-embedding-3-small",
                input="测试文本",
                encoding_format="float"
            )
    
    @pytest.mark.asyncio
    async def test_generate_character_embeddings(self, embedding_service, mock_character, mock_session):
        """测试为角色生成向量嵌入"""
        with patch.object(embedding_service, 'generate_embedding', new_callable=AsyncMock) as mock_generate:
            # 模拟生成不同类型的嵌入
            mock_generate.side_effect = [
                [0.1] * 1536,  # persona 嵌入
                [0.2] * 1536,  # bio 嵌入
                [0.3] * 1536,  # combined 嵌入
            ]
            
            with patch.object(embedding_service, '_delete_character_embeddings', new_callable=AsyncMock) as mock_delete:
                result = await embedding_service.generate_character_embeddings(
                    mock_character, mock_session
                )
                
                # 验证生成了3种类型的嵌入
                assert len(result) == 3
                assert mock_generate.call_count == 3
                assert mock_delete.call_count == 3
                
                # 验证数据库操作
                assert mock_session.add.call_count == 3
                assert mock_session.commit.call_count == 3
                assert mock_session.refresh.call_count == 3
    
    @pytest.mark.asyncio
    async def test_search_similar_characters(self, embedding_service, mock_session):
        """测试相似角色搜索"""
        with patch.object(embedding_service, 'generate_embedding', new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = [0.1] * 1536
            
            # 模拟数据库查询结果
            mock_result = [
                (
                    uuid4(), "角色1", "简介1", None, "人格1", None, None, True,
                    "2023-01-01", "2023-01-01", 0.95
                ),
                (
                    uuid4(), "角色2", "简介2", None, "人格2", None, None, True,
                    "2023-01-01", "2023-01-01", 0.85
                )
            ]
            
            with patch.object(mock_session, 'exec', return_value=mock_result):
                result = await embedding_service.search_similar_characters(
                    "测试查询", mock_session, limit=10
                )
                
                assert len(result) == 2
                assert result[0]["name"] == "角色1"
                assert result[0]["similarity_score"] == 0.95
                assert result[1]["name"] == "角色2"
                assert result[1]["similarity_score"] == 0.85
    
    @pytest.mark.asyncio
    async def test_batch_generate_embeddings(self, embedding_service, mock_session):
        """测试批量生成向量嵌入"""
        characters = [
            Character(id=uuid4(), name="角色1", short_bio="简介1", persona_text="人格1", is_active=True),
            Character(id=uuid4(), name="角色2", short_bio="简介2", persona_text="人格2", is_active=True)
        ]
        
        with patch.object(embedding_service, 'generate_character_embeddings', new_callable=AsyncMock) as mock_generate:
            # 模拟每个角色的嵌入生成结果
            mock_generate.side_effect = [
                [MagicMock()] * 3,  # 角色1的嵌入
                [MagicMock()] * 3,  # 角色2的嵌入
            ]
            
            result = await embedding_service.batch_generate_embeddings(
                characters, mock_session
            )
            
            assert len(result) == 2
            assert len(result[characters[0].id]) == 3
            assert len(result[characters[1].id]) == 3
            assert mock_generate.call_count == 2
    
    @pytest.mark.asyncio
    async def test_generate_embedding_error_handling(self, embedding_service):
        """测试生成嵌入时的错误处理"""
        with patch.object(embedding_service.client.embeddings, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.side_effect = Exception("API 错误")
            
            with pytest.raises(Exception, match="API 错误"):
                await embedding_service.generate_embedding("测试文本")
    
    def test_embedding_service_initialization(self):
        """测试嵌入服务初始化"""
        service = EmbeddingService()
        assert service.model_name == "text-embedding-3-small"
        assert service.dimension == 1536
        assert service.client is not None
