from http import HTTPStatus

from fastapi.testclient import TestClient
from jwt import decode

from alexandria.models.db_models import UserDatabase
from alexandria.security import create_access_token
from alexandria.settings import Settings
from tests.conftest import UserFactory

settings = Settings()


def test_token_access(
    client: TestClient, clean_password: str, user: UserDatabase
) -> None:
    response = client.post(
        '/api/v1/auth/login', data={'username': user.email, 'password': clean_password}
    )

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in response.json()

    payload = decode(
        response.json()['access_token'], settings.TOKEN_SECRET_KEY, settings.ALGORITHM
    )

    assert payload.get('sub') == (user.email)

    assert response.json()['token_type'] == 'Bearer'


def test_token_with_wrong_password(client: TestClient, user: UserDatabase) -> None:
    response = client.post(
        '/api/v1/auth/login', data={'username': user.email, 'password': 'wrongpassword'}
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json()['detail'] == 'Email or Password incorrect.'
    assert response.json()['code'] == 'INVALID_EMAIL_OR_PASSWORD'


def test_token_with_wrong_email(
    client: TestClient, clean_password: str, user: UserDatabase
) -> None:
    response = client.post(
        '/api/v1/auth/login',
        data={'username': 'wrongemail', 'password': clean_password},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json()['detail'] == 'Email or Password incorrect.'
    assert response.json()['code'] == 'INVALID_EMAIL_OR_PASSWORD'


def test_token_with_invalid_token(client: TestClient) -> None:
    response = client.delete(
        '/api/v1/users/me', headers={'Authorization': 'Bearer invalid-token'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json()['detail'] == 'Credentials cannot be validateds.'
    assert response.json()['code'] == 'INVALID_CREDENTIALS'


def test_token_without_sub(client: TestClient) -> None:
    invalid_token = create_access_token({})

    response = client.delete(
        '/api/v1/users/me', headers={'Authorization': f'Bearer {invalid_token}'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json()['detail'] == 'Credentials cannot be validateds.'
    assert response.json()['code'] == 'INVALID_CREDENTIALS'


def test_invalid_user(client: TestClient) -> None:
    user = UserFactory()

    token = create_access_token({'sub': user.email})

    response = client.delete(
        '/api/v1/users/me', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json()['detail'] == 'Credentials cannot be validateds.'
    assert response.json()['code'] == 'INVALID_CREDENTIALS'
