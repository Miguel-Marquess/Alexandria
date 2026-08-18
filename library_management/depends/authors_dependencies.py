from typing import Annotated

from fastapi import Query

from library_management.schemas.authors_schemas import AuthorFilter

T_AuthorFilter = Annotated[AuthorFilter, Query()]
