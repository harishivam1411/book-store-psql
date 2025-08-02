from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from store.database import get_database
from store.models.order_model import OrderCreate, OrderResponse
from store.services import order_service


order_router = APIRouter(prefix="/orders", tags=["Orders"])


@order_router.post("/", response_model=OrderResponse)
async def place_order(
    order_data: OrderCreate, db: AsyncSession = Depends(get_database)
):
    
    return await order_service.create_order(db, order_data)


@order_router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: int, db: AsyncSession = Depends(get_database)):
    return await order_service.get_order(db, order_id)
