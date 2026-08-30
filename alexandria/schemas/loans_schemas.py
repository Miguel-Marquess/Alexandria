from datetime import datetime
from enum import Enum
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict, computed_field

from alexandria.schemas.core_schemas import FilterPage


class LoanStatus(str, Enum):
    ACTIVE = 'active'
    RETURNED = 'returned'


class LoanSchema(BaseModel):
    book_isbn: str


class LoanPublic(BaseModel):
    id: int
    user_id: int
    book_id: int
    loan_date: datetime
    due_date: datetime
    returned_at: datetime | None = None
    status: LoanStatus

    @computed_field  # permite property serializaveis
    @property  # trata metodo como atributo
    def is_overdue(self) -> bool:
        return self.status == LoanStatus.ACTIVE and self.due_date < datetime.now(
            tz=ZoneInfo('UTC')
        )

    model_config = ConfigDict(from_attributes=True)


class LoanList(BaseModel):
    loans: list['LoanPublic']

    model_config = ConfigDict(from_attributes=True)


class LoanFilter(FilterPage):
    status: LoanStatus | None = None
    book_id: int | None = None
    overdue: bool | None = None
