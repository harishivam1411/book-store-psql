from typing import List
from pydantic import BaseModel
from datetime import datetime
from store.models.base_model import CreateUpdateSchema


class OrderItemCreate(BaseModel):
    book_id: int
    quantity: int


class OrderCreate(BaseModel):
    items: List[OrderItemCreate]


class OrderItemResponse(BaseModel):
    book_id: int
    quantity: int
    price_per_item: float

    class Config:
        from_attributes = True


class OrderResponse(CreateUpdateSchema):
    total_amount: float
    items: List[OrderItemResponse]

    class Config:
        from_attributes = True