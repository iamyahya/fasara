import enum

from sqlalchemy import (
    Column,
    Integer,
    SmallInteger,
    Text,
    String,
    ForeignKey,
    Enum,
    Table
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.db import Base, Model


class Language(enum.Enum):

    AR = 'ar'

    EN = 'en'

    RU = 'ru'


class BookType(enum.Enum):

    QURAN = "quran"

    SAHIH = "sahih"


class ChapterType(enum.Enum):

    SURAH = "surah"

    CHAPTER = "chapter"


class TextType(enum.Enum):

    AYAT = "ayat"

    HADITH = "hadith"



class Book(Base, Model):

    __tablename__ = "book"

    title = Column(String, index=True, nullable=False, unique=True)

    versions = relationship("Version", back_populates="book", lazy="selectin")

    index = relationship("Index", back_populates="book", lazy="selectin")

    @property
    def order(self):
        return self.id

    @property
    def languages(self):
        return [ v.language for v in self.versions ]


class Version(Base, Model):

    __tablename__ = "version"

    language = Column(Enum(Language), nullable=False, default=Language.AR, index=True)

    book_id = Column(Integer, ForeignKey("book.id"), index=True)

    book = relationship("Book", back_populates="versions", lazy="selectin")

    chapters = relationship("Chapter", back_populates="version")

    texts = relationship("Text", back_populates="version")


IndexChapter = Table(
    'index_chapter',
    Base.metadata,
    Column('index_id', Integer, ForeignKey('index.id')),
    Column('chapter_id', Integer, ForeignKey('chapter.id')),
)


IndexText = Table(
    'index_text',
    Base.metadata,
    Column('index_id', Integer, ForeignKey('index.id')),
    Column('text_id', Integer, ForeignKey('text.id')),
)


class Index(Base, Model):

    __tablename__ = "index"

    book_id = Column(Integer, ForeignKey("book.id"), index=True)

    chapter_number = Column(SmallInteger, nullable=False, index=True)

    text_number = Column(SmallInteger, nullable=False, index=True)

    book = relationship("Book", back_populates="index", lazy="selectin")

    chapters = relationship("Chapter", secondary=IndexChapter, back_populates="index")

    texts = relationship("Text", secondary=IndexText, back_populates="index")


class Chapter(Base, Model):

    __tablename__ = "chapter"

    name = Column(String, nullable=False)

    version_id = Column(Integer, ForeignKey("version.id"), index=True)

    version = relationship("Version", back_populates="chapters")

    # TODO: Add ordering for next attribue Text.index.text_number
    texts = relationship("Text", back_populates="chapter")

    index = relationship("Index", secondary=IndexChapter, back_populates="chapters", lazy="selectin")

    @property
    def number(self):
        return self.index[0].chapter_number

    @property
    def type(self):
        if self.version.book.title == "quran":
            return ChapterType.SURAH
        return ChapterType.CHAPTER

    @property
    def structure(self):
        # TODO: Add total count of texts in the chapter
        result = {
            "book": self.version.book.title,
            "language": self.version.language
        }
        return result


class Text(Base, Model):

    __tablename__ = "text"

    content = Column(Text, nullable=False)

    meta = Column(JSONB)

    chapter_id = Column(Integer, ForeignKey("chapter.id"), index=True)

    version_id = Column(Integer, ForeignKey("version.id"), index=True)

    chapter = relationship("Chapter", back_populates="texts", lazy="selectin")

    version = relationship("Version", back_populates="texts", lazy="selectin")

    index = relationship("Index", secondary=IndexText, back_populates="texts", lazy="selectin", uselist=False)

    @property
    def type(self):
        if self.version.book.title == "quran":
            return TextType.AYAT
        return TextType.HADITH

    @property
    def structure(self):
        keys = {
            TextType.AYAT: ChapterType.SURAH,
            TextType.HADITH: ChapterType.CHAPTER
        }
        return {
            "book": {
                "title": self.version.book.title,
                "language": self.version.language,
            },
            keys[self.type]: {
                "number": self.index.chapter_number,
                "name": self.chapter.name,
            }
        }

    @property
    def number(self):
        return self.index.text_number
