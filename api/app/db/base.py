from datetime import datetime

import asyncpg
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.sql.functions import count, now
from sqlalchemy import Column, Integer, DateTime, select
from sqlalchemy.exc import InvalidRequestError
import alembic.config

from app.config import settings


Base = declarative_base()

_engine = create_async_engine(
    settings.db_dsn, future=True, echo=False,
)


class Model:

    id = Column(Integer, primary_key=True, autoincrement=True)

    created_at = Column(DateTime, server_default=now())

    updated_at = Column(DateTime, onupdate=now())

    @property
    def created(self):
        """ Prevent matching users by entity creation time. """
        days = (datetime.now() - self.created_at).days
        if days == 0:
            return "today"
        if days < 7:
            return f"{days} day(s) ago"
        if days < 30:
            return f"{days // 7} week(s) ago"
        if days < 365:
            return f"{days // 30} month(s) ago"
        return f"{days // 365} year(s) ago"

    @staticmethod
    async def get_session() -> AsyncSession:
        async_session = sessionmaker(
            _engine, class_=AsyncSession, expire_on_commit=False
        )
        async with async_session() as session:
            yield session

    @property
    def __args__(self):
        attrs = {}
        for key in self.__class__.__table__.columns:
            value = getattr(self, key.name)
            if value is not None:
                attrs[key.name] = value
        return attrs

    async def count(self, where=()):
        query = select(count()) \
                    .select_from(self.__class__) \
                    .filter_by(**self.__args__)
        for c in where:
            query = query.filter(c)
        async for session in self.get_session():
            return await session.scalar(query)

    async def save(self):
        async for session in self.get_session():
            try:
                session.add(self)
            except InvalidRequestError:
                self = await session.merge(self)
                session.add(self)
            await session.commit()
            await session.refresh(self)
            return self

    def _list_query_create(
        self, limit=settings.max_list, offset=0, where=(), join=()
    ):
        query = select(self.__class__) \
                .group_by(self.__class__.id) \
                .filter_by(**self.__args__) \
                .limit(limit) \
                .offset(offset * limit if limit else 0)
        for j in join:
            query = query.join(j)
        for c in where:
            query = query.filter(c)
        return query

    async def _list_iems_prepare(self, query):
        query = query.order_by(self.__class__.created_at.desc())
        limit = query._limit_clause
        if limit is not None:
            limit = limit.value
        async for session in self.get_session():
            try:
                items = [
                    item[self.__class__]
                    for item in await session.execute(query)
                ]
                return items[0] if limit == 1 else items
            except:
                return None if limit == 1 else []

    async def list(self, *args, **kwargs):
        query = self._list_query_create(*args, **kwargs)
        return await self._list_iems_prepare(query)

    async def one(self, where=(), join=()):
        return await self.list(limit=1, where=where, join=join)


async def setup_test_db():
    db_dsn = settings.db_dsn
    db_dsn = db_dsn.replace("+asyncpg", "")
    db_dsn = db_dsn.replace("test", "template1")
    try:
        sys_connect = await asyncpg.connect(db_dsn)
        # await sys_connect.execute("DROP DATABASE test;")
        await sys_connect.execute("CREATE DATABASE test;")
        await sys_connect.close()
    except:
        pass
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
