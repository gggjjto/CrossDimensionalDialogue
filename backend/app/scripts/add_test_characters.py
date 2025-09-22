#!/usr/bin/env python3
"""
添加测试角色数据的脚本
"""
import uuid
from typing import List

from sqlmodel import Session

from app.core.db import engine
from app.crud.character import character, character_tag
from app.models.character import CharacterCreate, CharacterTagCreate


def create_test_tags(db: Session) -> List[uuid.UUID]:
    """创建测试标签"""
    test_tags = [
        {"name": "哲学", "description": "哲学相关角色", "color": "#FF6B6B"},
        {"name": "文学", "description": "文学相关角色", "color": "#4ECDC4"},
        {"name": "历史", "description": "历史人物", "color": "#45B7D1"},
        {"name": "科幻", "description": "科幻角色", "color": "#96CEB4"},
        {"name": "动漫", "description": "动漫角色", "color": "#FFEAA7"},
        {"name": "游戏", "description": "游戏角色", "color": "#DDA0DD"},
    ]
    
    tag_ids = []
    for tag_data in test_tags:
        # 检查标签是否已存在
        existing_tag = character_tag.get_by_name(db, name=tag_data["name"])
        if existing_tag:
            tag_ids.append(existing_tag.id)
            continue
            
        tag = character_tag.create(db, obj_in=CharacterTagCreate(**tag_data))
        tag_ids.append(tag.id)
        print(f"创建标签: {tag.name}")
    
    return tag_ids


def create_test_characters(db: Session, tag_ids: List[uuid.UUID]) -> None:
    """创建测试角色"""
    test_characters = [
        {
            "name": "苏格拉底",
            "short_bio": "古希腊哲学家，西方哲学的奠基人之一",
            "persona_text": "我是苏格拉底，古希腊的哲学家。我以'我知道我一无所知'而闻名。我喜欢通过提问来引导人们思考，相信真正的智慧来自于承认自己的无知。我会用苏格拉底式的对话方式与您交流，通过不断提问来帮助您发现真理。",
            "example_lines": [
                "我知道我一无所知，但我知道这一点。",
                "未经审视的人生不值得过。",
                "告诉我，你认为什么是正义？"
            ],
            "source": "古希腊哲学史",
            "tag_ids": [tag_ids[0]]  # 哲学
        },
        {
            "name": "哈利·波特",
            "short_bio": "魔法世界的年轻巫师，勇敢而善良",
            "persona_text": "我是哈利·波特，霍格沃茨魔法学校的学生。我有着闪电形状的伤疤，是'大难不死的男孩'。我勇敢、忠诚，总是愿意为朋友和正义而战。我会用魔法世界的视角与您交流，分享我在霍格沃茨的冒险经历。",
            "example_lines": [
                "除你武器！",
                "友谊和勇气比魔法更强大。",
                "选择比能力更能体现一个人的本质。"
            ],
            "source": "哈利·波特系列小说",
            "tag_ids": [tag_ids[1], tag_ids[4]]  # 文学、动漫
        },
        {
            "name": "爱因斯坦",
            "short_bio": "20世纪最伟大的物理学家，相对论的创立者",
            "persona_text": "我是阿尔伯特·爱因斯坦，理论物理学家。我提出了相对论，改变了人类对时间和空间的理解。我相信想象力比知识更重要，因为知识是有限的，而想象力概括着世界的一切。我会用科学家的思维与您探讨宇宙的奥秘。",
            "example_lines": [
                "想象力比知识更重要。",
                "上帝不会掷骰子。",
                "生活就像骑自行车，要保持平衡，就必须不断前进。"
            ],
            "source": "现代物理学史",
            "tag_ids": [tag_ids[0], tag_ids[2]]  # 哲学、历史
        },
        {
            "name": "孙悟空",
            "short_bio": "中国古典小说《西游记》中的主要角色",
            "persona_text": "我是孙悟空，齐天大圣！我有着七十二变的神通，一根如意金箍棒在手，天下无敌。我虽然顽皮好动，但心地善良，保护师父西天取经。我会用古典文学的韵味与您交流，分享我在取经路上的奇遇。",
            "example_lines": [
                "俺老孙来也！",
                "师父，有妖怪！",
                "金箍棒，长！长！长！"
            ],
            "source": "《西游记》",
            "tag_ids": [tag_ids[1], tag_ids[2]]  # 文学、历史
        },
        {
            "name": "钢铁侠",
            "short_bio": "漫威超级英雄，天才发明家和企业家",
            "persona_text": "我是托尼·斯塔克，也就是钢铁侠。我是天才发明家、亿万富翁、花花公子，同时也是超级英雄。我创造了钢铁侠战甲，用科技保护世界。我会用现代科技和幽默的方式与您交流，分享我的发明创造。",
            "example_lines": [
                "我是钢铁侠！",
                "科技改变一切。",
                "有时候你必须先学会跑，才能学会走。"
            ],
            "source": "漫威漫画",
            "tag_ids": [tag_ids[3], tag_ids[5]]  # 科幻、游戏
        }
    ]
    
    for char_data in test_characters:
        # 检查角色是否已存在
        existing_char = character.get_by_name(db, name=char_data["name"])
        if existing_char:
            print(f"角色已存在: {char_data['name']}")
            continue
            
        char = character.create(db, obj_in=CharacterCreate(**char_data))
        print(f"创建角色: {char.name}")


def main():
    """主函数"""
    print("开始创建测试数据...")
    
    with Session(engine) as db:
        # 创建测试标签
        print("\n创建测试标签...")
        tag_ids = create_test_tags(db)
        
        # 创建测试角色
        print("\n创建测试角色...")
        create_test_characters(db, tag_ids)
        
        print("\n测试数据创建完成！")
        print(f"创建了 {len(tag_ids)} 个标签")
        print("创建了 5 个测试角色")


if __name__ == "__main__":
    main()
