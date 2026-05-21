from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.engine import Result
from models import Order as OrderModel
from schemas import OrderCreate, OrderUpdate
from typing import Optional, List

class AbstractOrderRepository(ABC):
    @abstractmethod
    async def get(self, order_id: int) -> Optional[OrderModel]:
        pass

    @abstractmethod
    async def get_all(self) -> List[OrderModel]:
        pass

    @abstractmethod
    async def create(self, order: OrderCreate) -> OrderModel:
        pass

    @abstractmethod
    async def update(self, order_id: int, order: OrderUpdate) -> Optional[OrderModel]:
        pass

    @abstractmethod
    async def delete(self, order_id: int) -> bool:
        pass

class OrderRepository(AbstractOrderRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, order_id: int) -> Optional[OrderModel]:
        result = await self.session.execute(
            select(OrderModel).where(OrderModel.id == order_id)
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> List[OrderModel]:
        result = await self.session.execute(select(OrderModel))
        return result.scalars().all()

    async def create(self, order: OrderCreate) -> OrderModel:
        db_order = OrderModel(**order.model_dump())
        self.session.add(db_order)
        await self.session.commit()
        await self.session.refresh(db_order)
        return db_order

    async def update(self, order_id: int, order: OrderUpdate) -> Optional[OrderModel]:
        db_order = await self.get(order_id)
        if not db_order:
            return None
        update_data = order.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_order, key, value)
        await self.session.commit()
        await self.session.refresh(db_order)
        return db_order

    async def delete(self, order_id: int) -> bool:
        db_order = await self.get(order_id)
        if not db_order:
            return False
        await self.session.delete(db_order)
        await self.session.commit()
        return True