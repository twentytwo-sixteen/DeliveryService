from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings
from functools import lru_cache
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class Environment(str, Enum):
    LOCAL = "local"
    STAGING = "staging"
    PRODUCTION = "production"

class Settings(BaseSettings):
    env: Environment = Field(Environment.LOCAL, env="ENV")
    app_name: str = Field("delivery_service", env="APP_NAME")
    debug: bool = Field(True, env="DEBUG")

    db_host: str = Field(..., env="POSTGRES_HOST")
    db_port: int = Field(5432, env="POSTGRES_PORT")
    db_name: str = Field(..., env="POSTGRES_DB")
    db_user: str = Field(..., env="POSTGRES_USER")
    db_password: str = Field(..., env="POSTGRES_PASSWORD")

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
        return f"amqp://{self.rabbitmq_user}:{self.rabbitmq_pass}@{self.rabbitmq_host}:{self.rabbitmq_port}{self.rabbitmq_vhost}"

    secret_key: SecretStr = Field(..., env="SECRET_KEY")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    settings = Settings()
    logger.info(f"Loaded settings for {settings.app_name} (env: {settings.env}, debug: {settings.debug})")
    return settings
