from fastapi import HTTPException
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, func, desc, and_
from sqlalchemy.orm import joinedload

from store.models.review_model import ReviewCreate, ReviewUpdate, ReviewCreateResponse, ReviewUpdateResponse, ReviewResponse, ReviewsResponse
from store.models.db_model import Review, Book, User

class ReviewService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def retrieve_reviews(self, book_id: int) -> list[ReviewsResponse]:
        try:
            # Check if book exists
            book_result = await self.db.execute(select(Book).where(Book.id == book_id))
            book = book_result.scalars().first()
            if not book:
                raise HTTPException(status_code=404, detail=f"Book with ID {book_id} not found")
            
            # Get reviews for this book
            result = await self.db.execute(
                select(Review)
                .options(joinedload(Review.user))
                .where(Review.book_id == book_id)
                .order_by(desc(Review.created_at))
            )
            reviews = result.scalars().all()
            
            return [ReviewsResponse(
                id=review.id,
                book_id=review.book_id,
                user={
                    "id": review.user.id,
                    "username": review.user.username
                } if review.user else {
                    "id": review.user_id,
                    "username": "Unknown user"
                },
                rating=review.rating,
                title=review.title,
                content=review.content,
                created_at=review.created_at,
                updated_at=review.updated_at
            ) for review in reviews]
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid book ID format")
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=500, detail=f"Error retrieving reviews: {str(e)}")

    async def create_review(self, book_id: int, user_id: int, review_create: ReviewCreate) -> ReviewCreateResponse:
        try:
            # Check if book exists
            book_result = await self.db.execute(select(Book).where(Book.id == book_id))
            book = book_result.scalars().first()
            if not book:
                raise HTTPException(status_code=404, detail="Book not found")
            
            # Check if user exists
            user_result = await self.db.execute(select(User).where(User.id == user_id))
            user = user_result.scalars().first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            # Check if user has already reviewed this book
            existing_review_result = await self.db.execute(
                select(Review).where(
                    and_(
                        Review.book_id == book_id,
                        Review.user_id == user_id
                    )
                )
            )
            existing_review = existing_review_result.scalars().first()
            if existing_review:
                raise HTTPException(status_code=400, detail="User has already reviewed this book")
            
            # Create new review
            review_dict = review_create.model_dump()
            new_review = Review(
                book_id=book_id,
                user_id=user_id,
                rating=review_dict["rating"],
                title=review_dict["title"],
                content=review_dict["content"],
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            
            self.db.add(new_review)
            await self.db.commit()
            await self.db.refresh(new_review)
            
            # Increment user's review count
            user.review_count = (user.review_count or 0) + 1
            
            # Update user's recent reviews
            new_recent_review = {
                "id": new_review.id,
                "book": {
                    "id": book.id,
                    "title": book.title
                },
                "rating": new_review.rating,
                "created_at": new_review.created_at
            }
            
            # Initialize recent_reviews if it doesn't exist
            if user.recent_reviews is None:
                user.recent_reviews = []
            
            # Add new review to the beginning of recent_reviews
            user.recent_reviews.insert(0, new_recent_review)
            
            # Keep only the 5 most recent reviews
            if len(user.recent_reviews) > 5:
                user.recent_reviews = user.recent_reviews[:5]
            
            # Update book's average rating
            avg_rating_result = await self.db.execute(
                select(func.avg(Review.rating)).where(Review.book_id == book_id)
            )
            avg_rating = avg_rating_result.scalar() or 0.0
            
            if avg_rating:
                book.average_rating = round(avg_rating * 1.0, 1)
                
            await self.db.commit()
            
            # Get complete review with user information
            result = await self.db.execute(
                select(Review)
                .options(joinedload(Review.user))
                .where(Review.id == new_review.id)
            )
            inserted_review = result.scalars().first()
            
            return ReviewCreateResponse(
                id=inserted_review.id,
                book_id=inserted_review.book_id,
                user={
                    "id": inserted_review.user.id,
                    "username": inserted_review.user.username
                },
                rating=inserted_review.rating,
                title=inserted_review.title,
                content=inserted_review.content,
                created_at=inserted_review.created_at,
                updated_at=inserted_review.updated_at
            )
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid ID format")
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=500, detail=f"Error creating review: {str(e)}")

    async def retrieve_review(self, book_id: int, review_id: int) -> ReviewResponse:
        try:
            # Query review with joins to book and user
            result = await self.db.execute(
                select(Review)
                .options(joinedload(Review.user))
                .where(
                    and_(
                        Review.id == review_id,
                        Review.book_id == book_id
                    )
                )
            )
            review = result.scalars().first()
            
            if not review:
                raise HTTPException(status_code=404, detail="Review not found")
            
            # Prepare user info
            user_info = {
                "id": review.user.id,
                "username": review.user.username,
                "first_name": review.user.first_name or "",
                "last_name": review.user.last_name or ""
            } if review.user else {
                "id": review.user_id,
                "username": "Unknown user",
                "first_name": "",
                "last_name": ""
            }
            
            return ReviewResponse(
                id=review.id,
                book_id=review.book_id,
                user=user_info,
                rating=review.rating,
                title=review.title,
                content=review.content,
                created_at=review.created_at,
                updated_at=review.updated_at
            )
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid ID format")
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=500, detail=f"Error retrieving review: {str(e)}")

    async def update_review(self, book_id: int, review_id: int, user_id: int, review_update: ReviewUpdate) -> ReviewUpdateResponse:
        try:
            # Check if review exists and belongs to this book
            result = await self.db.execute(
                select(Review)
                .options(joinedload(Review.user))
                .where(
                    and_(
                        Review.id == review_id,
                        Review.book_id == book_id
                    )
                )
            )
            review = result.scalars().first()
            
            if not review:
                raise HTTPException(status_code=404, detail="Review not found")
            
            # Check if user is authorized to update this review
            if review.user_id != user_id:
                raise HTTPException(status_code=403, detail="Not authorized to update this review")
            
            # Get update data
            update_data = review_update.model_dump(exclude_unset=True)
            
            if not update_data:
                raise HTTPException(status_code=400, detail="No fields to update")
            
            # Update timestamp
            update_data["updated_at"] = datetime.now(timezone.utc)
            
            # Update review
            await self.db.execute(
                update(Review)
                .where(Review.id == review_id)
                .values(**update_data)
            )
            
            await self.db.commit()
            
            # Get updated review with book and user information
            updated_review_result = await self.db.execute(
                select(Review)
                .options(joinedload(Review.user), joinedload(Review.book))
                .where(Review.id == review_id)
            )
            updated_review = updated_review_result.scalars().first()
            
            if "rating" in update_data:
                # Recalculate book's average rating
                avg_rating_result = await self.db.execute(
                    select(func.avg(Review.rating)).where(Review.book_id == book_id)
                )
                avg_rating = avg_rating_result.scalar()
                
                if avg_rating:
                    book_result = await self.db.execute(select(Book).where(Book.id == book_id))
                    book = book_result.scalars().first()
                    
                    if book:
                        book.average_rating = avg_rating
                
                # Update user's recent reviews if this review is in the list
                user_result = await self.db.execute(select(User).where(User.id == user_id))
                user = user_result.scalars().first()
                
                if user and user.recent_reviews:
                    for i, recent_review in enumerate(user.recent_reviews):
                        if recent_review.get("id") == review_id:
                            user.recent_reviews[i]["rating"] = update_data["rating"]
                            break
                
                await self.db.commit()
            
            # Prepare user info for response
            user_info = {
                "id": updated_review.user.id,
                "username": updated_review.user.username
            } if updated_review.user else {
                "id": updated_review.user_id,
                "username": "Unknown user"
            }
            
            return ReviewUpdateResponse(
                id=updated_review.id,
                book_id=updated_review.book_id,
                user=user_info,
                rating=updated_review.rating,
                title=updated_review.title,
                content=updated_review.content,
                created_at=updated_review.created_at,
                updated_at=updated_review.updated_at
            )
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid ID format")
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=500, detail=f"Error updating review: {str(e)}")