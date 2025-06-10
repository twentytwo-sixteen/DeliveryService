from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from typing import Optional
from src.app.api.routes.parcels import router_package_register, router_packages_get, router_package_by_id_get
from src.app.api.routes.parcel_types import router_package_type
import uuid
from src.app.cache.cache_init import init_cache
from src.app.api.routes.company import router_assign_company

app = FastAPI()

@app.on_event("startup")
async def startup():
    await init_cache()
    

@app.middleware("http")
async def session_middleware(request: Request, call_next) -> Response:
    try:
        # Получаем или генерируем session_id
        session_id: Optional[str] = request.cookies.get("session_id") or str(uuid.uuid4())
        
        # Продолжаем цепочку middleware и обработчиков
        response: Response = await call_next(request)
        
        # Устанавливаем cookie если нужно
        if not request.cookies.get("session_id"):
            response.set_cookie(
                key="session_id",
                value=session_id,
                httponly=True,
                max_age=30*24*60*60  # Срок жизни (30 дней)
            )
            
        return response
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )

app.include_router(router_package_register)
app.include_router(router_package_type)
app.include_router(router_packages_get)
app.include_router(router_package_by_id_get)
app.include_router(router_assign_company)