from datetime import datetime
from http import HTTPStatus
from typing import cast

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from alexandria.models.db_models import BookDatabase, LoanDatabase, UserDatabase
from alexandria.schemas.loans_schemas import LoanList, LoanPublic, LoanStatus
from tests.conftest import BookFactory, LoanFactory


@pytest.mark.asyncio
async def test_create_loan(
    client: TestClient,
    user: UserDatabase,
    token: str,
    book_db: BookDatabase,
    session: AsyncSession,
) -> None:
    response = client.post(
        f'/api/v1/loans/{book_db.isbn}',
        headers={'Authorization': f'Bearer {token}'},
    )

    loan = await session.scalar(
        select(LoanDatabase)
        .join(BookDatabase)
        .where(
            BookDatabase.isbn == book_db.isbn,
            LoanDatabase.user_id == user.id,
            LoanDatabase.status == LoanStatus.ACTIVE,
        )
    )

    assert loan is not None

    loan_public = LoanPublic.model_validate(loan)

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == loan_public.model_dump(mode='json')
    assert book_db.quantity > book_db.availables


def test_create_loan_has_already_loan(
    client: TestClient, loan: LoanDatabase, token: str, book_db: BookDatabase
) -> None:
    response = client.post(
        f'/api/v1/loans/{book_db.isbn}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json()['detail'] == (
        f'You already a loan with ID {loan.id} with a Book with ISBN {book_db.isbn}.'
    )
    assert response.json()['code'] == ('LOAN_ALREADY_WITH_BOOK')


def test_create_loan_book_not_exist(client: TestClient, token: str) -> None:
    response = client.post(
        '/api/v1/loans/1',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()['detail'] == 'Book with ISBN 1 was not found.'
    assert response.json()['code'] == ('BOOK_NOT_FOUND')


def test_create_loan_has_max_limit(
    client: TestClient, token: str, book_db: BookDatabase, three_loans: LoanList
) -> None:
    response = client.post(
        f'/api/v1/loans/{book_db.isbn}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json()['detail'] == (
        'User has reached the maximum number of active loans.'
    )
    assert response.json()['code'] == ('MAXIMUM_LOANS')


@pytest.mark.asyncio
async def test_create_loan_book_not_availables(
    client: TestClient, session: AsyncSession, token: str, book_db: BookDatabase
) -> None:
    book_db.availables = 0
    session.add(book_db)
    await session.commit()

    response = client.post(
        f'/api/v1/loans/{book_db.isbn}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json()['detail'] == (
        f'Book with ISBN {book_db.isbn} is not available.'
    )
    assert response.json()['code'] == ('BOOK_NOT_AVAILABLE')


@pytest.mark.asyncio
async def test_create_loan_user_have_late_loans_in_database(
    client: TestClient,
    token: str,
    session: AsyncSession,
    book_db: BookDatabase,
    user: UserDatabase,
) -> None:
    book = BookFactory()
    loan = cast(
        LoanDatabase,
        LoanFactory(
            due_date=datetime(2026, 6, 11), book_id=book_db.id, user_id=user.id
        ),
    )

    session.add_all([loan, book])

    await session.commit()
    await session.refresh(loan)

    response = client.post(
        f'/api/v1/loans/{book.isbn}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json()['detail'] == (
        f"You have late loans with ID's [{loan.id}]. Verify and try again."
    )
    assert response.json()['code'] == ('LATE_LOAN')
