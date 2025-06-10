from sqlalchemy.ext.asyncio import AsyncSession
from collections.abc import AsyncGenerator
from loguru import logger 
from src.app.db.session import AsyncSessionLocal


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    try:
        async with AsyncSessionLocal() as session:
            yield session
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise
    finally:
        logger.debug("Database session closed")
        