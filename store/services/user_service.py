from fastapi import HTTPException
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, and_, or_
from sqlalchemy.orm import joinedload

from store.utils.util import get_hashed_password
from store.models.user_model import UserCreate, UserUpdate, UserCreateResponse, UserUpdateResponse, UserResponse, UsersResponse
from store.models.db_model import User, Review, Book

class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def retrieve_users(self) -> list[UsersResponse]:
        # Query all users
        result = await self.db.execute(select(User))
        users = result.scalars().all()
        
        return [UsersResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            created_at=user.created_at,
            updated_at=user.updated_at,
            review_count=user.review_count or 0
        ) for user in users]

    async def create_user(self, user_create: UserCreate) -> UserCreateResponse:
        # Check if username or email already exists
        result = await self.db.execute(
            select(User).where(
                or_(
                    User.username == user_create.username,
                    User.email == user_create.email
                )
            )
        )
        existing_user = result.scalars().first()
        
        if existing_user:
            if existing_user.username == user_create.username:
                raise HTTPException(status_code=400, detail="Username already exists")
            else:
                raise HTTPException(status_code=400, detail="Email already exists")
        
        # Hash the password
        user_dict = user_create.model_dump()
        user_dict["password"] = get_hashed_password(user_dict["password"])
        
        # Create new user
        new_user = User(
            username=user_dict["username"],
            email=user_dict["email"],
            password=user_dict["password"],
            first_name=user_dict["first_name"],
            last_name=user_dict["last_name"],
            review_count=0
        )
        
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        
        return await self.retrieve_user(new_user.id)

    async def retrieve_user(self, user_id: int) -> UserResponse:
        # Simplified error handling - no need to catch ValueError since user_id is already an int
        try:
            # Query user by ID with recent reviews
            result = await self.db.execute(
                select(User)
                .options(joinedload(User.reviews).joinedload(Review.book))
                .where(User.id == user_id)
            )
            user = result.scalars().first()
            
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            # Get recent reviews (limit to 5)
            recent_reviews = []
            if user.reviews:
                sorted_reviews = sorted(user.reviews, key=lambda x: x.created_at, reverse=True)[:5]
                for review in sorted_reviews:
                    recent_reviews.append({
                        "id": review.id,
                        "book": {
                            "id": review.book.id,
                            "title": review.book.title
                        },
                        "rating": review.rating,
                        "created_at": review.created_at
                    })
            
            return UserResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                created_at=user.created_at,
                updated_at=user.updated_at,
                review_count=user.review_count or 0,
                recent_reviews=recent_reviews
            )
            
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=500, detail=f"Error retrieving user: {str(e)}")

    async def update_user(self, user_id: int, user_update: UserUpdate) -> UserUpdateResponse:
        # Simplified error handling - no need to catch ValueError since user_id is already an int
        try:
            # Check if user exists
            result = await self.db.execute(select(User).where(User.id == user_id))
            user = result.scalars().first()
            
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            # Get update data
            update_data = user_update.model_dump(exclude_unset=True)
            
            # Check if username is being updated and if it already exists
            if "username" in update_data:
                result = await self.db.execute(
                    select(User).where(
                        and_(
                            User.username == update_data["username"],
                            User.id != user_id
                        )
                    )
                )
                if result.scalars().first():
                    raise HTTPException(status_code=400, detail="Username already exists")
            
            # Check if email is being updated and if it already exists
            if "email" in update_data:
                result = await self.db.execute(
                    select(User).where(
                        and_(
                            User.email == update_data["email"],
                            User.id != user_id
                        )
                    )
                )
                if result.scalars().first():
                    raise HTTPException(status_code=400, detail="Email already exists")
            
            # Update user
            update_data["updated_at"] = datetime.now(timezone.utc)
            
            await self.db.execute(
                update(User)
                .where(User.id == user_id)
                .values(**update_data)
            )
            
            await self.db.commit()
            
            # Return updated user
            return await self.retrieve_user(user_id)
            
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=500, detail=f"Error updating user: {str(e)}")