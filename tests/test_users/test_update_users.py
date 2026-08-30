from http import HTTPStatus

import pytest
from sqlalchemy import select

from alexandria.models.db_models import UserDatabase
from alexandria.schemas.users_schemas import UserPublic
from alexandria.security import verify_password


def test_update_user(client, user, token):
    response = client.patch(
        'users/me',
        headers={'Authorization': f'Bearer {token}'},
        json={'username': 'updated_name', 'email': 'updated_email@example.com'},
    )

    user_assert = UserPublic.model_validate(user).model_dump()

    # user e um obj mapeado pela session, ele atualiza automaticamente
    assert response.json() == user_assert


@pytest.mark.asyncio
async def test_update_user_password(client, user, session, token):
    password = 'updatedpassword'
    response = client.patch(
        '/users/me',
        json={'password': password},
        headers={'Authorization': f'Bearer {token}'},
    )

    user_password = await session.scalar(
        select(UserDatabase).where(UserDatabase.id == user.id)
    )

    assert response.status_code == HTTPStatus.OK
    assert verify_password(password, user_password.password) is True
