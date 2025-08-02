from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, date
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

import json
from sqlalchemy.future import select
from store.models.db_model import Author
@author_router.post("/load-authors/")
async def load_authors(db: AsyncSession = Depends(get_database)):
    with open(
        "C:\\Users\\SOFT SUAVE A-3\\Desktop\\harishivam1411\\book-store-psql\\data\\authors.json"
    ) as f:
        authors = json.load(f)
    for author in authors:

        if isinstance(author["birth_date"], str):
            author["birth_date"] = datetime.strptime(
                author["birth_date"], "%Y-%m-%d"
            ).date()

        result = await db.execute(select(Author).where(Author.name == author["name"]))
        existing = result.scalar_one_or_none()
        if not existing:
            db.add(Author(**author))

    await db.commit()
    return {"status": "Inserted authors"}