from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from services import ItemService
from schemas import Item, ItemCreate, ItemUpdate
from typing import List

router = APIRouter(prefix="/items", tags=["items"])

# Единственный экземпляр сервиса (синглтон)
item_service = ItemService()


@router.post("/", response_model=Item)
async def create_item(
    item_data: ItemCreate,
    db: AsyncSession = Depends(get_db)
):
    return await item_service.create_item(db, item_data)

@router.get("/", response_model=List[Item])
async def read_items(db: AsyncSession = Depends(get_db)):
    return await item_service.get_all_items(db)

@router.get("/{item_id}", response_model=Item)
async def read_item(
    item_id: int,
    db: AsyncSession = Depends(get_db)
):
    item = await item_service.get_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.put("/{item_id}", response_model=Item)
async def update_item(
    item_id: int,
    item_data: ItemUpdate,
    db: AsyncSession = Depends(get_db)
):
    updated = await item_service.update_item(db, item_id, item_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Item not found")
    return updated

@router.delete("/{item_id}")
async def delete_item(
    item_id: int,
    db: AsyncSession = Depends(get_db)
):
    deleted = await item_service.delete_item(db, item_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Item not found")
    return None
