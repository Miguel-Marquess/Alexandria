from pydantic import BaseModel, ConfigDict


class AuthorSchema(BaseModel):
    name: str | None = None


class AuthorPublic(AuthorSchema):
    id: int

    model_config = ConfigDict(from_attributes=True)


class AuthorsList(BaseModel):
    authors: list[AuthorPublic]


class AuthorFilter(AuthorSchema):
    order: bool | None = None
