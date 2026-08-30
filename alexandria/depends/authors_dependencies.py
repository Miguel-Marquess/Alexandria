from typing import Annotated

from fastapi import Query

from alexandria.schemas.authors_schemas import AuthorFilter

T_AuthorFilter = Annotated[AuthorFilter, Query()]
