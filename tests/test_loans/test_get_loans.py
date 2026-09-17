from datetime import datetime
from http import HTTPStatus
from typing import cast
from zoneinfo import ZoneInfo

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from alexandria.models.db_models import BookDatabase, LoanDatabase, UserDatabase
from alexandria.schemas.loans_schemas import LoanList, LoanStatus
from tests.conftest import LoanFactory


def test_my_loans(three_loans: LoanList, client: TestClient, token: str) -> None:
    response = client.get('/api/v1/loans', headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == HTTPStatus.OK
    assert response.json() == three_loans.model_dump(mode='json')


def test_get_loans_active(
    client: TestClient, three_loans: LoanList, token: str
) -> None:
    response = client.get(
        '/api/v1/loans',
        headers={'Authorization': f'Bearer {token}'},
        params={'status': 'active'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == three_loans.model_dump(mode='json')


@pytest.mark.asyncio
async def test_get_loans_returned(
    client: TestClient,
    token: str,
    session: AsyncSession,
    user: UserDatabase,
    book_db: BookDatabase,
) -> None:
    loan = cast(
        LoanDatabase,
        LoanFactory(
            status=LoanStatus.RETURNED,
            returned_at=datetime.now(tz=ZoneInfo('UTC')),
            user_id=user.id,
            book_id=book_db.id,
        ),
    )

    session.add(loan)
    await session.commit()

    response = client.get(
        '/api/v1/loans',
        headers={'Authorization': f'Bearer {token}'},
        params={'status': 'returned'},
    )

    assert response.json()['loans'][0]['status'] == 'returned'
    assert response.json() == LoanList(loans=[loan]).model_dump(mode='json')


@pytest.mark.asyncio
async def test_get_not_overdue_loan(
    client: TestClient,
    token: str,
    book_db: BookDatabase,
    user: UserDatabase,
    session: AsyncSession,
    loan: LoanDatabase,
) -> None:
    loan_database = cast(
        LoanDatabase,
        LoanFactory(
            due_date=datetime(2026, 6, 11, tzinfo=ZoneInfo('UTC')),
            book_id=book_db.id,
            user_id=user.id,
        ),
    )
    session.add(loan_database)
    await session.commit()

    response = client.get(
        '/api/v1/loans',
        headers={'Authorization': f'Bearer {token}'},
        params={'overdue': False},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == LoanList(loans=[loan]).model_dump(mode='json')


@pytest.mark.asyncio
async def test_get_true_overdue_loan(
    client: TestClient,
    token: str,
    book_db: BookDatabase,
    user: UserDatabase,
    session: AsyncSession,
    loan: LoanDatabase,
) -> None:
    loan_database = cast(
        LoanDatabase,
        LoanFactory(
            due_date=datetime(2026, 6, 11, tzinfo=ZoneInfo('UTC')),
            book_id=book_db.id,
            user_id=user.id,
        ),
    )
    session.add(loan_database)
    await session.commit()

    response = client.get(
        '/api/v1/loans',
        headers={'Authorization': f'Bearer {token}'},
        params={'overdue': True},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == LoanList(loans=[loan_database]).model_dump(mode='json')


@pytest.mark.asyncio
async def test_get_book_id_loan(
    client: TestClient,
    token: str,
    book_db: BookDatabase,
    user: UserDatabase,
    session: AsyncSession,
    loan: LoanDatabase,
) -> None:
    loan_database = cast(
        LoanDatabase,
        LoanFactory(
            book_id=book_db.id,
            user_id=user.id,
            status=LoanStatus.RETURNED,
            returned_at=datetime.now(tz=ZoneInfo('UTC')),
        ),
    )
    session.add(loan_database)
    await session.commit()

    response = client.get(
        '/api/v1/loans',
        headers={'Authorization': f'Bearer {token}'},
        params={'book_id': book_db.id},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == LoanList(loans=[loan, loan_database]).model_dump(
        mode='json'
    )
