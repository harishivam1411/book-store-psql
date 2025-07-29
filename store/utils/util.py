import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from jose import jwt
from fastapi import HTTPException, status
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from store.models.auth_model import TokenPayload, TokenResponse
from store.models.db_model import User

load_dotenv()
password_context = CryptContext(schemes=["argon2"], deprecated="auto")

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7
ALGORITHM = os.environ['ALGORITHM']
JWT_SECRET_KEY = os.environ['JWT_SECRET_KEY']
JWT_REFRESH_SECRET_KEY = os.environ['JWT_REFRESH_SECRET_KEY']

def get_hashed_password(password: str) -> str:
    """Hash a password using Argon2"""
    return password_context.hash(password)

def verify_hashed_password(password: str, hashed_pass: str) -> bool:
    """Verify a password against its hash"""
    return password_context.verify(password, hashed_pass)

def generate_tokens(user_id: int) -> TokenResponse:
    """Generate access and refresh tokens for a user"""
    # Convert to string as jwt requires JSON serializable values
    user_id_str = str(user_id)
    return TokenResponse(
        access_token = create_access_token({"user_id": user_id_str, "token_type": "access"}),
        refresh_token = create_refresh_token({"user_id": user_id_str, "token_type": "refresh"})
    )

def create_access_token(data: dict) -> str:
    """Create a JWT access token with expiration time"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict) -> str:
    """Create a JWT refresh token with longer expiration time"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_REFRESH_SECRET_KEY, algorithm=ALGORITHM)

def validate_token(token: str, token_type: str) -> TokenPayload:
    """Validate a JWT token and return the token data"""
    try:
        # Use the correct secret key based on token type
        key = JWT_REFRESH_SECRET_KEY if token_type == "refresh token" else JWT_SECRET_KEY
        payload = jwt.decode(token, key, algorithms=[ALGORITHM])
        token_data = TokenPayload(
            user_id=payload["user_id"],
            exp=datetime.fromtimestamp(payload["exp"], timezone.utc),
            token_type=payload["token_type"],
            valid=True
        )
        return token_data
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"{token_type} expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token, {token_type}")

async def get_user_by_username(db: AsyncSession, username: str) -> User:
    """Get a user by username using SQLAlchemy"""
    result = await db.execute(select(User).where(User.username == username))
    return result.scalars().first()

async def get_user_by_email(db: AsyncSession, email: str) -> User:
    """Get a user by email using SQLAlchemy"""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()

async def get_user_by_id(db: AsyncSession, user_id: int) -> User:
    """Get a user by ID using SQLAlchemy"""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalars().first()