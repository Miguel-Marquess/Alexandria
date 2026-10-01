from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from alexandria.exceptions.auth_exceptions import IncorrectEmailOrPassword

handler = FastAPI()


@handler.exception_handler(IncorrectEmailOrPassword)
async def email_or_password_incorrect(
    req: Request, exc: IncorrectEmailOrPassword
) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={
            'detail': 'Email or Password incorrect.',
            'code': 'INVALID_EMAIL_OR_PASSWORD',
        },
    )


auth_exceptions_handelers = {
    IncorrectEmailOrPassword: email_or_password_incorrect,
}
