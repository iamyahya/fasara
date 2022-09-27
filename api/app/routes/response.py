from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy import select
from sqlalchemy import func as fn

from app.schemas import ResponseCreate, ResponseList, ResponsePublic
from app.models import User, Topic, Response, Book
from app.models.user import UserSecurity
from app.models.topic import TopicStatus

from app.db.base import Model


# TODO: Add Response delete and Response Users list routes

router = APIRouter()


@router.get("/response/{topic_id}", response_model=ResponseList)
async def route_list_responses(topic_id: int, page: int = 1):
    if not await Topic(
        id=topic_id,
        status=TopicStatus.PUBLIC
    ).count():
        raise HTTPException(404, "Topic not found")
    where = (Response.topic_id == topic_id,)
    results = await Response().list(
        offset=page - 1, where=where
    )
    query = select(fn.count(), Response.index_id) \
              .group_by(Response.index_id) \
              .filter(Response.topic_id == topic_id)
    async for session in Model.get_session():
        totals = {
            i: t for t, i in await session.execute(query)
        }
    for response in results:
        response.doubles = totals[response.index_id] - 1
    return {
        "page": page,
        "total": await Response().count(where=where),
        "results": results
    }


@router.post("/response/{topic_id}", response_model=ResponsePublic)
async def route_create_response(
    topic_id: int,
    form: ResponseCreate,
    user: User = Depends(UserSecurity.get_me),
):
    topic = await Topic(
        id=topic_id,
        status=TopicStatus.PUBLIC
    ).one()
    if not topic:
        raise HTTPException(404, "Topic not found")
    book = await Book(title=form.book_title).one()
    BOOKS_TOTAL = 7 # Quran + Kutub al-Sittah
    if not book:
        raise HTTPException(422, "Book not found")
    for index in book.index:
        if index.chapter_number == form.chapter_number and \
            index.text_number == form.text_number:
            attrs = {
                "topic_id": topic.id,
                "user_id": user.id,
                "index_id": index.id,
                "order": int(f"{10+index.book_id}{100+index.chapter_number}{1000+index.text_number}")
            }
            if await Response(**attrs).count():
                raise HTTPException(422, "Response already exist")
            return await Response(**attrs).save()
    raise HTTPException(422, "Index not found")
