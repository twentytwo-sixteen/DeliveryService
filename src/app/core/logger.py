import os
import sys
from pathlib import Path
from typing import Union
from loguru import logger

def sanitize(message: str) -> str:
    """Скрытие чувствительных данных в логах"""
    secrets = ["password=", "token=", "secret=", "authorization:"]
    for s in secrets:
        if s in message.lower():
            message = message.replace(s.split("=")[0] + "=[REDACTED]")
    return message

def setup_logging(log_level: Union[str, int] = "INFO"):
    """Настройка логирования для приложения"""
    
    # Очистка и базовая конфигурация
    logger.remove()
    
    # Формат логов
    fmt = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )
    
    # Вывод в консоль
    logger.add(
        sys.stdout,
        format=fmt,
        level=os.getenv("LOG_LEVEL", log_level),
        enqueue=True,
        backtrace=True,
        diagnose=os.getenv("APP_ENV") == "dev",
        filter=lambda record: record["level"].no >= logger.level(log_level).no
    )
    
    # # Ротация логов в файлы (только для production)
    # if os.getenv("APP_ENV") == "prod":
    #     logs_dir = Path("logs")
    #     logs_dir.mkdir(exist_ok=True)
        
    #     logger.add(
    #         logs_dir / "{time:YYYY-MM-DD}.log",
    #         rotation="00:00",  # Ротация в полночь
    #         retention="30 days",
    #         compression="zip",
    #         format=fmt,
    #         level="INFO"
    #     )
    
    # Перехват стандартных логов
    class InterceptHandler:
        def write(self, message):
            if message.strip():
                logger.opt(depth=1).info(sanitize(message.strip()))
        def flush(self):
            pass
    
    # Uvicorn/FastAPI
    import logging
    logging.basicConfig(handlers=[InterceptHandler()], level=0)
    for name in ("uvicorn", "uvicorn.error", "fastapi", "sqlalchemy"):
        logging.getLogger(name).handlers = [InterceptHandler()]
