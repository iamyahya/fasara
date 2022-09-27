from typing import List, Dict, Optional

from pydantic import BaseModel

from app.models.book import Language, TextType, ChapterType, BookType


class Book(BaseModel):

    order: int

    title: str

    languages: List[Language] = []

    class Config:
        orm_mode = True


class BookList(BaseModel):

    results: List[Book] = []


class Chapter(BaseModel):

    number: int

    type: ChapterType

    name: str

    class Config:
        orm_mode = True


class VersionOpen(BaseModel):

    type: BookType

    language: Language

    results: List[Chapter] = []


class Text(BaseModel):

    number: int

    type: TextType

    meta: Optional[Dict]

    content: str

    class Config:
        orm_mode = True


class ChapterOpen(BaseModel):

    number: int

    type: ChapterType

    name: str

    structure: Dict

    results: List[Text] = []


class TextOpen(Text):

    structure: Dict
