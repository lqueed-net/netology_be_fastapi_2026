from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from async_lru import alru_cache

from schemas import Item, ItemCreate, ItemUpdate
from repositories import ItemRepository
from exceptions import ItemNotFoundError, DatabaseError, DuplicateItemError


class ItemService:
    def __init__(self):
        # Кеш для списка товаров (максимум 128 элементов)
        pass

    @alru_cache(maxsize=128)
    async def get_all_items(self, db: AsyncSession) -> List[Item]:
        """Получить все товары (с кешированием)."""
        repo = ItemRepository(db)
        try:
            items = await repo.get_all()
        except SQLAlchemyError as e:
            # Превращаем низкоуровневую ошибку в HTTP-исключение с кодом 500
            raise DatabaseError(f"Failed to fetch items: {e}") from e

        return [Item.model_validate(item) for item in items]

    async def create_item(self, db: AsyncSession, item_data: ItemCreate) -> Item:
        repo = ItemRepository(db)
        try:
            new_item = await repo.create(item_data)
        except IntegrityError as e:
            # Ошибка уникальности — возвращаем 400
            raise DuplicateItemError(f"Item with name '{item_data.name}' already exists") from e
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to create item: {e}") from e

        self.get_all_items.cache_clear()
        return Item.model_validate(new_item)

    async def update_item(self, db: AsyncSession, item_id: int, item_data: ItemUpdate) -> Item:
        repo = ItemRepository(db)
        try:
            updated_item = await repo.update(item_id, item_data)
        except IntegrityError as e:
            raise DuplicateItemError(f"Update leads to duplicate value for item {item_id}") from e
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to update item {item_id}: {e}") from e

        if updated_item is None:
            raise ItemNotFoundError(item_id)

        self.get_all_items.cache_clear()
        return Item.model_validate(updated_item)

    async def delete_item(self, db: AsyncSession, item_id: int) -> bool:
        repo = ItemRepository(db)
        try:
            deleted = await repo.delete(item_id)
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to delete item {item_id}: {e}") from e

        if not deleted:
            raise ItemNotFoundError(item_id)

        self.get_all_items.cache_clear()
        return True

    async def get_item(self, db: AsyncSession, item_id: int) -> Item:
        repo = ItemRepository(db)
        try:
            item = await repo.get(item_id)
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to fetch item {item_id}: {e}") from e

        if item is None:
            raise ItemNotFoundError(item_id)

        return Item.model_validate(item)