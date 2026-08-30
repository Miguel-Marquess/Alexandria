import pytest
from sqlalchemy import select

from alexandria.models.db_models import BookDatabase, LoanDatabase
from alexandria.services.loans_service import LoanService


@pytest.mark.asyncio
async def test_create_loan_rollback(session, user, book_db, mocker):
    mocker.patch.object(session, 'commit', side_effect=Exception('Erro no commit'))

    book_isbn = book_db.isbn
    user_id = user.id

    with pytest.raises(Exception, match='Erro no commit'):
        await LoanService(session).create_loan(book_isbn, user)

    book = await session.scalar(
        select(BookDatabase).where(BookDatabase.isbn == book_isbn)
    )

    loan = await session.scalar(
        select(LoanDatabase).where(
            LoanDatabase.book_id == book_db.id, LoanDatabase.user_id == user_id
        )
    )

    assert book.availables == book_db.availables
    assert loan is None
