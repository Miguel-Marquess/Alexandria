from dataclasses import asdict

import pytest
from sqlalchemy import select

from alexandria.models.db_models import BookDatabase, UserDatabase
from tests.conftest import BookFactory, UserFactory


@pytest.mark.asyncio
async def test_create_user_db(session, mock_db_time):
    with mock_db_time(model=UserDatabase) as time:
        user = UserFactory()

        session.add(user)
        await session.commit()

        user_db = await session.scalar(
            select(UserDatabase).where(UserDatabase.id == user.id)
        )

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
async def test_book(session):
    book = BookFactory()
    session.add(book)
    await session.commit()
    obj = await session.scalar(select(BookDatabase))

    assert obj
