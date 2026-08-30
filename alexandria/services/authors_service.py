from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from alexandria.depends.authors_dependencies import T_AuthorFilter
from alexandria.exceptions.authors_exceptions import (
    AuthorHasRegisteredBooks,
    AuthorNone,
    AuthorNotFound,
)
from alexandria.models.db_models import Author
from alexandria.schemas.authors_schemas import AuthorSchema


@dataclass
class AuthorService:
    session: AsyncSession

    async def read_authors(self, filter: T_AuthorFilter) -> list[Author]:
        query = select(Author)
        author_name = filter.name

        if author_name:
            query = query.where(Author.name.contains(author_name))

        if filter.order:
            query = query.order_by(Author.name)

        return await self.session.scalars(query)

    async def create_author(self, author_schema: AuthorSchema) -> Author:
        if not author_schema.name:
            raise AuthorNone()

        author = Author(name=author_schema.name)
        self.session.add(author)
        await self.session.commit()

        return author

    async def delete_author(self, author_id: int) -> None:
        author = await self.session.scalar(
            select(Author)
            .options(selectinload(Author.books))
            .where(Author.id == author_id)
        )
        if not author:
            raise AuthorNotFound(author_id)

        if author.books:
            raise AuthorHasRegisteredBooks(author.id)

        await self.session.delete(author)
