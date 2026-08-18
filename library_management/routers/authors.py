from fastapi import APIRouter

from library_management.depends.authors_dependencies import T_AuthorFilter
from library_management.depends.database_dependencies import Session
from library_management.depends.users_dependencies import Current_user
from library_management.schemas.authors_schemas import (
    AuthorPublic,
    AuthorSchema,
    AuthorsList,
)
from library_management.schemas.core_schemas import Message
from library_management.services.authors_service import AuthorService

router = APIRouter(tags=['authors'], prefix='/authors')


@router.get('/', response_model=AuthorsList, status_code=200)
async def read_authors(
    author_filter: T_AuthorFilter,
    session: Session,
    user: Current_user,
):
    return {'authors': await AuthorService(session).read_authors(author_filter)}


@router.post('/', status_code=201, response_model=AuthorPublic)
async def create_author(author: AuthorSchema, user: Current_user, session: Session):
    return await AuthorService(session).create_author(author)


@router.delete('/{author_id}', status_code=200, response_model=Message)
async def delete_author(author_id: int, user: Current_user, session: Session):
    await AuthorService(session).delete_author(author_id)
    return {'message': 'Author was deleted.'}
