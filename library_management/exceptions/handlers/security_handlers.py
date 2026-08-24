from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from library_management.exceptions.security_exceptions import InvalidCredentials

handler = FastAPI()


@handler.exception_handler(InvalidCredentials)
async def invalid_credentials(req: Request, exc: InvalidCredentials):
    return JSONResponse(
        status_code=401,
        content='Credentials cannot be validateds.',
        headers={'WWW-Authenticate': 'Bearer'},
    )


security_exc_handlers = {
    InvalidCredentials: invalid_credentials,
}
