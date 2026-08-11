from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from library_management.depends.books_dependencies import BookFilter
from library_management.depends.database_dependencies import Session
from library_management.depends.users_dependencies import Current_user
from library_management.models.db_models import Author, BookDatabase
from library_management.schemas.books_schemas import (
    AuthorFilter,
    AuthorPublic,
    AuthorSchema,
    AuthorsList,
    Book,
    BookList,
    BookOrder,
    BookPublic,
)
from library_management.schemas.core_schemas import Message

router = APIRouter(tags=['library'], prefix='/books')


@router.post('/', status_code=201, response_model=BookPublic)
async def insert_books(book: Book, session: Session, current_user: Current_user):

    author_orm = await session.scalar(select(Author).where(Author.id == book.author_id))

    if not author_orm:
        raise HTTPException(
            status_code=404, detail=f'Author with id {book.author_id} not exist.'
        )

    db_book = BookDatabase(**book.model_dump(exclude='author_id'), author=author_orm)

    session.add(db_book)
    await session.commit()
    await session.refresh(db_book)
    return db_book


@router.get('/', status_code=200, response_model=BookList)
async def read_books(filter: BookFilter, current_user: Current_user, session: Session):
    query = select(BookDatabase)
    if filter.isbn or filter.book_id:
        if filter.isbn:
            book = await session.scalar(
                select(BookDatabase).where(BookDatabase.isbn == filter.isbn)
            )

            if not book:
                raise HTTPException(status_code=404, detail='ISBN is not valid.')

        if filter.book_id:
            book = await session.scalar(
                select(BookDatabase).where(BookDatabase.id == filter.book_id)
            )

            if not book:
                raise HTTPException(status_code=404, detail='This Book ID not exist.')

        return {'books': [book]}

    if filter.author_name:
        query = query.join(Author).where(Author.name.contains(filter.author_name))

    book_filters = {
        'title': lambda v: BookDatabase.title.contains(v),
        'author_id': lambda v: BookDatabase.author_id == v,
        'year': lambda v: BookDatabase.year == v,
        'publisher': lambda v: BookDatabase.publisher.contains(v),
    }

    for key, value in filter.model_dump(exclude_none=True).items():
        if key in book_filters:
            query = query.where(book_filters[key](value))

    order = {
        BookOrder.title: BookDatabase.title,
        BookOrder.year: BookDatabase.year,
        BookOrder.author_name: Author.name,
        BookOrder.publisher: BookDatabase.publisher,
        BookOrder.isbn: BookDatabase.isbn,
    }

    if filter.order_by:
        if filter.order_by == BookOrder.author_name and not filter.author_name:
            query = query.join(Author)
        query = query.order_by(order[filter.order_by])

    result = await session.scalars(query.offset(filter.start).limit(filter.ends))

    return {'books': result}


@router.delete('/{book_isbn}', status_code=200, response_model=Message)
async def delete_book(book_isbn: str, user: Current_user, session: Session):
    book = await session.scalar(
        select(BookDatabase).where(BookDatabase.isbn == book_isbn)
    )

    if book:
        if book.quantity != book.availables:
            raise HTTPException(
                status_code=409, detail='Book is currently on loan. Cannot delete him.'
            )

    if not book:
        raise HTTPException(status_code=404, detail='Book not exist. Verify the ISBN')

    await session.delete(book)

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
