from typing import Optional, List, Dict

from pydantic import BaseModel

from app.models.book import Language

from . import Author, TextOpen


class Response(BaseModel):

    id: int

    created: str

    user: Author

    doubles: int = 0

    texts: List[TextOpen]

    class Config:
        orm_mode = True


class Create(BaseModel):

    book_title: str

    chapter_number: int

    text_number: int


class List(BaseModel):

    page: int

    total: int

    results: List[Response] = []

