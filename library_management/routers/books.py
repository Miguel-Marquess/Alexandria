from fastapi import APIRouter

from library_management.depends.books_dependencies import BookFilter
from library_management.depends.database_dependencies import Session
from library_management.depends.users_dependencies import Current_user
from library_management.schemas.books_schemas import (
    Book,
    BookList,
    BookPublic,
)
from library_management.schemas.core_schemas import Message
from library_management.services.books_service import BookService

router = APIRouter(tags=['library'], prefix='/books')


@router.post('/', status_code=201, response_model=BookPublic)
async def insert_books(book: Book, session: Session, current_user: Current_user):
    return await BookService(session).insert_book(book)


@router.get('/', status_code=200, response_model=BookList)
async def read_books(filter: BookFilter, current_user: Current_user, session: Session):
    return {'books': await BookService(session).read_books(filter)}


@router.delete('/{book_isbn}', status_code=200, response_model=Message)
async def delete_book(book_isbn: str, user: Current_user, session: Session):
    await BookService(session).delete_book(book_isbn)
    return {'message': 'Book was deleted.'}
