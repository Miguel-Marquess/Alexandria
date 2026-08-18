from http import HTTPStatus

import pytest
from sqlalchemy import select

from library_management.models.db_models import Author, BookDatabase


@pytest.mark.asyncio
async def test_delete_author(client, token, author, session):
    response = client.delete(
        f'/books/author/{author.id}', headers={'Authorization': f'Bearer {token}'}
    )

    db_author = await session.scalar(select(Author).where(Author.id == author.id))

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Author was deleted.'}
    assert not db_author


def test_delete_author_with_wrong_id(client, token):
    response = client.delete(
        f'/books/author/{1}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Author not exist. Verify the ID.'}


def test_delete_author_who_contains_registered_books(client, token, book_db, author):
    response = client.delete(
        f'/books/author/{author.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {
        'detail': 'Author has registered books. '
        'If you want continue, delete the authors books.'
    }


@pytest.mark.asyncio
async def test_delete_book(client, token, session, book_db):
    response = client.delete(
        f'/books/{book_db.isbn}', headers={'Authorization': f'Bearer {token}'}
    )

    book = await session.scalar(
        select(BookDatabase).where(BookDatabase.id == book_db.id)
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Book was deleted.'}
    assert not book


def test_dont_delete_book_with_active_loan(client, token, book_db, loan):
    response = client.delete(
        f'/books/{book_db.isbn}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == (
        f'Book (ISBN [{book_db.isbn}]) is currently on loan. Cannot delete him.'
    )


def test_delete_book_not_found(client, token):
    response = client.delete('/books/-1', headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == 'Book (ISBN [-1]) not found. Verify.'
