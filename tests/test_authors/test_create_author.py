from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from alexandria.models.db_models import Author


@pytest.mark.asyncio
async def test_create_author(
    client: TestClient, token: str, session: AsyncSession
) -> None:
    response = client.post(
        '/api/v1/authors',
        headers={'Authorization': f'Bearer {token}'},
        json={'name': 'testauthor'},
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json()['id']

    author = await session.scalar(
        select(Author).where(Author.id == response.json()['id'])
    )

    assert author is not None

    assert response.json()['name'] == author.name


def test_create_author_with_name_none(
    client: TestClient, token: str, session: AsyncSession
) -> None:
    response = client.post(
        '/api/v1/authors',
        headers={'Authorization': f'Bearer {token}'},
        json={'name': ''},
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.json() == 'Author name cannot be None.'
