from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from alexandria.exceptions.authors_exceptions import (
    AuthorHasRegisteredBooks,
    AuthorNone,
    AuthorNotFound,
)

handler = FastAPI()


@handler.exception_handler(AuthorNotFound)
async def author_not_found_handler(req: Request, exc: AuthorNotFound) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={
            'detail': f'Author with ID {exc.author_id} was not found.',
            'code': 'AUTHOR_NOT_FOUND',
        },
    )


@handler.exception_handler(AuthorNone)
async def author_cannot_none(req: Request, exc: AuthorNone) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={'detail': 'Author name cannot be None.', 'code': 'AUTHOR_NAME_NONE'},
    )


@handler.exception_handler(AuthorHasRegisteredBooks)
async def author_has_registed_books(
    req: Request, exc: AuthorHasRegisteredBooks
) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={
            'detail': f'Author with ID {exc.author_id} has registered books. '
            "If you want to continue, delete the author's books.",
            'code': 'AUTHOR_HAS_BOOKS',
        },
    )


author_exc_handlers = {
    AuthorNotFound: author_not_found_handler,
    AuthorNone: author_cannot_none,
    AuthorHasRegisteredBooks: author_has_registed_books,
}
