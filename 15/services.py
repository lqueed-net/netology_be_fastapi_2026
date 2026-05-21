import json
import os
from http.client import HTTPException

from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from schemas import Item, ItemCreate, ItemUpdate
from repositories.item import ItemRepository  # конкретная реализация
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from async_lru import alru_cache

from schemas import Order, OrderCreate, OrderUpdate, OrderItem, OrderItemCreate, OrderItemUpdate
from repositories.order import OrderRepository
from repositories.order_item import OrderItemRepository

from exceptions import ItemServiceError, ItemNotFoundError, DatabaseError, DuplicateItemError

# Импортируем Redis клиент из redis_client
from redis_client import redis_client


class ItemService:
    def __init__(self):
        # Кеш для списка товаров (максимум 128 элементов)
        # Декоратор применён ниже к методу, поэтому здесь ничего не нужно
        pass

    async def get_all_items(self, db: AsyncSession) -> List[Item]:
        """Получить все товары (с кешированием в Redis)."""
        # Попробуем получить данные из Redis кэша
        cache_key = "items:all"
        if redis_client:
            try:
                cached_items = await redis_client.get(cache_key)
                if cached_items:
                    items_data = json.loads(cached_items)
                    return [Item(**item) for item in items_data]
            except Exception as e:
                print(f"Ошибка при получении из Redis кэша: {e}")

        # Если нет в кэше, получаем из БД
        repo = ItemRepository(db)
        try:
            items = await repo.get_all()
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to fetch items: {e}") from e

        items_list = [Item.model_validate(item) for item in items]

        # Сохраняем в Redis кэш на 5 минут
        if redis_client:
            try:
                items_json = json.dumps([item.model_dump() for item in items_list])
                await redis_client.setex(cache_key, 300, items_json)  # 300 секунд = 5 минут
            except Exception as e:
                print(f"Ошибка при сохранении в Redis кэш: {e}")

        return items_list

    async def create_item(self, db: AsyncSession, item_data: ItemCreate) -> Item:
        repo = ItemRepository(db)
        try:
            new_item = await repo.create(item_data)
        except IntegrityError as e:
            raise DuplicateItemError(f"Item with name {item_data.name} already exists") from e
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to create item: {e}") from e

        # Инвалидируем кеш списка
        if redis_client:
            try:
                await redis_client.delete("items:all")
            except Exception as e:
                print(f"Ошибка при удалении кэша: {e}")

        return Item.model_validate(new_item)

    async def update_item(self, db: AsyncSession, item_id: int, item_data: ItemUpdate) -> Optional[Item]:
        repo = ItemRepository(db)
        try:
            updated_item = await repo.update(item_id, item_data)
        except IntegrityError as e:
            raise DuplicateItemError(f"Duplicate value for item {item_id}") from e
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to update item: {e}") from e

        if updated_item:
            # Инвалидируем кеш списка
            if redis_client:
                try:
                    await redis_client.delete("items:all")
                except Exception as e:
                    print(f"Ошибка при удалении кэша: {e}")

            return Item.model_validate(updated_item)
        return None

    async def delete_item(self, db: AsyncSession, item_id: int) -> bool:
        repo = ItemRepository(db)
        deleted = await repo.delete(item_id)
        if deleted:
            # Инвалидируем кеш списка
            if redis_client:
                try:
                    await redis_client.delete("items:all")
                except Exception as e:
                    print(f"Ошибка при удалении кэша: {e}")
        return deleted

    async def get_item(self, db: AsyncSession, item_id: int) -> Optional[Item]:
        repo = ItemRepository(db)
        item = await repo.get(item_id)
        return Item.model_validate(item) if item else None
    



class OrderService:
    def __init__(self):
        # Кеш для списка заказов
        pass

    async def get_all_orders(self, db: AsyncSession) -> List[Order]:
        """Получить все заказы."""
        repo = OrderRepository(db)
        orders = await repo.get_all()
        return [Order.model_validate(order) for order in orders]

    async def create_order(self, db: AsyncSession, order_data: OrderCreate) -> Order:
        repo = OrderRepository(db)
        new_order = await repo.create(order_data)
        # Инвалидируем кеш списка заказов
        self.get_all_orders.cache_clear()
        return Order.model_validate(new_order)

    async def update_order(self, db: AsyncSession, order_id: int, order_data: OrderUpdate) -> Optional[Order]:
        repo = OrderRepository(db)
        updated_order = await repo.update(order_id, order_data)
        if updated_order:
            # Инвалидируем кеш списка заказов
            self.get_all_orders.cache_clear()
            return Order.model_validate(updated_order)
        return None

    async def delete_order(self, db: AsyncSession, order_id: int) -> bool:
        repo = OrderRepository(db)
        deleted = await repo.delete(order_id)
        if deleted:
            # Инвалидируем кеш списка заказов
            self.get_all_orders.cache_clear()
            # Также можно инвалидировать кеш списка позиций, но для простоты опустим
        return deleted

    async def get_order(self, db: AsyncSession, order_id: int) -> Optional[Order]:
        repo = OrderRepository(db)
        order = await repo.get(order_id)
        return Order.model_validate(order) if order else None


class OrderItemService:
    def __init__(self):
        # Кеш для списка всех позиций
        pass

    async def get_all_order_items(self, db: AsyncSession) -> List[OrderItem]:
        """Получить все позиции заказов."""
        repo = OrderItemRepository(db)
        items = await repo.get_all()
        return [OrderItem.model_validate(item) for item in items]

    async def get_items_by_order(self, db: AsyncSession, order_id: int) -> List[OrderItem]:
        """Получить все позиции конкретного заказа (без кеширования)."""
        repo = OrderItemRepository(db)
        items = await repo.get_by_order(order_id)
        return [OrderItem.model_validate(item) for item in items]

    async def get_items_by_item(self, db: AsyncSession, item_id: int) -> List[OrderItem]:
        """Получить все позиции с конкретным товаром (без кеширования)."""
        repo = OrderItemRepository(db)
        items = await repo.get_by_item(item_id)
        return [OrderItem.model_validate(item) for item in items]

    async def create_order_item(self, db: AsyncSession, item_data: OrderItemCreate) -> OrderItem:
        repo = OrderItemRepository(db)
        new_item = await repo.create(item_data)
        # Инвалидируем кеш списка всех позиций
        self.get_all_order_items.cache_clear()
        return OrderItem.model_validate(new_item)

    async def update_order_item(self, db: AsyncSession, item_id: int, item_data: OrderItemUpdate) -> Optional[OrderItem]:
        repo = OrderItemRepository(db)
        updated_item = await repo.update(item_id, item_data)
        if updated_item:
            # Инвалидируем кеш списка всех позиций
            self.get_all_order_items.cache_clear()
            return OrderItem.model_validate(updated_item)
        return None

    async def delete_order_item(self, db: AsyncSession, item_id: int) -> bool:
        repo = OrderItemRepository(db)
        deleted = await repo.delete(item_id)
        if deleted:
            # Инвалидируем кеш списка всех позиций
            self.get_all_order_items.cache_clear()
        return deleted

    async def get_order_item(self, db: AsyncSession, item_id: int) -> Optional[OrderItem]:
        repo = OrderItemRepository(db)
        item = await repo.get(item_id)
        return OrderItem.model_validate(item) if item else None