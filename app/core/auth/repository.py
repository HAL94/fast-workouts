from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_async_session
from app.core.database.base_repo import BaseRepo
from app.models import User

from .schema import UserRead


def get_user_repo(db: AsyncSession = Depends(get_async_session)):
    return UserRepository(session=db)


class UserRepository(BaseRepo[User, UserRead]):
    __dbmodel__ = User
    __model__ = UserRead
