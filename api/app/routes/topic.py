from fastapi import Depends, APIRouter, HTTPException

from app.schemas import TopicPublic, TopicCreate, TopicList
from app.models import User, Topic, Complaint
from app.models.user import UserSecurity
from app.models.topic import TopicStatus
from app.config import settings


# TODO: Add following to Topic


router = APIRouter()


@router.post("/topic", response_model=TopicPublic)
async def route_create_topic(
    form: TopicCreate,
    user: User = Depends(UserSecurity.get_me),
):
    return await Topic(
        **form.dict(), user_id=user.id
    ).save()


@router.get("/topic", response_model=TopicList)
async def route_list_topics(q: str = None, page: int = 1):
    # TODO: Add sorting parameter - last, popular
    where = [Topic.status == TopicStatus.PUBLIC]
    if q is not None:
        where.append(Topic.text.contains(q))
    return {
        "page": page,
        "total": await Topic().count(where=where),
        "results": await Topic().list(
            offset=page - 1, where=where
        )
    }


@router.get("/topic/{id_}", response_model=TopicPublic)
async def route_get_topic(id_: int):
    topic = await Topic(
        id=id_, status=TopicStatus.PUBLIC
    ).one()
    if topic is None:
        raise HTTPException(
            status_code=404, detail="Topic not found",
        )
    return topic


@router.put("/topic/{id_}", response_model=TopicPublic)
async def route_update_topic(
    form: TopicCreate,
    id_: int,
    user: User = Depends(UserSecurity.get_me),
):
    topic = await Topic(
        id=id_, status=TopicStatus.DRAFT, user_id=user.id
    ).one()
    if topic is None:
        raise HTTPException(
            status_code=404, detail="Topic not found",
        )
    topic.text = form.text
    topic.status = form.status
    await topic.save()
    return topic


@router.delete("/topic/{id_}")
async def route_delete_topic(
    id_: int,
    user: User = Depends(UserSecurity.get_me),
):
    topic = await Topic(
        id=id_, status=TopicStatus.PUBLIC
    ).one()
    if topic is None:
        raise HTTPException(
            status_code=404, detail="Topic not found",
        )
    if len(topic.complaints) == settings.max_complaints:
        topic.status = TopicStatus.MODERATION
    elif user.id in [_.user_id for _ in topic.complaints]:
        raise HTTPException(
            status_code=409, detail="Complaint already exists",
        )
    else:
        topic.complaints.append(
            Complaint(user_id=user.id)
        )
    await topic.save()
