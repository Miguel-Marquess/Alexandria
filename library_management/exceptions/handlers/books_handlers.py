from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from library_management.exceptions.books_exceptions import (
    BookIdOrIsbnNotFound,
    BookInCurrentLoan,
    BookNotAvailable,
    BookNotFound,
)

handler = FastAPI()


@handler.exception_handler(BookNotFound)
async def book_not_found_handler(req: Request, exc: BookNotFound):
    return JSONResponse(
        status_code=404, content=f'Book (ISBN [{exc.book_isbn}]) not found. Verify.'
    )


@handler.exception_handler(BookIdOrIsbnNotFound)
async def book_id_or_isbn_not_found_handler(req: Request, exc: BookNotFound):
    return JSONResponse(status_code=404, content='Book ID or ISBN not found.')


@handler.exception_handler(BookNotAvailable)
async def book_not_available_handler(req: Request, exc: BookNotAvailable):
    return JSONResponse(
        status_code=409, content=f'Book (ISBN [{exc.book_isbn}]) is not available.'
    )


@handler.exception_handler(BookInCurrentLoan)
async def book_in_current_loan(req: Request, exc: BookInCurrentLoan):
    return JSONResponse(
        status_code=409,
        content=f'Book (ISBN [{exc.book_isbn}]) '
        f'is currently on loan. Cannot delete him.',
    )


book_exc_handlers = {
    BookNotFound: book_not_found_handler,
    BookNotAvailable: book_not_available_handler,
    BookIdOrIsbnNotFound: book_id_or_isbn_not_found_handler,
    BookInCurrentLoan: book_in_current_loan,
}
