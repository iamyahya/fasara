from fastapi import APIRouter, HTTPException

from app.schemas import BookList, VersionOpen, ChapterOpen, TextOpen
from app.models import Book, Version, Chapter, Text, Index
from app.models.book import Language, ChapterType, BookType


router = APIRouter()

CACHE = {
    "list": [],
    "chapters": {}
}


@router.get("/quran", response_model=BookList)
async def route_list_books():
    if not len(CACHE["list"]):
        CACHE["list"].extend(
            await Book().list(
                join=(
                    Book.versions,
                ),
                where=(
                    Book.title == "quran",
                ),
                limit=None
            )
        )
    return {
            "results": CACHE["list"]
    }


@router.get("/quran:{language}/{chapter_number}/{text_number}", response_model=TextOpen)
async def route_open_ayat(language: Language, chapter_number: int, text_number: int):
    text = await Text().one(
        join=(
            Text.version,
            Text.index
        ),
        where=(
            Version.language == language,
            Version.book.has(title="quran"),
            Text.index.has(
                chapter_number=chapter_number,
                text_number=text_number
            )
        )
    )
    if not text:
        raise HTTPException(404, "Text not found")
    return text


@router.get("/quran:{language}/{chapter_number}", response_model=ChapterOpen)
async def route_open_version(language: Language, chapter_number: int):
    results = await Text().list(
        join=(
            Text.version,
            Text.index
        ),
        where=(
            Version.language == language,
            Version.book.has(title="quran"),
            Index.chapter_number == chapter_number
        ),
        limit=None
    )
    if not results:
        raise HTTPException(404, "Chapter not found")
    return {
        "number": chapter_number,
        "type": ChapterType.SURAH,
        "name": results[0].chapter.name,
        "structure": results[0].chapter.structure,
        "results": results,
    }


@router.get("/quran:{language}", response_model=VersionOpen)
async def route_open_version(language: Language):
    if language not in CACHE["chapters"]:
        CACHE["chapters"][language] = await Chapter().list(
            join=(
                Chapter.version,
                Version.book,
            ),
            where=(
                Chapter.version.has(language=language),
                Version.book.has(title="quran")
            ),
            limit=None
        )
    return {
        "type": BookType.QURAN,
        "language": language,
        "results": CACHE["chapters"][language]
    }
