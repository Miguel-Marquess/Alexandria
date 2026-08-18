from http import HTTPStatus

import pytest
from sqlalchemy import select

from library_management.models.db_models import Author, BookDatabase
from library_management.schemas.books_schemas import BookPublic


def get_list_books(*book_db):
    return {'books': [BookPublic.model_validate(book).model_dump() for book in book_db]}


def test_get_book_by_isbn(client, book_db, token):
    response = client.get(
        '/books',
        headers={'Authorization': f'Bearer {token}'},
        params={'isbn': book_db.isbn},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == get_list_books(book_db)


def test_invalid_isbn(client, token):
    response = client.get(
        '/books',
        headers={'Authorization': f'Bearer {token}'},
        params={'isbn': 'invalid'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == 'Book ID or ISBN not found.'


def test_get_book_by_title(client, book_db, token):
    response = client.get(
        '/books',
        headers={'Authorization': f'Bearer {token}'},
        params={'title': book_db.title[:4]},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == get_list_books(book_db)


def test_get_5_books_by_author_id(client, token, author, many_books):
    response = client.get(
        '/books',
        headers={'Authorization': f'Bearer {token}'},
        params={'author_id': author.id},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'books': many_books}


def test_get_books_whos_contains_a(client, token, many_books):
    response = client.get(
        '/books',
        headers={'Authorization': f'Bearer {token}'},
        params={'title': 'a'},
    )
    books = [book for book in many_books if 'a' in book['title']]

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'books': books}


def test_get_5_books(client, token, many_books):
    response = client.get('/books', headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'books': many_books}


@pytest.mark.asyncio
async def test_get_book_order_by_year(client, token, many_books, session):
    db_books = await session.scalars(select(BookDatabase).order_by(BookDatabase.year))
    response = client.get(
        '/books',
        headers={'Authorization': f'Bearer {token}'},
        params={'order_by': 'year'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'books': [
            BookPublic.model_validate(book).model_dump(mode='json') for book in db_books
        ]
    }


@pytest.mark.asyncio
async def test_get_book_order_by_author_name_without_name_author(
    client, token, many_books, session
):
    db_books = await session.scalars(
        select(BookDatabase).join(Author).order_by(Author.name)
    )
    response = client.get(
        '/books',
        headers={'Authorization': f'Bearer {token}'},
        params={'order_by': 'author_name'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'books': [
            BookPublic.model_validate(book).model_dump(mode='json') for book in db_books
        ]
    }


@pytest.mark.asyncio
async def test_get_book_order_by_title(client, token, many_books, session):
    db_books = await session.scalars(select(BookDatabase).order_by(BookDatabase.title))
    response = client.get(
        '/books',
        headers={'Authorization': f'Bearer {token}'},
        params={'order_by': 'year'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'books': [
            BookPublic.model_validate(book).model_dump(mode='json') for book in db_books
        ]
    }


def test_get_book_by_author_name(client, book_db, token):
    response = client.get(
        '/books',
        headers={'Authorization': f'Bearer {token}'},
        params={'author_name': book_db.author.name},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == get_list_books(book_db)
