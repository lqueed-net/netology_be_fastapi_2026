from pydantic import BaseModel, ConfigDict
from typing import Optional

# Базовая схема с общими атрибутами
class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float

# Схема для создания элемента
class ItemCreate(ItemBase):
    pass

# Схема для обновления элемента (все поля опциональны)
class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None

# Схема для ответа (содержит id)
class Item(ItemBase):
    id: int
    model_config = ConfigDict(from_attributes=True)  # позволяет использовать SQLAlchemy модели