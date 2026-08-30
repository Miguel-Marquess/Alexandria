from http import HTTPStatus

import pytest
from sqlalchemy import select

from alexandria.models.db_models import Author


@pytest.mark.asyncio
async def test_create_author(client, token, session):
    response = client.post(
        '/authors',
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
        '/authors', headers={'Authorization': f'Bearer {token}'}, json={'name': ''}
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.json() == 'Author name cannot be None.'
