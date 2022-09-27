from fastapi import APIRouter, HTTPException

from app.schemas import BookList, VersionOpen, ChapterOpen, TextOpen
from app.models import Book, Version, Chapter, Text, Index
from app.models.book import Language, BookType, ChapterType


router = APIRouter()

CACHE = {
    "list": [],
    "chapters": {}
}


@router.get("/hadith", response_model=BookList)
async def route_list_books():
    if not len(CACHE["list"]):
        CACHE["list"].extend(
            await Book().list(
                join=(
                    Book.versions,
                ),
                where=(
                    Book.title != "quran",
                ),
                limit=None
            )
        )
    return {
        "results": CACHE["list"]
    }


@router.get("/hadith/{title}:{language}//{text_number}", response_model=TextOpen)
async def route_open_hadith(title: str, language: Language, text_number: int):
    text = await Text().one(
        join=(
            Text.version,
            Text.index
        ),
        where=(
            Version.language == language,
            Version.book.has(title=title),
            Text.index.has(text_number=text_number)
        )
    )
    if not text:
        raise HTTPException(404, "Text not found")
    return text


@router.get("/hadith/{title}:{language}/{chapter_number}", response_model=ChapterOpen)
async def route_open_chapter(title: str, language: Language, chapter_number: int):
    results = await Text().list(
        join=(
            Text.version,
            Text.index
        ),
        where=(
            Version.language == language,
            Version.book.has(title=title),
            Index.chapter_number == chapter_number
        ),
        limit=None
    )
    if not results:
        raise HTTPException(404, "Chapter not found")
    return {
        "number": chapter_number,
        "type": ChapterType.CHAPTER,
        "name": results[0].chapter.name,
        "structure": results[0].chapter.structure,
        "results": results
    }


@router.get("/hadith/{title}:{language}", response_model=VersionOpen)
async def route_open_version(title: str, language: Language):
    if language not in CACHE["chapters"]:
        CACHE["chapters"][language] = {}
    if title not in CACHE["chapters"][language]:
        CACHE["chapters"][language][title] = await Chapter().list(
            join=(
                Chapter.version,
                Version.book,
            ),
            where=(
                Chapter.version.has(language=language),
                Version.book.has(title=title)
            ),
            limit=None
        )
    return {
        "type": BookType.SAHIH,
        "language": language,
        "results": CACHE["chapters"][language][title]
    }
