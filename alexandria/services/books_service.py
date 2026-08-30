from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from alexandria.exceptions.authors_exceptions import AuthorNotFound
from alexandria.exceptions.books_exceptions import (
    BookIdOrIsbnNotFound,
    BookInCurrentLoan,
    BookNotFound,
)
from alexandria.models.db_models import Author, BookDatabase
from alexandria.schemas.books_schemas import Book, BookOrder, FilterBook


@dataclass
class BookService:
    session: AsyncSession

    async def insert_book(self, book_schema: Book) -> BookDatabase:
        author_db = await self.session.scalar(
            select(Author).where(Author.id == book_schema.author_id)
        )

        if not author_db:
            raise AuthorNotFound(book_schema.author_id)

        db_book = BookDatabase(
            **book_schema.model_dump(exclude={'author_id'}), author=author_db
        )

        self.session.add(db_book)
        await self.session.commit()
        await self.session.refresh(db_book)

        return db_book

    async def read_books(self, filter: FilterBook) -> list[BookDatabase] | list[None]:
        query = select(BookDatabase)
        if filter.isbn or filter.book_id:
            # abstracao necessaria? nao saberemos
            filters = [
                getattr(BookDatabase, key) == value
                for key, value in filter.model_dump(
                    include={'isbn', 'book_id'},
                    exclude_unset=True,
                ).items()
            ]

            book = await self.session.scalar(select(BookDatabase).where(*filters))

            if not book:
                raise BookIdOrIsbnNotFound()

            return [book]

        if filter.author_name:
            query = query.join(Author).where(Author.name.contains(filter.author_name))

        book_filters = {
            'title': lambda v: BookDatabase.title.contains(v),
            'author_id': lambda v: BookDatabase.author_id == v,
            'year': lambda v: BookDatabase.year == v,
            'publisher': lambda v: BookDatabase.publisher.contains(v),
        }

        for key, value in filter.model_dump(exclude_none=True).items():
            if key in book_filters:
                query = query.where(book_filters[key](value))

        order = {
            BookOrder.title: BookDatabase.title,
            BookOrder.year: BookDatabase.year,
            BookOrder.author_name: Author.name,
            BookOrder.publisher: BookDatabase.publisher,
            BookOrder.isbn: BookDatabase.isbn,
        }

        if filter.order_by:
            if filter.order_by == BookOrder.author_name and not filter.author_name:
                query = query.join(Author)
            query = query.order_by(order[filter.order_by])

        result = await self.session.scalars(
            query.offset(filter.start).limit(filter.ends)
        )

        return result

    async def delete_book(self, book_isbn: str) -> None:
        book = await self.session.scalar(
            select(BookDatabase).where(BookDatabase.isbn == book_isbn)
        )

        if not book:
            raise BookNotFound(book_isbn)

        if book.quantity != book.availables:
            raise BookInCurrentLoan(book.isbn)

        await self.session.delete(book)
