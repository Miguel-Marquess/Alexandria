from http import HTTPStatus

from fastapi.testclient import TestClient


def test_delete_user(client: TestClient, token: str) -> None:
    response = client.delete(
        '/api/v1/users/me', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User was deleted.'}
