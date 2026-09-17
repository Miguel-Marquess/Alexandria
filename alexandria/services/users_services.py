from dataclasses import dataclass

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from alexandria.exceptions.users_exceptions import EmailAlreadyExist
from alexandria.models.db_models import UserDatabase
from alexandria.schemas.users_schemas import UserSchema, UserUpdate
from alexandria.security import get_password_hash


@dataclass
class UserService:
    session: AsyncSession

    async def create_user(self, user_schema: UserSchema) -> UserDatabase:
        user = UserDatabase(
            **user_schema.model_dump(exclude={'password'}),
            password=get_password_hash(user_schema.password),
        )
        try:
            self.session.add(user)
            await self.session.commit()
        except IntegrityError:
            raise EmailAlreadyExist()

        await self.session.refresh(user)

        return user

    async def delete_user(self, current_user: UserDatabase) -> None:
        await self.session.delete(current_user)

    async def update_user(
        self, current_user: UserDatabase, user_update: UserUpdate
    ) -> UserDatabase:
        for key, value in user_update.model_dump(
            exclude_unset=True, exclude={'password'}
        ).items():
            setattr(current_user, key, value)

        if user_update.password:
            current_user.password = get_password_hash(user_update.password)

        await self.session.commit()
        await self.session.refresh(current_user)

        return current_user
