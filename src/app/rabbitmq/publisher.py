import aio_pika
from aio_pika.abc import AbstractRobustConnection
from src.app.schemas.tasks import PackageTask
from src.app.core.config import get_settings
from src.app.core.logger import logger
from contextlib import asynccontextmanager

settings = get_settings()
RABBIT_QUEUE = "package_register"

@asynccontextmanager
async def get_rabbit_channel():
    connection: AbstractRobustConnection = None
    try:
        # Connect with RabbitMQ
        connection = await aio_pika.connect_robust(settings.rabbitmq_url)
        
        # Make a channel
        channel = await connection.channel()
        
        # Set a limit: one message at a time
        await channel.set_qos(prefetch_count=1)
        
        # Return a channel
        yield channel
    except Exception as e:
        logger.error(f"RabbitMQ connection error: {str(e)}")
        raise
    finally:
        if connection:
            await connection.close()
            

async def send_package_to_queue(task: PackageTask):
    try:
        async with get_rabbit_channel() as channel:
            # make a query if not exists
            await channel.declare_queue(
                RABBIT_QUEUE,
                durable=True, # safe messages after reboot RabbitMQ
                arguments={
                    'x-message-ttl': settings.rabbitmq_message_ttl, # time message's life
                    'x-dead-letter-exchange': settings.rabbitmq_dlx_exchange # Куда слать "просроченные" сообщения
                }
            )
            
            # Упаковываем задачу в письмо (сообщение)
            message = aio_pika.Message(
                body=task.json().encode(), #json-format
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,# Сохранить на диске (чтобы не потерять при падении)
                headers={
                    'created_at': task.created_at.isoformat(),
                    'version': '1.0'
                }
            )
            # Кидаем письмо в очередь (routing_key = название очереди)
            await channel.default_exchange.publish(message, routing_key=RABBIT_QUEUE)
            logger.info(f"Task sent to RabbitMQ: {task.session_id}")
            
    except Exception as e:
        logger.error(f"Failed to send task to RabbitMQ: {str(e)}")
        raise
    