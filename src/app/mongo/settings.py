from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseSettings

class MongoSettings(BaseSettings):
    mongo_url: str = "mongodb://mongo:27017"
    mongo_db: str = "delivery"

mongo_settings = MongoSettings()
mongo_client = AsyncIOMotorClient(mongo_settings.mongo_url)
mongo_db = mongo_client[mongo_settings.mongo_db]
