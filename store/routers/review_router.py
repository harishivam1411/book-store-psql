from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from store.database import get_database
from store.utils.dependencies import get_current_user
from store.models.auth_model import TokenPayload
from store.services.review_service import ReviewService
from store.models.review_model import ReviewCreate, ReviewUpdate, ReviewCreateResponse, ReviewUpdateResponse, ReviewResponse, ReviewsResponse

review_router = APIRouter(prefix='/books/{book_id}/reviews', tags=['Reviews'])

@review_router.get('/', response_model=list[ReviewsResponse])
async def retrieve_reviews(book_id: int, db: AsyncSession = Depends(get_database)):
    service = ReviewService(db)
    return await service.retrieve_reviews(book_id)

@review_router.post('/', response_model=ReviewCreateResponse)
async def create_review(book_id: int, review: ReviewCreate, db: AsyncSession = Depends(get_database), current_user: TokenPayload = Depends(get_current_user)):
    service = ReviewService(db)
    return await service.create_review(book_id, current_user.user_id, review)

@review_router.get('/{review_id}', response_model=ReviewResponse)
async def retrieve_review(book_id: int, review_id: int, db: AsyncSession = Depends(get_database)):
    service = ReviewService(db)
    return await service.retrieve_review(book_id, review_id)

@review_router.put('/{review_id}', response_model=ReviewUpdateResponse)
async def update_review(book_id: int, review_id: int, review: ReviewUpdate, db: AsyncSession = Depends(get_database), current_user: TokenPayload = Depends(get_current_user)):
    service = ReviewService(db)
    return await service.update_review(book_id, review_id, current_user.user_id, review)