from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from store.database import get_database
from store.utils.dependencies import get_current_user
from store.models.auth_model import TokenPayload
from store.services.category_service import CategoryService
from store.models.category_model import CategoryCreate, CategoryUpdate, CategoryCreateResponse, CategoryUpdateResponse, CategoryResponse, CategorysResponse

category_router = APIRouter(prefix='/categories', tags=['Categories'])

@category_router.get('/', response_model=list[CategorysResponse])
async def retrieve_categories(db: AsyncSession = Depends(get_database)):
    service = CategoryService(db)
    return await service.retrieve_categories()

@category_router.post('/', response_model=CategoryCreateResponse)
async def create_category(category: CategoryCreate, db: AsyncSession = Depends(get_database)):
    service = CategoryService(db)
    return await service.create_category(category)

@category_router.get('/{category_id}', response_model=CategoryResponse)
async def retrieve_category(category_id: int, db: AsyncSession = Depends(get_database)):
    service = CategoryService(db)
    return await service.retrieve_category(category_id)

@category_router.put('/{category_id}', response_model=CategoryUpdateResponse)
async def update_category(category_id: int, category: CategoryUpdate, db: AsyncSession = Depends(get_database)):
    service = CategoryService(db)
    return await service.update_category(category_id, category)