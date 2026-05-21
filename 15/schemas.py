from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

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


# ---------- Order schemas ----------
class OrderBase(BaseModel):
    status: str = "pending"

class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    status: Optional[str] = None

class Order(OrderBase):
    id: int
    created_at: datetime = datetime.now()
    model_config = ConfigDict(from_attributes=True) 


# ---------- OrderItem schemas ----------
class OrderItemBase(BaseModel):
    order_id: int
    item_id: int
    quantity: int = 1
    price_at_order: float

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemUpdate(BaseModel):
    quantity: Optional[int] = None
    price_at_order: Optional[float] = None

class OrderItem(OrderItemBase):
    id: int
    model_config = ConfigDict(from_attributes=True) 