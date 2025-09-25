import logging
import sys
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# 日志格式
LOG_FORMAT = (
    "%(asctime)s [%(levelname)s] [%(name)s] %(filename)s:%(lineno)d | %(message)s"
)


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """获取一个带文件+控制台输出的 logger"""
    logger = logging.getLogger(name)

    if logger.handlers:
        # 避免重复添加 handler
        return logger

    logger.setLevel(level)

    # 控制台输出
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT))

    # 文件输出（每天滚动）
    file_handler = TimedRotatingFileHandler(
        LOG_DIR / f"{name}.log",
        when="midnight",
        interval=1,
        backupCount=7,
        encoding="utf-8",
    )
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
