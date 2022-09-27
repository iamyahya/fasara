import enum

from sqlalchemy import (
    Column,
    Integer,
    Enum,
    ForeignKey,
    select,
    distinct
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import count

from app.db import Base, Model
from app.config import settings

from . import Text
from .book import IndexText


class ResponseStatus(enum.Enum):

    DRAFT = 0

    PUBLIC = 1


class Response(Base, Model):

    __tablename__ = "response"

    topic_id = Column(Integer, ForeignKey("topic.id"), index=True)

    user_id = Column(Integer, ForeignKey("user.id"), index=True)

    index_id = Column(Integer, ForeignKey("index.id"),  index=True)

    order = Column(Integer, nullable=False, default=0)

    status = Column(Enum(ResponseStatus), nullable=False, default=ResponseStatus.PUBLIC)

    user = relationship("User", lazy="selectin")

    index = relationship("Index", lazy="selectin")

    texts = relationship(
        "Text",
        secondary=IndexText,
        primaryjoin=index_id == IndexText.c.index_id,
        secondaryjoin=IndexText.c.text_id == Text.id,
        lazy="selectin",
        viewonly=True,
    )

    # async def fill_users(self, limit=settings.max_list):
    #     self.users = []
    #     query = self.__class__(
    #         index_id=self.index_id,
    #         topic_id=self.topic_id
    #     )._list_query_create(limit=limit)
    #     for response in await self._list_iems_prepare(query.order_by(self.__class__.created_at.asc())):
    #         if response.user not in self.users:
    #             self.users.append(response.user)
    #     return self

    # Extend base.Model class.
    # Response rows need to be grouped by index_id.

    async def list(
        self, *args, **kwargs
    ):
        query = self._list_query_create(*args, **kwargs)
        query = query.order_by(
            self.__class__.order.asc(), self.__class__.created_at.asc()
        ).distinct(self.__class__.order)
        return await self._list_iems_prepare(query)

    # async def save(self):
    #     return await (await super().save()).fill_users(99)
