from pydantic import BaseModel, Field


class Message(BaseModel):
    message: str


class FilterPage(BaseModel):
    start: int = Field(ge=0, default=0)
    ends: int = Field(ge=0, default=10)
