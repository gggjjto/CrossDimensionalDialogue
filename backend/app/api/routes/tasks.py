"""
任务管理API路由
"""

import uuid
from typing import Optional

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.task import (
    TaskCancelRequest,
    TaskListRequest,
    TaskListResponse,
    TaskResponse,
    TaskStatsResponse,
)
from app.services.task_queue_service import task_queue_service
from app.utils.response import error_response, success_response
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/{task_id}")
async def get_task_status(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    task_id: str,
):
    """
    获取任务状态

    Args:
        db: 数据库会话
        current_user: 当前用户
        task_id: 任务ID

    Returns:
        任务状态信息
    """
    try:
        task = await task_queue_service.get_task(
            db=db, task_id=task_id, user_id=current_user.id
        )

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="任务不存在或无权限访问"
            )

        return success_response(data=task.dict(), msg="任务状态获取成功")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取任务状态失败: {str(e)}",
        )


@router.get("/")
async def get_user_tasks(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    task_type: Optional[str] = Query(None, description="任务类型过滤"),
    status_1: Optional[str] = Query(None, description="任务状态过滤"),
    conversation_id: Optional[uuid.UUID] = Query(None, description="会话ID过滤"),
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回的记录数"),
    order_by: str = Query("created_at", description="排序字段"),
    order: str = Query("desc", description="排序方向"),
):
    """
    获取用户任务列表

    Args:
        db: 数据库会话
        current_user: 当前用户
        task_type: 任务类型过滤
        status: 任务状态过滤
        conversation_id: 会话ID过滤
        skip: 跳过的记录数
        limit: 返回的记录数
        order_by: 排序字段
        order: 排序方向

    Returns:
        任务列表
    """
    try:
        request = TaskListRequest(
            task_type=task_type,
            status=status_1,
            conversation_id=conversation_id,
            skip=skip,
            limit=limit,
            order_by=order_by,
            order=order,
        )

        result = await task_queue_service.get_user_tasks(
            db=db, user_id=current_user.id, request=request
        )

        return success_response(data=result.dict(), msg="任务列表获取成功")

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取任务列表失败: {str(e)}",
        )


@router.post("/{task_id}/cancel")
async def cancel_task(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    task_id: str,
    request: TaskCancelRequest,
):
    """
    取消任务

    Args:
        db: 数据库会话
        current_user: 当前用户
        task_id: 任务ID
        request: 取消请求

    Returns:
        取消结果
    """
    try:
        success = await task_queue_service.cancel_task(
            db=db, task_id=task_id, user_id=current_user.id, reason=request.reason
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="任务不存在或无权限访问"
            )

        return success_response(
            data={"task_id": task_id, "cancelled": True}, msg="任务已取消"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"取消任务失败: {str(e)}",
        )


@router.get("/stats/summary")
async def get_task_stats(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取任务统计信息

    Args:
        db: 数据库会话
        current_user: 当前用户

    Returns:
        任务统计信息
    """
    try:
        stats = await task_queue_service.get_task_stats(db=db, user_id=current_user.id)

        return success_response(data=stats.dict(), msg="任务统计获取成功")

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取任务统计失败: {str(e)}",
        )
