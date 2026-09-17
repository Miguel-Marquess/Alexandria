from http import HTTPStatus
from typing import Any, Sequence

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from alexandria.models.db_models import Author
from alexandria.schemas.authors_schemas import AuthorPublic, AuthorsList


def authors_list(authors: Sequence[Author | AuthorPublic]) -> dict[str, str | Any]:
    return AuthorsList(authors=authors).model_dump(mode='json')


# get_auhtors
def test_get_all_authors(
    client: TestClient, many_authors: AuthorsList, token: str
) -> None:

    response = client.get(
        '/api/v1/authors',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == many_authors.model_dump(mode='json')


def test_get_all_authors_with_name_contains_c(
    client: TestClient, many_authors: AuthorsList, token: str
) -> None:
    authors = [author for author in many_authors.authors if 'c' in author.name]
    response = client.get(
        '/api/v1/authors',
        headers={'Authorization': f'Bearer {token}'},
        params={'name': 'c'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == authors_list(authors=authors)


@pytest.mark.asyncio
async def test_get_all_authors_order(
    session: AsyncSession, client: TestClient, many_authors: AuthorsList, token: str
) -> None:
    authors = (await session.scalars(select(Author).order_by(Author.name))).all()
    response = client.get(
        '/api/v1/authors',
        headers={'Authorization': f'Bearer {token}'},
        params={'order': True},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == authors_list(authors=authors)
