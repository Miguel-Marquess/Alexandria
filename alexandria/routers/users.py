from fastapi import APIRouter

from alexandria.depends.database_dependencies import Session
from alexandria.depends.users_dependencies import Current_user
from alexandria.schemas.core_schemas import Message
from alexandria.schemas.users_schemas import (
    UserPublic,
    UserSchema,
    UserUpdate,
)
from alexandria.services.users_services import UserService

router = APIRouter(tags=['users'], prefix='/api/v1/users')


@router.get('/', status_code=200, response_model=UserPublic)
def me(current_user: Current_user) -> UserPublic:
    user = UserPublic.model_validate(current_user)
    return user


@router.post('/', status_code=201, response_model=UserPublic)
async def create_user(user: UserSchema, session: Session) -> UserPublic:
    user_created = await UserService(session).create_user(user)
    return UserPublic.model_validate(user_created)


@router.delete('/me', status_code=200, response_model=Message)
async def delete_user(current_user: Current_user, session: Session) -> dict[str, str]:
    await UserService(session).delete_user(current_user)
    return {'message': 'User was deleted.'}


@router.patch('/me', status_code=200, response_model=UserPublic)
async def update_user(
    current_user: Current_user, user: UserUpdate, session: Session
) -> UserPublic:
    user_updated = await UserService(session).update_user(current_user, user)
    return UserPublic.model_validate(user_updated)
