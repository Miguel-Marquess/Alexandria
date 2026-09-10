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
        f'/authors/{author.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == (
        f'Author (ID [{author.id}]) has registered books. '
        'If you want continue, delete the authors books.'
    )


def test_delete_author_with_wrong_id(client: TestClient, token: str) -> None:
    response = client.delete(
        '/authors/-1', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == 'Author (ID [-1]) not found.'


@pytest.mark.asyncio
async def test_delete_author(
    client: TestClient, token: str, author: Author, session: AsyncSession
) -> None:

    response = client.delete(
        f'/authors/{author.id}', headers={'Authorization': f'Bearer {token}'}
    )

    db_author = await session.scalar(select(Author).where(Author.id == author.id))

    assert not db_author

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Author was deleted.'}
