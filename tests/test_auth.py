from http import HTTPStatus

from jwt import decode

from library_management.security import create_access_token
from library_management.settings import Settings
from tests.conftest import UserFactory

settings = Settings()


def test_token_access(client, user):
    response = client.post(
        '/auth/login', data={'username': user.email, 'password': user.clean_password}
    )

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in response.json()

    payload = decode(
        response.json()['access_token'], settings.TOKEN_SECRET_KEY, settings.ALGORITHM
    )

    assert payload.get('sub') == (user.email)

    assert response.json()['token_type'] == 'Bearer'


def test_token_with_wrong_password(client, user):
    response = client.post(
        '/auth/login', data={'username': user.email, 'password': 'wrongpassword'}
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == 'Email or Password incorrect.'


def test_token_with_wrong_email(client, user):
    response = client.post(
        '/auth/login', data={'username': 'wrongemail', 'password': user.clean_password}
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == 'Email or Password incorrect.'


def test_token_with_invalid_token(client):
    response = client.delete(
        '/users/me', headers={'Authorization': 'Bearer invalid-token'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Credentials cannot be validateds.'}


def test_token_without_sub(client):
    invalid_token = create_access_token({})

    response = client.delete(
        '/users/me', headers={'Authorization': f'Bearer {invalid_token}'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Credentials cannot be validateds.'}


def test_invalid_user(client):
    user = UserFactory()

    token = create_access_token({'sub': user.email})

    response = client.delete('/users/me', headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Credentials cannot be validateds.'}
