"""
测试 pgvector 扩展是否正常工作
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlmodel import Session, create_engine, text
from app.core.config import settings


def test_pgvector_extension():
    """测试 pgvector 扩展是否正常工作"""
    print("🚀 开始测试 pgvector 扩展...")

    # 创建数据库连接
    engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))

    with Session(engine) as session:
        try:
            # 0. 启用 pgvector 扩展（如果已存在就跳过） CREATE EXTENSION IF NOT EXISTS vector;
            # 1. 检查 pgvector 扩展是否已安装
            print("📋 检查 pgvector 扩展...")
            result = session.exec(
                text(
                    "SELECT extname, extversion FROM pg_extension WHERE extname = 'vector'"
                )
            ).first()
            if result:
                print(f"✅ pgvector 扩展已安装: {result[0]} v{result[1]}")
            else:
                print("❌ pgvector 扩展未安装")
                return False


            # 3. 测试向量操作
            print("🔍 测试向量操作...")

            # 创建测试表
            session.exec(
                text(
                    """
                CREATE TABLE IF NOT EXISTS test_vectors (
                    id SERIAL PRIMARY KEY,
                    name TEXT,
                    embedding VECTOR(3)
                )
            """
                )
            )
            session.commit()

            # 插入测试数据
            session.exec(
                text(
                    """
                INSERT INTO test_vectors (name, embedding) VALUES 
                ('vector1', '[1,2,3]'),
                ('vector2', '[4,5,6]'),
                ('vector3', '[1,1,1]')
                ON CONFLICT DO NOTHING
            """
                )
            )
            session.commit()

            # 测试向量相似度搜索
            print("🔍 测试向量相似度搜索...")
            similarity_result = session.exec(
                text(
                    """
                SELECT name, embedding <-> '[1,2,3]' as distance
                FROM test_vectors
                ORDER BY embedding <-> '[1,2,3]'
                LIMIT 3
            """
                )
            ).all()

            if similarity_result:
                print("✅ 向量相似度搜索成功:")
                for row in similarity_result:
                    print(f"   {row[0]}: 距离 {row[1]:.4f}")
            else:
                print("❌ 向量相似度搜索失败")
                return False

            # 测试余弦相似度
            print("🔍 测试余弦相似度...")
            cosine_result = session.exec(
                text(
                    """
                SELECT name, 1 - (embedding <=> '[1,2,3]') as cosine_similarity
                FROM test_vectors
                ORDER BY embedding <=> '[1,2,3]'
                LIMIT 3
            """
                )
            ).all()

            if cosine_result:
                print("✅ 余弦相似度计算成功:")
                for row in cosine_result:
                    print(f"   {row[0]}: 相似度 {row[1]:.4f}")
            else:
                print("❌ 余弦相似度计算失败")
                return False

            # 清理测试表
            session.exec(text("DROP TABLE IF EXISTS test_vectors"))
            session.commit()

            print("🎉 pgvector 扩展测试完成！")
            return True

        except Exception as e:
            print(f"❌ pgvector 测试失败: {str(e)}")
            return False


if __name__ == "__main__":
    success = test_pgvector_extension()
    if success:
        print("\n✅ pgvector 扩展工作正常，可以开始使用向量搜索功能！")
    else:
        print("\n❌ pgvector 扩展有问题，请检查 Docker 配置和数据库连接。")
