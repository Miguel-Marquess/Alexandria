from http import HTTPStatus

from fastapi.testclient import TestClient


def test_should_return_welcome(client: TestClient) -> None:
    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Welcome to my Library Management!'}
