from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from models import Item as ItemModel
from schemas import ItemCreate, ItemUpdate
from typing import Optional, List

# Абстрактный репозиторий (интерфейс)
class AbstractItemRepository(ABC):
    @abstractmethod
    async def get(self, item_id: int) -> Optional[ItemModel]:
        pass

    @abstractmethod
    async def get_all(self) -> List[ItemModel]:
        pass

    @abstractmethod
    async def create(self, item: ItemCreate) -> ItemModel:
        pass

    @abstractmethod
    async def update(self, item_id: int, item: ItemUpdate) -> Optional[ItemModel]:
        pass

    @abstractmethod
    async def delete(self, item_id: int) -> bool:
        pass


# Конкретная реализация
class ItemRepository(AbstractItemRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, item_id: int) -> Optional[ItemModel]:
        result = await self.session.execute(
            select(ItemModel).where(ItemModel.id == item_id)
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> List[ItemModel]:
        result = await self.session.execute(select(ItemModel))
        return list(result.scalars().all())

    async def create(self, item: ItemCreate) -> ItemModel:
        db_item = ItemModel(**item.model_dump())
        self.session.add(db_item)
        await self.session.commit()
        await self.session.refresh(db_item)
        return db_item

    async def update(self, item_id: int, item: ItemUpdate) -> Optional[ItemModel]:
        # Получаем существующую запись
        db_item = await self.get(item_id)
        if not db_item:
            return None
        # Обновляем только переданные поля
        update_data = item.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_item, key, value)
        await self.session.commit()
        await self.session.refresh(db_item)
        return db_item

    async def delete(self, item_id: int) -> bool:
        db_item = await self.get(item_id)
        if not db_item:
            return False
        await self.session.delete(db_item)
        await self.session.commit()
        return True