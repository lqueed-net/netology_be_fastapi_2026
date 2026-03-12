from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    price = Column(Float, nullable=False)

    # Связь с позициями заказа (один ко многим)
    order_items = relationship("OrderItem", back_populates="item", lazy="selectin", cascade="all, delete-orphan")



class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="pending")  # статус заказа

    # Связь с позициями заказа (один ко многим)
    order_items = relationship("OrderItem", back_populates="order", lazy="selectin", cascade="all, delete-orphan")


# Связи между заказами и товарами реализованы через 
# промежуточную модель, что является стандартным паттерном в реальных проектах.

# Можно хранить количество каждого товара в заказе.
# Легко расширять модель дополнительными полями (например, скидка, комментарий).
# Сохраняется целостность данных через внешние ключи.

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    price_at_order = Column(Float, nullable=False)  # фиксируем цену товара на момент оформления заказа

    # Связи
    order = relationship("Order", back_populates="order_items", lazy="selectin")
    item = relationship("Item", back_populates="order_items", lazy="selectin")