from library_management.exceptions.auth_exceptions import IncorrectEmailOrPassword
from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import JSONResponse

handler = FastAPI()


@handler.exception_handler(IncorrectEmailOrPassword)
async def email_or_password_incorrect(req: Request, exc: IncorrectEmailOrPassword):
    return JSONResponse(status_code=400, content='Email or Password incorrect.')


auth_exceptions_handelers = {
    IncorrectEmailOrPassword: email_or_password_incorrect,
}