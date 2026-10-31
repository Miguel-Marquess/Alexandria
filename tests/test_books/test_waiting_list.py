from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import cast
from alexandria.models.db_models import (
    BookDatabase,
    LoanDatabase,
    Reserve,
    UserDatabase
)
from tests.conftest import UserFactory


@pytest.mark.asyncio
async def test_create_reservation(
    client: TestClient, book_db: BookDatabase, token: str, session: AsyncSession
) -> None:
    book_db.availables = 0

    session.add(book_db)
    await session.commit()

    response = client.post(
        f'/api/v1/books/queue/{book_db.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.CREATED


def test_already_reserved_book(
    client: TestClient, token: str, book_db: BookDatabase, reserve: Reserve
) -> None:
    response = client.post(
        f'/api/v1/books/queue/{book_db.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json()['detail'] == (
        'You have already reservation for this '
        'book or you have more than the maximum number of reservations.'
    )
    assert response.json()['code'] == 'MAX_RESERVATIONS'


def test_waiting_list_book_not_found(client: TestClient, token: str) -> None:
    response = client.post(
        '/api/v1/books/queue/-1', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()['detail'] == 'Book with ID -1 was not found.'
    assert response.json()['code'] == 'BOOK_NOT_FOUND'


def test_waiting_list_already_availables_books(
    client: TestClient, token: str, book_db: BookDatabase
) -> None:
    response = client.post(
        f'/api/v1/books/queue/{book_db.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json()['detail'] == (
        f'Book with ID {book_db.id} are already available. No reservation is needed.'
    )
    assert response.json()['code'] == 'BOOK_ALREADY_AVAILABLE'


@pytest.mark.asyncio
async def test_waiting_list_already_loan_with_book(
    client: TestClient,
    token: str,
    loan: LoanDatabase,
    book_db: BookDatabase,
    session: AsyncSession,
) -> None:
    book_db.availables = 0
    session.add(book_db)
    await session.commit()

    response = client.post(
        f'/api/v1/books/queue/{book_db.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json()['detail'] == (
        f'You already a loan with ID {loan.id} with a Book with ID {book_db.id}.'
    )
    assert response.json()['code'] == 'LOAN_ALREADY_WITH_BOOK'


@pytest.mark.asyncio
async def test_make_reserve_and_make_loan_when_return_it(
    client: TestClient,
    token: str,
    loan: LoanDatabase,
    reserve: Reserve,
    session: AsyncSession,
    book_db: BookDatabase,
) -> None:
    user = cast(UserDatabase, UserFactory())
    reserve.user = user
    objs = [user, reserve]
    session.add_all(objs)
    await session.commit()
    for obj in objs:
        await session.refresh(obj)

    response = client.patch(
        f'/api/v1/loans/{loan.id}/return', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()['status'] == 'returned'

    deleted_reserve = await session.scalar(
        select(Reserve).where(Reserve.id == reserve.id)
    )

    assert deleted_reserve is None

    loan_from_reserve = await session.scalar(
        select(LoanDatabase).where(LoanDatabase.user_id == user.id)
    )

    assert loan_from_reserve is not None
    assert loan_from_reserve.user_id == user.id
    assert loan_from_reserve.book_id == book_db.id
