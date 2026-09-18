from datetime import datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jwt import decode, encode
from jwt.exceptions import DecodeError
from pwdlib import PasswordHash
from sqlalchemy import select

from alexandria.depends.database_dependencies import Session
from alexandria.exceptions.security_exceptions import InvalidCredentials
from alexandria.models.db_models import UserDatabase
from alexandria.settings import Settings

settings = Settings()
pwd_context = PasswordHash.recommended()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/v1/auth/login')


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(pure_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(pure_password, hashed_password)


def create_access_token(claims: dict) -> str:
    to_encode = claims.copy()

    expire = datetime.now(tz=ZoneInfo('UTC')) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES_TIME
    )

    to_encode.update({'exp': expire})

    encoded_token = encode(to_encode, settings.TOKEN_SECRET_KEY, settings.ALGORITHM)

    return encoded_token


async def get_current_user(
    session: Session, access_token: str = Depends(oauth2_scheme)
) -> UserDatabase:

    def decode_bearer_token(payload: str) -> dict[str, Any]:
        credentials = decode(payload, settings.TOKEN_SECRET_KEY, settings.ALGORITHM)
        if not credentials.get('sub') or not credentials.get('exp'):
            raise InvalidCredentials()
        return credentials

    try:
        payload_decoded = decode_bearer_token(access_token)
    except DecodeError:
        raise InvalidCredentials()

    user = await session.scalar(
        select(UserDatabase).where(UserDatabase.email == payload_decoded.get('sub'))
    )

    if not user:
        raise InvalidCredentials()

    return user
