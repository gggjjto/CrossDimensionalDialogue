from typing import Any, Dict, Optional, Union
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)


class APIResponse:
    """统一API响应格式"""
    
    @staticmethod
    def success(
        data: Any = None,
        msg: str = "ok",
        code: int = 0
    ) -> Dict[str, Any]:
        """
        成功响应
        
        Args:
            data: 响应数据
            msg: 响应消息
            code: 响应代码
            
        Returns:
            统一格式的响应字典
        """
        return {
            "code": code,
            "msg": msg,
            "data": data
        }
    
    @staticmethod
    def error(
        msg: str = "error",
        code: int = 1,
        data: Any = None
    ) -> Dict[str, Any]:
        """
        错误响应
        
        Args:
            msg: 错误消息
            code: 错误代码
            data: 错误数据
            
        Returns:
            统一格式的响应字典
        """
        return {
            "code": code,
            "msg": msg,
            "data": data
        }
    
    @staticmethod
    def validation_error(
        errors: list,
        msg: str = "数据验证失败"
    ) -> Dict[str, Any]:
        """
        数据验证错误响应
        
        Args:
            errors: 验证错误列表
            msg: 错误消息
            
        Returns:
            统一格式的响应字典
        """
        return {
            "code": 400,
            "msg": msg,
            "data": {
                "errors": errors
            }
        }
    
    @staticmethod
    def not_found(
        resource: str = "资源",
        msg: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        资源未找到响应
        
        Args:
            resource: 资源名称
            msg: 自定义消息
            
        Returns:
            统一格式的响应字典
        """
        if msg is None:
            msg = f"{resource}未找到"
        return {
            "code": 404,
            "msg": msg,
            "data": None
        }
    
    @staticmethod
    def unauthorized(
        msg: str = "未授权访问"
    ) -> Dict[str, Any]:
        """
        未授权响应
        
        Args:
            msg: 错误消息
            
        Returns:
            统一格式的响应字典
        """
        return {
            "code": 401,
            "msg": msg,
            "data": None
        }
    
    @staticmethod
    def forbidden(
        msg: str = "权限不足"
    ) -> Dict[str, Any]:
        """
        权限不足响应
        
        Args:
            msg: 错误消息
            
        Returns:
            统一格式的响应字典
        """
        return {
            "code": 403,
            "msg": msg,
            "data": None
        }
    
    @staticmethod
    def server_error(
        msg: str = "服务器内部错误"
    ) -> Dict[str, Any]:
        """
        服务器错误响应
        
        Args:
            msg: 错误消息
            
        Returns:
            统一格式的响应字典
        """
        return {
            "code": 500,
            "msg": msg,
            "data": None
        }


class GlobalExceptionHandler:
    """全局异常处理器"""
    
    @staticmethod
    async def http_exception_handler(
        request: Request,
        exc: HTTPException
    ) -> JSONResponse:
        """
        HTTP异常处理器
        
        Args:
            request: 请求对象
            exc: HTTP异常
            
        Returns:
            JSON响应
        """
        logger.warning(f"HTTP异常: {exc.status_code} - {exc.detail}")
        
        # 根据状态码返回不同的错误信息
        if exc.status_code == 404:
            response_data = APIResponse.not_found(msg=exc.detail)
        elif exc.status_code == 401:
            response_data = APIResponse.unauthorized(msg=exc.detail)
        elif exc.status_code == 403:
            response_data = APIResponse.forbidden(msg=exc.detail)
        elif exc.status_code == 422:
            response_data = APIResponse.validation_error(
                errors=[exc.detail],
                msg="请求参数错误"
            )
        else:
            response_data = APIResponse.error(
                msg=exc.detail,
                code=exc.status_code
            )
        
        return JSONResponse(
            status_code=exc.status_code,
            content=response_data
        )
    
    @staticmethod
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError
    ) -> JSONResponse:
        """
        请求验证异常处理器
        
        Args:
            request: 请求对象
            exc: 验证异常
            
        Returns:
            JSON响应
        """
        logger.warning(f"请求验证异常: {exc.errors()}")
        
        # 格式化验证错误
        formatted_errors = []
        for error in exc.errors():
            field = " -> ".join(str(loc) for loc in error["loc"])
            formatted_errors.append({
                "field": field,
                "message": error["msg"],
                "type": error["type"]
            })
        
        response_data = APIResponse.validation_error(
            errors=formatted_errors,
            msg="请求参数验证失败"
        )
        
        return JSONResponse(
            status_code=422,
            content=response_data
        )
    
    @staticmethod
    async def pydantic_validation_exception_handler(
        request: Request,
        exc: ValidationError
    ) -> JSONResponse:
        """
        Pydantic验证异常处理器
        
        Args:
            request: 请求对象
            exc: Pydantic验证异常
            
        Returns:
            JSON响应
        """
        logger.warning(f"Pydantic验证异常: {exc.errors()}")
        
        # 格式化Pydantic验证错误
        formatted_errors = []
        for error in exc.errors():
            field = " -> ".join(str(loc) for loc in error["loc"])
            formatted_errors.append({
                "field": field,
                "message": error["msg"],
                "type": error["type"]
            })
        
        response_data = APIResponse.validation_error(
            errors=formatted_errors,
            msg="数据模型验证失败"
        )
        
        return JSONResponse(
            status_code=422,
            content=response_data
        )
    
    @staticmethod
    async def general_exception_handler(
        request: Request,
        exc: Exception
    ) -> JSONResponse:
        """
        通用异常处理器
        
        Args:
            request: 请求对象
            exc: 异常
            
        Returns:
            JSON响应
        """
        logger.error(f"未处理的异常: {type(exc).__name__}: {str(exc)}", exc_info=True)
        
        response_data = APIResponse.server_error(
            msg="服务器内部错误，请稍后重试"
        )
        
        return JSONResponse(
            status_code=500,
            content=response_data
        )


# 便捷函数
def success_response(data: Any = None, msg: str = "ok", code: int = 0) -> Dict[str, Any]:
    """成功响应便捷函数"""
    return APIResponse.success(data=data, msg=msg, code=code)


def error_response(msg: str = "error", code: int = 1, data: Any = None) -> Dict[str, Any]:
    """错误响应便捷函数"""
    return APIResponse.error(msg=msg, code=code, data=data)


def not_found_response(resource: str = "资源", msg: Optional[str] = None) -> Dict[str, Any]:
    """未找到响应便捷函数"""
    return APIResponse.not_found(resource=resource, msg=msg)


def unauthorized_response(msg: str = "未授权访问") -> Dict[str, Any]:
    """未授权响应便捷函数"""
    return APIResponse.unauthorized(msg=msg)


def forbidden_response(msg: str = "权限不足") -> Dict[str, Any]:
    """权限不足响应便捷函数"""
    return APIResponse.forbidden(msg=msg)


def server_error_response(msg: str = "服务器内部错误") -> Dict[str, Any]:
    """服务器错误响应便捷函数"""
    return APIResponse.server_error(msg=msg)
