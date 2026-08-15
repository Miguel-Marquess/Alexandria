from dataclasses import dataclass
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from library_management.exceptions.books_exceptions import (
    BookNotAvailable,
    BookNotFound,
)
from library_management.exceptions.loans_exceptions import (
    HasAlreadyLoanWithBook,
    LateLoans,
    LoanAlreadyReturned,
    LoanNotFound,
    MaxUserLoans,
)
from library_management.models.db_models import BookDatabase, LoanDatabase, UserDatabase
from library_management.schemas.loans_schemas import LoanPublic, LoanStatus
from library_management.settings import Settings

settings = Settings()


@dataclass
class LoanService:
    session: AsyncSession

    async def get_book(self, book_isbn):
        return await self.session.scalar(
            select(BookDatabase)
            .options(selectinload(BookDatabase.author))  # carrega o author tambem
            .where(BookDatabase.isbn == book_isbn)
        )

    async def create_loan(self, book_isbn: str, user: UserDatabase):
        late_loans = (
            await self.session.scalars(
                select(LoanDatabase).where(
                    LoanDatabase.user_id == user.id,
                    LoanDatabase.status == LoanStatus.ACTIVE,
                    LoanDatabase.due_date < datetime.now(tz=ZoneInfo('UTC')),
                )
            )
        ).all()

        if late_loans:
            raise LateLoans([loan.id for loan in late_loans])

        book = await self.get_book(book_isbn)

        active_loans = await self.session.scalar(
            select(func.count())
            .select_from(LoanDatabase)
            .where(
                LoanDatabase.user_id == user.id,
                LoanDatabase.status == LoanStatus.ACTIVE,
            )
        )

        has_already_loan = await self.session.scalar(
            select(LoanDatabase)
            .join(BookDatabase)
            .where(
                BookDatabase.isbn == book_isbn,
                LoanDatabase.user_id == user.id,
                LoanDatabase.status == LoanStatus.ACTIVE,
            )
        )

        if has_already_loan:
            raise HasAlreadyLoanWithBook(
                has_already_loan.id, has_already_loan.book.isbn
            )
        if not book:
            raise BookNotFound(book_isbn)
        if active_loans >= settings.MAX_VALUE_LOANS:
            raise MaxUserLoans()
        if book.availables <= 0:
            raise BookNotAvailable(book_isbn)

        book.availables -= 1
        loan = LoanDatabase(
            user_id=user.id,
            book_id=book.id,
            due_date=datetime.now(tz=ZoneInfo('UTC')) + timedelta(days=15),
        )

        self.session.add_all([book, loan])
        try:
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise
        await self.session.refresh(loan)

        return LoanPublic.model_validate(loan)

    async def return_loan(self, loan_id: int, user: UserDatabase):
        loan = await self.session.scalar(
            select(LoanDatabase).where(
                LoanDatabase.id == loan_id, LoanDatabase.user_id == user.id
            )
        )

        if not loan:
            raise LoanNotFound(loan_id)

        if loan.status == LoanStatus.RETURNED:
            raise LoanAlreadyReturned(loan.id)

        loan.returned_at = datetime.now(tz=ZoneInfo('UTC'))
        loan.status = LoanStatus.RETURNED

        book = await self.session.scalar(
            select(BookDatabase).where(BookDatabase.id == loan.book_id)
        )
        book.availables += 1

        self.session.add_all([loan, book])
        await self.session.commit()

        return LoanPublic.model_validate(loan)
