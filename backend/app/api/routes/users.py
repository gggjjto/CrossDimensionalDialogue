import uuid
from typing import Any

from app.api.deps import CurrentUser, SessionDep, get_current_active_superuser
from app.core.config import settings
from app.core.security import get_password_hash, verify_password
from app.crud import user as crud_user
from app.models import (
    Item,
    Message,
    UpdatePassword,
    User,
    UserCreate,
    UserPublic,
    UserRegister,
    UsersPublic,
    UserUpdate,
    UserUpdateMe,
)
from app.utils import generate_new_account_email, send_email
from app.utils.response import success_response, error_response, not_found_response
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlmodel import col, delete, select

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/")
def read_users(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """
    获取用户列表。
    """
    count_statement = select(func.count()).select_from(User)
    count = session.exec(count_statement).one()

    statement = select(User).offset(skip).limit(limit)
    users = session.exec(statement).all()
    
    return success_response(
        data={
            "users": [user.model_dump() for user in users],
            "total": count,
            "skip": skip,
            "limit": limit,
        },
        msg="获取用户列表成功"
    )


@router.post("/")
def create_user(*, session: SessionDep, user_in: UserCreate) -> Any:
    """
    创建新用户。
    """
    user = crud_user.get_user_by_email(session=session, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="用户邮箱已存在",
        )

    user = crud_user.create_user(session=session, user_create=user_in)
    if settings.emails_enabled and user_in.email:
        email_data = generate_new_account_email(
            email_to=user_in.email, username=user_in.email, password=user_in.password
        )
        send_email(
            email_to=user_in.email,
            subject=email_data.subject,
            html_content=email_data.html_content,
        )
    return success_response(data=user.model_dump(), msg="用户创建成功")


@router.patch("/me")
def update_user_me(
    *, session: SessionDep, user_in: UserUpdateMe, current_user: CurrentUser
) -> Any:
    """
    更新当前用户信息。
    """

    if user_in.email:
        existing_user = crud_user.get_user_by_email(
            session=session, email=user_in.email
        )
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=409, detail="用户邮箱已存在"
            )
    user_data = user_in.model_dump(exclude_unset=True)
    current_user.sqlmodel_update(user_data)
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return success_response(data=current_user.model_dump(), msg="用户信息更新成功")


@router.patch("/me/password")
def update_password_me(
    *, session: SessionDep, body: UpdatePassword, current_user: CurrentUser
) -> Any:
    """
    更新当前用户密码。
    """
    if not verify_password(body.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="当前密码错误")
    if body.current_password == body.new_password:
        raise HTTPException(
            status_code=400, detail="新密码不能与当前密码相同"
        )
    hashed_password = get_password_hash(body.new_password)
    current_user.hashed_password = hashed_password
    session.add(current_user)
    session.commit()
    return success_response(msg="密码更新成功")


@router.get("/me")
def read_user_me(current_user: CurrentUser) -> Any:
    """
    获取当前用户信息。
    """
    return success_response(data=current_user.model_dump(), msg="获取用户信息成功")


@router.delete("/me")
def delete_user_me(session: SessionDep, current_user: CurrentUser) -> Any:
    """
    删除当前用户。
    """
    if current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="超级用户不能删除自己"
        )
    session.delete(current_user)
    session.commit()
    return success_response(msg="用户删除成功")


@router.post("/signup")
def register_user(session: SessionDep, user_in: UserRegister) -> Any:
    """
    用户注册（无需登录）。
    """
    user = crud_user.get_user_by_email(session=session, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="用户邮箱已存在",
        )
    user_create = UserCreate.model_validate(user_in)
    user = crud_user.create_user(session=session, user_create=user_create)
    return success_response(data=user.model_dump(), msg="用户注册成功")


@router.get("/{user_id}")
def read_user_by_id(
    user_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    根据ID获取用户信息。
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if user == current_user:
        return success_response(data=user.model_dump(), msg="获取用户信息成功")
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="用户权限不足",
        )
    return success_response(data=user.model_dump(), msg="获取用户信息成功")


@router.patch("/{user_id}")
def update_user(
    *,
    session: SessionDep,
    user_id: uuid.UUID,
    user_in: UserUpdate,
) -> Any:
    """
    更新用户信息。
    """

    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="用户不存在",
        )
    if user_in.email:
        existing_user = crud_user.get_user_by_email(
            session=session, email=user_in.email
        )
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=409, detail="用户邮箱已存在"
            )

    db_user = crud_user.update_user(session=session, db_user=db_user, user_in=user_in)
    return success_response(data=db_user.model_dump(), msg="用户信息更新成功")


@router.delete("/{user_id}")
def delete_user(
    session: SessionDep, current_user: CurrentUser, user_id: uuid.UUID
) -> Any:
    """
    删除用户。
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if user == current_user:
        raise HTTPException(
            status_code=403, detail="超级用户不能删除自己"
        )
    statement = delete(Item).where(col(Item.owner_id) == user_id)
    session.exec(statement)  # type: ignore
    session.delete(user)
    session.commit()
    return success_response(msg="用户删除成功")
