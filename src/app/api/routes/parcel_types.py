from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.app.db.dependencies import get_db_session
from src.app.services.package_type import get_all_package_types
from src.app.schemas.parcel_type import PackageTypeOut
from fastapi_cache.decorator import cache

router_package_type = APIRouter()

@router_package_type.get("/package-types/", response_model=list[PackageTypeOut])
@cache(expire=24 * 60 * 60) # 24 hours
async def get_package_types(
    skip: int = 0,
    limit: int = 5,
    session: AsyncSession = Depends(get_db_session)
):
    return await get_all_package_types(session=session, skip=skip, limit=limit)

