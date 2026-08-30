from datetime import datetime
from http import HTTPStatus
from zoneinfo import ZoneInfo

import pytest

from alexandria.schemas.loans_schemas import LoanStatus


@pytest.mark.asyncio
async def test_return_loan(client, book_db, loan, session, token):
    before_return = datetime.now(tz=ZoneInfo('UTC'))
    response = client.patch(
        f'/loans/{loan.id}/return', headers={'Authorization': f'Bearer {token}'}
    )

    await session.refresh(book_db)

    returned_at = datetime.fromisoformat(response.json()['returned_at'])

    assert response.status_code == HTTPStatus.OK
    assert response.json()['status'] == LoanStatus.RETURNED.value
    assert returned_at >= before_return
    assert book_db.quantity == book_db.availables

    await session.refresh(loan)

    assert loan.status == LoanStatus.RETURNED
    assert loan.returned_at is not None


def test_return_not_existent_loan(client, token):
    response = client.patch(
        f'/loans/{-1}/return', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == 'Loan (ID [-1]) not found.'


def test_return_loan_already_returned(client, token, loan):
    response = client.patch(
        f'/loans/{loan.id}/return', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK

    response2 = client.patch(
        f'/loans/{loan.id}/return', headers={'Authorization': f'Bearer {token}'}
    )

    assert response2.status_code == HTTPStatus.CONFLICT
    assert response2.json() == f'Loan (ID [{loan.id}]) is already returned.'
