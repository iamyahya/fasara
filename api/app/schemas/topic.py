from typing import Optional, List

from pydantic import BaseModel

from app.models.topic import TopicStatus

from .complaint import Complaint
from . import *


class Topic(BaseModel):

    # TODO: Count of Responses and Complaints

    id: int

    created: str

    text: str

    status: TopicStatus

    user: Author

    complaints: List[Complaint] = []

    class Config:
        orm_mode = True


class Create(BaseModel):

    # TODO: Validate Topic.text lenght
    text: str

    status: Optional[TopicStatus] = TopicStatus.DRAFT


class List(BaseModel):

    page: int

    total: int

    results: List[Topic] = []
