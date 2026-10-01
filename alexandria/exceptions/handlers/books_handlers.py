from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from alexandria.exceptions.books_exceptions import (
    BookInCurrentLoan,
    BookNotAvailable,
    BookNotFound,
)

handler = FastAPI()


@handler.exception_handler(BookNotFound)
async def book_not_found_handler(req: Request, exc: BookNotFound) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={
            'detail': f'Book with ISBN {exc.book_isbn} was not found.',
            'code': 'BOOK_NOT_FOUND',
        },
    )


@handler.exception_handler(BookNotAvailable)
async def book_not_available_handler(
    req: Request, exc: BookNotAvailable
) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={
            'detail': f'Book with ISBN {exc.book_isbn} is not available.',
            'code': 'BOOK_NOT_AVAILABLE',
        },
    )


@handler.exception_handler(BookInCurrentLoan)
async def book_in_current_loan(req: Request, exc: BookInCurrentLoan) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={
            'detail': f'Book with ISBN {exc.book_isbn} '
            f'is currently on loan. Cannot delete him.',
            'code': 'BOOK_IN_CURRENTLY_LOAN',
        },
    )


book_exc_handlers = {
    BookNotFound: book_not_found_handler,
    BookNotAvailable: book_not_available_handler,
    BookInCurrentLoan: book_in_current_loan,
}
