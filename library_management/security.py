from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jwt import decode, encode
from jwt.exceptions import DecodeError
from pwdlib import PasswordHash
from sqlalchemy import select

from library_management.depends.database_dependencies import Session
from library_management.exceptions.security_exceptions import InvalidCredentials
from library_management.models.db_models import UserDatabase
from library_management.settings import Settings

settings = Settings()
pwd_context = PasswordHash.recommended()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/login')


def get_password_hash(password: str):
    return pwd_context.hash(password)


def verify_password(pure_password: str, hashed_password: str):
    return pwd_context.verify(pure_password, hashed_password)


def create_access_token(claims: dict):
    to_encode = claims.copy()

    expire = datetime.now(tz=ZoneInfo('UTC')) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES_TIME
    )

    to_encode.update({'exp': expire})

    encoded_token = encode(to_encode, settings.TOKEN_SECRET_KEY, settings.ALGORITHM)

    return encoded_token


async def get_current_user(
    session: Session, access_token: str = Depends(oauth2_scheme)
):

    def decode_bearer_token(jwt: dict):
        credentials = decode(jwt, settings.TOKEN_SECRET_KEY, settings.ALGORITHM)
        if not credentials.get('sub') or not credentials.get('exp'):
            raise InvalidCredentials()
        return credentials

    try:
        payload = decode_bearer_token(access_token)
    except DecodeError:
        raise InvalidCredentials()

    user = await session.scalar(
        select(UserDatabase).where(UserDatabase.email == payload.get('sub'))
    )

    if not user:
        raise InvalidCredentials()

    return user
