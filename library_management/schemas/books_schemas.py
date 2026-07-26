from enum import Enum

from pydantic import BaseModel, ConfigDict

from library_management.schemas.core_schemas import FilterPage


class Book(BaseModel):
    title: str
    author_id: int
    isbn: str
    year: int
    publisher: str
    quantity: int
    availables: int


class BookPublic(Book):
    id: int
    model_config = ConfigDict(from_attributes=True)


class BookList(BaseModel):
    books: list[BookPublic]


class AuthorSchema(BaseModel):
    name: str | None = None


class AuthorPublic(AuthorSchema):
    id: int

    model_config = ConfigDict(from_attributes=True)


class AuthorsList(BaseModel):
    authors: list[AuthorPublic]


class BookOrder(Enum):
    title = 'title'
    author_name = 'author_name'
    year = 'year'
    publisher = 'publisher'
    isbn = 'isbn'


class FilterBook(FilterPage):
    title: str | None = None
    author_id: int | None = None
    author_name: str | None = None
    year: int | None = None
    publisher: str | None = None
    isbn: str | None = None
    order_by: BookOrder | None = None


class AuthorFilter(AuthorSchema):
    order: bool | None = None
