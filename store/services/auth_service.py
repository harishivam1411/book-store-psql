from datetime import datetime, timezone
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from store.models.db_model import User
from store.models.user_model import UserCreate
from store.models.auth_model import PasswordReset, TokenResponse, UserLogin
from store.utils.util import get_hashed_password, verify_hashed_password, generate_tokens

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def login_user(self, user_credentials: UserLogin) -> TokenResponse:
        """Authenticate user and generate tokens"""
        username = user_credentials.username.lower()
        
        # Query user by username
        result = await self.db.execute(select(User).where(User.username == username))
        user = result.scalars().first()
        
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        if not verify_hashed_password(user_credentials.password, user.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        
        user_id = str(user.id)
        return generate_tokens(user_id)

    async def refresh_tokens(self, user_id: int) -> TokenResponse:
        """Generate new tokens using refresh token"""
        # Query user by ID
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        return generate_tokens(user_id)

    async def register_user(self, user_data: UserCreate) -> TokenResponse:
        """Register a new user and return tokens"""
        # Check if username or email already exists
        result = await self.db.execute(
            select(User).where(
                (User.username == user_data.username.lower()) | 
                (User.email == user_data.email.lower())
            )
        )
        existing_user = result.scalars().first()
        
        if existing_user:
            if existing_user.username == user_data.username.lower():
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")
            else:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
        
        # Create new user
        hashed_password = get_hashed_password(user_data.password)
        
        new_user = User(
            username=user_data.username.lower(),
            email=user_data.email.lower(),
            password=hashed_password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            review_count=0,
            recent_reviews=[]
        )
        
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        
        user_id = str(new_user.id)
        return generate_tokens(user_id)

    async def reset_password(self, user_id: int, password_data: PasswordReset) -> JSONResponse:
        """Reset user password"""
        # Query user by ID
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        # If old password is provided, verify it
        if password_data.old_password:
            if not verify_hashed_password(password_data.old_password, user.password):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")
        
        # Update password
        hashed_password = get_hashed_password(password_data.new_password)
        
        user.password = hashed_password
        user.updated_at = datetime.now(timezone.utc)
        
        await self.db.commit()
        
        return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Password updated successfully"})