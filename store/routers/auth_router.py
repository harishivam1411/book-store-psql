from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from store.database import get_database
# from store.utils.dependencies import validate_access_token, validate_refresh_token
from store.models.user_model import UserCreate
from store.models.auth_model import TokenResponse, TokenPayload, PasswordReset, UserLogin
from store.services.auth_service import AuthService

auth_router = APIRouter(prefix='/auth', tags=['Auth'])

@auth_router.post(
    "/token/",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate user and get tokens",
    description="Authenticates a user and returns access and refresh tokens"
)
async def login(
    user_credentials: UserLogin, db: AsyncSession = Depends(get_database)):
    service = AuthService(db)
    return await service.login_user(user_credentials)

# @auth_router.post(
#     "/refresh/",
#     response_model=TokenResponse,
#     status_code=status.HTTP_200_OK,
#     summary="Refresh tokens",
#     description="Use a refresh token to get a new access token"
# )
# async def refresh_tokens(
#     token_data: TokenPayload = Depends(validate_refresh_token), db: AsyncSession = Depends(get_database)):
#     service = AuthService(db)
#     return await service.refresh_tokens(token_data.user_id)

@auth_router.post(
    "/register/",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Register a new user and return access and refresh tokens"
)
async def register_user(
    user_data: UserCreate, db: AsyncSession = Depends(get_database) ):
    service = AuthService(db)
    return await service.register_user(user_data)

# @auth_router.put(
#     "/reset-password/",
#     status_code=status.HTTP_200_OK,
#     summary="Reset password",
#     description="Reset user password"
# )
# async def reset_password(
#     password_data: PasswordReset,
#     token_data: TokenPayload = Depends(validate_access_token), db: AsyncSession = Depends(get_database)):
#     service = AuthService(db)
#     return await service.reset_password(token_data.user_id, password_data)