from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from library_management.exceptions.authors_exceptions import AuthorNotFound

handler = FastAPI()


@handler.exception_handler(AuthorNotFound)
async def author_not_found_handler(req: Request, exc: AuthorNotFound):
    return JSONResponse(
        status_code=404, content=f'Author (ID [{exc.author_id}]) not found.'
    )


author_exc_handlers = {
    AuthorNotFound: author_not_found_handler,
}
