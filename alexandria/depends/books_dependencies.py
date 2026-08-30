from typing import Annotated

from fastapi import Query

from alexandria.schemas.books_schemas import FilterBook

BookFilter = Annotated[FilterBook, Query()]
