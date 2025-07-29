from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from store.database import get_database
from store.utils.dependencies import get_current_user
from store.models.auth_model import TokenPayload
from store.services.author_service import AuthorService
from store.models.author_model import AuthorCreate, AuthorUpdate, AuthorCreateResponse, AuthorUpdateResponse, AuthorResponse, AuthorsResponse

author_router = APIRouter(prefix='/authors', tags=['Authors'])

@author_router.get('/', response_model=list[AuthorsResponse])
async def retrieve_authors(db: AsyncSession = Depends(get_database)):
    service = AuthorService(db)
    return await service.retrieve_authors()

@author_router.post('/', response_model=AuthorCreateResponse)
async def create_author(author: AuthorCreate, db: AsyncSession = Depends(get_database)):
    service = AuthorService(db)
    return await service.create_author(author)

@author_router.get('/{author_id}', response_model=AuthorResponse)
async def retrieve_author(author_id: int, db: AsyncSession = Depends(get_database)):
    service = AuthorService(db)
    return await service.retrieve_author(author_id)

@author_router.put('/{author_id}', response_model=AuthorUpdateResponse)
async def update_author(author_id: int, author: AuthorUpdate, db: AsyncSession = Depends(get_database)):
    service = AuthorService(db)
    return await service.update_author(author_id, author)