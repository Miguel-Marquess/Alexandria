from fastapi import FastAPI

from alexandria.exceptions.handlers import (
    auth_handlers,
    authors_handlers,
    books_handlers,
    loans_handlers,
    security_handlers,
)
from alexandria.routers import auth, authors, books, loans, users


def registry_routers(app: FastAPI, routers: list) -> None:
    for endpoint in routers:
        app.include_router(endpoint.router)


def registry_handlers(app: FastAPI, handlers: list) -> None:
    for handler in handlers:
        for exc, func in handler.items():
            app.add_exception_handler(exc, func)


app = FastAPI(title='Library System', version='0.1.0')

registry_routers(app, [auth, authors, books, loans, users])
registry_handlers(
    app,
    [
        auth_handlers.auth_exceptions_handelers,
        authors_handlers.author_exc_handlers,
        books_handlers.book_exc_handlers,
        loans_handlers.loans_exc_handlers,
        security_handlers.security_exc_handlers,
    ],
)


@app.get('/')
def welcome():
    return {'message': 'Welcome to my Library Management!'}
