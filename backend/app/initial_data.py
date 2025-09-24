import logging

from sqlmodel import Session

from app.core.db import engine, init_db
from app.services.voice_catalog_service import init_qwen3_tts_voice_catalog

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init() -> None:
    with Session(engine) as session:
        init_db(session)
        # 初始化 Qwen3-TTS 17 音色目录（幂等）
        created = init_qwen3_tts_voice_catalog(session)
        if created:
            logger.info(f"Initialized {created} qwen3-tts voices into catalog")


def main() -> None:
    logger.info("Creating initial data")
    init()
    logger.info("Initial data created")


if __name__ == "__main__":
    main()
