from fastapi import HTTPException
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, func, desc, and_

from store.models.category_model import CategoryCreate, CategoryUpdate, CategoryCreateResponse
from store.models.category_model import CategoryUpdateResponse, CategoryResponse, CategorysResponse, TopBooksSchema
from store.models.db_model import Category, Book, Author, book_category, Review

class CategoryService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def retrieve_categories(self) -> list[CategorysResponse]:
        # Query all categories
        result = await self.db.execute(select(Category))
        categories = result.scalars().all()
        
        return [CategorysResponse(
            id=category.id,
            name=category.name,
            description=category.description,
            book_count=category.book_count,
            created_at=category.created_at,
            updated_at=category.updated_at
        ) for category in categories]
    
    async def create_category(self, category: CategoryCreate) -> CategoryCreateResponse:
       
        result = await self.db.execute(select(Category).where(Category.name == category.name))
        existing = result.scalars().first()
        
        if existing:
            raise HTTPException(status_code=400, detail="Category with this name already exists")
        
        new_category = Category(
            name=category.name,
            description=category.description,
            book_count=0
        )
        
        self.db.add(new_category)
        await self.db.commit()
        await self.db.refresh(new_category)
        
        return await self.retrieve_category(new_category.id)
    
    async def retrieve_category(self, category_id: int) -> CategoryResponse:
        try:
            # Get the category
            result = await self.db.execute(select(Category).where(Category.id == category_id))
            category = result.scalars().first()
            
            if not category:
                raise HTTPException(status_code=404, detail="Category not found")
            
            # First, get books in this category with average ratings
            top_books_query = (
                select(Book.id, Book.title, Book.author_id, func.avg(Review.rating).label("avg_rating"))
                .join(book_category, Book.id == book_category.c.book_id)
                .join(Category, book_category.c.category_id == Category.id)
                .outerjoin(Review, Book.id == Review.book_id)
                .where(Category.id == category_id)
                .group_by(Book.id)
                .order_by(desc("avg_rating"))
                .limit(5)
            )
            
            top_books_result = await self.db.execute(top_books_query)
            top_books_data = []
            
            # Get book details with authors
            for book_id, book_title, author_id, avg_rating in top_books_result:
                # Get author information if available
                author_data = None
                if author_id:
                    author_query = select(Author).where(Author.id == author_id)
                    author_result = await self.db.execute(author_query)
                    author = author_result.scalars().first()
                    if author:
                        author_data = {"id": author.id, "name": author.name}
                
                top_books_data.append(
                    TopBooksSchema(
                        id=book_id,
                        title=book_title,
                        author=author_data,
                        average_rating=round(avg_rating, 1) if avg_rating else 0
                    )
                )
            
            return CategoryResponse(
                id=category.id,
                name=category.name,
                description=category.description,
                book_count=category.book_count,
                top_books=top_books_data,
                created_at=category.created_at,
                updated_at=category.updated_at
            )
            
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=500, detail=f"Error retrieving category: {str(e)}")

    async def update_category(self, category_id: int, category: CategoryUpdate) -> CategoryUpdateResponse:
        try:
            # Find existing category
            result = await self.db.execute(select(Category).where(Category.id == category_id))
            existing = result.scalars().first()
            
            if not existing:
                raise HTTPException(status_code=404, detail="Category not found")
            
            # Extract update data
            update_data = category.model_dump(exclude_unset=True)
            
            if "name" in update_data:
                name_check = await self.db.execute(
                    select(Category).where(
                        and_(
                            Category.name == update_data["name"],
                            Category.id != category_id
                        )
                    )
                )
                if name_check.scalars().first():
                    raise HTTPException(status_code=400, detail="Category with this name already exists")
            
            # Update timestamp
            update_data["updated_at"] = datetime.now(timezone.utc)
            
            # Perform update
            await self.db.execute(
                update(Category)
                .where(Category.id == category_id)
                .values(**update_data)
            )
            
            await self.db.commit()
            
            return await self.retrieve_category(category_id)
            
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=500, detail=f"Error updating category: {str(e)}")