from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.app.db.models import Package
from fastapi import HTTPException, status


from src.app.db.models import Company

async def assign_company(package_id: int, company_id: int, session: AsyncSession):
    # Проверяем, что компания существует
    company = await session.get(Company, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    result = await session.execute(
        select(Package)
        .where(Package.id == package_id)
        .with_for_update(skip_locked=True)
    )
    package = result.scalar_one_or_none()

    if package is None:
        raise HTTPException(status_code=404, detail="Package not found")

    if package.company_id is not None:
        raise HTTPException(status_code=409, detail="Package already assigned")

    package.company_id = company_id
    await session.commit()
    return {"message": f"Package {package_id} assigned to company {company_id}"}
