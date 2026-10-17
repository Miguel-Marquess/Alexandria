from pydantic import BaseModel, ConfigDict

from alexandria.schemas.core_schemas import FilterPage


class AuthorSchema(BaseModel):
    name: str


class AuthorPublic(AuthorSchema):
    id: int

    model_config = ConfigDict(from_attributes=True)


class AuthorsList(BaseModel):
    authors: list[AuthorPublic]


class AuthorFilter(FilterPage):
    name: str | None = None
    order: bool | None = None
