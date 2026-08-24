from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select

from library_management.database import get_session
from library_management.exceptions.auth_exceptions import IncorrectEmailOrPassword
from library_management.models.db_models import UserDatabase
from library_management.schemas.auth_schemas import Token
from library_management.security import create_access_token, verify_password

router = APIRouter(tags=['auth'], prefix='/auth')


@router.post('/login', response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session=Depends(get_session),
):
    user = await session.scalar(
        select(UserDatabase).where(UserDatabase.email == form_data.username)
    )

    if not user or not verify_password(form_data.password, user.password):
        raise IncorrectEmailOrPassword()

    token = create_access_token({'sub': user.email})

    return {'access_token': token, 'token_type': 'Bearer'}
