from fastapi import HTTPException
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from sqlalchemy.orm import joinedload

from store.models.db_model import Book, Author, Category, Review
from store.models.book_model import BookCreate, BookUpdate, BookCreateResponse, BookUpdateResponse, BookResponse, BooksResponse

class BookService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def retrieve_books(self) -> list[BooksResponse]:
   
        result = await self.db.execute(
            select(Book).options(
                joinedload(Book.author),
                joinedload(Book.categories)
            )
        )
        books = result.unique().scalars().all()
        
        result_books = []
        for book in books:
            # Create author data
            author_data = {"id": "", "name": "Unknown Author"}
            if book.author:
                author_data = {"id": book.author.id, "name": book.author.name}
            
            # Create categories data
            categories_data = []
            for category in book.categories:
                categories_data.append({"id": category.id, "name": category.name})

            # Calculate average rating
            reviews_result = await self.db.execute(
                select(func.avg(Review.rating)).where(Review.book_id == book.id)
            )
            avg_rating = reviews_result.scalar() or 0.0
            if avg_rating:
                avg_rating = round(avg_rating * 1.0, 1)
            
            book_response = BookResponse(
                id=book.id,
                title=book.title,
                isbn=book.isbn or "",
                publication_date=book.publication_date,
                description=book.description,
                page_count=book.page_count,
                language=book.language,
                author=author_data,
                categories=categories_data,
                average_rating=avg_rating,
                created_at=book.created_at,
                updated_at=book.updated_at
            )
            result_books.append(book_response)
            
        return result_books

    async def create_book(self, book: BookCreate) -> BookCreateResponse:
        
        existing = await self.db.execute(select(Book).where(Book.isbn == book.isbn))
        existing_book = existing.scalars().first()

        if existing_book:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Bad Request",
                    "message": "Invalid input data",
                    "details": {
                        "isbn": [f"A book with ISBN '{book.isbn}' already exists."]
                    }
                }
            )
        
        # Validate author exists
        author = None
        if book.author_id:
            author_result = await self.db.execute(select(Author).where(Author.id == book.author_id))
            author = author_result.scalars().first()
            if not author:
                raise HTTPException(status_code=400, detail={
                    "error": "Bad Request",
                    "message": "Invalid input data",
                    "details": {
                        "author_id": [f"Author with ID {book.author_id} does not exist"]
                    }
                })

        # Validate categories exist
        found_categories = []
        if book.category_ids:
            category_ids = book.category_ids
            categories_result = await self.db.execute(
                select(Category).where(Category.id.in_(category_ids))
            )
            found_categories = categories_result.scalars().all()

            if len(found_categories) != len(category_ids):
                found_ids = [cat.id for cat in found_categories]
                invalid_ids = [cat_id for cat_id in category_ids if cat_id not in found_ids]

                raise HTTPException(status_code=400, detail={
                    "error": "Bad Request",
                    "message": "Invalid input data",
                    "details": {
                        "category_ids": [f"Category with ID {cat_id} does not exist" for cat_id in invalid_ids]
                    }
                })

        # Create new book and assign categories before flush/commit
        new_book = Book(
            title=book.title,
            isbn=book.isbn,
            publication_date=book.publication_date,
            description=book.description,
            page_count=book.page_count,
            language=book.language,
            author_id=book.author_id if book.author_id else None,
            average_rating=0.0,
            categories=found_categories  
        )

        self.db.add(new_book)
        await self.db.flush()  

        # Update book count for categories
        for category in found_categories:
            category.book_count += 1

        # Update author book count
        if author:
            author.book_count += 1

        await self.db.commit()
        await self.db.refresh(new_book)

        return await self.retrieve_book(new_book.id)

    async def retrieve_book(self, book_id: int) -> BookResponse:
        try:
            # Query book by ID with author and categories
            result = await self.db.execute(
                select(Book).options(
                    joinedload(Book.author),
                    joinedload(Book.categories)
                ).where(Book.id == book_id)
            )
            book = result.unique().scalars().first()
            
            if not book:
                raise HTTPException(status_code=404, detail=f"Book with ID {book_id} not found")
            
            # Create author data
            author_data = {"id": "", "name": "Unknown Author"}
            if book.author:
                author_data = {"id": book.author.id, "name": book.author.name}
            
            # Create categories data
            categories_data = []
            for category in book.categories:
                categories_data.append({"id": category.id, "name": category.name})
            
            # Calculate average rating
            reviews_result = await self.db.execute(
                select(func.avg(Review.rating)).where(Review.book_id == book_id)
            )
            avg_rating = reviews_result.scalar() or 0.0
            if avg_rating:
                print(avg_rating)
                avg_rating = round(avg_rating * 1.0, 1)
                print(avg_rating)
            
            return BookResponse(
                id=book.id,
                title=book.title,
                isbn=book.isbn or "",
                publication_date=book.publication_date,
                description=book.description,
                page_count=book.page_count,
                language=book.language,
                author=author_data,
                categories=categories_data,
                average_rating=avg_rating,
                created_at=book.created_at,
                updated_at=book.updated_at
            )
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=404, detail=f"Book with ID {book_id} not found")

    async def update_book(self, book_id: int, book: BookUpdate) -> BookUpdateResponse:
        # Verify book exists
        book_result = await self.db.execute(
            select(Book).options(
                joinedload(Book.categories)
            ).where(Book.id == book_id)
        )
        existing_book = book_result.unique().scalars().first()
        
        if not existing_book:
            raise HTTPException(status_code=404, detail=f"Book with ID {book_id} not found")
        
        if book.isbn:
            existing_isbn = await self.db.execute(
                select(Book).where(Book.isbn == book.isbn, Book.id != book_id)
            )
            isbn_conflict = existing_isbn.scalars().first()

            if isbn_conflict:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "Bad Request",
                        "message": "ISBN already exists",
                        "details": {
                            "isbn": [f"A book with ISBN '{book.isbn}' already exists."]
                        }
                    }
                )
        
        update_data = book.model_dump(exclude_unset=True)
        
        # Validate author if being updated
        if "author_id" in update_data and update_data["author_id"]:
            author_result = await self.db.execute(select(Author).where(Author.id == update_data["author_id"]))
            author = author_result.scalars().first()
            
            if not author:
                raise HTTPException(status_code=400, detail={
                    "error": "Bad Request",
                    "message": "Invalid input data",
                    "details": {
                        "author_id": [f"Author with ID {update_data['author_id']} does not exist"]
                    }
                })
            
            # Update author book count if changed
            if existing_book.author_id != update_data["author_id"]:
                # Decrement old author's book count if exists
                if existing_book.author_id:
                    old_author_result = await self.db.execute(select(Author).where(Author.id == existing_book.author_id))
                    old_author = old_author_result.scalars().first()
                    if old_author and old_author.book_count > 0:
                        old_author.book_count -= 1
                
                # Increment new author's book count
                author.book_count += 1
        
        # Validate categories if being updated
        if "category_ids" in update_data and update_data["category_ids"]:
            category_ids = [cat_id for cat_id in update_data["category_ids"]]
            categories_result = await self.db.execute(
                select(Category).where(Category.id.in_(category_ids))
            )
            found_categories = categories_result.scalars().all()
            
            if len(found_categories) != len(category_ids):
                found_ids = [cat.id for cat in found_categories]
                invalid_ids = [cat_id for cat_id in category_ids if cat_id not in found_ids]
                
                raise HTTPException(status_code=400, detail={
                    "error": "Bad Request", 
                    "message": "Invalid input data",
                    "details": {
                        "category_ids": [f"Category with ID {cat_id} does not exist" for cat_id in invalid_ids]
                    }
                })
            
            # Get current categories for the book
            current_category_ids = [cat.id for cat in existing_book.categories]
            
            # Update categories
            # Clear existing categories
            existing_book.categories = []
            await self.db.commit()
            
            # Update category book counts
            for cat_id in current_category_ids:
                if cat_id not in category_ids:
                    # Decrement book count for removed categories
                    cat_result = await self.db.execute(select(Category).where(Category.id == cat_id))
                    category = cat_result.scalars().first()
                    if category and category.book_count > 0:
                        category.book_count -= 1
            
            for category in found_categories:
                # Add category to book
                existing_book.categories.append(category)
                # Increment book count for new categories
                if category.id not in current_category_ids:
                    category.book_count += 1
        
        # Update book fields
        for key, value in update_data.items():
            if key not in ["category_ids"]:  # Skip category_ids as we handle it separately
                setattr(existing_book, key, value)
        
        existing_book.updated_at = datetime.now(timezone.utc)
        
        await self.db.commit()
        await self.db.refresh(existing_book)
        
        return await self.retrieve_book(book_id)