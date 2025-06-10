from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.db.dependencies import get_db_session
from src.app.schemas.company import AssignCompanyRequest
from src.app.services import company as crud_packages

router_assign_company = APIRouter()


@router_assign_company.post("/packages/{package_id}/assign_company")
async def assign_company(
    package_id: int = Path(..., gt=0),
    payload: AssignCompanyRequest = Depends(),
    session: AsyncSession = Depends(get_db_session),
):
    return await crud_packages.assign_company(package_id, payload.company_id, session)
