#!/usr/bin/env python3
"""
测试角色搜索功能的脚本
"""
import uuid
from typing import List

from sqlmodel import Session

from app.core.db import engine
from app.crud.character import character
from app.models.character import CharacterSearchRequest


def test_text_search():
    """测试文本搜索功能"""
    print("=== 测试文本搜索功能 ===")
    
    with Session(engine) as db:
        # 测试1: 按名称搜索
        print("\n1. 按名称搜索 '苏格拉底':")
        search_request = CharacterSearchRequest(
            query="苏格拉底",
            search_type="text",
            limit=10
        )
        result = character.search(db, search_request=search_request)
        print(f"找到 {result.total} 个结果:")
        for item in result.results:
            print(f"  - {item.character.name}: {item.character.short_bio}")
        
        # 测试2: 按描述搜索
        print("\n2. 按描述搜索 '哲学':")
        search_request = CharacterSearchRequest(
            query="哲学",
            search_type="text",
            limit=10
        )
        result = character.search(db, search_request=search_request)
        print(f"找到 {result.total} 个结果:")
        for item in result.results:
            print(f"  - {item.character.name}: {item.character.short_bio}")
        
        # 测试3: 按人格描述搜索
        print("\n3. 按人格描述搜索 '魔法':")
        search_request = CharacterSearchRequest(
            query="魔法",
            search_type="text",
            limit=10
        )
        result = character.search(db, search_request=search_request)
        print(f"找到 {result.total} 个结果:")
        for item in result.results:
            print(f"  - {item.character.name}: {item.character.short_bio}")
        
        # 测试4: 按标签搜索
        print("\n4. 按标签搜索 (哲学标签):")
        # 先获取哲学标签的ID
        from app.crud.character import character_tag
        philosophy_tag = character_tag.get_by_name(db, name="哲学")
        if philosophy_tag:
            search_request = CharacterSearchRequest(
                query="",
                search_type="text",
                limit=10,
                tag_ids=[philosophy_tag.id]
            )
            result = character.search(db, search_request=search_request)
            print(f"找到 {result.total} 个结果:")
            for item in result.results:
                print(f"  - {item.character.name}: {item.character.short_bio}")
        
        # 测试5: 空查询
        print("\n5. 空查询 (获取所有角色):")
        search_request = CharacterSearchRequest(
            query="",
            search_type="text",
            limit=10
        )
        result = character.search(db, search_request=search_request)
        print(f"找到 {result.total} 个结果:")
        for item in result.results:
            print(f"  - {item.character.name}: {item.character.short_bio}")


def test_vector_search():
    """测试向量搜索功能"""
    print("\n=== 测试向量搜索功能 ===")
    print("注意: 向量搜索功能尚未完全实现，目前返回空结果")
    
    with Session(engine) as db:
        search_request = CharacterSearchRequest(
            query="智慧",
            search_type="vector",
            limit=10
        )
        result = character.search(db, search_request=search_request)
        print(f"向量搜索 '智慧' 找到 {result.total} 个结果")


def test_hybrid_search():
    """测试混合搜索功能"""
    print("\n=== 测试混合搜索功能 ===")
    print("注意: 混合搜索目前使用文本搜索")
    
    with Session(engine) as db:
        search_request = CharacterSearchRequest(
            query="科学",
            search_type="hybrid",
            limit=10
        )
        result = character.search(db, search_request=search_request)
        print(f"混合搜索 '科学' 找到 {result.total} 个结果:")
        for item in result.results:
            print(f"  - {item.character.name}: {item.character.short_bio}")


def main():
    """主函数"""
    print("开始测试角色搜索功能...")
    
    # 测试文本搜索
    test_text_search()
    
    # 测试向量搜索
    test_vector_search()
    
    # 测试混合搜索
    test_hybrid_search()
    
    print("\n搜索功能测试完成！")


if __name__ == "__main__":
    main()
