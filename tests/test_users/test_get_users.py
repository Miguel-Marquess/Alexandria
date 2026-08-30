from alexandria.schemas.users_schemas import UserPublic


def test_get_me(client, token, user):
    response = client.get('/users', headers={'Authorization': f'Bearer {token}'})

    assert response.json() == UserPublic.model_validate(user).model_dump()
