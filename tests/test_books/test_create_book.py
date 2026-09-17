from http import HTTPStatus
from typing import Any

from fastapi.testclient import TestClient

from alexandria.models.db_models import Author


def test_insert_book(
    client: TestClient, author: Author, token: str, book: dict[str, Any]
) -> None:
    book.update({'author_id': author.id})
    response = client.post(
        '/api/v1/books',
        headers={'Authorization': f'Bearer {token}'},
        json=book,
    )
    book.update({'id': 1})

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == book


def test_insert_book_author_not_found(
    client: TestClient, token: str, book: dict[str, Any]
) -> None:
    book.update({'author_id': 0})
    response = client.post(
        '/api/v1/books',
        headers={'Authorization': f'Bearer {token}'},
        json=book,
    )
    book.update({'id': 1})

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == 'Author (ID [0]) not found.'
