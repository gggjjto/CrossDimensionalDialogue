"""
调试向量搜索问题
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlmodel import Session, create_engine, text
from app.core.config import settings
from app.services.embedding_service import embedding_service


async def test_vector_debug():
    """调试向量搜索问题"""
    print("🚀 开始调试向量搜索...")

    # 创建数据库连接
    engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))

    with Session(engine) as session:
        try:
            # 生成测试向量
            test_text = "古希腊哲学家"
            query_embedding = await embedding_service.generate_embedding(test_text)
            print(f"✅ 查询向量维度: {len(query_embedding)}")

            # 测试简单的向量查询
            # 将向量转换为字符串格式
            vector_str = "[" + ",".join(map(str, query_embedding)) + "]"

            simple_stmt = f"""
            SELECT 
                ce.character_id,
                1 - (ce.embedding <=> '{vector_str}'::vector) as similarity_score
            FROM character_embeddings ce
            WHERE ce.embedding_type = 'combined'
            ORDER BY ce.embedding <=> '{vector_str}'::vector
            LIMIT 5
            """

            print("🔍 测试简单向量查询...")
            try:
                results = session.exec(text(simple_stmt)).all()
                print(f"✅ 简单查询成功，找到 {len(results)} 个结果")
                for result in results:
                    print(f"   - 角色ID: {result[0]}, 相似度: {result[1]:.4f}")
            except Exception as e:
                print(f"❌ 简单查询失败: {str(e)}")
                import traceback

                traceback.print_exc()

            # 测试计数查询
            count_stmt = f"""
            SELECT COUNT(*)
            FROM character_embeddings ce
            WHERE ce.embedding_type = 'combined'
            AND 1 - (ce.embedding <=> '{vector_str}'::vector) > 0.5
            """

            print("\n🔍 测试计数查询...")
            try:
                total = session.exec(text(count_stmt)).one()
                print(f"✅ 计数查询成功，总数: {total}")
            except Exception as e:
                print(f"❌ 计数查询失败: {str(e)}")
                import traceback

                traceback.print_exc()

        except Exception as e:
            print(f"❌ 调试失败: {str(e)}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_vector_debug())
