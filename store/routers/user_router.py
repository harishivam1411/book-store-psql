from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from store.database import get_database
from store.utils.dependencies import get_current_user
from store.models.auth_model import TokenPayload
from store.services.user_service import UserService
from store.models.user_model import UserCreate, UserUpdate, UserCreateResponse, UserUpdateResponse, UserResponse, UsersResponse

user_router = APIRouter(prefix='/users', tags=['Users'])

@user_router.get('/', response_model=list[UsersResponse])
async def retrieve_users(db: AsyncSession = Depends(get_database)):
    service = UserService(db)
    return await service.retrieve_users()

@user_router.post('/', response_model=UserCreateResponse)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_database)):
    service = UserService(db)
    return await service.create_user(user)

@user_router.get('/{user_id}', response_model=UserResponse)
async def retrieve_user(user_id: int, db: AsyncSession = Depends(get_database), current_user: TokenPayload = Depends(get_current_user)):
    if current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this user")
    service = UserService(db)
    return await service.retrieve_user(user_id)

@user_router.put('/{user_id}', response_model=UserUpdateResponse)
async def update_user(user_id: int, user: UserUpdate, db: AsyncSession = Depends(get_database), current_user: TokenPayload = Depends(get_current_user)):
    if current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this user")
    service = UserService(db)
    return await service.update_user(user_id, user)