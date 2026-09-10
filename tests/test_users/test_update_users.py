from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from alexandria.models.db_models import UserDatabase
from alexandria.schemas.users_schemas import UserPublic
from alexandria.security import verify_password


def test_update_user(client: TestClient, user: UserDatabase, token: str) -> None:
    response = client.patch(
        'users/me',
        headers={'Authorization': f'Bearer {token}'},
        json={'username': 'updated_name', 'email': 'updated_email@example.com'},
    )

    user_assert = UserPublic.model_validate(user).model_dump()

    # user e um obj mapeado pela session, ele atualiza automaticamente
    assert response.json() == user_assert
    assert response.status_code == HTTPStatus.OK


@pytest.mark.asyncio
async def test_update_user_password(
    client: TestClient, user: UserDatabase, session: AsyncSession, token: str
) -> None:
    password = 'updatedpassword'
    response = client.patch(
        '/users/me',
        json={'password': password},
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert verify_password(password, user.password) is True
    # user.password ja esta atualizada devido ao identity map do sa
