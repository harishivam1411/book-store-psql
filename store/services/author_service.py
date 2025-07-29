from fastapi import HTTPException
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from store.models.db_model import Author, Book
from store.models.author_model import AuthorCreate, AuthorUpdate, AuthorCreateResponse
from store.models.author_model import AuthorResponse, AuthorsResponse, AuthorBooksSchema

class AuthorService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def retrieve_authors(self) -> list[AuthorsResponse]:
        # Query all authors
        result = await self.db.execute(select(Author))
        authors = result.scalars().all()
        
        return [AuthorsResponse(
            id=author.id,
            name=author.name,
            biography=author.biography,
            birth_date=author.birth_date,
            death_date=author.death_date,
            country=author.country,
            book_count=author.book_count,
            created_at=author.created_at,
            updated_at=author.updated_at
        ) for author in authors]

    async def create_author(self, author: AuthorCreate) -> AuthorCreateResponse:
        # Create new author
        new_author = Author(
            name=author.name,
            biography=author.biography,
            birth_date=author.birth_date,
            death_date=None,
            country=author.country,
            book_count=0
        )
        
        self.db.add(new_author)
        await self.db.commit()
        await self.db.refresh(new_author)
        
        return await self.retrieve_author(new_author.id)

    async def retrieve_author(self, author_id: int) -> AuthorResponse:
        try:
            # Query author by ID
            result = await self.db.execute(select(Author).where(Author.id == author_id))
            author = result.scalars().first()
            
            if not author:
                raise HTTPException(status_code=404, detail=f"Author with ID {author_id} not found")
            
            # Get books by this author
            books_result = await self.db.execute(select(Book).where(Book.author_id == author_id))
            books = books_result.scalars().all()
            
            books_data = [
                AuthorBooksSchema(
                    id=book.id,
                    title=book.title,
                    isbn=book.isbn or "",
                    publication_date=book.publication_date
                ) for book in books
            ]
            
            return AuthorResponse(
                id=author.id,
                name=author.name,
                biography=author.biography,
                birth_date=author.birth_date,
                death_date=author.death_date,
                country=author.country,
                book_count=author.book_count,
                books=books_data,
                created_at=author.created_at,
                updated_at=author.updated_at
            )
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            # It's better to log the actual exception for debugging
            print(f"Error retrieving author: {str(e)}")
            raise HTTPException(status_code=404, detail=f"Author with ID {author_id} not found")

    async def update_author(self, author_id: int, author: AuthorUpdate) -> AuthorResponse:
        # Verify author exists
        result = await self.db.execute(select(Author).where(Author.id == author_id))
        existing_author = result.scalars().first()
        
        if not existing_author:
            raise HTTPException(status_code=404, detail=f"Author with ID {author_id} not found")
        
        # Update author fields
        update_data = author.model_dump(exclude_unset=True)
        
        for key, value in update_data.items():
            setattr(existing_author, key, value)
        
        existing_author.updated_at = datetime.now(timezone.utc)
        
        await self.db.commit()
        await self.db.refresh(existing_author)
        
        return await self.retrieve_author(author_id)