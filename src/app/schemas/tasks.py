from pydantic import BaseModel, Field
from datetime import datetime

class PackageTask(BaseModel):
    """
    
    Модель задачи для обработки посылки через RabbitMQ
    
    """
        
    session_id: str = Field(
        ...,
        min_length=1,
        max_length=36,
        description="Уникальный идентификатор сессии/запроса"
    )
    title: str = Field(
        ...,
        min_length=2,
        max_length=100,
        example="Смартфон",
        description="Название посылки"
    )
    weight_kg: float = Field(
        ...,
        gt=0,
        le=1000, 
        example=0.5,
        description="Вес в килограммах"
    )
    type_id: int = Field(
        ...,
        gt=0,
        example=1,
        description="ID типа посылки"
    )
    content_price_usd: float = Field(
        ...,
        gt=0,
        example=999.99,
        description="Стоимость содержимого в USD"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
