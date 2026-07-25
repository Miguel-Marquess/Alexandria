from contextlib import contextmanager
from datetime import datetime, timedelta

import factory
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from testcontainers.postgres import PostgresContainer

from library_management.app import app
from library_management.database import get_session
from library_management.models.db_models import (
    Author,
    BookDatabase,
    LoanDatabase,
    UserDatabase,
    registry_table,
)
from library_management.schemas.loans_schemas import LoanPublic, LoanStatus
from library_management.security import get_password_hash


@pytest.fixture
def client(session):
    async def get_session_override():
        yield session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client
    app.dependency_overrides.clear()


@pytest.fixture(scope='session')
def engine():
    with PostgresContainer('postgres:17', driver='psycopg') as postgres:
        yield create_async_engine(postgres.get_connection_url())


@pytest_asyncio.fixture
async def session(engine):
    async with engine.begin() as conn:
        await conn.run_sync(registry_table.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as ss:
        yield ss

    async with engine.begin() as conn:
        await conn.run_sync(registry_table.metadata.drop_all)


@pytest_asyncio.fixture
async def user(session):
    password = 'testpassword'

    user = UserFactory(password=get_password_hash(password))

    session.add(user)
    await session.commit()
    await session.refresh(user)

    user.clean_password = password
    # cria um atributo temporario no ORM
    return user


@pytest_asyncio.fixture
async def other_user(session):
    password = 'testpassword'

    user = UserFactory(password=get_password_hash(password))
    session.add(user)
    await session.commit()
    await session.refresh(user)

    user.clean_password = password

    return user


class UserFactory(factory.Factory):
    class Meta:
        model = UserDatabase

    username = factory.Sequence(lambda n: f'test{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    password = factory.LazyAttribute(lambda obj: f'{obj.username}password')


@contextmanager
def _mock_db_time(model, time=datetime(2026, 6, 11)):
    def fake_hook_time(mapper, connection, target):
        if hasattr(target, 'created_at'):
            target.created_at = time

        if hasattr(target, 'updated_at'):
            target.updated_at = time

    event.listen(model, 'before_insert', fake_hook_time)
    yield time
    event.remove(model, 'before_insert', fake_hook_time)


@pytest.fixture
def mock_db_time():
    return _mock_db_time


@pytest.fixture
def token(client, user):
    response = client.post(
        'auth/login', data={'username': user.email, 'password': user.clean_password}
    )

    return response.json()['access_token']


@pytest_asyncio.fixture
async def author(session):
    author = AuthorFactory()

    session.add(author)
    await session.commit()
    return author


class AuthorFactory(factory.Factory):
    class Meta:
        model = Author

    name = factory.faker.Faker('name')


@pytest_asyncio.fixture
async def book_db(author, session):
    book = BookFactory(author=author)
    session.add(book)
    await session.commit()
    await session.refresh(book)

    return book


def to_serialize(book):
    return {
        'title': book.title,
        'author_id': book.author.id,
        'isbn': book.isbn,
        'year': book.year,
        'publisher': book.publisher,
        'quantity': 5,
        'availables': 5,
        'id': book.id,
    }


@pytest.fixture
def book():
    book = BookFactory()
    return to_serialize(book)


@pytest_asyncio.fixture
async def many_books(author, session):
    books = BookFactory.create_batch(5, author=author)
    session.add_all(books)
    await session.commit()
    for book in books:
        await session.refresh(book)
    return [to_serialize(book) for book in books]


class BookFactory(factory.Factory):
    class Meta:
        model = BookDatabase

    title = factory.Sequence(lambda n: f'booktest{n}')
    author = factory.SubFactory(AuthorFactory)
    isbn = factory.Sequence(lambda n: f'isbn{n + 1 * 1234568890}')
    year = factory.Sequence(lambda n: n + 1 * 1111)
    publisher = factory.Sequence(lambda n: f'publishertest{n}')
    quantity = 5
    availables = 5


class LoanFactory(factory.Factory):
    class Meta:
        model = LoanDatabase

    user_id = factory.SelfAttribute('user.id')
    book_id = factory.SelfAttribute('book.id')

    due_date = factory.LazyFunction(lambda: datetime.now() + timedelta(days=15))
    returned_at = None
    status = LoanStatus.ACTIVE


@pytest_asyncio.fixture
async def loan(session, user, book_db):
    loan_database = LoanFactory(user_id=user.id, book_id=book_db.id)
    book_db.availables -= 1
    session.add_all([loan_database, book_db])
    await session.commit()
    await session.refresh(loan_database)

    return loan_database


@pytest_asyncio.fixture
async def three_loans(session, user):
    books = BookFactory.create_batch(3, availables=4)
    session.add_all(books)
    await session.commit()

    loans = [LoanFactory(user_id=user.id, book_id=book.id) for book in books]

    session.add_all(loans)
    await session.commit()
    for loan in loans:
        await session.refresh(loan)

    return loans


def serialize_author(author):
    return {'id': author.id, 'name': author.name}


@pytest_asyncio.fixture
async def many_authors(session):
    authors = AuthorFactory.create_batch(5)
    session.add_all(authors)
    await session.commit()

    return {
        'authors': [
            serialize_author(to_serialize_author) for to_serialize_author in authors
        ]
    }


@pytest.fixture
def three_loans_json(three_loans):
    return [
        LoanPublic.model_validate(loan).model_dump(mode='json') for loan in three_loans
    ]
