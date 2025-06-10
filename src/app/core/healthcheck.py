from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from loguru import logger
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from pymongo import MongoClient
from redis.asyncio import Redis
from aio_pika import connect_robust
from src.app.core.config import get_settings
from src.app.db.session import engine

router = APIRouter(tags=["System"])
settings = get_settings()

async def check_postgres() -> dict:
    """Проверка подключения к PostgreSQL"""
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {"postgres": "OK"}
    except Exception as e:
        logger.error(f"PostgreSQL healthcheck failed: {e}")
        return {"postgres": f"Error: {str(e)}"}

async def check_mongo() -> dict:
    """Проверка подключения к MongoDB"""
    try:
        client = MongoClient(settings.mongo_uri)
        db = client[settings.mongo_db]
        await db.command("ping")
        return {"mongodb": "OK"}
    except Exception as e:
        logger.error(f"MongoDB healthcheck failed: {e}")
        return {"mongodb": f"Error: {str(e)}"}

async def check_redis() -> dict:
    """Проверка подключения к Redis"""
    try:
        redis = Redis.from_url(f"redis://{settings.redis_host}:{settings.redis_port}")
        await redis.ping()
        return {"redis": "OK"}
    except Exception as e:
        logger.error(f"Redis healthcheck failed: {e}")
        return {"redis": f"Error: {str(e)}"}

async def check_rabbitmq() -> dict:
    """Проверка подключения к RabbitMQ"""
    try:
        connection = await connect_robust(settings.rabbitmq_url)
        await connection.close()
        return {"rabbitmq": "OK"}
    except Exception as e:
        logger.error(f"RabbitMQ healthcheck failed: {e}")
        return {"rabbitmq": f"Error: {str(e)}"}

@router.get("/health", summary="Проверка состояния сервисов")
async def healthcheck():
    """Проверка всех внешних зависимостей"""
    services = {
        "postgres": await check_postgres(),
        "mongodb": await check_mongo(),
        "redis": await check_redis(),
        "rabbitmq": await check_rabbitmq(),
    }
    
    # Определяем общий статус (200 или 503)
    all_ok = all("OK" in str(v) for v in services.values())
    status_code = (
        status.HTTP_200_OK 
        if all_ok 
        else status.HTTP_503_SERVICE_UNAVAILABLE
    )
    
    return JSONResponse(
        content={"services": services},
        status_code=status_code,
    )