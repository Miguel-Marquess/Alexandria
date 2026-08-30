from fastapi import APIRouter

from alexandria.depends.authors_dependencies import T_AuthorFilter
from alexandria.depends.database_dependencies import Session
from alexandria.depends.users_dependencies import Current_user
from alexandria.schemas.authors_schemas import (
    AuthorPublic,
    AuthorSchema,
    AuthorsList,
)
from alexandria.schemas.core_schemas import Message
from alexandria.services.authors_service import AuthorService

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
