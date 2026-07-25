from typing import Annotated

from fastapi import Query

from library_management.schemas.loans_schemas import LoanFilter

FilterLoan = Annotated[LoanFilter, Query()]
