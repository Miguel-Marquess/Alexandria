from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from alexandria.models.db_models import Author, BookDatabase


def test_delete_author_who_contains_registered_books(
    client: TestClient, token: str, book_db: BookDatabase, author: Author
) -> None:
    response = client.delete(
        f'/api/v1/authors/{author.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json()['detail'] == (
        f'Author with ID {author.id} has registered books. '
        "If you want to continue, delete the author's books."
    )
    assert response.json()['code'] == 'AUTHOR_HAS_BOOKS'


def test_delete_author_with_wrong_id(client: TestClient, token: str) -> None:
    response = client.delete(
        '/api/v1/authors/-1', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()['detail'] == 'Author with ID -1 was not found.'
    assert response.json()['code'] == 'AUTHOR_NOT_FOUND'


@pytest.mark.asyncio
async def test_delete_author(
    client: TestClient, token: str, author: Author, session: AsyncSession
) -> None:

    response = client.delete(
        f'/api/v1/authors/{author.id}', headers={'Authorization': f'Bearer {token}'}
    )

    db_author = await session.scalar(select(Author).where(Author.id == author.id))

    assert not db_author

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Author was deleted.'}
