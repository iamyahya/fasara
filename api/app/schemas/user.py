from uuid import UUID, uuid4
from typing import Optional, List
from datetime import datetime

from pydantic import BaseModel, MissingError, validator

from app.config import settings


class SignUp(BaseModel):

    code: Optional[UUID]

    username: str

    password: str

    # TODO: Validate password complexity

    @validator("code", pre=True, always=True)
    def validate_invite(cls, value):
        if settings.is_bare:
            return uuid4()
        if value is None:
            raise MissingError
        try:
            UUID(value, version=4)
        except ValueError as err:
            raise TypeError(err)
        return value


class Invite(BaseModel):

    code: UUID

    used: bool

    class Config:
        orm_mode = True


class InviteList(BaseModel):

    page: int

    total: int

    results: List[Invite] = []


class User(BaseModel):

    username: str

    public_id: UUID

    class Config:
        orm_mode = True


class Author(BaseModel):

    public_id: UUID

    class Config:
        orm_mode = True

