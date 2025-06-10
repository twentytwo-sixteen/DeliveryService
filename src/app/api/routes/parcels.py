from fastapi import APIRouter, Request, Depends, HTTPException, Response, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4
from src.app.db.dependencies import get_db_session
from src.app.schemas.parcel import PackageCreate, PackageOut
from src.app.services.parcel import create_package
from src.app.services.parcel import get_packages, get_package_by_id
from src.app.schemas.tasks import PackageTask
from src.app.rabbitmq.publisher import send_package_to_queue
from typing import Annotated
from fastapi import BackgroundTasks
import logging

router_package_register = APIRouter(prefix="/packages", tags=["packages"])
logger = logging.getLogger(__name__)

#===REGISTER PACKAGE===#

@router_package_register.post("/register", response_model=PackageOut, status_code=201)
async def register_package(
    payload: PackageCreate,
    background_tasks: BackgroundTasks,
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_db_session),
):
    try:
        # Получаем/генерируем session_id
        session_id = request.cookies.get("session_id") or str(uuid4())
        
        # Создаем посылку
        package = await create_package(session, payload, session_id)
        
        # Устанавливаем cookie (если был сгенерирован новый)
        if not request.cookies.get("session_id"):
            response.set_cookie(
                key="session_id",
                value=session_id,
                httponly=True,
                max_age=30*24*60*60  # 30 дней
            )
            
        # Формируем задачу для RabbitMQ
        task = PackageTask(
            session_id=session_id,
            title=package.title,
            weight_kg=package.weight_kg,
            type_id=package.type_id,
            content_price_usd=package.content_price_usd
        )
        
        # Отправляем в фоне (не блокируем ответ)
        background_tasks.add_task(send_package_to_queue, task)
        
        # Используем Pydantic модель для формирования ответа
        return PackageOut(
            id=package.id,
            title=package.title,
            weight_kg=package.weight_kg,
            content_price_usd=package.content_price_usd,
            delivery_price_rub=package.delivery_price_rub,
            type_name=package.type.name
        )
        
    except HTTPException:
        raise  # Пробрасываем уже обработанные ошибки
    except Exception as e:
        logger.error(f"Package creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
    


#===GET ALL PACKAGES===#

router_packages_get = APIRouter(tags=["packages"])

@router_packages_get.get(
    "/packages",
    response_model=list[PackageOut],
    summary="Get packages by session",
    description="Retrieves list of packages filtered by session ID and optional filters",
    responses={
        400: {"description": "Missing session ID"},
        500: {"description": "Internal server error"}
    }
)
async def list_packages(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    type_id: Annotated[int | None, Query(description="Filter by package type ID")] = None,
    has_delivery_price: Annotated[bool | None, Query(description="Filter by delivery price existence")] = None,
    limit: Annotated[int, Query(description="Pagination limit", le=100, ge=1)] = 10,
    offset: Annotated[int, Query(description="Pagination offset", ge=0)] = 0
) -> list[PackageOut]:
    """
    Get packages for current session with optional filtering.
    
    Requires session_id cookie for authentication.
    """
    try:
        # Session validation
        session_id = request.cookies.get("session_id")
        if not session_id:
            logger.warning("Attempt to access packages without session_id")
            raise HTTPException(
                status_code=400,
                detail="Session ID is required"
            )

        # Log request parameters
        logger.debug(
            f"Fetching packages for session {session_id[:8]}... "
            f"Filters: type_id={type_id}, has_delivery={has_delivery_price}"
        )

        # Get data from service
        packages = await get_packages(
            session=session,
            session_id=session_id,
            type_id=type_id,
            has_delivery_price=has_delivery_price,
            limit=min(limit, 100),  # Additional safety
            offset=offset
        )

        # Response transformation
        return [
            PackageOut(
                id=pkg.id,
                title=pkg.title,
                weight_kg=pkg.weight_kg,
                content_price_usd=pkg.content_price_usd,
                type_name=pkg.type.name,  # type is loaded via joinedload
                delivery_price_rub=pkg.delivery_price_rub
            )
            for pkg in packages
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch packages: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
        


#===GET ONE PACKAGE BY ID===#


router_package_by_id_get = APIRouter()

@router_package_by_id_get.get(
    "/packages/{package_id}",
    response_model=PackageOut,
    summary="Get package details",
    responses={
        400: {"description": "Missing session ID"},
        404: {"description": "Package not found"},
        500: {"description": "Internal server error"}
    }
)
async def get_package_details(
    package_id: int,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
) -> PackageOut:
    """
    Retrieve detailed information about a specific package.
    
    Requires valid session_id cookie.
    Package must belong to the current session.
    """
    try:
        # Session validation
        session_id = request.cookies.get("session_id")
        if not session_id:
            logger.warning("Package access attempt without session_id")
            raise HTTPException(
                status_code=400,
                detail="Session ID is required"
            )

        # Get package with type relation loaded
        package = await get_package_by_id(
            session=session,
            package_id=package_id,
            session_id=session_id
        )

        # Transform to response model
        return PackageOut(
            id=package.id,
            title=package.title,
            weight_kg=package.weight_kg,
            content_price_usd=package.content_price_usd,
            type_name=package.type.name,
            delivery_price_rub=package.delivery_price_rub
        )
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Failed to fetch package {package_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )