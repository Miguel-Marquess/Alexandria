from collections.abc import Callable
from contextlib import AbstractContextManager
from dataclasses import asdict
from datetime import datetime
from typing import cast

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from alexandria.models.db_models import BookDatabase, UserDatabase
from tests.conftest import BookFactory, UserFactory


@pytest.mark.asyncio
async def test_create_user_db(
    session: AsyncSession, mock_db_time: Callable[..., AbstractContextManager[datetime]]
) -> None:
    with mock_db_time(model=UserDatabase) as time:
        user = cast(UserDatabase, UserFactory())

        session.add(user)
        await session.commit()

        user_db = await session.scalar(
            select(UserDatabase).where(UserDatabase.id == user.id)
        )

        assert user_db is not None

    assert asdict(user_db) == {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'password': user.password,
        'created_at': time,
        'updated_at': time,
        'loans': [],
    }


@pytest.mark.asyncio
async def test_book(session: AsyncSession) -> None:
    book = BookFactory()
    session.add(book)
    await session.commit()
    obj = await session.scalar(select(BookDatabase))

    assert obj
