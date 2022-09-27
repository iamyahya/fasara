import enum

from sqlalchemy import Column, Integer, Enum, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.db import Base, Model


# TODO: Add Categories and Tags for Topics


class TopicStatus(enum.Enum):

    DRAFT = 0

    MODERATION = 1

    PUBLIC = 2


class Topic(Base, Model):

    __tablename__ = "topic"

    user_id = Column(Integer, ForeignKey('user.id'), index=True, nullable=False)

    text = Column(Text, nullable=False)

    status = Column(Enum(TopicStatus), nullable=False, default=TopicStatus.PUBLIC)

    user = relationship("User", lazy="selectin")

    complaints = relationship("Complaint", lazy="selectin", backref="topic")
