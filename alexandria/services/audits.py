from typing import Any

from alexandria.models.db_models import UserDatabase


def set_created_audits(user: UserDatabase, obj: Any) -> None:
    obj.created_by = user.id


def set_updated_audits(user: UserDatabase, objects: list[Any]) -> None:
    for obj in objects:
        obj.updated_by = user.id
