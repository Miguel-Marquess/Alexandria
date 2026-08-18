from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from library_management.depends.books_dependencies import BookFilter
from library_management.depends.database_dependencies import Session
from library_management.depends.users_dependencies import Current_user
from library_management.models.db_models import Author
from library_management.schemas.books_schemas import (
    AuthorFilter,
    AuthorPublic,
    AuthorSchema,
    AuthorsList,
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


@router.get('/authors', response_model=AuthorsList, status_code=200)
async def read_authors(
    author_filter: Annotated[AuthorFilter, Query()],
    session: Session,
    user: Current_user,
):
    query = select(Author)
    author_name = author_filter.name

    if author_name:
        query = query.where(Author.name.contains(author_name))

    if author_filter.order:
        query = query.order_by(Author.name)

    authors = await session.scalars(query)

    return {'authors': authors}


@router.post('/author', status_code=201, response_model=AuthorPublic)
async def create_author(author: AuthorSchema, user: Current_user, session: Session):
    if not author.name:
        raise HTTPException(status_code=422, detail='Author name cannot be None.')

    author = Author(name=author.name)
    session.add(author)
    await session.commit()

    return author


@router.delete('/author/{author_id}', status_code=200, response_model=Message)
async def delete_author(author_id: int, user: Current_user, session: Session):
    author = await session.scalar(
        select(Author).options(selectinload(Author.books)).where(Author.id == author_id)
    )
    if not author:
        raise HTTPException(status_code=404, detail='Author not exist. Verify the ID.')

    if author.books:
        raise HTTPException(
            status_code=409,
            detail='Author has registered books. If you want continue, '
            'delete the authors books.',
        )

    await session.delete(author)

    return {'message': 'Author was deleted.'}
