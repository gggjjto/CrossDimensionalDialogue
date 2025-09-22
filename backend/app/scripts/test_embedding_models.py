"""
测试多种嵌入模型功能
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.services.embedding_service import embedding_service
from app.core.config import settings


async def test_embedding_models():
    """测试多种嵌入模型功能"""
    print("🚀 开始测试嵌入模型功能...")

    test_text = "这是一个测试文本，用于验证嵌入模型的性能。"

    # 测试当前配置的模型
    print(f"\n📊 当前配置的提供商: {settings.EMBEDDING_PROVIDER}")

    try:
        # 获取模型信息
        model_info = embedding_service.get_model_info()
        print(f"📋 模型信息: {model_info}")

        # 生成单个嵌入
        print(f"\n🔍 生成单个嵌入...")
        embedding = await embedding_service.generate_embedding(test_text)
        print(f"✅ 嵌入维度: {len(embedding)}")
        print(f"✅ 嵌入前5个值: {embedding[:5]}")

        # 生成批量嵌入
        print(f"\n🔍 生成批量嵌入...")
        texts = ["第一个测试文本", "第二个测试文本", "第三个测试文本"]
        embeddings = await embedding_service.generate_embeddings_batch(texts)
        print(f"✅ 批量嵌入数量: {len(embeddings)}")
        print(f"✅ 每个嵌入维度: {[len(emb) for emb in embeddings]}")

    except Exception as e:
        print(f"❌ 测试当前模型失败: {str(e)}")
        print("   请检查 API 密钥配置")
        return

    # 测试模型切换（如果配置了多个提供商）
    print(f"\n🔄 测试模型切换功能...")

    # 尝试切换到阿里云（如果配置了）
    if settings.ALIYUN_API_KEY:
        try:
            print("   尝试切换到阿里云...")
            await embedding_service.switch_provider("aliyun")
            model_info = embedding_service.get_model_info()
            print(f"✅ 已切换到: {model_info}")

            # 测试阿里云模型
            embedding = await embedding_service.generate_embedding(test_text)
            print(f"✅ 阿里云嵌入维度: {len(embedding)}")

        except Exception as e:
            print(f"❌ 切换到阿里云失败: {str(e)}")

    # 尝试切换回 OpenAI（如果配置了）
    if settings.OPENAI_API_KEY:
        try:
            print("   尝试切换回 OpenAI...")
            await embedding_service.switch_provider("openai")
            model_info = embedding_service.get_model_info()
            print(f"✅ 已切换回: {model_info}")

        except Exception as e:
            print(f"❌ 切换到 OpenAI 失败: {str(e)}")

    print("\n🎉 嵌入模型测试完成！")


async def test_model_comparison():
    """比较不同模型的嵌入结果"""
    print("\n🔬 开始模型比较测试...")

    test_text = "人工智能和机器学习的发展"

    # 保存原始提供商
    original_provider = settings.EMBEDDING_PROVIDER

    results = {}

    # 测试 OpenAI（如果配置了）
    if settings.OPENAI_API_KEY:
        try:
            await embedding_service.switch_provider("openai")
            embedding = await embedding_service.generate_embedding(test_text)
            results["openai"] = {
                "provider": "OpenAI",
                "model": settings.OPENAI_EMBEDDING_MODEL,
                "dimension": len(embedding),
                "embedding": embedding[:5],  # 只保存前5个值用于比较
            }
            print(f"✅ OpenAI 测试完成")
        except Exception as e:
            print(f"❌ OpenAI 测试失败: {str(e)}")

    # 测试阿里云（如果配置了）
    if settings.ALIYUN_API_KEY:
        try:
            await embedding_service.switch_provider("aliyun")
            embedding = await embedding_service.generate_embedding(test_text)
            results["aliyun"] = {
                "provider": "阿里云",
                "model": settings.ALIYUN_EMBEDDING_MODEL,
                "dimension": len(embedding),
                "embedding": embedding[:5],  # 只保存前5个值用于比较
            }
            print(f"✅ 阿里云测试完成")
        except Exception as e:
            print(f"❌ 阿里云测试失败: {str(e)}")

    # 恢复原始提供商
    try:
        await embedding_service.switch_provider(original_provider)
    except:
        pass

    # 显示比较结果
    print(f"\n📊 模型比较结果:")
    print(f"{'提供商':<10} {'模型':<20} {'维度':<8} {'前5个值'}")
    print("-" * 60)

    for key, result in results.items():
        embedding_str = ", ".join([f"{x:.4f}" for x in result["embedding"]])
        print(
            f"{result['provider']:<10} {result['model']:<20} {result['dimension']:<8} [{embedding_str}]"
        )

    if len(results) > 1:
        print(
            f"\n💡 提示: 不同模型的嵌入向量不能直接比较，因为它们的训练数据和算法不同"
        )


if __name__ == "__main__":
    asyncio.run(test_embedding_models())
    asyncio.run(test_model_comparison())
