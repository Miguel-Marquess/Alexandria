from http import HTTPStatus

import pytest
from sqlalchemy import select

from library_management.models.db_models import Author
from library_management.schemas.authors_schemas import AuthorPublic


# get_auhtors
def test_get_all_authors(client, many_authors, token):
    response = client.get(
        '/authors',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == many_authors


def test_get_all_authors_with_name_contains_c(client, many_authors, token):
    authors = [author for author in many_authors['authors'] if 'c' in author['name']]
    response = client.get(
        '/authors',
        headers={'Authorization': f'Bearer {token}'},
        params={'name': 'c'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'authors': authors}


@pytest.mark.asyncio
async def test_get_all_authors_order(session, client, many_authors, token):
    authors = await session.scalars(select(Author).order_by(Author.name))
    response = client.get(
        '/authors',
        headers={'Authorization': f'Bearer {token}'},
        params={'order': True},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'authors': [
            AuthorPublic.model_validate(author).model_dump(mode='json')
            for author in authors
        ]
    }
