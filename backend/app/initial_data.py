from sqlmodel import Session

from app.core.db import engine, init_db
from app.services.voice_catalog_service import init_qwen3_tts_voice_catalog
from app.core.logger import get_logger
logger = get_logger("initial_data")


def init() -> None:
    with Session(engine) as session:
        init_db(session)
        # 初始化 Qwen3-TTS 17 音色目录（幂等）
        created = init_qwen3_tts_voice_catalog(session)
        if created:
            logger.info("将 %s qwen3-tts voices 写入音色目录", created)


def main() -> None:
    logger.info("创建初始数据")
    init()
    logger.info("初始数据创建完成")


if __name__ == "__main__":
    main()
