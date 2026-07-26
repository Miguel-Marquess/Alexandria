from datetime import datetime
from http import HTTPStatus
from zoneinfo import ZoneInfo

import pytest

from library_management.schemas.loans_schemas import LoanPublic, LoanStatus
from tests.conftest import LoanFactory


def test_my_loans(three_loans_json, client, token):
    response = client.get('/loans', headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'loans': three_loans_json}



def test_get_loans_active(client, three_loans_json, token):
    response = client.get(
        '/loans',
        headers={'Authorization': f'Bearer {token}'},
        params={'status': 'active'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'loans': three_loans_json}


@pytest.mark.asyncio
async def test_get_loans_returned(client, token, session, user, book_db):
    loan = LoanFactory(
        status=LoanStatus.RETURNED,
        returned_at=datetime.now(tz=ZoneInfo('UTC')),
        user_id=user.id,
        book_id=book_db.id,
    )

    session.add(loan)
    await session.commit()

    response = client.get(
        '/loans',
        headers={'Authorization': f'Bearer {token}'},
        params={'status': 'returned'},
    )

    assert response.json()['loans'][0]['status'] == 'returned'
    assert response.json() == ({
        'loans': [LoanPublic.model_validate(loan).model_dump(mode='json')]
    })


@pytest.mark.asyncio
async def test_get_not_overdue_loan(client, token, book_db, user, session, loan):
    loan_database = LoanFactory(
        due_date=datetime(2026, 6, 11, tzinfo=ZoneInfo('UTC')),
        book_id=book_db.id,
        user_id=user.id,
    )
    session.add(loan_database)
    await session.commit()

    response = client.get(
        '/loans',
        headers={'Authorization': f'Bearer {token}'},
        params={'overdue': False},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'loans': [LoanPublic.model_validate(loan).model_dump(mode='json')]
    }


@pytest.mark.asyncio
async def test_get_true_overdue_loan(client, token, book_db, user, session, loan):
    loan_database = LoanFactory(
        due_date=datetime(2026, 6, 11, tzinfo=ZoneInfo('UTC')),
        book_id=book_db.id,
        user_id=user.id,
    )
    session.add(loan_database)
    await session.commit()

    response = client.get(
        '/loans',
        headers={'Authorization': f'Bearer {token}'},
        params={'overdue': True},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'loans': [LoanPublic.model_validate(loan_database).model_dump(mode='json')]
    }


@pytest.mark.asyncio
async def test_get_book_id_loan(client, token, book_db, user, session, loan):
    loan_database = LoanFactory(
        book_id=book_db.id,
        user_id=user.id,
        status=LoanStatus.RETURNED,
        returned_at=datetime.now(tz=ZoneInfo('UTC')),
    )
    session.add(loan_database)
    await session.commit()

    response = client.get(
        '/loans',
        headers={'Authorization': f'Bearer {token}'},
        params={'book_id': book_db.id},
    )

    loans = [loan, loan_database]

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'loans': [
            LoanPublic.model_validate(loan).model_dump(mode='json') for loan in loans
        ]
    }
