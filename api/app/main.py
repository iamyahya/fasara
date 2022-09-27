from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.models import Invite
from app.routes import *


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    # TODO: Move origins to the env
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# TODO: Books, Chapters, Texts caching logic
for route in routes:
    app.include_router(route)


@app.on_event("startup")
async def startup():
    if await Invite().count():
        settings.is_bare = False
