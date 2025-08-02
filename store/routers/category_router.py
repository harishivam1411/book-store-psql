import json

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from store.database import get_database
from store.models.category_model import (
    CategoryCreate,
    CategoryCreateResponse,
    CategoryResponse,
    CategorysResponse,
    CategoryUpdate,
    CategoryUpdateResponse,
)
from store.models.db_model import Category
from store.services.category_service import CategoryService

category_router = APIRouter(prefix="/categories", tags=["Categories"])


@category_router.get("/", response_model=list[CategorysResponse])
async def retrieve_categories(db: AsyncSession = Depends(get_database)):
    service = CategoryService(db)
    return await service.retrieve_categories()


@category_router.post("/", response_model=CategoryCreateResponse)
async def create_category(
    category: CategoryCreate, db: AsyncSession = Depends(get_database)
):
    service = CategoryService(db)
    return await service.create_category(category)


@category_router.get("/{category_id}", response_model=CategoryResponse)
async def retrieve_category(category_id: int, db: AsyncSession = Depends(get_database)):
    service = CategoryService(db)
    return await service.retrieve_category(category_id)


@category_router.put("/{category_id}", response_model=CategoryUpdateResponse)
async def update_category(
    category_id: int, category: CategoryUpdate, db: AsyncSession = Depends(get_database)
):
    service = CategoryService(db)
    return await service.update_category(category_id, category)


@category_router.post("/load-categories/")
async def load_categories(db: AsyncSession = Depends(get_database)):
    with open(
        "C:\\Users\\SOFT SUAVE A-3\\Desktop\\harishivam1411\\book-store-psql\\data\\categoies.json"
    ) as f:
        categories = json.load(f)
    for cat in categories:
        result = await db.execute(select(Category).where(Category.name == cat["name"]))
        existing = result.scalar_one_or_none()
        if not existing:
            db.add(Category(**cat))

    await db.commit()
    return {"status": "Inserted categories"}
