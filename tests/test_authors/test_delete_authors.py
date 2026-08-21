from http import HTTPStatus

import pytest
from sqlalchemy import select

from library_management.models.db_models import Author


def test_delete_author_who_contains_registered_books(client, token, book_db, author):
    response = client.delete(
        f'/authors/{author.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == (
        f'Author (ID [{author.id}]) has registered books. '
        'If you want continue, delete the authors books.'
    )


def test_delete_author_with_wrong_id(client, token):
    response = client.delete(
        '/authors/-1', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == 'Author (ID [-1]) not found.'


@pytest.mark.asyncio
async def test_delete_author(client, token, author, session):
    response = client.delete(
        f'/authors/{author.id}', headers={'Authorization': f'Bearer {token}'}
    )

    db_author = await session.scalar(select(Author).where(Author.id == author.id))

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Author was deleted.'}
    assert not db_author
