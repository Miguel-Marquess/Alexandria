from http import HTTPStatus

import pytest
from sqlalchemy import select

from library_management.models.db_models import Author
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
    assert response.json() == {'detail': 'ISBN is not valid.'}


def test_get_book_by_author_name(client, book_db, token):
    response = client.get(
        '/books',
        headers={'Authorization': f'Bearer {token}'},
        params={'author_name': book_db.author.name},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == get_list_books(book_db)


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


# get_auhtors
def test_get_all_authors(client, many_authors, token):
    response = client.get(
        '/books/authors',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == many_authors


def test_get_all_authors_with_name_contains_c(client, many_authors, token):
    authors = [author for author in many_authors['authors'] if 'c' in author['name']]
    response = client.get(
        '/books/authors',
        headers={'Authorization': f'Bearer {token}'},
        params={'name': 'c'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'authors': authors}


@pytest.mark.asyncio
async def test_create_author(client, token, session):
    response = client.post(
        '/books/author',
        headers={'Authorization': f'Bearer {token}'},
        json={'name': 'testauthor'},
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json()['id']

    author = await session.scalar(
        select(Author).where(Author.id == response.json()['id'])
    )

    assert response.json()['name'] == author.name


def test_create_author_with_name_none(client, token, session):
    response = client.post(
        '/books/author', headers={'Authorization': f'Bearer {token}'}, json={'name': ''}
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.json() == {'detail': 'Author name cannot be None.'}

def test_get_book_order_by(client, token, many_books):
    response = client.get(
        '/books',
        headers={'Authorization': f'Bearer {token}'},
        params={'order_by': 'year'},
    )

    assert response
