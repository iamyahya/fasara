from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.db import Base, Model


class Complaint(Base, Model):

    __tablename__ = "complaint"

    user_id = Column(Integer, ForeignKey('user.id'), index=True, nullable=False)

    topic_id = Column(Integer, ForeignKey('topic.id'), index=True, nullable=False)

    user = relationship("User")
