import pytest
import asyncio

from httpx import AsyncClient

from app.db.base import setup_test_db
from app.config import settings
from app.main import app

from app.models import (
    Book,
    Version,
    Chapter,
    Text,
    User,
    Index
)
from app.models.book import Language


@pytest.fixture(scope="function")
async def client():
    await setup_test_db()
    settings.is_bare = True
    settings.max_complaints = 0
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def userform():
    yield {
        "username": "username",
        "password": "password"
    }

@pytest.fixture(scope="function")
async def hadith():
    book = Book(title="title")
    index = Index(chapter_number=0, text_number=0)
    book.index.append(index)
    version = Version(language=Language.AR)
    chapter = Chapter(name="name")
    chapter.index.append(index)
    text = Text(content="content", meta={"narrated": "firstname"})
    index.texts.append(text)
    chapter.texts.append(text)
    version.texts.append(text)
    version.chapters.append(chapter)
    book.versions.append(version)
    await book.save()


async def generate_access_token(client):
    userform = {
        "username": "username",
        "password": "password"
    }
    await client.post("/sign-up", json=userform)
    return (
        await client.post("/sign-in", data=userform)
    ).json().get("access_token")




# TODO: Test for Quran and Complaint routes
# TODO: Test import logic
