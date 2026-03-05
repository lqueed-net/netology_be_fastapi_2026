from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from async_lru import alru_cache
from schemas import Item, ItemCreate, ItemUpdate
from repositories import ItemRepository  # конкретная реализация


# pip install async-lru

class ItemService:

    @alru_cache(maxsize=128)
    async def get_all_items(self, db: AsyncSession) -> List[Item]:
        """Получить все товары (с кешированием)."""
        repo = ItemRepository(db)
        items = await repo.get_all()
        return [Item.model_validate(item) for item in items]

    async def create_item(self, db: AsyncSession, item_data: ItemCreate) -> Item:
        repo = ItemRepository(db)
        new_item = await repo.create(item_data)
        # Инвалидируем кеш списка
        self.get_all_items.cache_clear()
        return Item.model_validate(new_item)

    async def update_item(self, db: AsyncSession, item_id: int, item_data: ItemUpdate) -> Optional[Item]:
        repo = ItemRepository(db)
        updated_item = await repo.update(item_id, item_data)
        if updated_item:
            # Инвалидируем кеш списка
            self.get_all_items.cache_clear()
            return Item.model_validate(updated_item)
        return None

    async def delete_item(self, db: AsyncSession, item_id: int) -> bool:
        repo = ItemRepository(db)
        deleted = await repo.delete(item_id)
        if deleted:
            # Инвалидируем кеш списка
            self.get_all_items.cache_clear()
        return deleted

    async def get_item(self, db: AsyncSession, item_id: int) -> Optional[Item]:
        repo = ItemRepository(db)
        item = await repo.get(item_id)
        return Item.model_validate(item) if item else None