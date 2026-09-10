from http import HTTPStatus
from typing import Any, Sequence

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from alexandria.models.db_models import Author, BookDatabase
from alexandria.schemas.books_schemas import BookList, BookPublic


def book_list(books: Sequence[BookDatabase | BookPublic]) -> dict[str, str | Any]:
    return BookList(books=books).model_dump(mode='json')


def test_get_book_by_isbn(
    client: TestClient, book_db: BookDatabase, token: str
) -> None:
    response = client.get(
        '/books',
        headers={'Authorization': f'Bearer {token}'},
        params={'isbn': book_db.isbn},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == book_list([book_db])


def test_invalid_isbn(client: TestClient, token: str) -> None:
    response = client.get(
        '/books',
        headers={'Authorization': f'Bearer {token}'},
        params={'isbn': 'invalid'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == 'Book ID or ISBN not found.'


def test_get_book_by_title(
    client: TestClient, book_db: BookDatabase, token: str
) -> None:
    response = client.get(
        '/books',
        headers={'Authorization': f'Bearer {token}'},
        params={'title': book_db.title[:4]},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == book_list([book_db])


def test_get_5_books_by_author_id(
    client: TestClient, token: str, author: Author, many_books: BookList
) -> None:
    response = client.get(
        '/books',
        headers={'Authorization': f'Bearer {token}'},
        params={'author_id': author.id},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == many_books.model_dump(mode='json')


def test_get_books_whos_contains_a(
    client: TestClient, token: str, many_books: BookList
) -> None:
    response = client.get(
        '/books',
        headers={'Authorization': f'Bearer {token}'},
        params={'title': 'a'},
    )
    books = [
        book for book in many_books.books if book is not None and 'a' in book.title
    ]

    assert response.status_code == HTTPStatus.OK
    assert response.json() == book_list(books)


def test_get_5_books(client: TestClient, token: str, many_books: BookList) -> None:
    response = client.get('/books', headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == HTTPStatus.OK
    assert response.json() == many_books.model_dump(mode='json')


@pytest.mark.asyncio
async def test_get_book_order_by_year(
    client: TestClient, token: str, many_books: BookList, session: AsyncSession
) -> None:
    db_books = (
        await session.scalars(select(BookDatabase).order_by(BookDatabase.year))
    ).all()

    assert db_books is not None

    response = client.get(
        '/books',
        headers={'Authorization': f'Bearer {token}'},
        params={'order_by': 'year'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == book_list(db_books)


@pytest.mark.asyncio
async def test_get_book_order_by_author_name_without_name_author(
    client: TestClient, token: str, many_books: BookList, session: AsyncSession
) -> None:
    db_books = (
        await session.scalars(select(BookDatabase).join(Author).order_by(Author.name))
    ).all()

    assert db_books is not None

    response = client.get(
        '/books',
        headers={'Authorization': f'Bearer {token}'},
        params={'order_by': 'author_name'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == book_list(db_books)


@pytest.mark.asyncio
async def test_get_book_order_by_title(
    client: TestClient, token: str, many_books: BookList, session: AsyncSession
) -> None:
    db_books = (
        await session.scalars(select(BookDatabase).order_by(BookDatabase.title))
    ).all()

    assert db_books is not None

    response = client.get(
        '/books',
        headers={'Authorization': f'Bearer {token}'},
        params={'order_by': 'year'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == book_list(db_books)


def test_get_book_by_author_name(
    client: TestClient, book_db: BookDatabase, token: str
) -> None:
    response = client.get(
        '/books',
        headers={'Authorization': f'Bearer {token}'},
        params={'author_name': book_db.author.name},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == book_list([book_db])
