from pydantic import BaseModel, Field


class Message(BaseModel):
    message: str


class FilterPage(BaseModel):
    offset: int = Field(ge=0, default=0)
    limit: int = Field(ge=0, default=10)
