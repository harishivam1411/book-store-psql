from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from store.database import get_database
from store.utils.dependencies import get_current_user
from store.models.auth_model import TokenPayload
from store.services.book_service import BookService
from store.models.book_model import BookCreate, BookUpdate, BookCreateResponse, BookUpdateResponse, BookResponse, BooksResponse

book_router = APIRouter(prefix='/books', tags=['Books'])

@book_router.get('/', response_model=list[BooksResponse])
async def retrieve_books(db: AsyncSession = Depends(get_database)):
    service = BookService(db)
    return await service.retrieve_books()

@book_router.post('/', response_model=BookCreateResponse)
async def create_book(book: BookCreate, db: AsyncSession = Depends(get_database)):
    service = BookService(db)
    return await service.create_book(book)

@book_router.get('/{book_id}', response_model=BookResponse)
async def retrieve_book(book_id: int, db: AsyncSession = Depends(get_database)):
    service = BookService(db)
    return await service.retrieve_book(book_id)

@book_router.put('/{book_id}', response_model=BookUpdateResponse)
async def update_book(book_id: int, book: BookUpdate, db: AsyncSession = Depends(get_database)):
    service = BookService(db)
    return await service.update_book(book_id, book)