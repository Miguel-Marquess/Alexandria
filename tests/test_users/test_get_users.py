from http import HTTPStatus

from fastapi.testclient import TestClient

from alexandria.models.db_models import UserDatabase
from alexandria.schemas.users_schemas import UserPublic


def test_get_me(client: TestClient, token: str, user: UserDatabase) -> None:
    response = client.get('/users', headers={'Authorization': f'Bearer {token}'})

    assert response.json() == UserPublic.model_validate(user).model_dump()
    assert response.status_code == HTTPStatus.OK
