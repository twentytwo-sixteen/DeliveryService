from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.app.db.models import PackageType
from typing import Sequence
import logging

logger = logging.getLogger(__name__)

async def get_all_package_types(
    session: AsyncSession,
    skip: int = 0,
    limit: int = 5
) -> Sequence[PackageType]: # can List[PackageType] but Sequence better
    """
    Retrieve all package types with pagination support.
    
    Args:
        session (AsyncSession): _description_
        skip (int, optional): _description_. Defaults to 0.
        limit (int, optional): _description_. Defaults to 5.

    Returns:
        Sequence[PackageType]: _description_
        
    Raises:
        DatabaseError: If there's an issue with the database operation
    """
    try:
        logger.debug("Fetching package types with skip=%s, limit=%s", skip, limit)
        result = await session.execute(
            select(PackageType)
            .offset(skip)
            .limit(limit)
            .order_by(PackageType.id)
        )
        return result.scalars().all()
    except Exception as e:
        logger.error("Error fetching package types: %s", str(e))
        raise