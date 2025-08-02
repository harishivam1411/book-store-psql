from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, date
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

import json
from sqlalchemy.future import select
from store.models.db_model import Book, Category


@book_router.post("/load-books/")
async def load_books(db: AsyncSession = Depends(get_database)):
    with open(
        "C:\\Users\\SOFT SUAVE A-3\\Desktop\\harishivam1411\\book-store-psql\\data\\books.json"
    ) as f:
        books = json.load(f)
    for book in books:
        if isinstance(book["publication_date"], str):
            book["publication_date"] = datetime.strptime(
                book["publication_date"], "%Y-%m-%d"
            ).date()

        # Don't pass category_ids to Book(**book_data)
        category_ids = book.pop("category_ids", [])

        # Create Book instance
        book = Book(**book)

        # Attach related categories
        if category_ids:
            result = await db.execute(select(Category).where(Category.id.in_(category_ids)))
            book.categories = result.scalars().all()

        db.add(book)
    await db.commit()
    return {"status": "Inserted books"}