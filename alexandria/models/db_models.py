from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, func
from sqlalchemy.orm import (
    Mapped,
    mapped_as_dataclass,
    mapped_column,
    registry,
    relationship,
)

from alexandria.models.mixins import AuditorMixin, TimeStampMixin
from alexandria.schemas.loans_schemas import LoanStatus

registry_table = registry()


@mapped_as_dataclass(registry_table)
class UserDatabase(TimeStampMixin):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    username: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    password: Mapped[str] = mapped_column(nullable=False)
    loans: Mapped[list['LoanDatabase']] = relationship(
        back_populates='user',
        lazy='selectin',
        init=False,
        foreign_keys='LoanDatabase.user_id',
    )


@mapped_as_dataclass(registry_table)
class BookDatabase(AuditorMixin):
    __tablename__ = 'books'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey('authors.id'), init=False)
    author: Mapped['Author'] = relationship(back_populates='books', repr=False)
    isbn: Mapped[str] = mapped_column(nullable=False, unique=True)
    year: Mapped[int]
    publisher: Mapped[str] = mapped_column(nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False)
    availables: Mapped[int] = mapped_column(nullable=False)
    loans: Mapped[list['LoanDatabase']] = relationship(
        back_populates='book', lazy='selectin', init=False
    )


@mapped_as_dataclass(registry_table)
class LoanDatabase(AuditorMixin):
    __tablename__ = 'loan'

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    book_id: Mapped[int] = mapped_column(ForeignKey('books.id'))
    loan_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), init=False, server_default=func.now()
    )
    due_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    returned_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )
    status: Mapped[LoanStatus] = mapped_column(
        Enum(LoanStatus), default=LoanStatus.ACTIVE
    )
    user: Mapped['UserDatabase'] = relationship(
        back_populates='loans', init=False, repr=False, foreign_keys=[user_id]
    )
    book: Mapped['BookDatabase'] = relationship(
        back_populates='loans', init=False, repr=False, lazy='selectin'
    )


@mapped_as_dataclass(registry_table)
class Author(AuditorMixin):
    __tablename__ = 'authors'

    id: Mapped[int] = mapped_column(nullable=False, primary_key=True, init=False)
    name: Mapped[str] = mapped_column(nullable=False)
    books: Mapped[list['BookDatabase']] = relationship(
        # Author -> N books --> One-to-Many
        init=False,
        lazy='selectin',
        back_populates='author',
        repr=False,
    )
