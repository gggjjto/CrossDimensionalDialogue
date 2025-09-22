"""
测试向量搜索功能
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlmodel import Session, create_engine, select
from app.core.config import settings
from app.models.character import Character, CharacterTag, CharacterTagMap
from app.services.embedding_service import embedding_service
from app.crud.character_embedding import character_embedding_crud


async def test_vector_search():
    """测试向量搜索功能"""
    print("🚀 开始测试向量搜索功能...")

    # 显示当前模型信息
    try:
        model_info = embedding_service.get_model_info()
        print(
            f"📊 当前嵌入模型: {model_info['provider']} - {model_info['model_name']} ({model_info['dimension']}维)"
        )
    except Exception as e:
        print(f"⚠️  获取模型信息失败: {str(e)}")

    # 创建数据库连接
    engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))

    with Session(engine) as session:
        # 1. 创建测试角色
        print("📝 创建测试角色...")

        # 创建测试标签（如果不存在）
        test_tag = session.exec(
            select(CharacterTag).where(CharacterTag.name == "测试标签")
        ).first()
        if not test_tag:
            test_tag = CharacterTag(
                name="测试标签", description="用于测试的标签", color="#FF5733"
            )
            session.add(test_tag)
            session.commit()
            session.refresh(test_tag)

        # 创建测试角色（如果不存在）
        test_character = session.exec(
            select(Character).where(Character.name == "苏格拉底")
        ).first()
        if not test_character:
            test_character = Character(
                name="苏格拉底",
                short_bio="古希腊哲学家，以问答法著称",
                persona_text="我是苏格拉底，古希腊的哲学家。我以问答法闻名，相信通过不断的提问和思考，我们可以发现真理。我总是说'我知道我什么都不知道'，这体现了我对知识的谦逊态度。",
                example_lines=[
                    "我知道我什么都不知道",
                    "未经审视的人生不值得过",
                    "美德即知识",
                ],
                source="古希腊哲学",
                is_active=True,
            )
            session.add(test_character)
            session.commit()
            session.refresh(test_character)

        # 创建角色-标签关系（如果不存在）
        existing_map = session.exec(
            select(CharacterTagMap).where(
                CharacterTagMap.character_id == test_character.id,
                CharacterTagMap.tag_id == test_tag.id,
            )
        ).first()
        if not existing_map:
            tag_map = CharacterTagMap(
                character_id=test_character.id, tag_id=test_tag.id
            )
            session.add(tag_map)
            session.commit()

        print(f"✅ 创建角色: {test_character.name}")

        # 2. 生成向量嵌入
        print("🧠 生成向量嵌入...")
        try:
            embeddings = await embedding_service.generate_character_embeddings(
                test_character, session
            )
            print(f"✅ 生成了 {len(embeddings)} 个向量嵌入")
            for emb in embeddings:
                print(f"   - {emb.embedding_type}: {emb.dimension}维")
        except Exception as e:
            print(f"❌ 生成向量嵌入失败: {str(e)}")
            return

        # 3. 测试文本搜索
        print("🔍 测试文本搜索...")
        from app.models.character import CharacterSearchRequest

        text_search_request = CharacterSearchRequest(
            query="哲学家", search_type="text", limit=10, offset=0, is_active=True
        )

        text_results = character_embedding_crud.text_search_characters(
            session, text_search_request
        )
        print(f"✅ 文本搜索找到 {len(text_results.results)} 个结果")

        # 4. 测试向量搜索
        print("🔍 测试向量搜索...")
        try:
            query_embedding = await embedding_service.generate_embedding(
                "智慧 思考 真理"
            )

            vector_search_request = CharacterSearchRequest(
                query="智慧 思考 真理",
                search_type="vector",
                limit=10,
                offset=0,
                is_active=True,
            )

            vector_results = character_embedding_crud.vector_search_characters(
                session, vector_search_request, query_embedding
            )
            print(f"✅ 向量搜索找到 {len(vector_results.results)} 个结果")

            for result in vector_results.results:
                print(f"   - {result.character.name}: 相似度 {result.score:.3f}")

        except Exception as e:
            print(f"❌ 向量搜索失败: {str(e)}")
            print("   注意：这可能需要数据库支持 pgvector 扩展")

        # 5. 测试混合搜索
        print("🔍 测试混合搜索...")
        try:
            hybrid_search_request = CharacterSearchRequest(
                query="古希腊 哲学 智慧",
                search_type="hybrid",
                limit=10,
                offset=0,
                is_active=True,
            )

            hybrid_results = character_embedding_crud.hybrid_search_characters(
                session, hybrid_search_request, query_embedding
            )
            print(f"✅ 混合搜索找到 {len(hybrid_results.results)} 个结果")

            for result in hybrid_results.results:
                print(
                    f"   - {result.character.name}: 分数 {result.score:.3f} ({result.match_type})"
                )

        except Exception as e:
            print(f"❌ 混合搜索失败: {str(e)}")

        print("🎉 测试完成！")


if __name__ == "__main__":
    asyncio.run(test_vector_search())
