import asyncio
import json
import aio_pika
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.db.session import get_engine, get_session_maker
from src.app.core.config import settings
from src.app.schemas.tasks import PackageTask
from src.app.services.delivery import handle_package_task

import motor.motor_asyncio
from loguru import logger


RABBIT_QUEUE = "package_register"


async def main():
    logger.info("Starting consumer...")

    connection = await aio_pika.connect_robust(settings.rabbitmq_url)
    channel = await connection.channel()
    queue = await channel.declare_queue(RABBIT_QUEUE, durable=True)

    engine = get_engine()
    sessionmaker = get_session_maker(engine)
    mongo_client = motor.motor_asyncio.AsyncIOMotorClient(settings.mongodb_uri)

    async with sessionmaker() as session:
        async def on_message(message: aio_pika.IncomingMessage):
            async with message.process():
                try:
                    payload = json.loads(message.body)
                    task = PackageTask(**payload)
                    await handle_package_task(task, session, mongo_client)
                except Exception as e:
                    logger.exception("Error processing message")

        await queue.consume(on_message)
        logger.success("Consumer ready. Waiting for messages...")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
