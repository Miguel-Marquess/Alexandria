from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from alexandria.exceptions.books_exceptions import (
    AlreadyAvailablesBooks,
    BookInCurrentLoan,
    BookNotAvailable,
    BookNotFound,
    MaxReservedBooksAchieved,
)

handler = FastAPI()


@handler.exception_handler(BookNotFound)
async def book_not_found_handler(req: Request, exc: BookNotFound) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={
            'detail': f'Book with ID {exc.book_id} was not found.',
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
            'detail': f'Book with ID {exc.book_id} is not available.',
            'code': 'BOOK_NOT_AVAILABLE',
        },
    )


@handler.exception_handler(AlreadyAvailablesBooks)
async def book_already_available(
    req: Request, exc: AlreadyAvailablesBooks
) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={
            'detail': f'Book with ID {exc.book_id} '
            f'are already available. No reservation is needed.',
            'code': 'BOOK_ALREADY_AVAILABLE',
        },
    )


@handler.exception_handler(BookInCurrentLoan)
async def book_in_current_loan(req: Request, exc: BookInCurrentLoan) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={
            'detail': f'Book with ID {exc.book_id} '
            f'is currently on loan. Cannot delete him.',
            'code': 'BOOK_IN_CURRENTLY_LOAN',
        },
    )


@handler.exception_handler(MaxReservedBooksAchieved)
async def max_reserved_books(
    req: Request, exc: MaxReservedBooksAchieved
) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={
            'detail': 'You have already reservation for this book'
            ' or you have more than the maximum number of reservations.',
            'code': 'MAX_RESERVATIONS',
        },
    )


book_exc_handlers = {
    BookNotFound: book_not_found_handler,
    BookNotAvailable: book_not_available_handler,
    BookInCurrentLoan: book_in_current_loan,
    AlreadyAvailablesBooks: book_already_available,
    MaxReservedBooksAchieved: max_reserved_books,
}
