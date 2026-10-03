from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from alexandria.exceptions.loans_exceptions import (
    HasAlreadyLoanWithBook,
    LateLoans,
    LoanAlreadyReturned,
    LoanNotFound,
    MaxUserLoans,
)

handler = FastAPI()


@handler.exception_handler(LateLoans)
async def late_loans_handler(res: Request, exc: LateLoans) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content=({
            'detail': f"You have late loans with ID's "
            f'{exc.loans_id}. Verify and try again.',
            'code': 'LATE_LOAN',
        }),
    )


@handler.exception_handler(HasAlreadyLoanWithBook)
async def has_already_loan_with_book_handler(
    res: Request, exc: HasAlreadyLoanWithBook
) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content=({
            'detail': f'You already a loan with ID {exc.loan_id} '
            f'with a Book with ID {exc.book_id}.',
            'code': 'LOAN_ALREADY_WITH_BOOK',
        }),
    )


@handler.exception_handler(MaxUserLoans)
async def max_user_loans_handler(res: Request, exc: MaxUserLoans) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={
            'detail': 'User has reached the maximum number of active loans.',
            'code': 'MAXIMUM_LOANS',
        },
    )


@handler.exception_handler(LoanNotFound)
async def loan_not_found_handler(res: Request, exc: LoanNotFound) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={
            'detail': f'Loan with ID {exc.loan_id} was not found.',
            'code': 'LOAN_NOT_FOUND',
        },
    )


@handler.exception_handler(LoanAlreadyReturned)
async def loan_has_already_returned_handler(
    res: Request, exc: LoanAlreadyReturned
) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={
            'detail': f'Loan with ID {exc.loan_id} is already returned.',
            'code': 'LOAN_ALREADY_RETURNED',
        },
    )


loans_exc_handlers = {
    LateLoans: late_loans_handler,
    HasAlreadyLoanWithBook: has_already_loan_with_book_handler,
    MaxUserLoans: max_user_loans_handler,
    LoanNotFound: loan_not_found_handler,
    LoanAlreadyReturned: loan_has_already_returned_handler,
}
