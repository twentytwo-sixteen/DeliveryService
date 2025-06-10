import sys 
from loguru import logger

def setup_logging():
    logger.remove()
    
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
               "<level>{message}</level>",
        level="INFO",
        enqueue=True,
        backtrace=True,
        diagnose=True,
    )
    
    # uvicorn.logger --> loguru
    class InterceptHandler:
        def write(self, message):
            message = message.strip()
            if message:
                logger.info(message)
        def flush(self):
            pass
    
    import logging
    logging.getLogger("uvicorn.access").handlers = [InterceptHandler()]
    logging.getLogger("uvicorn.error").handlers = [InterceptHandler()]
    logging.getLogger("fastapi").handlers = [InterceptHandler()]
