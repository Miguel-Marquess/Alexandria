from fastapi import FastAPI
from fastapi.responses import JSONResponse, Response

from library_management.exceptions.loans_exceptions import (
    HasAlreadyLoanWithBook,
    LateLoans,
    LoanNotFound,
    MaxUserLoans,
    LoanAlreadyReturned
)

handler = FastAPI()


@handler.exception_handler(LateLoans)
async def late_loans_handler(res: Response, exc: LateLoans):
    return JSONResponse(
        status_code=409,
        content=(
            f"You have late loans with ID's {exc.loans_id}. Verify and try again."
        ),
    )


@handler.exception_handler(HasAlreadyLoanWithBook)
async def has_already_loan_with_book_handler(
    res: Response, exc: HasAlreadyLoanWithBook
):
    return JSONResponse(
        status_code=409,
        content=(
            f'You already a loan (ID [{exc.loan_id}]) '
            f'with this Book (ISBN [{exc.book_isbn}]).'
        ),
    )


@handler.exception_handler(MaxUserLoans)
async def max_user_loans_handler(res: Response, exc: MaxUserLoans):
    return JSONResponse(
        status_code=409, content='User has reached the maximum number of active loans.'
    )


@handler.exception_handler(LoanNotFound)
async def loan_not_found_handler(res: Response, exc: LoanNotFound):
    return JSONResponse(
        status_code=404, content=f'Loan (ID [{exc.loan_id}]) not found.'
    )

@handler.exception_handler(LoanAlreadyReturned)
async def loan_has_already_returned_handler(
    res: Response, exc: LoanAlreadyReturned
):
    return JSONResponse(
        status_code=409,
        content=f'Loan (ID [{exc.loan_id}]) is already returned.'
    )

loans_exc_handlers = {
    LateLoans: late_loans_handler,
    HasAlreadyLoanWithBook: has_already_loan_with_book_handler,
    MaxUserLoans: max_user_loans_handler,
    LoanNotFound: loan_not_found_handler,
    LoanAlreadyReturned: loan_has_already_returned_handler
}
