from __future__ import annotations

from typing import Iterable, List, Optional

from app.core.logger import get_logger
from app.crud.voice_catalog import voice_catalog_crud
from app.models.voice_catalog import VoiceCatalog, VoiceCatalogCreate
from sqlmodel import Session

logger = get_logger("voice_catalog_service")


QWEN3_TTS_17_VOICES: List[VoiceCatalogCreate] = [
    # 说明：官方文档展示了丰富的地域与风格音色，这里依据公开示例补齐到17个常用名；
    # voice 与展示名保持一致；preview_url 暂留占位，后续可替换为实际可访问链接。
    VoiceCatalogCreate(
        provider="qwen3-tts",
        name="芊悦",
        voice="Cherry",
        preview_url=None,
        description="阳光积极、亲切自然小姐姐。",
    ),
    VoiceCatalogCreate(
        provider="qwen3-tts",
        name="晨煦",
        voice="Ethan",
        preview_url=None,
        description="标准普通话，带部分北方口音。阳光、温暖、活力、朝气。",
    ),
    VoiceCatalogCreate(
        provider="qwen3-tts",
        name="不吃鱼",
        voice="Nofish",
        preview_url=None,
        description="不会翘舌音的设计师。",
    ),
    VoiceCatalogCreate(
        provider="qwen3-tts",
        name="詹妮弗",
        voice="Jennifer",
        preview_url=None,
        description="品牌级、电影质感般美语女声。",
    ),
    VoiceCatalogCreate(
        provider="qwen3-tts",
        name="甜茶",
        voice="Ryan",
        preview_url=None,
        description="节奏拉满，戏感炸裂，真实与张力共舞。",
    ),
    VoiceCatalogCreate(
        provider="qwen3-tts",
        name="卡捷琳娜",
        voice="Katerina",
        preview_url=None,
        description="御姐音色，韵律回味十足。",
    ),
    VoiceCatalogCreate(
        provider="qwen3-tts",
        name="墨讲师",
        voice="Elias",
        preview_url=None,
        description="严谨叙事，适合知识讲解。",
    ),
    VoiceCatalogCreate(
        provider="qwen3-tts",
        name="上海-阿珍",
        voice="Jada",
        preview_url=None,
        description="沪上阿姐，风风火火",
    ),
    VoiceCatalogCreate(
        provider="qwen3-tts",
        name="北京-晓东",
        voice="Dylan",
        preview_url=None,
        description="北京胡同里长大的少年。",
    ),
    VoiceCatalogCreate(
        provider="qwen3-tts",
        name="四川-晴儿",
        voice="Sunny",
        preview_url=None,
        description="甜到你心里的川妹子",
    ),
    VoiceCatalogCreate(
        provider="qwen3-tts",
        name="南京-老李",
        voice="li",
        preview_url=None,
        description="耐心的瑜伽老师",
    ),
    VoiceCatalogCreate(
        provider="qwen3-tts",
        name="陕西-秦川",
        voice="Marcus",
        preview_url=None,
        description="面宽话短，心实声沉",
    ),
    VoiceCatalogCreate(
        provider="qwen3-tts",
        name="闽南-阿杰",
        voice="Roy",
        preview_url=None,
        description="诙谐直爽、市井活泼的台湾哥仔形象。",
    ),
    VoiceCatalogCreate(
        provider="qwen3-tts",
        name="天津-李彼得",
        voice="Peter",
        preview_url=None,
        description="相声捧哏风格",
    ),
    VoiceCatalogCreate(
        provider="qwen3-tts",
        name="粤语-阿强",
        voice="Rocky",
        preview_url=None,
        description="幽默风趣，在线陪聊",
    ),
    VoiceCatalogCreate(
        provider="qwen3-tts",
        name="粤语-阿清",
        voice="Kiki",
        preview_url=None,
        description="甜美港风闺蜜",
    ),
    VoiceCatalogCreate(
        provider="qwen3-tts",
        name="四川-程川",
        voice="Eric",
        preview_url=None,
        description="一个跳脱市井的四川成都男子。",
    ),
]


def upsert_voice_catalog(
    session: Session, *, items: Iterable[VoiceCatalogCreate]
) -> int:
    """将音色目录写入数据库（已存在则跳过）。返回新增数量。"""
    created = 0
    for item in items:
        existed = voice_catalog_crud.get_by_voice(
            session, provider=item.provider, voice=item.voice
        )
        if existed:
            continue
        voice_catalog_crud.create(session, obj_in=item)
        created += 1
    return created


def list_voices(session: Session, *, provider: str = "qwen3-tts") -> list[VoiceCatalog]:
    items, _ = voice_catalog_crud.get_multi(session, provider=provider, limit=500)
    return items


def init_qwen3_tts_voice_catalog(session: Session) -> int:
    """项目初始化时调用：初始化 Qwen3-TTS 的 17 种音色目录。"""
    return upsert_voice_catalog(session, items=QWEN3_TTS_17_VOICES)


def get_voice_catalog_with_demos(
    session: Session, *, provider: str = "qwen3-tts"
) -> list[VoiceCatalog]:
    """获取包含示例语音的音色目录"""
    items, _ = voice_catalog_crud.get_multi(session, provider=provider, limit=500)
    return items
