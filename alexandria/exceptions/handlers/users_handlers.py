from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from alexandria.exceptions.users_exceptions import EmailAlreadyExist

handler = FastAPI()


@handler.exception_handler(EmailAlreadyExist)
async def email_already_exists(req: Request, exc: EmailAlreadyExist) -> JSONResponse:
    return JSONResponse(
        status_code=409, content={'detail': 'This Email already exist.'}
    )


users_exc_handlers = {EmailAlreadyExist: email_already_exists}
