from dataclasses import asdict
from http import HTTPStatus

from alexandria.schemas.users_schemas import UserPublic
from tests.conftest import UserFactory


def test_create_user(client):
    user = UserFactory()
    response = client.post('/users', json=asdict(user))

    user.id = 1

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == UserPublic.model_validate(user).model_dump()
