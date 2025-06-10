from sqlalchemy.ext.asyncio import AsyncSession
from src.app.db.models import Package, PackageType
from src.app.schemas.parcel import PackageCreate
from fastapi import HTTPException
from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import Sequence, Optional
from sqlalchemy import and_
from sqlalchemy.orm import joinedload
from src.app.db.models import Package

# create package
async def create_package(session: AsyncSession, data: PackageCreate, session_id: str) -> Package:
    try:
        type_obj = await session.get(PackageType, data.type_id)
        if not type_obj:
            raise HTTPException(status_code=400, detail="Invalid package type")
        
        package = Package(
            title=data.title,
            weight_kg=data.weight_kg,
            content_price_usd=data.content_price_usd,
            type_id=data.type_id,
            session_id=session_id,
        )
        
        session.add(package)
        await session.commit()
        
        package = await session.execute(
             select(Package)
            .where(Package.id == package.id)
            .options(selectinload(Package.type)) 
        )
        package = package.scalar_one() 

        return package
        
    except Exception as e:
        await session.rollback() 
        logger.error(f"Failed to create package: {e}")
        raise HTTPException(status_code=500, detail="Database error")


# get packages for session id
async def get_packages(
    session: AsyncSession,
    session_id: str,
    type_id: Optional[int] = None,
    has_delivery_price: Optional[bool] = None,
    limit: int = 5,
    offset: int = 0
) -> Sequence[Package]:
    """
    Retrieve packages by session ID with optional filtering.

    Args:
        session (AsyncSession): _description_
        session_id (str): _description_
        type_id (Optional[int], optional): _description_. Defaults to None.
        has_delivery_price (Optional[bool], optional): _description_. Defaults to None.
        limit (int, optional): _description_. Defaults to 5.
        offset (int, optional): _description_. Defaults to 0.

    Returns:
        Sequence[Package]: _description_
    
    Raises:
        DatabaseError: If there's an issue executing query
    """
    try:
        query = (
            select(Package)
            .options(joinedload(Package.type))
            .where(Package.session_id == session_id)
            .order_by(Package.id)
        )   
        
        # Apply filters
        filters = []
        if type_id is not None:
            filters.append(Package.type_id == type_id)
            
        if has_delivery_price is not None:
            filters.append(
                Package.delivery_price_rub.isnot(None) if has_delivery_price
                else Package.delivery_price_rub.is_(None)
            )
        
        if filters:
            query = query.where(and_(*filters))
            
        # Apply pagination
        query = query.limit(min(limit, 1000)).offset(offset)
        
        logger.debug(f"Executing query: {query}")
        result = await session.execute(query)
        return result.unique().scalars().all() 
    
    except Exception as e:
        logger.error(f"Error fetching packages: {e}")
        raise



# get package for it's personal id

async def get_package_by_id(
    session: AsyncSession,
    package_id: int,
    session_id: str,
    include_type: bool = True
) -> Optional[Package]:
    """
    Retrieve a package by ID with session validation.
    
    Args:
        session: Async SQLAlchemy session
        package_id: ID of the package to retrieve
        session_id: Session ID for validation
        include_type: Whether to join load package type
        
    Returns:
        Package object if found, None otherwise
        
    Raises:
        HTTPException: 404 if package not found or session mismatch
    """
    try:
        query = select(Package).where(
            Package.id == package_id,
            Package.session_id == session_id
        )
        
        if include_type:
            query = query.options(joinedload(Package.type))
            
        result = await session.execute(query)
        package = result.unique().scalar_one_or_none()
        
        if not package:
            logger.warning(f"Package not found: id={package_id}, session={session_id[:8]}...")
            raise HTTPException(
                status_code=404,
                detail="Package not found or access denied"
            )
            
        return package
        
    except Exception as e:
        logger.error(f"Error fetching package {package_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Database error"
        )