from datetime import datetime
from typing import List

from fastapi import Depends, APIRouter, HTTPException

from app.schemas import InviteList, UserMe, TopicPublic, TopicList
from app.models import User, Topic, Invite
from app.models.user import UserSecurity
from app.models.topic import TopicStatus


router = APIRouter()


@router.get("/user", response_model=UserMe)
async def route_me(
    user: User = Depends(UserSecurity.get_me),
):
    return user


@router.get("/user/invite", response_model=InviteList)
async def route_invites(
    user: User = Depends(UserSecurity.get_me),
    page: int = 1
):
    where = [
        Invite.from_id == user.id,
        Invite.created_at <= datetime.utcnow()
    ]
    return {
        "page": page,
        "total": await Invite().count(where=where),
        "results": await Invite().list(
            offset=page - 1, where=where
        )
    }


@router.get("/user/topic", response_model=TopicList)
async def route_topics(
    user: User = Depends(UserSecurity.get_me),
    q: str = None,
    page: int = 1
):
    where = [
        Topic.user_id == user.id,
        Topic.status != TopicStatus.MODERATION
    ]
    if q is not None:
        where.append(Topic.text.contains(q))
    return {
        "page": page,
        "total": await Topic().count(where=where),
        "results": await Topic().list(
            offset=page - 1, where=where
        )
    }


@router.get("/user/topic/{id_}", response_model=TopicPublic)
async def route_topics(
    id_: int,
    user: User = Depends(UserSecurity.get_me),
):
    topic = await Topic(user_id=user.id).one(where=[Topic.status != TopicStatus.MODERATION])
    if not topic:
        raise HTTPException(404, "Topic not found")
    return topic
