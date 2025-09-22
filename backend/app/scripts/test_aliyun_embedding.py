"""
测试阿里云嵌入模型功能
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.services.embedding_service import embedding_service
from app.core.config import settings


async def test_aliyun_embedding():
    """测试阿里云嵌入模型功能"""
    print("🚀 开始测试阿里云嵌入模型功能...")
    
    # 显示配置信息
    print(f"📊 当前配置:")
    print(f"   提供商: {settings.EMBEDDING_PROVIDER}")
    print(f"   模型: {settings.ALIYUN_EMBEDDING_MODEL}")
    print(f"   API 密钥: {'已配置' if settings.ALIYUN_API_KEY else '未配置'}")
    
    # 获取模型信息
    try:
        model_info = embedding_service.get_model_info()
        print(f"\n📋 模型信息: {model_info}")
    except Exception as e:
        print(f"❌ 获取模型信息失败: {str(e)}")
        return
    
    # 测试单个嵌入生成
    print(f"\n🔍 测试单个嵌入生成...")
    test_texts = [
        "苏格拉底是古希腊哲学家",
        "人工智能和机器学习的发展",
        "今天天气很好，适合出去散步",
        "编程是一门艺术，需要不断练习",
        "哲学思考让我们更深入地理解世界"
    ]
    
    for i, text in enumerate(test_texts, 1):
        try:
            embedding = await embedding_service.generate_embedding(text)
            print(f"✅ 文本 {i}: 维度 {len(embedding)}, 前3个值: {embedding[:3]}")
        except Exception as e:
            print(f"❌ 文本 {i} 失败: {str(e)}")
    
    # 测试批量嵌入生成
    print(f"\n🔍 测试批量嵌入生成...")
    try:
        embeddings = await embedding_service.generate_embeddings_batch(test_texts)
        print(f"✅ 批量生成成功: {len(embeddings)} 个嵌入")
        for i, emb in enumerate(embeddings, 1):
            print(f"   嵌入 {i}: 维度 {len(emb)}")
    except Exception as e:
        print(f"❌ 批量生成失败: {str(e)}")
    
    # 测试相似度计算
    print(f"\n🔍 测试相似度计算...")
    try:
        text1 = "苏格拉底是古希腊哲学家"
        text2 = "哲学思考让我们更深入地理解世界"
        text3 = "今天天气很好，适合出去散步"
        
        emb1 = await embedding_service.generate_embedding(text1)
        emb2 = await embedding_service.generate_embedding(text2)
        emb3 = await embedding_service.generate_embedding(text3)
        
        # 计算余弦相似度
        def cosine_similarity(a, b):
            import math
            dot_product = sum(x * y for x, y in zip(a, b))
            magnitude_a = math.sqrt(sum(x * x for x in a))
            magnitude_b = math.sqrt(sum(x * x for x in b))
            return dot_product / (magnitude_a * magnitude_b)
        
        sim_1_2 = cosine_similarity(emb1, emb2)
        sim_1_3 = cosine_similarity(emb1, emb3)
        sim_2_3 = cosine_similarity(emb2, emb3)
        
        print(f"✅ 相似度计算结果:")
        print(f"   '{text1}' vs '{text2}': {sim_1_2:.4f}")
        print(f"   '{text1}' vs '{text3}': {sim_1_3:.4f}")
        print(f"   '{text2}' vs '{text3}': {sim_2_3:.4f}")
        
        # 分析结果
        if sim_1_2 > sim_1_3 and sim_1_2 > sim_2_3:
            print(f"   💡 哲学相关文本相似度最高，符合预期")
        else:
            print(f"   ⚠️  相似度结果可能需要进一步调优")
            
    except Exception as e:
        print(f"❌ 相似度计算失败: {str(e)}")
    
    # 测试模型切换（如果配置了 OpenAI）
    if settings.OPENAI_API_KEY:
        print(f"\n🔄 测试模型切换...")
        try:
            print("   切换到 OpenAI...")
            await embedding_service.switch_provider("openai")
            model_info = embedding_service.get_model_info()
            print(f"   ✅ 已切换到: {model_info}")
            
            # 测试 OpenAI 嵌入
            embedding = await embedding_service.generate_embedding("测试 OpenAI 嵌入")
            print(f"   ✅ OpenAI 嵌入维度: {len(embedding)}")
            
            # 切换回阿里云
            print("   切换回阿里云...")
            await embedding_service.switch_provider("aliyun")
            model_info = embedding_service.get_model_info()
            print(f"   ✅ 已切换回: {model_info}")
            
        except Exception as e:
            print(f"   ❌ 模型切换失败: {str(e)}")
    else:
        print(f"\n⚠️  未配置 OpenAI API 密钥，跳过模型切换测试")
    
    print(f"\n🎉 阿里云嵌入模型测试完成！")


if __name__ == "__main__":
    asyncio.run(test_aliyun_embedding())
