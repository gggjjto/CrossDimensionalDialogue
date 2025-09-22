from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
import logging

from app.utils.response import GlobalExceptionHandler

logger = logging.getLogger(__name__)


def setup_exception_handlers(app: FastAPI) -> None:
    """
    设置全局异常处理器

    Args:
        app: FastAPI应用实例
    """

    # HTTP异常处理器
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return await GlobalExceptionHandler.http_exception_handler(request, exc)

    # 请求验证异常处理器
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        return await GlobalExceptionHandler.validation_exception_handler(request, exc)

    # Pydantic验证异常处理器
    @app.exception_handler(ValidationError)
    async def pydantic_validation_exception_handler(
        request: Request, exc: ValidationError
    ):
        return await GlobalExceptionHandler.pydantic_validation_exception_handler(
            request, exc
        )

    # 通用异常处理器
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        return await GlobalExceptionHandler.general_exception_handler(request, exc)

    logger.info("全局异常处理器已设置")
