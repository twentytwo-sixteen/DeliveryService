# src/app/core/config.py
from pydantic import Field
from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App
    env: str = Field("local", env="ENV")
    app_name: str = Field("delivery_service", env="APP_NAME")
    debug: bool = Field(True, env="DEBUG")

    # DB
    db_host: str = Field(..., env="POSTGRES_HOST")
    db_port: int = Field(..., env="POSTGRES_PORT")
    db_name: str = Field(..., env="POSTGRES_DB")
    db_user: str = Field(..., env="POSTGRES_USER")
    db_password: str = Field(..., env="POSTGRES_PASSWORD")

    # Redis
    redis_host: str = Field(..., env="REDIS_HOST")
    redis_port: int = Field(..., env="REDIS_PORT")

    # Mongo
    mongo_uri: str = Field(..., env="MONGO_URI")
    mongo_db: str = Field(..., env="MONGO_DB")

    # RabbitMQ
    rabbitmq_host: str = Field(..., env="RABBITMQ_HOST")
    rabbitmq_user: str = Field(..., env="RABBITMQ_USER")
    rabbitmq_pass: str = Field(..., env="RABBITMQ_PASS")
    rabbitmq_timeout: int = 10
    rabbitmq_message_ttl: int = 86400000
    rabbitmq_dlx_exchange: str = "package_dlx"
    @property
    def rabbitmq_url(self) -> str:
        return f"amqp://{self.rabbitmq_user}:{self.rabbitmq_pass}@{self.rabbitmq_host}/"

    # Other
    secret_key: str = Field(..., env="SECRET_KEY")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

@lru_cache()
def get_settings():
    return Settings()
