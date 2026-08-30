from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from alexandria.exceptions.authors_exceptions import (
    AuthorHasRegisteredBooks,
    AuthorNone,
    AuthorNotFound,
)

handler = FastAPI()


@handler.exception_handler(AuthorNotFound)
async def author_not_found_handler(req: Request, exc: AuthorNotFound):
    return JSONResponse(
        status_code=404, content=f'Author (ID [{exc.author_id}]) not found.'
    )


@handler.exception_handler(AuthorNone)
async def author_cannot_none(req: Request, exc: AuthorNone):
    return JSONResponse(status_code=422, content='Author name cannot be None.')


@handler.exception_handler(AuthorHasRegisteredBooks)
async def author_has_registed_books(req: Request, exc: AuthorHasRegisteredBooks):
    return JSONResponse(
        status_code=409,
        content=f'Author (ID [{exc.author_id}]) has registered books. '
        'If you want continue, delete the authors books.',
    )


author_exc_handlers = {
    AuthorNotFound: author_not_found_handler,
    AuthorNone: author_cannot_none,
    AuthorHasRegisteredBooks: author_has_registed_books,
}
