import enum
from uuid import uuid4
from datetime import datetime

from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException
from sqlalchemy import Column, Integer, Enum, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db import Base, Model
from app.config import settings


# TODO: User comuling information: Complaints, solidarity by other Users ...


class UserSecurity:

    crypto = CryptContext(
        schemes=["bcrypt"], deprecated="auto"
    )

    scheme = OAuth2PasswordBearer(tokenUrl="token")

    def __init__(self, username, password, *args, **kwargs):
        self.username = username
        self.password = password + settings.secret

    async def authenticate(self):
        self.user = await User(
            username=self.username,
            status=UserStatus.ACTIVE
        ).one()
        if self.user is None:
            return False
        if not self.crypto.verify(self.password, self.user.hashed_password):
            return False
        return True

    @property
    def access_token(self):
        data = {
            "sub": self.user.username,
            "exp": datetime.utcnow() + settings.jwt_delta
        }
        return jwt.encode(
            data, settings.secret, algorithm=settings.sec_algorithm
        )

    @classmethod
    def to_hash(cls, password):
        return cls.crypto.hash(password + settings.secret)

    @staticmethod
    async def get_me(token: str = Depends(scheme)):
        try:
            payload = jwt.decode(
                token, settings.secret, algorithms=[settings.sec_algorithm]
            )
            username: str = payload.get("sub")
            if username is None:
                raise JWTError
            user = await User(username=username).one(join=(User.invite, ))
            if user is None:
                raise JWTError
            return user
        except JWTError:
            raise HTTPException(
                status_code=401,
                detail="Could not validate credentials",
            )


class UserStatus(enum.Enum):

    DISABLED = 0

    ACTIVE = 1


class User(Base, Model):

    __tablename__ = "user"

    username = Column(String(32), nullable=False, unique=True, index=True)

    hashed_password = Column(String(128), nullable=False)

    status = Column(Enum(UserStatus), nullable=False, default=UserStatus.ACTIVE)

    invite = relationship(
        "Invite", primaryjoin="User.id == Invite.to_id", uselist=False, lazy="selectin"
    )

    invites = relationship(
        "Invite", primaryjoin="User.id == Invite.from_id",
    )

    topics = relationship(
        "Topic", back_populates="user"
    )

    @property
    def public_id(self):
        return self.invite.code


class Invite(Base, Model):

    __tablename__ = "invite"

    code = Column(UUID(as_uuid=True), default=uuid4)

    from_id = Column(Integer, ForeignKey('user.id'))

    to_id = Column(Integer, ForeignKey('user.id'))

    @property
    def used(self):
        return self.to_id is not None

    async def save(self):
        # Disable sign up users without invite code.
        settings.is_bare = False
        return await super().save()

    async def one(self):
        if settings.is_bare:
            return await Invite().save()
        return await super().one()

    async def clone(self):
        if self.from_id is None:
            return None
        return await Invite(
            from_id=self.from_id,
            created_at=datetime.utcnow() + settings.invite_delta
        ).save()
