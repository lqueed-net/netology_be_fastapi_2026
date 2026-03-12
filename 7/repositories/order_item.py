from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.engine import Result
from models import OrderItem as OrderItemModel
from schemas import OrderItemCreate, OrderItemUpdate
from typing import Optional, List

class AbstractOrderItemRepository(ABC):
    @abstractmethod
    async def get(self, order_item_id: int) -> Optional[OrderItemModel]:
        pass

    @abstractmethod
    async def get_all(self) -> List[OrderItemModel]:
        pass

    @abstractmethod
    async def get_by_order(self, order_id: int) -> List[OrderItemModel]:
        pass

    @abstractmethod
    async def get_by_item(self, item_id: int) -> List[OrderItemModel]:
        pass

    @abstractmethod
    async def create(self, order_item: OrderItemCreate) -> OrderItemModel:
        pass

    @abstractmethod
    async def update(self, order_item_id: int, order_item: OrderItemUpdate) -> Optional[OrderItemModel]:
        pass

    @abstractmethod
    async def delete(self, order_item_id: int) -> bool:
        pass

class OrderItemRepository(AbstractOrderItemRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, order_item_id: int) -> Optional[OrderItemModel]:
        result = await self.session.execute(
            select(OrderItemModel).where(OrderItemModel.id == order_item_id)
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> List[OrderItemModel]:
        result = await self.session.execute(select(OrderItemModel))
        return result.scalars().all()

    async def get_by_order(self, order_id: int) -> List[OrderItemModel]:
        result = await self.session.execute(
            select(OrderItemModel).where(OrderItemModel.order_id == order_id)
        )
        return result.scalars().all()

    async def get_by_item(self, item_id: int) -> List[OrderItemModel]:
        result = await self.session.execute(
            select(OrderItemModel).where(OrderItemModel.item_id == item_id)
        )
        return result.scalars().all()

    async def create(self, order_item: OrderItemCreate) -> OrderItemModel:
        db_order_item = OrderItemModel(**order_item.model_dump())
        self.session.add(db_order_item)
        await self.session.commit()
        await self.session.refresh(db_order_item)
        return db_order_item

    async def update(self, order_item_id: int, order_item: OrderItemUpdate) -> Optional[OrderItemModel]:
        db_order_item = await self.get(order_item_id)
        if not db_order_item:
            return None
        update_data = order_item.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_order_item, key, value)
        await self.session.commit()
        await self.session.refresh(db_order_item)
        return db_order_item

    async def delete(self, order_item_id: int) -> bool:
        db_order_item = await self.get(order_item_id)
        if not db_order_item:
            return False
        await self.session.delete(db_order_item)
        await self.session.commit()
        return True