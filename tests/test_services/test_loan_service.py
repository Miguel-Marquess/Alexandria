import pytest
from pytest_mock import MockerFixture
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from alexandria.models.db_models import BookDatabase, LoanDatabase, UserDatabase
from alexandria.services.loans_service import LoanService


@pytest.mark.asyncio
async def test_create_loan_rollback(
    session: AsyncSession,
    user: UserDatabase,
    book_db: BookDatabase,
    mocker: MockerFixture,
) -> None:
    mocker.patch.object(session, 'commit', side_effect=Exception('Erro no commit'))

    book_isbn = book_db.isbn
    user_id = user.id

    with pytest.raises(Exception, match='Erro no commit'):
        await LoanService(session).create_loan(book_isbn, user)

    book = await session.scalar(
        select(BookDatabase).where(BookDatabase.isbn == book_isbn)
    )

    assert book is not None

    loan = await session.scalar(
        select(LoanDatabase).where(
            LoanDatabase.book_id == book_db.id, LoanDatabase.user_id == user_id
        )
    )

    assert book.availables == book_db.availables
    assert loan is None
