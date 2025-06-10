from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from src.app.core.config import get_settings
from collections.abc import AsyncGenerator
from loguru import logger 

settings = get_settings()

DATABASE_URL = (
    f"postgresql+asyncpg://{settings.db_user}:{settings.db_password}"
    f"@{settings.db_host}:{settings.db_port}/{settings.db_name}"
)

engine = create_async_engine(DATABASE_URL, echo=settings.debug)

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

