from typing import List
from uuid import uuid4, UUID

from api.schemas.Item import Item
from db import get_session
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

router = APIRouter()

# Database emulation
items_db: List[Item] = []


@router.post("/items/", response_model=Item)
async def create_item(item: Item, db: Session = Depends(get_session)):
    item.id = uuid4()
    items_db.append(item)
    return item


@router.get("/items", response_model=List[Item])
async def read_items(db: Session = Depends(get_session)):
    return items_db


@router.get("/items/{item_id}", response_model=Item)
async def read_item(item_id: UUID, db: Session = Depends(get_session)):
    for item in items_db:
        if item.id == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")


@router.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: UUID, item_data: Item, db: Session = Depends(get_session)):
    for index, item in enumerate(items_db):
        if item.id == item_id:
            item.name = item_data.name
            item.description = item_data.description
            items_db[index] = item
            return item
    raise HTTPException(status_code=404, detail="Item not found")


@router.delete("/items/{item_id}", response_model=Item)
async def delete_item(item_id: UUID, db: Session = Depends(get_session)):
    for index, item in enumerate(items_db):
        if item.id == item_id:
            del items_db[index]
            return item
    raise HTTPException(status_code=404, detail="Item not found")
