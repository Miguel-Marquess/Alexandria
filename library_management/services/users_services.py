from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from library_management.models.db_models import UserDatabase
from library_management.schemas.users_schemas import UserSchema, UserUpdate
from library_management.security import get_password_hash


@dataclass
class UserService:
    session: AsyncSession

    async def create_user(self, user_schema: UserSchema) -> UserDatabase:
        user = UserDatabase(
            **user_schema.model_dump(exclude={'password'}),
            password=get_password_hash(user_schema.password),
        )

        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)

        return user

    async def delete_user(self, current_user: UserDatabase) -> dict:
        await self.session.delete(current_user)
        return {'message': 'User was deleted.'}

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
