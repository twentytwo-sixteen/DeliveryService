import httpx
import motor.motor_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.app.db.models import Package, PackageType
from src.app.core.config import get_settings
from src.app.schemas.tasks import PackageTask

from datetime import datetime, date
from loguru import logger

usd_url = 'https://www.cbr-xml-daily.ru/daily_json.js'

async def fetch_usd_url() -> float:
    async with httpx.AsyncClient() as client:
        r = await client.get(usd_url)
        r.raise_for_status()
        return r.json()["Valute"]["USD"]["Value"]

async def calculate_delivery_price(weight_kg: float, content_price_usd: float) -> float:
    value = await fetch_usd_url()
    return round((weight_kg * 0.5 + content_price_usd * 0.01) * value, 2)

async def get_daily_delivery_stats(
    mongo_client: motor.motor_asyncio.AsyncIOMotorClient,
    target_date: date = None
) -> dict:
    """
    Получить статистику доставок за день по типам посылок
    
    Args:
        mongo_client: клиент MongoDB
        target_date: дата для статистики (по умолчанию текущая)
    
    Returns:
        Словарь с суммой доставок по типам за день
        {
            "date": "2023-01-01",
            "stats": [
                {"type_id": 1, "total_price": 1500.50},
                {"type_id": 2, "total_price": 3000.00}
            ]
        }
    """
    if target_date is None:
        target_date = date.today()
    
    start_date = datetime.combine(target_date, datetime.min.time())
    end_date = datetime.combine(target_date, datetime.max.time())
    
    mongo = mongo_client["delivery"]["logs"]
    
    pipeline = [
        {
            "$match": {
                "timestamp": {
                    "$gte": start_date.isoformat(),
                    "$lte": end_date.isoformat()
                }
            }
        },
        {
            "$group": {
                "_id": "$type_id",
                "total_price": {"$sum": "$delivery_price_rub"}
            }
        },
        {
            "$project": {
                "type_id": "$_id",
                "total_price": 1,
                "_id": 0
            }
        }
    ]
    
    cursor = mongo.aggregate(pipeline)
    stats = await cursor.to_list(length=None)
    
    return {
        "date": target_date.isoformat(),
        "stats": stats
    }

async def handle_package_task(
    task: PackageTask,
    session: AsyncSession,
    mongo_client: motor.motor_asyncio.AsyncIOMotorClient
):
    logger.info(f"Handling task: {task}")
    
    delivery_price_rub = await calculate_delivery_price(task.weight_kg, task.content_price_usd)
    
    # add to postgres
    package = Package(
        session_id=task.session_id,
        title=task.title,
        weight_kg=task.weight_kg,
        content_price_usd=task.content_price_usd,
        type_id=task.type_id,
        delivery_price_rub=delivery_price_rub,
    )
    session.add(package)
    await session.commit()
    
    # log in MongoDB
    log_entry = {
        "session_id": task.session_id,
        "title": task.title,
        "delivery_price_rub": delivery_price_rub,
        "type_id": task.type_id,
        "timestamp": datetime.utcnow(),
    }
    
    mongo = mongo_client["delivery"]["logs"]
    await mongo.insert_one(log_entry)
    
    logger.success(f"Package saved and logged: {package.title}")