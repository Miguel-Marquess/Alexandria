from typing import Annotated

from fastapi import Query

from alexandria.schemas.loans_schemas import LoanFilter

FilterLoan = Annotated[LoanFilter, Query()]
