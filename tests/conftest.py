from collections.abc import Callable, Generator
from contextlib import AbstractContextManager, contextmanager
from datetime import datetime, timedelta
from typing import Any, AsyncGenerator, cast

import factory
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from testcontainers.postgres import PostgresContainer

from alexandria.app import app
from alexandria.database import get_session
from alexandria.models.db_models import (
    Author,
    BookDatabase,
    LoanDatabase,
    UserDatabase,
    registry_table,
)
from alexandria.schemas.authors_schemas import AuthorsList
from alexandria.schemas.books_schemas import BookList, BookPublic
from alexandria.schemas.loans_schemas import LoanList, LoanStatus
from alexandria.security import get_password_hash


@pytest.fixture
def client(session: AsyncSession) -> Generator[TestClient]:
    async def get_session_override() -> AsyncGenerator[AsyncSession]:
        yield session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client
    app.dependency_overrides.clear()


@pytest.fixture(scope='session')
# o escopo de session usa o mesmo valor para toda a bateria de testes
# sem o escopo, por padrao, usa o mesmo valor por teste, no proximo muda.
def engine() -> Generator[AsyncEngine]:
    with PostgresContainer('postgres:17', driver='psycopg') as postgres:
        yield create_async_engine(postgres.get_connection_url())


@pytest_asyncio.fixture
async def session(engine: AsyncEngine) -> AsyncGenerator[AsyncSession]:
    async with engine.begin() as conn:
        await conn.run_sync(registry_table.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as ss:
        yield ss

    async with engine.begin() as conn:
        await conn.run_sync(registry_table.metadata.drop_all)


@pytest.fixture
def clean_password() -> str:
    return 'testpassword'


@pytest_asyncio.fixture
async def user(session: AsyncSession, clean_password: str) -> UserDatabase:

    user = cast(UserDatabase, UserFactory(password=get_password_hash(clean_password)))

    session.add(user)
    await session.commit()
    await session.refresh(user)

    return user


class UserFactory(factory.Factory):
    class Meta:
        model = UserDatabase

    username = factory.Sequence(lambda n: f'test{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    password = factory.LazyAttribute(lambda obj: f'{obj.username}password')


@contextmanager
def _mock_db_time(
    model: Any, time: datetime = datetime(2026, 6, 11)
) -> Generator[datetime]:
    def fake_hook_time(mapper: Any, connection: AsyncSession, target: Any) -> None:
        if hasattr(target, 'created_at'):
            target.created_at = time

        if hasattr(target, 'updated_at'):
            target.updated_at = time

    event.listen(model, 'before_insert', fake_hook_time)
    yield time
    event.remove(model, 'before_insert', fake_hook_time)


@pytest.fixture
def mock_db_time() -> Callable[[Any], AbstractContextManager[datetime]]:
    return _mock_db_time


@pytest.fixture
def token(client: TestClient, user: UserDatabase, clean_password: str) -> Any:
    response = client.post(
        'auth/login', data={'username': user.email, 'password': clean_password}
    )

    payload = response.json()['access_token']

    return payload


@pytest_asyncio.fixture
async def author(session: AsyncSession) -> Author:
    author = cast(Author, AuthorFactory())

    session.add(author)
    await session.commit()
    return author


class AuthorFactory(factory.Factory):
    class Meta:
        model = Author

    name = factory.faker.Faker('name')


@pytest_asyncio.fixture
async def book_db(author: Author, session: AsyncSession) -> BookDatabase:
    book = cast(BookDatabase, BookFactory(author=author))
    session.add(book)
    await session.commit()
    await session.refresh(book)

    return book

def to_serialize(book: BookDatabase) -> dict[str, Any]:
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
def book(author: Author) -> dict[str, Any]:
    book = BookFactory()
    return to_serialize(book)


@pytest_asyncio.fixture
async def many_books(author: Author, session: AsyncSession) -> BookList:
    books = BookFactory.create_batch(5, author=author)
    session.add_all(books)
    await session.commit()
    for book in books:
        await session.refresh(book)
    return BookList(books=books)


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
async def loan(
    session: AsyncSession, user: UserDatabase, book_db: BookDatabase
) -> LoanDatabase:
    loan_database = cast(LoanDatabase, LoanFactory(user_id=user.id, book_id=book_db.id))
    book_db.availables -= 1
    session.add_all([loan_database, book_db])
    await session.commit()
    await session.refresh(loan_database)

    return loan_database


@pytest_asyncio.fixture
async def three_loans(session: AsyncSession, user: UserDatabase) -> LoanList:
    books = BookFactory.create_batch(3, availables=4)
    session.add_all(books)
    await session.commit()

    loans = [LoanFactory(user_id=user.id, book_id=book.id) for book in books]

    session.add_all(loans)
    await session.commit()
    for loan in loans:
        await session.refresh(loan)

    return LoanList(loans=loans)


@pytest_asyncio.fixture
async def many_authors(session: AsyncSession) -> AuthorsList:
    authors = AuthorFactory.create_batch(5)
    session.add_all(authors)
    await session.commit()

    return AuthorsList(authors=authors)
