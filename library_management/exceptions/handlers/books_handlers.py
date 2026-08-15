from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from library_management.exceptions.books_exceptions import (
    BookNotAvailable,
    BookNotFound,
)

handler = FastAPI()


@handler.exception_handler(BookNotFound)
async def book_not_found_handler(request: Request, exc: BookNotFound):
    return JSONResponse(
        status_code=404, content=f'Book with ISBN {exc.book_isbn} not found. Verify.'
    )


@handler.exception_handler(BookNotAvailable)
async def book_not_available_handler(req: Request, exc: BookNotAvailable):
    return JSONResponse(
        status_code=409, content=f'Book (ISBN [{exc.book_isbn}]) is not available.'
    )


book_exc_handlers = {
    BookNotFound: book_not_found_handler,
    BookNotAvailable: book_not_available_handler,
}
