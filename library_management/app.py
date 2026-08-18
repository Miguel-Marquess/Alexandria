from fastapi import FastAPI

from library_management.exceptions.handlers import (
    authors_handlers,
    books_handlers,
    loans_handlers,
)
from library_management.routers import auth, authors, books, loans, users

app = FastAPI(title='Library System', version='0.1.0')
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(books.router)
app.include_router(loans.router)
app.include_router(authors.router)

for exc, func_handler in books_handlers.book_exc_handlers.items():
    app.add_exception_handler(exc, func_handler)

for exc, func_handler in loans_handlers.loans_exc_handlers.items():
    app.add_exception_handler(exc, func_handler)

for exc, func_handler in authors_handlers.author_exc_handlers.items():
    app.add_exception_handler(exc, func_handler)


@app.get('/')
def welcome():
    return {'message': 'Welcome to my Library Management!'}
