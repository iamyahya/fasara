import json

from alembic import op
import sqlalchemy as sa

from app.models import Chapter, Text
from app.models.book import Index


session = sa.orm.Session(bind=op.get_bind())

# TODO: After acreditation separate texts to another repository
# TODO: Grades for each hadith, with grade author. Ex: { name: Al-Albani, grade: Hasan Sahih }
# TODO: Text without tashkeel, to simplify Text search engine

GRADES = [
    "sahih",
    "hasan",
    "da'if",
      "maqlub",
      "shadh",
      "munkar",
      "mawdu'",
    "marfu'",
    "mawquf",
    "maqtu'"
]


def add_hadiths(filename, book, version):
    # TODO: Mark quote text from whole content
    with open(filename) as f:
        for _ in json.load(f):
            if "text" not in _:
                continue
            meta = {}
            if "narrated" in _:
                meta["narrated"] = _["narrated"]
            if "chapter" in _:
                meta["subchapter"] = _["chapter"]
            if "grade" in _:
                grade_full = _["grade"]
                for grade in GRADES:
                    if grade in grade_full:
                        meta["grade"] = grade
                        break
                else:
                    meta["grade"] = grade_full
            text = Text(content=_["text"])
            if len(meta):
                text.meta = meta
            version.texts.append(text)
            for chapter in version.chapters:
                if chapter.name == _["book"]:
                    break
            else:
                chapter = Chapter(name=_["book"])
                version.chapters.append(chapter)
            chapter.texts.append(text)
            for index in book.index:
                if index.chapter_number == len(version.chapters) and \
                    index.text_number == _["number"]:
                    break
            else:
                index = Index(
                    chapter_number=len(version.chapters),
                    text_number=_["number"]
                )
                book.index.append(index)
            chapter.index.append(index)
            index.texts.append(text)


def add_ayats(filename, book, version):
    # TODO: Add information about location for surahs. Ex.: Makkah or Medina
    with open(filename) as f:
        for _ in json.load(f):
            text = Text(content=_["ayat"])
            if "meta" in _:
                text.meta = _.get("meta")
            version.texts.append(text)
            for chapter in version.chapters:
                if chapter.name == _["surah"]:
                    break
            else:
                chapter = Chapter(name=_["surah"])
                version.chapters.append(chapter)
            chapter.texts.append(text)
            for index in book.index:
                if index.chapter_number == len(version.chapters) and \
                    index.text_number == _["number"]:
                    break
            else:
                index = Index(
                    chapter_number=len(version.chapters),
                    text_number=_["number"]
                )
                book.index.append(index)
            chapter.index.append(index)
            index.texts.append(text)
