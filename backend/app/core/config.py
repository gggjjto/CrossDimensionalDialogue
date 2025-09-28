import secrets
import warnings
from pathlib import Path
from typing import Annotated, Any, Literal

from pydantic import (
    AnyUrl,
    BeforeValidator,
    EmailStr,
    HttpUrl,
    PostgresDsn,
    computed_field,
    model_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Self

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
ENV_PATH = BASE_DIR / ".env"


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # Use top level .env file (one level above ./backend/)
        env_file=str(ENV_PATH),
        env_ignore_empty=True,
        extra="ignore",
    )
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    FRONTEND_HOST: str = "http://localhost:5173"
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    BACKEND_CORS_ORIGINS: Annotated[list[AnyUrl] | str, BeforeValidator(parse_cors)] = (
        []
    )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def all_cors_origins(self) -> list[str]:
        return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS] + [
            self.FRONTEND_HOST
        ]

    PROJECT_NAME: str = ""
    SENTRY_DSN: HttpUrl | None = None
    POSTGRES_SERVER: str = ""
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = ""
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = ""

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql+psycopg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

    SMTP_TLS: bool = True
    SMTP_SSL: bool = False
    SMTP_PORT: int = 587
    SMTP_HOST: str | None = None
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    EMAILS_FROM_EMAIL: EmailStr | None = None
    EMAILS_FROM_NAME: EmailStr | None = None

    @model_validator(mode="after")
    def _set_default_emails_from(self) -> Self:
        if not self.EMAILS_FROM_NAME:
            self.EMAILS_FROM_NAME = self.PROJECT_NAME
        return self

    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48

    # 邮箱验证验证码配置
    EMAIL_VERIFICATION_CODE_TTL_SECONDS: int = 600  # 验证码有效期：10分钟
    EMAIL_VERIFICATION_CODE_LENGTH: int = 6  # 验证码长度：6位数字

    @computed_field  # type: ignore[prop-decorator]
    @property
    def emails_enabled(self) -> bool:
        return bool(self.SMTP_HOST and self.EMAILS_FROM_EMAIL)

    EMAIL_TEST_USER: EmailStr = "test@example.com"
    FIRST_SUPERUSER: EmailStr = "admin@example.com"
    FIRST_SUPERUSER_PASSWORD: str = ""

    # AI模型配置
    LLM_PROVIDER: str = "qwen"
    # DeepSeek 配置
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_MODEL: str = "deepseek-chat"
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"

    # 通义千问配置
    QWEN_API_KEY: str = ""
    # 文生文
    QWEN_CHAT_MODEL: str = "qwen-turbo"
    # 文生图
    QWEN_IMAGE_MODEL: str = "wan2.2-t2i-flash"
    # 向量嵌入
    QWEN_EMBEDDING_MODEL: str = "text-embedding-v4"

    # 音频存储配置
    AUDIO_STORAGE_PATH: str = "data/audio_files"
    MAX_AUDIO_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB

    # 七牛云存储配置
    QINIU_ACCESS_KEY: str = ""
    QINIU_SECRET_KEY: str = ""
    QINIU_BUCKET_NAME: str = ""
    QINIU_DOMAIN: str = ""  # 七牛云存储空间绑定的域名
    QINIU_USE_HTTPS: bool = False
    QINIU_CDN_DOMAIN: str = ""  # CDN加速域名（可选）

    # 最大会话数量限制
    MAX_CONVERSATIONS_LIMIT: int = 10

    # Redis配置
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_MAX_CONNECTIONS: int = 20
    REDIS_RETRY_ON_TIMEOUT: bool = True
    REDIS_HEALTH_CHECK_INTERVAL: int = 30

    # 任务队列配置
    TASK_QUEUE_ENABLED: bool = True
    TASK_DEFAULT_TIMEOUT: int = 300  # 5分钟
    TASK_DEFAULT_RETRY: int = 3
    TASK_RESULT_TTL: int = 3600  # 结果保存1小时
    TASK_FAILURE_TTL: int = 86400  # 失败信息保存24小时
    TASK_MAX_WORKERS: int = 4

    # 语音转文本(STT)配置
    STT_ENGINE: Literal["openai", "azure", "google", "whisper"] = "whisper"
    WHISPER_MODEL_SIZE: str = "base"  # tiny, base, small, medium, large

    # 文本转语音(TTS)配置
    TTS_ENGINE: Literal["openai", "azure", "google", "elevenlabs", "local"] = "openai"

    def _check_default_secret(self, var_name: str, value: str | None) -> None:
        if value == "changethis":
            message = (
                f'The value of {var_name} is "changethis", '
                "for security, please change it, at least for deployments."
            )
            if self.ENVIRONMENT == "local":
                warnings.warn(message, stacklevel=1)
            else:
                raise ValueError(message)

    @model_validator(mode="after")
    def _enforce_non_default_secrets(self) -> Self:
        self._check_default_secret("SECRET_KEY", self.SECRET_KEY)
        self._check_default_secret("POSTGRES_PASSWORD", self.POSTGRES_PASSWORD)
        self._check_default_secret(
            "FIRST_SUPERUSER_PASSWORD", self.FIRST_SUPERUSER_PASSWORD
        )

        return self


settings = Settings()  # type: ignore
