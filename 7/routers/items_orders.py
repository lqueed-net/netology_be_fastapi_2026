from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from services import OrderService, OrderItemService
from schemas import Order, OrderCreate, OrderUpdate, OrderItem, OrderItemCreate, OrderItemUpdate
from typing import List

# Роутер для заказов
router_orders = APIRouter(prefix="/orders", tags=["orders"])

# Роутер для позиций заказов
router_order_items = APIRouter(prefix="/order-items", tags=["order-items"])

# Экземпляры сервисов (синглтоны)
order_service = OrderService()
order_item_service = OrderItemService()


# ---------- CRUD для Order ----------
@router_orders.post("/", response_model=Order, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    db: AsyncSession = Depends(get_db)
):
    """Создать новый заказ."""
    return await order_service.create_order(db, order_data)


@router_orders.get("/", response_model=List[Order])
async def read_orders(db: AsyncSession = Depends(get_db)):
    """Получить список всех заказов."""
    return await order_service.get_all_orders(db)


@router_orders.get("/{order_id}", response_model=Order)
async def read_order(
    order_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получить заказ по ID."""
    order = await order_service.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router_orders.put("/{order_id}", response_model=Order)
async def update_order(
    order_id: int,
    order_data: OrderUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Обновить заказ."""
    updated = await order_service.update_order(db, order_id, order_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Order not found")
    return updated


@router_orders.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(
    order_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Удалить заказ (каскадно удалятся связанные позиции)."""
    deleted = await order_service.delete_order(db, order_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Order not found")
    return None


# ---------- Дополнительный эндпоинт: позиции конкретного заказа ----------
@router_orders.get("/{order_id}/items", response_model=List[OrderItem])
async def read_order_items(
    order_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получить все позиции указанного заказа."""
    # Проверим, существует ли заказ (можно и не проверять, сервис вернёт пустой список)
    order = await order_service.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return await order_item_service.get_items_by_order(db, order_id)


# ---------- CRUD для OrderItem ----------
@router_order_items.post("/", response_model=OrderItem, status_code=status.HTTP_201_CREATED)
async def create_order_item(
    item_data: OrderItemCreate,
    db: AsyncSession = Depends(get_db)
):
    """Добавить товар в заказ (создать позицию)."""
    # Можно дополнительно проверить существование заказа и товара, но сервис сделает это сам
    return await order_item_service.create_order_item(db, item_data)


@router_order_items.get("/", response_model=List[OrderItem])
async def read_order_items_all(db: AsyncSession = Depends(get_db)):
    """Получить список всех позиций (может быть большим, лучше фильтровать по заказу)."""
    return await order_item_service.get_all_order_items(db)


@router_order_items.get("/{item_id}", response_model=OrderItem)
async def read_order_item(
    item_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получить позицию по её ID."""
    item = await order_item_service.get_order_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Order item not found")
    return item


@router_order_items.put("/{item_id}", response_model=OrderItem)
async def update_order_item(
    item_id: int,
    item_data: OrderItemUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Обновить позицию (например, изменить количество)."""
    updated = await order_item_service.update_order_item(db, item_id, item_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Order item not found")
    return updated


@router_order_items.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order_item(
    item_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Удалить позицию из заказа."""
    deleted = await order_item_service.delete_order_item(db, item_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Order item not found")
    return None