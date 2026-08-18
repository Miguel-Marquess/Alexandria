from http import HTTPStatus


def test_insert_book(client, author, token, book):
    book.update({'author_id': author.id})
    response = client.post(
        '/books',
        headers={'Authorization': f'Bearer {token}'},
        json=book,
    )
    book.update({'id': 1})

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == book


def test_insert_book_author_not_found(client, token, book):
    book.update({'author_id': 0})
    response = client.post(
        '/books',
        headers={'Authorization': f'Bearer {token}'},
        json=book,
    )
    book.update({'id': 1})

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == 'Author (ID [0]) not found.'
