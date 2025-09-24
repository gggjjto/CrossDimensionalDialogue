"""
嵌入模型适配器测试
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.services.ai_module import (
    AliyunEmbeddingAdapter,
)


class TestAliyunEmbeddingAdapter:
    """阿里云适配器测试类"""

    @pytest.fixture
    def adapter(self):
        """创建阿里云适配器实例"""
        with patch("app.services.ai_module.adapters.dashscope"):
            return AliyunEmbeddingAdapter(
                api_key="test-key", model_name="text-embedding-v4"
            )

    def test_init(self, adapter):
        """测试初始化"""
        assert adapter.api_key == "test-key"
        assert adapter.model_name == "text-embedding-v4"
        assert adapter.dimension == 1024

    def test_get_model_info(self, adapter):
        """测试获取模型信息"""
        info = adapter.get_model_info()
        assert info["provider"] == "aliyun"
        assert info["model_name"] == "text-embedding-v4"
        assert info["dimension"] == 1024

    @pytest.mark.asyncio
    async def test_generate_embedding(self, adapter):
        """测试生成单个嵌入"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.output = {"embeddings": [{"embedding": [0.1, 0.2, 0.3]}]}

        with patch(
            "app.services.ai_module.adapters.TextEmbedding"
        ) as mock_text_embedding:
            mock_text_embedding.call.return_value = mock_response

            result = await adapter.generate_embedding("test text")

            assert result == [0.1, 0.2, 0.3]
            mock_text_embedding.call.assert_called_once_with(
                model="text-embedding-v4", input="test text"
            )

    @pytest.mark.asyncio
    async def test_generate_embeddings_batch(self, adapter):
        """测试批量生成嵌入"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.output = {
            "embeddings": [
                {"embedding": [0.1, 0.2, 0.3]},
                {"embedding": [0.4, 0.5, 0.6]},
            ]
        }

        with patch(
            "app.services.ai_module.adapters.TextEmbedding"
        ) as mock_text_embedding:
            mock_text_embedding.call.return_value = mock_response

            result = await adapter.generate_embeddings_batch(["text1", "text2"])

            assert result == [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
            mock_text_embedding.call.assert_called_once_with(
                model="text-embedding-v4", input=["text1", "text2"]
            )

    @pytest.mark.asyncio
    async def test_generate_embedding_error(self, adapter):
        """测试生成嵌入时的错误处理"""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.code = "INVALID_REQUEST"
        mock_response.message = "Invalid request"

        with patch(
            "app.services.ai_module.adapters.TextEmbedding"
        ) as mock_text_embedding:
            mock_text_embedding.call.return_value = mock_response

            with pytest.raises(Exception, match="阿里云 API 错误"):
                await adapter.generate_embedding("test text")
