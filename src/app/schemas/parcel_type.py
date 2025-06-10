from pydantic import BaseModel, Field
from typing import Optional

class PackageTypeOut(BaseModel):
    id: int = Field(..., 
        example=1,
        description="Уникальный идентификатор типа посылки"
    )
    name: str = Field(...,
        min_length=2,
        max_length=50,
        example="Электроника",
        description="Название типа посылки",
        pattern=r"^[a-zA-Zа-яА-Я0-9\s\-]+$"  # Только буквы, цифры, пробелы и дефисы
    )

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": 1,
                "name": "Документы"
            }
        }
        