from fastapi import APIRouter

from library_management.depends.database_dependencies import Session
from library_management.depends.users_dependencies import Current_user
from library_management.schemas.core_schemas import Message
from library_management.schemas.users_schemas import (
    UserPublic,
    UserSchema,
    UserUpdate,
)
from library_management.services.users_services import UserService

router = APIRouter(tags=['users'], prefix='/users')


@router.get('/', status_code=200, response_model=UserPublic)
def me(current_user: Current_user):
    return current_user


@router.post('/', status_code=201, response_model=UserPublic)
async def create_user(user: UserSchema, session: Session):
    return await UserService(session).create_user(user)


@router.delete('/me', status_code=200, response_model=Message)
async def delete_user(current_user: Current_user, session: Session):
    return await UserService(session).delete_user(current_user)


@router.patch('/me', status_code=200, response_model=UserPublic)
async def update_user(current_user: Current_user, user: UserUpdate, session: Session):
    return await UserService(session).update_user(current_user, user)
