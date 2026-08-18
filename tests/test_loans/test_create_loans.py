from datetime import datetime
from http import HTTPStatus

import pytest
from sqlalchemy import select

from library_management.models.db_models import BookDatabase, LoanDatabase
from library_management.schemas.loans_schemas import LoanPublic, LoanStatus
from tests.conftest import BookFactory, LoanFactory


@pytest.mark.asyncio
async def test_create_loan(client, user, token, book_db, session):
    response = client.post(
        f'/loans/{book_db.isbn}',
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

    loan_public = LoanPublic.model_validate(loan)

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == loan_public.model_dump(mode='json')
    assert book_db.quantity > book_db.availables


def test_create_loan_has_already_loan(client, loan, token, book_db):
    response = client.post(
        f'/loans/{book_db.isbn}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == (
        f'You already a loan (ID [{loan.id}]) with this Book (ISBN [{book_db.isbn}]).'
    )


def test_create_loan_book_not_exist(client, token):
    response = client.post(
        f'/loans/{1}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == 'Book (ISBN [1]) not found. Verify.'


def test_create_loan_has_max_limit(client, token, book_db, three_loans):
    response = client.post(
        f'/loans/{book_db.isbn}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == 'User has reached the maximum number of active loans.'


@pytest.mark.asyncio
async def test_create_loan_book_not_availables(client, session, token, book_db):
    book_db.availables = 0
    session.add(book_db)
    await session.commit()

    response = client.post(
        f'/loans/{book_db.isbn}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == f'Book (ISBN [{book_db.isbn}]) is not available.'


@pytest.mark.asyncio
async def test_create_loan_user_have_late_loans_in_database(
    client, token, session, book_db, user
):
    book = BookFactory()
    loan = LoanFactory(
        due_date=datetime(2026, 6, 11), book_id=book_db.id, user_id=user.id
    )

    session.add_all([loan, book])
    await session.commit()
    await session.refresh(loan)

    response = client.post(
        f'/loans/{book.isbn}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == (
        f"You have late loans with ID's [{loan.id}]. Verify and try again."
    )
