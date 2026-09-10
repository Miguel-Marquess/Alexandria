from pydantic import BaseModel, ConfigDict


class AuthorSchema(BaseModel):
    name: str


class AuthorPublic(AuthorSchema):
    id: int

    model_config = ConfigDict(from_attributes=True)


class AuthorsList(BaseModel):
    authors: list[AuthorPublic]


class AuthorFilter(BaseModel):
    name: str | None = None
    order: bool | None = None
