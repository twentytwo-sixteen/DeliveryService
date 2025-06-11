import logging
import os
from enum import Enum
from functools import lru_cache

from pydantic import Field
from pydantic import SecretStr
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


class Environment(str, Enum):
    LOCAL = "local"
    STAGING = "staging"
    PRODUCTION = "production"


class Settings(BaseSettings):
    env: Environment = Field(Environment.LOCAL, env="ENV")
    app_name: str = Field("delivery_service", env="APP_NAME")
    debug: bool = Field(True, env="DEBUG")

    db_host: str = Field(..., env=["DB_HOST", "POSTGRES_HOST"])
    db_port: int = Field(5432, env=["DB_PORT", "POSTGRES_PORT"])
    db_name: str = Field(..., env=["DB_NAME", "POSTGRES_DB"])
    db_user: str = Field(..., env=["DB_USER", "POSTGRES_USER"])
    db_password: str = Field(..., env=["DB_PASSWORD", "POSTGRES_PASSWORD"])

    redis_host: str = Field(..., env="REDIS_HOST")
    redis_port: int = Field(6379, env="REDIS_PORT")

    mongo_uri: str = Field(..., env="MONGO_URI")
    mongo_db: str = Field(..., env="MONGO_DB")

    rabbitmq_host: str = Field(..., env="RABBITMQ_HOST")
    rabbitmq_port: int = Field(5672, env="RABBITMQ_PORT")
    rabbitmq_user: str = Field(..., env="RABBITMQ_USER")
    rabbitmq_pass: str = Field(..., env="RABBITMQ_PASS")
    rabbitmq_vhost: str = Field("/", env="RABBITMQ_VHOST")

    @property
    def rabbitmq_url(self) -> str:
        return (
            f"amqp://{self.rabbitmq_user}:{self.rabbitmq_pass}"
            f"@{self.rabbitmq_host}:{self.rabbitmq_port}{self.rabbitmq_vhost}"
        )

    secret_key: SecretStr = Field(..., env="SECRET_KEY")

    @property
    def database_url(self) -> str:
        return os.getenv(
            "DATABASE_URL",
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}",
        )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    settings = Settings()
    logger.info(
        f"Loaded settings for {settings.app_name} "
        f"(env: {settings.env}, debug: {settings.debug})"
    )
    return settings
