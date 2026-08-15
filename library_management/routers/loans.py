from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import APIRouter
from sqlalchemy import select

from library_management.depends.database_dependencies import Session
from library_management.depends.loans_dependencies import FilterLoan
from library_management.depends.users_dependencies import Current_user
from library_management.models.db_models import LoanDatabase
from library_management.schemas.loans_schemas import LoanList, LoanPublic
from library_management.services.loans_service import LoanService

router = APIRouter(tags=['Loans'], prefix='/loans')


@router.post('/{book_isbn}', status_code=201, response_model=LoanPublic)
async def make_loan(book_isbn: str, user: Current_user, session: Session):
    return await LoanService(session).create_loan(book_isbn=book_isbn, user=user)


@router.patch('/{loan_id}/return', status_code=200, response_model=LoanPublic)
async def devolution(loan_id: int, user: Current_user, session: Session):
    return await LoanService(session).return_loan(loan_id, user)


@router.get('/', status_code=200, response_model=LoanList)
async def my_loans(user: Current_user, session: Session, filter: FilterLoan):
    query = select(LoanDatabase).where(LoanDatabase.user_id == user.id)
    # colocar verificacao se o usuario e admin ou nao, se sim,
    # podera puxar todos os loans

    if filter.status:
        query = query.where(LoanDatabase.status == filter.status)

    if filter.book_id:
        query = query.where(LoanDatabase.book_id == filter.book_id)

    if filter.overdue:
        query = query.where(LoanDatabase.due_date < datetime.now(tz=ZoneInfo('UTC')))
    if filter.overdue is False:
        query = query.where(LoanDatabase.due_date > datetime.now(tz=ZoneInfo('UTC')))

    loans = await session.scalars(query.offset(filter.start).limit(filter.ends))

    return {'loans': loans}
