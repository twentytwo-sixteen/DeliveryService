from pydantic import BaseModel, Field
from typing import Optional

class PackageCreate(BaseModel):
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


class PackageOut(BaseModel):
    id: int = Field(..., example=1)
    title: str = Field(..., example="Смартфон")
    weight_kg: float = Field(..., example=0.5)
    content_price_usd: float = Field(..., example=999.99)
    delivery_price_rub: Optional[float] = Field(
        None,
        example=7500.50,
        description="Стоимость доставки в RUB"
    )
    type_name: str = Field(..., example="Электроника")

    class Config:
        orm_mode = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "Смартфон",
                "weight_kg": 0.5,
                "content_price_usd": 999.99,
                "delivery_price_rub": 7500.50,
                "type_name": "Электроника",
            }
        }