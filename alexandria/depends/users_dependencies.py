from typing import Annotated

from fastapi import Depends

from alexandria.models.db_models import UserDatabase
from alexandria.security import get_current_user

Current_user = Annotated[UserDatabase, Depends(get_current_user)]
