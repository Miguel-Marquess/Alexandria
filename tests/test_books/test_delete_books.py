from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from alexandria.models.db_models import BookDatabase, LoanDatabase


@pytest.mark.asyncio
async def test_delete_book(
    client: TestClient, token: str, session: AsyncSession, book_db: BookDatabase
) -> None:
    response = client.delete(
        f'/api/v1/books/{book_db.id}', headers={'Authorization': f'Bearer {token}'}
    )

    book = await session.scalar(
        select(BookDatabase).where(BookDatabase.id == book_db.id)
    )

    assert not book

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Book was deleted.'}


def test_dont_delete_book_with_active_loan(
    client: TestClient, token: str, book_db: BookDatabase, loan: LoanDatabase
) -> None:
    response = client.delete(
        f'/api/v1/books/{book_db.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json()['detail'] == (
        f'Book with ID {book_db.id} is currently on loan. Cannot delete him.'
    )
    assert response.json()['code'] == ('BOOK_IN_CURRENTLY_LOAN')


def test_delete_book_not_found(client: TestClient, token: str) -> None:
    response = client.delete(
        '/api/v1/books/-1', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()['detail'] == 'Book with ID -1 was not found.'
    assert response.json()['code'] == ('BOOK_NOT_FOUND')
