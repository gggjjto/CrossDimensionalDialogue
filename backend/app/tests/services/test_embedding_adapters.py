"""
嵌入模型适配器测试
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.services.embedding_adapters import (
    OpenAIEmbeddingAdapter,
    AliyunEmbeddingAdapter,
)


class TestOpenAIEmbeddingAdapter:
    """OpenAI 适配器测试类"""
    
    @pytest.fixture
    def adapter(self):
        """创建 OpenAI 适配器实例"""
        with patch('app.services.embedding_adapters.openai_adapter.AsyncOpenAI'):
            return OpenAIEmbeddingAdapter(
                api_key="test-key",
                model_name="text-embedding-3-small"
            )
    
    @pytest.mark.asyncio
    async def test_generate_embedding(self, adapter):
        """测试生成单个嵌入"""
        with patch.object(adapter.client.embeddings, 'create', new_callable=AsyncMock) as mock_create:
            # 模拟 OpenAI API 响应
            mock_response = MagicMock()
            mock_response.data = [MagicMock()]
            mock_response.data[0].embedding = [0.1, 0.2, 0.3] * 512  # 1536维向量
            mock_create.return_value = mock_response
            
            result = await adapter.generate_embedding("测试文本")
            
            assert len(result) == 1536
            assert result[0] == 0.1
            mock_create.assert_called_once_with(
                model="text-embedding-3-small",
                input="测试文本",
                encoding_format="float"
            )
    
    @pytest.mark.asyncio
    async def test_generate_embeddings_batch(self, adapter):
        """测试批量生成嵌入"""
        with patch.object(adapter.client.embeddings, 'create', new_callable=AsyncMock) as mock_create:
            # 模拟 OpenAI API 响应
            mock_response = MagicMock()
            mock_response.data = [
                MagicMock(embedding=[0.1] * 1536),
                MagicMock(embedding=[0.2] * 1536),
                MagicMock(embedding=[0.3] * 1536),
            ]
            mock_create.return_value = mock_response
            
            texts = ["文本1", "文本2", "文本3"]
            result = await adapter.generate_embeddings_batch(texts)
            
            assert len(result) == 3
            assert all(len(emb) == 1536 for emb in result)
            mock_create.assert_called_once_with(
                model="text-embedding-3-small",
                input=texts,
                encoding_format="float"
            )
    
    def test_get_model_info(self, adapter):
        """测试获取模型信息"""
        info = adapter.get_model_info()
        assert info["provider"] == "openai"
        assert info["model_name"] == "text-embedding-3-small"
        assert info["dimension"] == 1536


class TestAliyunEmbeddingAdapter:
    """阿里云适配器测试类"""
    
    @pytest.fixture
    def adapter(self):
        """创建阿里云适配器实例"""
        with patch('app.services.embedding_adapters.aliyun_adapter.dashscope'):
            return AliyunEmbeddingAdapter(
                api_key="test-key",
                model_name="text-embedding-v4"
            )
    
    @pytest.mark.asyncio
    async def test_generate_embedding(self, adapter):
        """测试生成单个嵌入"""
        with patch('app.services.embedding_adapters.aliyun_adapter.TextEmbedding.call') as mock_call:
            # 模拟阿里云 API 响应
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.output = {
                'embeddings': [{'embedding': [0.1, 0.2, 0.3] * 512}]  # 1536维向量
            }
            mock_call.return_value = mock_response
            
            result = await adapter.generate_embedding("测试文本")
            
            assert len(result) == 1536
            assert result[0] == 0.1
            mock_call.assert_called_once_with(
                model="text-embedding-v4",
                input="测试文本"
            )
    
    @pytest.mark.asyncio
    async def test_generate_embeddings_batch(self, adapter):
        """测试批量生成嵌入"""
        with patch('app.services.embedding_adapters.aliyun_adapter.TextEmbedding.call') as mock_call:
            # 模拟阿里云 API 响应
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.output = {
                'embeddings': [
                    {'embedding': [0.1] * 1536},
                    {'embedding': [0.2] * 1536},
                    {'embedding': [0.3] * 1536},
                ]
            }
            mock_call.return_value = mock_response
            
            texts = ["文本1", "文本2", "文本3"]
            result = await adapter.generate_embeddings_batch(texts)
            
            assert len(result) == 3
            assert all(len(emb) == 1536 for emb in result)
            mock_call.assert_called_once_with(
                model="text-embedding-v4",
                input=texts
            )
    
    @pytest.mark.asyncio
    async def test_generate_embedding_error(self, adapter):
        """测试生成嵌入时的错误处理"""
        with patch('app.services.embedding_adapters.aliyun_adapter.TextEmbedding.call') as mock_call:
            # 模拟 API 错误响应
            mock_response = MagicMock()
            mock_response.status_code = 400
            mock_response.code = "InvalidParameter"
            mock_response.message = "参数错误"
            mock_call.return_value = mock_response
            
            with pytest.raises(Exception, match="阿里云 API 错误"):
                await adapter.generate_embedding("测试文本")
    
    def test_get_model_info(self, adapter):
        """测试获取模型信息"""
        info = adapter.get_model_info()
        assert info["provider"] == "aliyun"
        assert info["model_name"] == "text-embedding-v4"
        assert info["dimension"] == 1536
