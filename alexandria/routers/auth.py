from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select

from alexandria.depends.database_dependencies import Session
from alexandria.exceptions.auth_exceptions import IncorrectEmailOrPassword
from alexandria.models.db_models import UserDatabase
from alexandria.schemas.auth_schemas import Token
from alexandria.security import create_access_token, verify_password

router = APIRouter(tags=['auth'], prefix='/auth')


@router.post('/login', response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Session,
) -> dict[str, str]:
    user = await session.scalar(
        select(UserDatabase).where(UserDatabase.email == form_data.username)
    )

    if not user or not verify_password(form_data.password, user.password):
        raise IncorrectEmailOrPassword()

    token = create_access_token({'sub': user.email})

    return {'access_token': token, 'token_type': 'Bearer'}
