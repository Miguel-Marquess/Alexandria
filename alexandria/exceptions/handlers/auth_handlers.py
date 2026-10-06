from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from jwt.exceptions import ExpiredSignatureError

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


@handler.exception_handler(ExpiredSignatureError)
async def expired_signature(req: Request, exc: ExpiredSignatureError) -> JSONResponse:
    return JSONResponse(
        status_code=401,
        content={'detail': 'Signature has expired.', 'code': 'SIGNATURE_EXPIRED'},
    )


auth_exceptions_handelers = {
    IncorrectEmailOrPassword: email_or_password_incorrect,
    ExpiredSignatureError: expired_signature,
}
