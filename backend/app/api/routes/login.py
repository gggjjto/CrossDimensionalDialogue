import random
from datetime import timedelta
from typing import Annotated, Any

from app.api.deps import CurrentUser, SessionDep, get_current_active_superuser
from app.core import security
from app.core.config import settings
from app.core.redis import redis_client
from app.core.security import get_password_hash
from app.crud import user as crud_user
from app.models import Message, NewPassword, Token, UserPublic
from app.utils import (
    generate_password_reset_token,
    generate_reset_password_email,
    send_email,
    verify_password_reset_token,
)
from app.utils.response import error_response, success_response
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr

router = APIRouter(tags=["login"])


@router.post("/login/access-token")
def login_access_token(
    session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    """
    OAuth2兼容的令牌登录，获取访问令牌用于后续请求
    """
    user = crud_user.authenticate(
        session=session, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="邮箱或密码错误")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="用户账户未激活")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = Token(
        access_token=security.create_access_token(
            user.id, expires_delta=access_token_expires
        )
    )
    return token.dict()


@router.post("/login/access-token-v2")
def login_access_token_v2(
    session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    """
    OAuth2兼容的令牌登录，获取访问令牌用于后续请求
    """
    user = crud_user.authenticate(
        session=session, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="邮箱或密码错误")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="用户账户未激活")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = Token(
        access_token=security.create_access_token(
            user.id, expires_delta=access_token_expires
        )
    )
    return success_response(data=token.dict(), msg="登录成功")


@router.post("/login/test-token")
def test_token(current_user: CurrentUser):
    """
    测试访问令牌
    """
    return success_response(data=current_user.dict(), msg="令牌验证成功")


@router.post("/password-recovery/{email}")
def recover_password(email: str, session: SessionDep):
    """
    密码恢复
    """
    user = crud_user.get_user_by_email(session=session, email=email)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="该邮箱不存在于系统中。",
        )
    password_reset_token = generate_password_reset_token(email=email)
    email_data = generate_reset_password_email(
        email_to=user.email, email=email, token=password_reset_token
    )
    send_email(
        email_to=user.email,
        subject=email_data.subject,
        html_content=email_data.html_content,
    )
    return success_response(
        data={"message": "密码恢复邮件已发送"}, msg="密码恢复邮件已发送"
    )


@router.post("/reset-password/")
def reset_password(session: SessionDep, body: NewPassword):
    """
    重置密码
    """
    email = verify_password_reset_token(token=body.token)
    if not email:
        raise HTTPException(status_code=400, detail="无效的令牌")
    user = crud_user.get_user_by_email(session=session, email=email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="该邮箱不存在于系统中。",
        )
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="用户账户未激活")
    hashed_password = get_password_hash(password=body.new_password)
    user.hashed_password = hashed_password
    session.add(user)
    session.commit()
    return success_response(data={"message": "密码更新成功"}, msg="密码更新成功")


class SendVerificationCodeRequest(BaseModel):
    email: EmailStr


class VerifyEmailCodeRequest(BaseModel):
    email: EmailStr
    code: str


def _generate_numeric_code(length: int) -> str:
    digits = "0123456789"
    code_chars = [random.choice(digits) for _ in range(length)]
    return "".join(code_chars)


@router.post("/login/send-email-verification-code")
def send_email_verification_code(
    body: SendVerificationCodeRequest, _session: SessionDep
):
    """
    发送邮箱验证码，将验证码存入Redis并发送邮件。
    """
    code = _generate_numeric_code(settings.EMAIL_VERIFICATION_CODE_LENGTH)
    key = f"email_verification:{body.email}"
    ttl = settings.EMAIL_VERIFICATION_CODE_TTL_SECONDS

    # Redis 二进制客户端，需写入 bytes
    redis_client.client.setex(name=key, time=ttl, value=code.encode("utf-8"))

    from app.utils import generate_verify_email_code_email

    email_data = generate_verify_email_code_email(email_to=body.email, code=code)
    send_email(
        email_to=body.email,
        subject=email_data.subject,
        html_content=email_data.html_content,
    )

    return success_response(data={"message": "验证码已发送"}, msg="验证码已发送")


@router.post("/login/verify-email-code")
def verify_email_code(body: VerifyEmailCodeRequest, _session: SessionDep):
    """
    校验邮箱验证码，成功后将用户标记为已验证。
    """
    key = f"email_verification:{body.email}"
    value = redis_client.client.get(name=key)
    if not value:
        raise HTTPException(status_code=400, detail="验证码无效或已过期")

    stored_code = value.decode("utf-8")
    if stored_code != body.code:
        raise HTTPException(status_code=400, detail="验证码错误")

    # 校验通过后删除验证码，返回成功
    redis_client.client.delete(key)

    return success_response(data={"message": "邮箱验证成功"}, msg="邮箱验证成功")


@router.post(
    "/password-recovery-html-content/{email}",
    dependencies=[Depends(get_current_active_superuser)],
    response_class=HTMLResponse,
)
def recover_password_html_content(email: str, session: SessionDep) -> Any:
    """
    密码恢复的HTML内容
    """
    user = crud_user.get_user_by_email(session=session, email=email)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="该用户名不存在于系统中。",
        )
    password_reset_token = generate_password_reset_token(email=email)
    email_data = generate_reset_password_email(
        email_to=user.email, email=email, token=password_reset_token
    )

    return HTMLResponse(
        content=email_data.html_content, headers={"subject:": email_data.subject}
    )
