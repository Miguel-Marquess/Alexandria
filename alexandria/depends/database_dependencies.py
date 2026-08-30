from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from alexandria.database import get_session

Session = Annotated[AsyncSession, Depends(get_session)]
