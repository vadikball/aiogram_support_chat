from typing import Callable, Any, Optional, Union

from aiogram import types
from sqlalchemy import MetaData, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.ext.asyncio import AsyncConnection

from settings import Settings
from .models import User
from .base import Base

settings = Settings()

engine_kwargs = {
    'echo': True,
    'encoding': 'utf-8',
}

Engine = create_async_engine(url=settings.db_str, **engine_kwargs)

SessionMaker = sessionmaker(Engine, class_=AsyncSession)

session = SessionMaker(expire_on_commit=False)


async def proceed_session(func: Callable, **kwargs) -> Any:
    async with SessionMaker() as session:
        session: AsyncSession
        async with session.begin():
            result = await func(session, **kwargs)
    return result


async def proceed_schemas(
        engine: AsyncEngine = Engine,
        metadata: MetaData = Base.metadata
) -> None:
    async with engine.connect() as connection:
        connection: AsyncConnection
        await connection.run_sync(metadata.create_all)
        await connection.commit()
    await connection.close()


async def create_user(session: AsyncSession, user: User):
    await session.merge(user)


async def get_user(session: AsyncSession, user_id: int) -> Optional[User]:
    return (await session.scalar(select(User).where(User.user_id == user_id))).__dict__


async def get_user_active(session: AsyncSession, user_id: int) -> Optional[bool]:

    return await session.scalar(select(User.active).where(User.user_id == user_id))


async def get_user_phone(session: AsyncSession, user_id: int) -> str:
    return await session.scalar(select(User.phone_number).where(User.user_id == user_id))


async def change_user(session: AsyncSession, message: types.Message, key: str):
    user = await session.scalar(select(User).where(User.user_id == message.from_user.id))
    setattr(user, key, message.text)


async def change_user_admin(session: AsyncSession, user_id, key: str, value: Optional[Union[str, int, bool]]):
    user = await session.scalar(select(User).where(User.user_id == user_id))
    setattr(user, key, value)


async def get_active_users_id(session: AsyncSession) -> list[int]:
    return await session.scalars(select(User.user_id).where(User.active == True))


async def get_users_filter_active(session: AsyncSession, active: bool) -> tuple[User]:
    return tuple(await session.scalars(select(User).where(User.active == active)))


async def get_all_users(session: AsyncSession) -> tuple[Any]:
    return tuple(await session.scalars(select(User)))


async def get_user_with_query(session: AsyncSession, query: Any) -> Any:
    return await session.scalar(query)
