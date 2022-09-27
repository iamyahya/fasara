from pydantic import BaseModel

from . import Author


class Complaint(BaseModel):

    created: str

    user: Author

    class Config:
        orm_mode=True
