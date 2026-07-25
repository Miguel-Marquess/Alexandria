from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, registry, relationship

from library_management.schemas.loans_schemas import LoanStatus

registry_table = registry()


@registry_table.mapped_as_dataclass
class UserDatabase:
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    username: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    password: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), init=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        init=False,
        onupdate=func.now(),
        server_default=func.now(),
    )
    loans: Mapped[list['LoanDatabase']] = relationship(
        back_populates='user', lazy='selectin', init=False
    )


@registry_table.mapped_as_dataclass
class BookDatabase:
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


@registry_table.mapped_as_dataclass
class LoanDatabase:
    __tablename__ = 'loan'

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    book_id: Mapped[str] = mapped_column(ForeignKey('books.id'))
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
        back_populates='loans', init=False, repr=False
    )
    book: Mapped['BookDatabase'] = relationship(
        back_populates='loans', init=False, repr=False
    )


@registry_table.mapped_as_dataclass
class Author:
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
