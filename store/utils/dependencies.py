from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from store.database import get_database
from store.models.auth_model import TokenPayload
from store.utils.util import validate_token
from store.models.db_model import User

oauth2_bearer = HTTPBearer()

def validate_access_token(credentials: HTTPAuthorizationCredentials = Depends(oauth2_bearer)) -> TokenPayload:
    """Validate access token from Authorization header"""
    if not credentials or not credentials.credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Access token is required")
    try:
        token_data = validate_token(credentials.credentials, "access token")
        if token_data.token_type != 'access':
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Only access tokens can be used for authentication")
        return token_data

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Access token has expired")

    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token")

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


def validate_refresh_token(credentials: HTTPAuthorizationCredentials = Depends(oauth2_bearer)) -> TokenPayload:
    """Validate refresh token from Authorization header"""
    if not credentials or not credentials.credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token is required")
    try:
        token_data = validate_token(credentials.credentials, "refresh token")
        if token_data.token_type != 'refresh':
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Only refresh tokens can be used for renewing access tokens")
        return token_data

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token has expired")

    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

async def get_current_user(token_data: TokenPayload = Depends(validate_access_token), 
                          db: AsyncSession = Depends(get_database)) -> TokenPayload:
    """Get the current authenticated user from the token"""
    if not token_data.valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify user exists in database
    result = await db.execute(select(User).where(User.id == int(token_data.user_id)))
    user = result.scalars().first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    return token_data